import streamlit as st

# Streamlit UI for Medicine Interaction Checker
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
        # Placeholder for video display (this will be updated once the backend is ready)
        st.video("https://www.example.com/sample-video.mp4")  # Replace with dynamically generated video link
    else:
        st.error("Please enter a medicine name to check interactions.")
