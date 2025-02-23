import streamlit as st
import requests
from backend.database import get_database
from backend.interactions import fetch_smiles, get_interaction
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3000")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize database
db = get_database()
interactions_collection = None
if db is not None:
    collection_name = os.getenv('COLLECTION_NAME', 'drug_interaction')
    interactions_collection = db[collection_name]

# Streamlit UI setup
st.set_page_config(page_title="Medicine Interaction Checker", layout="centered")

# Custom CSS for UI enhancements
st.markdown("""
    <style>
        .title {
            font-size: 26px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 15px;
        }
        .custom-input {
            font-size: 18px;
            padding: 14px;
            width: 100%;
            border-radius: 8px;
            border: 1px solid #ccc;
            margin-right: 10px;
        }
        .custom-container {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .custom-button {
            padding: 14px 24px;
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        .custom-button:hover {
            background-color: #45a049;
        }
        .interaction-container {
            border: 2px solid #ff9966;
            border-radius: 10px;
            padding: 20px;
            background-color: #fff3e6;
            margin-top: 15px;
            text-align: center;
        }
        .no-interaction-container {
            border: 2px solid #4CAF50;
            border-radius: 10px;
            padding: 20px;
            background-color: #e8f5e9;
            margin-top: 15px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Page Title
st.markdown('<div class="title">Medicine Interaction Checker</div>', unsafe_allow_html=True)

# Input field & button layout in a responsive design
col1, col2 = st.columns([5, 1])
with col1:
    medicine_name = st.text_input(
        "",
        placeholder="Enter a medicine to check interactions",
        key="medicine_name",
        label_visibility="collapsed",
    )
with col2:
    search_button = st.button("Check", key="search_button")

def get_side_effects_description(side_effects):
    """Uses Gemini AI to simplify side effects into a patient-friendly description."""
    try:
        prompt = f"Describe these side effects in simple, clear terms: {side_effects}"
        response = requests.post(
            "https://api.gemini.com/v1/completions",
            headers={"Authorization": f"Bearer {GEMINI_API_KEY}"},
            json={"prompt": prompt, "max_tokens": 150, "temperature": 0.7}
        )
        response_data = response.json()
        return response_data.get("choices", [{}])[0].get("text", "").strip() or side_effects
    except Exception:
        return side_effects  # Return original if Gemini API fails

def check_interactions(medicine_name):
    """Checks for drug interactions and displays results with enhanced UI."""
    if interactions_collection is None:
        st.error("Database connection error. Please check the server.")
        return

    smiles = fetch_smiles(medicine_name)
    if not smiles:
        st.error(f"Could not fetch SMILES for {medicine_name}.")
        return

    state = type('State', (object,), {})()
    state.drug1 = medicine_name
    state.drug2 = None

    if 'medications' not in st.session_state:
        st.markdown('<div class="no-interaction-container">No medications saved. Add medications first.</div>', unsafe_allow_html=True)
        return

    medications = st.session_state.medications
    processed_meds = set()
    
    for med in medications:
        med = med.strip()
        if med in processed_meds:
            continue
        
        processed_meds.add(med)
        state.drug2 = med
        get_interaction(state, interactions_collection)

        if hasattr(state, 'result'):
            result = state.result
            
            if "Interaction found" in result:
                raw_side_effects = result.split(":")[1].strip()
                simplified_effects = get_side_effects_description(raw_side_effects)
                
                st.markdown(f"""
                    <div class="interaction-container">
                        <h3>Interaction Found</h3>
                        <p><strong>{medicine_name} and {med}</strong></p>
                        <p><strong>Side Effects:</strong> {simplified_effects}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Video generation
                payload = {
                    "drug1": medicine_name,
                    "drug2": med,
                    "smiles1": smiles,
                    "smiles2": fetch_smiles(med),
                    "sideEffects": result
                }
                
                try:
                    response = requests.post(f"{BACKEND_URL}/generate-video", json=payload)
                    if response.ok:
                        video_url = response.json().get("videoUrl")
                        if video_url:
                            if st.button("Watch Animation", key=f"watch_button_{med}"):
                                st.video(video_url)
                        else:
                            st.button("Generating Video...", key=f"generating_button_{med}", disabled=True)
                except Exception:
                    st.button("Video Generation Failed", key=f"failed_button_{med}", disabled=True)
            else:
                st.markdown(f"""
                    <div class="no-interaction-container">
                        <p>No interaction found between {medicine_name} and {med}</p>
                    </div>
                """, unsafe_allow_html=True)

# Button to trigger interaction check
if search_button:
    if medicine_name:
        check_interactions(medicine_name)
    else:
        st.error("Please enter a medicine name to check interactions.")
