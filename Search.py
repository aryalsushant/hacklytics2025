import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components
import requests
from backend.database import get_database
from backend.interactions import fetch_smiles, get_interaction
from dotenv import load_dotenv
import os
import re

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
st.set_page_config(page_title="Medicine Interaction Checker", layout="wide")

st.sidebar.image("logo.png", caption="Made with ❤️ at Hacklytics 2025", use_container_width=True)

# Custom CSS
st.markdown("""
    <style>
        .stTextInput {
            height: 80px !important;
            min-height: 80px !important;
        }
        .stTextInput > div {
            height: 80px !important;
        }
        .stTextInput > div > div > input {
            height: 60px !important;
            font-size: 18px !important;
            padding: 10px 12px !important;
        }
        div[data-testid="InputInstructions"] {
            display: none !important;
        }
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

# Optional JavaScript for container height (if needed)
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
st.title("💊 Medicine Interaction Checker")

# Input field & button layout
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
    """Uses Gemini AI to summarize side effects as a paragraph."""
    try:
        cleaned_effects = re.sub(r'\d+\s*:\s*', '', side_effects).strip().rstrip(';')
        prompt = f"Please summarize the following side effects as risks in a clear and concise paragraph without bullet points: {side_effects}"
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
        if response and response.candidates and response.candidates[0].content.parts:
            side_effects_description = response.candidates[0].content.parts[0].text.strip()
            return side_effects_description
        else:
            return "No reliable information found."
    except Exception as e:
        print("DEBUG: Exception occurred:", e)
        return side_effects

def check_interactions(medicine_name):
    """Checks for drug interactions and displays results.
       For the demo, after processing, we will display a video from Cloudflare R2 if available.
    """
    if interactions_collection is None:
        st.error("Database connection error. Please check the server.")
        return

    smiles = fetch_smiles(medicine_name)
    if not smiles:
        st.error(f"Could not fetch SMILES for {medicine_name}.")
        return

    # Simple object to store state
    state = type('State', (object,), {})()
    state.drug1 = medicine_name
    state.drug2 = None

    if 'medications' not in st.session_state:
        st.markdown('<div class="no-interaction-container">No medications saved. Add medications first.</div>', unsafe_allow_html=True)
        return

    medications = st.session_state.medications
    processed_meds = set()
    
    # Variable to store the video URL if found in the R2 bucket
    video_url_to_display = None
    
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
                # ----- Interaction found block -----
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

                # ----- Check for R2 video (try/except) -----
                filename_order1 = f"{medicine_name.lower()}_{med.lower()}_interaction.mp4"
                filename_order2 = f"{med.lower()}_{medicine_name.lower()}_interaction.mp4"
                potential_video_url1 = f"https://pub-e68a57c8844d462b9baedbc3cdf9f846.r2.dev/drug_videos/{filename_order1}"
                potential_video_url2 = f"https://pub-e68a57c8844d462b9baedbc3cdf9f846.r2.dev/drug_videos/{filename_order2}"

                try:
                    head_response1 = requests.head(potential_video_url1)
                    if head_response1.status_code == 200:
                        video_url_to_display = potential_video_url1
                    else:
                        head_response2 = requests.head(potential_video_url2)
                        if head_response2.status_code == 200:
                            video_url_to_display = potential_video_url2
                except Exception as e:
                    print("DEBUG: Exception during video check:", e)

            else:
                # ----- No interaction found block -----
                st.markdown(f"""
                    <div class="no-interaction-container">
                        <p>No interaction found between {medicine_name} and {med}</p>
                    </div>
                """, unsafe_allow_html=True)




    # If no R2 video was found, fall back to a default demo video
    if not video_url_to_display:
         st.markdown(f"""
                    <div class="no-interaction-container">
                        <p>No interaction animation was found. Please Try Again!!</p>
                    </div>
                """, unsafe_allow_html=True)
    st.markdown("<hr><h3>Watch Animation</h3>", unsafe_allow_html=True)
    html_code = f"""
    <video width="640" height="360" controls>
        <source src="{video_url_to_display}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    """
    st.markdown(html_code, unsafe_allow_html=True)

if search_button:
    if medicine_name:
        check_interactions(medicine_name)
    else:
        st.error("Please enter a medicine name to check interactions.")
