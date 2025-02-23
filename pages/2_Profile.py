import streamlit as st
import json
import os

st.set_page_config(page_title="Profile", page_icon="🩺", layout="wide")

# Function to load profile data from a file
def load_profile():
    try:
        if os.path.exists('.streamlit/profile_data.json'):
            with open('.streamlit/profile_data.json', 'r') as f:
                data = json.load(f)
                st.session_state.medications = data.get('medications', [])
                st.session_state.allergies = data.get('allergies', [])
    except Exception as e:
        print(f"Error loading profile: {e}")

# Function to save profile data to a file
def save_profile(medications, allergies):
    try:
        os.makedirs('.streamlit', exist_ok=True)
        with open('.streamlit/profile_data.json', 'w') as f:
            json.dump({
                'medications': medications,
                'allergies': allergies
            }, f)
    except Exception as e:
        print(f"Error saving profile: {e}")

# Initialize session state if needed
if 'medications' not in st.session_state:
    st.session_state.medications = []
if 'allergies' not in st.session_state:
    st.session_state.allergies = []

# Load existing profile data
load_profile()

st.title("🩺 User Profile - Medications & Allergies")

col1, col2 = st.columns(2)

with col1:
    st.header("Current Medications")
    medications = st.text_area(
        "Enter the medications you are currently taking:",
        value='\n'.join(st.session_state.medications) if st.session_state.medications else "",
        key="medications_input",
        height=200
    )

with col2:
    st.header("Allergies")
    allergies = st.text_area(
        "List any allergies you have:",
        value='\n'.join(st.session_state.allergies) if st.session_state.allergies else "",
        key="allergies_input",
        height=200
    )

# Save profile
if st.button("Save Profile"):
    if medications:
        # Update session state
        meds_list = [med.strip() for med in medications.split('\n') if med.strip()]
        allergies_list = [allergy.strip() for allergy in allergies.split('\n') if allergy.strip()]
        
        st.session_state.medications = meds_list
        st.session_state.allergies = allergies_list
        
        # Save to file
        save_profile(meds_list, allergies_list)
        
        st.success("Profile saved successfully!")
    else:
        st.error("Please enter at least one medication.")