import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import requests
from backend.database import get_database
from backend.interactions import fetch_smiles, get_interaction
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3000")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize database
db = get_database()
interactions_collection = None
if db is not None:
    collection_name = os.getenv('COLLECTION_NAME', 'drug_interaction')
    interactions_collection = db[collection_name]

# Streamlit UI setup
st.set_page_config(page_title="Medicine Interaction Checker", layout="centered")

# Custom CSS: Adjust input, hide helper text, and add orange border to interaction container
st.markdown("""
    <style>
        /* Force the outer container to a new height */
        .stTextInput {
            height: 80px !important;
            min-height: 80px !important;
        }
        .stTextInput > div {
            height: 80px !important;
        }
        /* Increase the actual input field's size */
        .stTextInput > div > div > input {
            height: 60px !important;
            font-size: 18px !important;
            padding: 10px 12px !important;
        }
        /* Hide the "Press Enter to apply" helper text */
        div[data-testid="InputInstructions"] {
            display: none !important;
        }
        /* Orange border for the interaction container */
        .interaction-container {
            border: 2px solid orange !important;
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

# JavaScript to adjust the container height (if needed)
components.html("""
<script>
  setTimeout(function(){
    document.querySelectorAll(".stTextInput").forEach(function(container) {
      container.style.height = "80px";
    });
  }, 500);
</script>
""", height=0)

# Page Title
st.markdown('<div style="font-size:26px; font-weight:bold; text-align:center; margin-bottom:15px;">Medicine Interaction Checker</div>', unsafe_allow_html=True)

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

import re

def get_side_effects_description(side_effects):
    """Uses Gemini AI to provide a concise, clear paragraph summarizing the side effects without any numbers."""
    try:
        # Remove numbers and colons from the side effects string.
        cleaned_effects = re.sub(r'\d+\s*:\s*', '', side_effects).strip().rstrip(';')
        # Build a clearer prompt with a newline and explicit summary directive.
        prompt = f"Please summarize in a clear and concise way the following side effects as risks that may pose to the person, who is trying to find out about the consequences of using these two drugs simultaneously.Do not use bullet points. The side effects to be summarized are: {side_effects}"
        # Make the API call.
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)

        if response and response.candidates:
            # Accessing the 'content' and 'parts' attributes directly
            candidate = response.candidates[0]
            content_parts = candidate.content.parts if hasattr(candidate.content, 'parts') else []
            
            if content_parts:
                side_effects_description = content_parts[0].text.strip() if hasattr(content_parts[0], 'text') else ""
                return side_effects_description
            else:
                return "No parts available in response."
        else:
            return "No information available."
    except Exception as e:
        print("DEBUG: Exception occurred:", e)
        return side_effects




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
                raw_side_effects = re.findall(r'\d+:\s*([^;]+)', result)
                side_effects_string = ", ".join(raw_side_effects)
                summary = get_side_effects_description(side_effects_string)
                
                st.markdown(f"""
                    <div class="interaction-container">
                        <h3>Interaction Found</h3>
                        <p><strong>{medicine_name} and {med} Side Effects</strong></p>
                        <p>{summary}</p>
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

if search_button:
    if medicine_name:
        check_interactions(medicine_name)
    else:
        st.error("Please enter a medicine name to check interactions.")
