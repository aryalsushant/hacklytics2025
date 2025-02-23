import streamlit as st

st.set_page_config(page_title="Profile", page_icon="🩺", layout="wide")

st.title("🩺 User Profile - Medications & Allergies")

col1, col2 = st.columns(2)

with col1:
    st.header("Current Medications")
    medications = st.text_area("Enter the medications you are currently taking:", "")

with col2:
    st.header("Allergies")
    allergies = st.text_area("List any allergies you have:", "")

# Save profile to session state
if st.button("Save Profile"):
    if medications:
        st.session_state.medications = medications.split('\n')  # Store medications as a list
        st.success("Profile saved successfully!")
    else:
        st.error("Please enter at least one medication.")
