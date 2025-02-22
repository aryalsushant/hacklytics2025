# app.py
from taipy.gui import Gui, notify, navigate
from backend.database import get_database, populate_mongodb, create_indexes
from backend.interactions import get_interaction
from dotenv import load_dotenv
import os
import requests
from markupsafe import Markup
import webbrowser

# Load environment variables
load_dotenv()
# Get the backend URL from environment variables with a default fallback.
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:3000")

# Global state variables for the GUI
drug1 = ""
drug2 = ""
search_drug = ""  # Added to prevent KeyError if referenced by Taipy
result = "<Empty>"
animation_url = ""
animation_button_text = "View Animation"
smiles1 = ""
smiles2 = ""

# Initialize database and collection
db = get_database()
interactions_collection = None
if db is not None:
    collection_name = os.getenv('COLLECTION_NAME', 'drug_interaction')
    interactions_collection = db[collection_name]

def check_interaction(state):
    """Call the backend to get interaction info and update state."""
    get_interaction(state, interactions_collection)
    # Ensure that get_interaction stores fetched SMILES in state (e.g., state.smiles1, state.smiles2)

def view_animation(state):
    """Call the Flask API to generate/fetch the animation video and open it in a new tab."""
    state.animation_button_text = "Creating Animation..."
    
    payload = {
        "drug1": state.drug1,
        "drug2": state.drug2,
        "smiles1": state.smiles1 if hasattr(state, "smiles1") else "",
        "smiles2": state.smiles2 if hasattr(state, "smiles2") else "",
        "sideEffects": "No specific side effects provided."
    }
    try:
        response = requests.post(f"{BACKEND_URL}/generate-video", json=payload)
        if response.ok:
            data = response.json()
            video_url = data.get("videoUrl")
            if video_url:
                state.animation_url = video_url
                # Open the URL in a new browser tab
                webbrowser.open(video_url)
                notify(state, "success", "Animation opened in new tab!")
            else:
                notify(state, "error", "Animation video URL not received.")
        else:
            notify(state, "error", f"Failed to generate animation: {response.text}")
    except Exception as e:
        notify(state, "error", f"Error: {str(e)}")
    finally:
        state.animation_button_text = "View Animation"

# Define the Taipy GUI layout - now we only need one page
main_page = """
<|part|class_name=card p-2|
# Drug Interaction Checker 💊

Enter two drug names to check for interactions:

<|layout|columns=2|
<|
Drug 1
<|{drug1}|input|label=Drug 1|>
|>

<|
Drug 2
<|{drug2}|input|label=Drug 2|>
|>
|>

<|Check Interaction|button|on_action=check_interaction|>

## Interaction Result:
<|{result}|text|>

<|{animation_button_text}|button|on_action=view_animation|>

|>
"""

# Simplified pages dictionary - we only need the main page
pages = {
    "/": "<|toggle|theme|>\n<center>\n<|navbar|>\n</center>",  # Root page with theme toggle
    "main": main_page,
}

if __name__ == "__main__":
    print("🚀 Starting Drug Interaction Checker...")

    # Populate MongoDB if needed and create indexes
    populate_mongodb(db)
    create_indexes(db)

    try:
        Gui(pages=pages, css_file="style.css").run(port=5001, title="Drug Interaction App", use_reloader=True, dark_mode=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print("Port 5001 is in use, trying port 5002...")
            try:
                Gui(pages=pages, css_file="style.css").run(port=5002, title="Drug Interaction App", use_reloader=True, dark_mode=True)
            except OSError:
                print("❌ Multiple ports are in use. Please try these solutions:")
                print("1. Kill existing processes:")
                print("   lsof -i :5001")
                print("   kill -9 <PID>")
                print("2. Or specify a different port:")
                print("   Gui(pages=pages, ...).run(port=8080)")
        else:
            raise e
