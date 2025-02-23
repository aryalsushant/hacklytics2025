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

# Initialize database and collection
db = get_database()
interactions_collection = None
if db is not None:
    collection_name = os.getenv('COLLECTION_NAME', 'drug_interaction')
    interactions_collection = db[collection_name]

# Streamlit UI setup
st.set_page_config(page_title="Medicine Interaction Checker", layout="centered")
st.title("Medicine Interaction Checker")
st.write("Enter the name of the medicine you want to learn about and check for interactions.")

# Input field for medicine search with button inline
col1, col2 = st.columns([5, 1])
with col1:
    medicine_name = st.text_input("Enter Medicine Name", placeholder="e.g., Ibuprofen", 
                                  label_visibility="collapsed", key="medicine_name", 
                                  help="Enter the name of the medicine you want to search for interactions with.")
with col2:
    search_button = st.button("See Interactions", key="search_button")

def get_side_effects_description(side_effects):
    """Generate a simplified description of side effects using Gemini AI."""
    try:
        prompt = f"Explain the following drug side effects in simple terms for a patient:\n{side_effects}"
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText",
            headers={"Content-Type": "application/json"},
            params={"key": GEMINI_API_KEY},
            json={"prompt": {"text": prompt}, "temperature": 0.7, "maxOutputTokens": 150}
        )
        response_data = response.json()
        return response_data.get("candidates", [{}])[0].get("output", "").strip()
    except Exception as e:
        return side_effects  # Fall back to original text if API fails

def check_interactions(medicine_name):
    """Check for medicine interactions."""
    if interactions_collection is None:
        st.error("Database connection error. Please check server logs.")
        return

    smiles = fetch_smiles(medicine_name)
    if not smiles:
        st.error(f"Could not fetch SMILES for {medicine_name}.")
        return

    state = type('State', (object,), {})()
    state.drug1 = medicine_name
    state.drug2 = None

    if 'medications' not in st.session_state:
        st.markdown("""
            <div style="border: 2px solid #4CAF50; border-radius: 8px; padding: 15px;">
                <p>No medications saved in your profile. Please add medications first.</p>
            </div>
        """, unsafe_allow_html=True)
        return

    medications = st.session_state.medications
    interaction_container = st.container()

    # Process each medication only once
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
                # Extract side effects and get simplified description
                raw_side_effects = result.split(":")[1].strip()
                simplified_effects = get_side_effects_description(raw_side_effects)
                
                # Display single interaction block
                with interaction_container:
                    st.markdown(f"""
                        <div style="border: 2px solid #ff9966; border-radius: 8px; padding: 15px;">
                            <h3>Interaction found between {medicine_name} and {med}</h3>
                            <p><strong>Side Effects:</strong></p>
                            <p>{simplified_effects}</p>
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
                # Display no interaction found
                with interaction_container:
                    st.markdown(f"""
                        <div style="border: 2px solid #4CAF50; border-radius: 8px; padding: 15px;">
                            <p>No interaction found between {medicine_name} and {med}</p>
                        </div>
                    """, unsafe_allow_html=True)

# Button to trigger interaction check
if search_button:
    if medicine_name:
        check_interactions(medicine_name)
    else:
        st.error("Please enter a medicine name to check interactions.")
