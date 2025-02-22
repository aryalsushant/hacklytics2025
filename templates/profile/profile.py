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

if st.button("Save Profile"):
    st.success("Profile saved successfully!")

# Button to navigate back to the Home (search) page
if st.button("Home"):
    # Use the absolute URL for your search page on port 8501
    st.markdown(
        '<meta http-equiv="refresh" content="0; url=http://localhost:8502" />',
        unsafe_allow_html=True
    )
