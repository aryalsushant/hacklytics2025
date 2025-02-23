import streamlit as st
import requests
from backend.database import get_database
from backend.interactions import fetch_smiles, get_interaction
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3000")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Assuming you have the Gemini API key stored

# Initialize database and collection
db = get_database()
interactions_collection = None
if db is not None:
    collection_name = os.getenv('COLLECTION_NAME', 'drug_interaction')
    interactions_collection = db[collection_name]

# Streamlit UI for Medicine Interaction Checker
st.set_page_config(page_title="Medicine Interaction Checker", layout="centered")
st.title("Medicine Interaction Checker")
st.write("Enter the name of the medicine you want to learn about and check for interactions.")

# Input field for medicine search
medicine_name = st.text_input("Enter Medicine Name", placeholder="e.g., Ibuprofen")

# Function to get a natural language description for side effects using Gemini API
def get_side_effects_description(side_effects):
    try:
        # Generate a natural language description using Gemini AI
        prompt = f"Describe the following side effects in simple terms: {side_effects}"
        response = requests.post(
            "https://api.gemini.com/v1/completions",
            headers={"Authorization": f"Bearer {GEMINI_API_KEY}"},
            json={"prompt": prompt, "max_tokens": 100, "temperature": 0.7}
        )
        response_data = response.json()
        description = response_data.get("choices", [{}])[0].get("text", "").strip()
        return description
    except Exception as e:
        st.error(f"Error with Gemini AI API: {e}")
        return "Unable to generate a description."

# Function to check interaction and show results
def check_interactions(medicine_name):
    if interactions_collection is None:
        st.error("Database connection error. Please check server logs.")
        return

    # Create dynamic placeholders
    interaction_placeholder = st.empty()
    side_effects_placeholder = st.empty()

    # Fetch SMILES for the input medicine
    smiles = fetch_smiles(medicine_name)
    if not smiles:
        st.error(f"Could not fetch SMILES for {medicine_name}.")
        return

    # Define the state object
    state = type('State', (object,), {})()  # Create a simple object to hold the state
    state.drug1 = medicine_name
    state.drug2 = None  # Placeholder for the second drug in the profile

    # Initially set the status to "Checking interactions..."
    interaction_placeholder.text(f"Checking interactions for {medicine_name}...")

    if 'medications' in st.session_state:
        medications = st.session_state.medications
        interactions = []
        video_url = None  # Variable to store the video URL

        # Loop through medications from the profile
        for med in medications:
            state.drug2 = med.strip()
            # Call the backend to check for interactions
            get_interaction(state, interactions_collection)

            # After calling get_interaction, the result will be in state.result
            if hasattr(state, 'result'):
                result = state.result
                if "Interaction found" in result:
                    interactions.append((med, result))

                    # Immediately request the backend to generate the video for the interaction
                    payload = {
                        "drug1": medicine_name,
                        "drug2": med.strip(),
                        "smiles1": smiles,
                        "smiles2": fetch_smiles(med.strip()),  # Fetch the second drug's SMILES
                        "sideEffects": result
                    }
                    try:
                        response = requests.post(f"{BACKEND_URL}/generate-video", json=payload)
                        if response.ok:
                            video_url = response.json().get("videoUrl")
                        else:
                            side_effects_placeholder.text("Failed to generate video.")
                    except Exception as e:
                        side_effects_placeholder.text(f"Error generating video: {e}")

        # If interactions were found, display them
        if interactions:
            interaction_placeholder.text(f"Interactions found for {medicine_name}!")
            for med, interaction in interactions:
                st.write(f"Interaction with {med}: {interaction}")

            # Generate a side effects description using Gemini AI for each interaction
            side_effects_text = " ".join([interaction.split(":")[1].strip() for med, interaction in interactions])
            side_effects_description = get_side_effects_description(side_effects_text)
            side_effects_placeholder.text(f"Side Effects: {side_effects_description}")

            if video_url:
                st.session_state.video_url = video_url  # Store the video URL in session state
                # Show button only after the video URL is available
                if st.button("Show Animation"):
                    st.video(video_url)  # Display the video in Streamlit
        else:
            interaction_placeholder.text(f"No interactions found for {medicine_name}.")
    else:
        interaction_placeholder.text("No medications saved in your profile. Please add medications first.")

# Button to trigger interaction check
if st.button("See Interactions"):
    if medicine_name:
        check_interactions(medicine_name)
    else:
        st.error("Please enter a medicine name to check interactions.")
