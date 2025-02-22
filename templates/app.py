import streamlit as st
import requests
import os
import webbrowser
from backend.database import get_database, populate_mongodb, create_indexes
from backend.interactions import get_interaction
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize database
st.set_page_config(page_title="Drug Interaction Checker", page_icon="💊", layout="centered")
db = get_database()
interactions_collection = None
if db is not None:
    collection_name = os.getenv('COLLECTION_NAME', 'drug_interaction')
    interactions_collection = db[collection_name]

# UI components
def main_page():
    st.title("💊 Drug Interaction Checker")
    st.write("Enter two drug names to check for interactions:")
    
    drug1 = st.text_input("Drug 1", key="drug1")
    drug2 = st.text_input("Drug 2", key="drug2")
    
    if st.button("Check Interaction"):
        result = get_interaction(st.session_state, interactions_collection)
        st.session_state.result = result if result else "No interaction found."
    
    st.write("## Interaction Result:")
    st.text(st.session_state.get("result", "<Empty>"))
    
    if st.button("View Animation"):
        view_animation()

# Function to fetch animation
def view_animation():
    st.session_state.animation_button_text = "Creating Animation..."
    
    payload = {
        "drug1": st.session_state.get("drug1", ""),
        "drug2": st.session_state.get("drug2", ""),
        "smiles1": st.session_state.get("smiles1", ""),
        "smiles2": st.session_state.get("smiles2", ""),
        "sideEffects": "No specific side effects provided."
    }
    
    try:
        response = requests.post("http://localhost:3000/generate-video", json=payload)
        if response.ok:
            data = response.json()
            video_url = data.get("videoUrl")
            if video_url:
                st.session_state.animation_url = video_url
                webbrowser.open(video_url)
                st.success("Animation opened in new tab!")
            else:
                st.error("Animation video URL not received.")
        else:
            st.error(f"Failed to generate animation: {response.text}")
    except Exception as e:
        st.error(f"Error: {str(e)}")
    finally:
        st.session_state.animation_button_text = "View Animation"

# Run setup
if __name__ == "__main__":
    print("🚀 Starting Drug Interaction Checker...")
    populate_mongodb(db)
    create_indexes(db)
    main_page()
