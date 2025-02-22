import streamlit as st

st.set_page_config(page_title="Medicine Interaction Checker", layout="centered")

st.title("Medicine Interaction Checker")
st.write("Enter the name of the medicine you want to learn about and check for interactions.")

# Input field for medicine search
medicine_name = st.text_input("Enter Medicine Name", placeholder="e.g., Ibuprofen")

# Button to check interactions
if st.button("See Interactions"):
    if medicine_name:
        st.success(f"Checking interactions for {medicine_name}...")
        st.info("Generating video description of interactions...")
        st.video("https://www.example.com/sample-video.mp4")  # Replace with your video link
    else:
        st.error("Please enter a medicine name to check interactions.")

# Button to navigate to the Profile page
if st.button("Profile"):
    # Use the absolute URL for your profile page on port 8502
    st.markdown(
        '<meta http-equiv="refresh" content="0; url=http://localhost:8501" />',
        unsafe_allow_html=True
    )
