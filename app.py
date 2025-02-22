# app.py
from taipy.gui import Gui, notify
from backend.database import get_database, populate_mongodb, create_indexes
from backend.interactions import get_interaction
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

# Global state variables for the GUI
drug1 = ""
drug2 = ""
result = "<Empty>"
animation_url = ""  # New state variable to hold the video URL
smiles1 = ""        # New state variable to hold SMILES for drug1
smiles2 = ""        # New state variable to hold SMILES for drug2

# Initialize database and collection
db = get_database()
interactions_collection = None
if db is not None:
    collection_name = os.getenv('COLLECTION_NAME', 'drug_interaction')
    interactions_collection = db[collection_name]

def check_interaction(state):
    """Call the backend to get interaction info and update state."""
    # Call the backend; it will update state.result.
    get_interaction(state, interactions_collection)
    # If an interaction is found, store the SMILES values in state for later use.
    if "Interaction found" in state.result:
        # The get_interaction function prints the result.
        # Here, we assume that the function has added attributes to the state.
        # For example, if you modify get_interaction to do:
        #    state.smiles1 = smiles1; state.smiles2 = smiles2
        # then you can use them below.
        # Alternatively, you can fetch them here again.
        # For this example, let's assume get_interaction added state.smiles1 and state.smiles2.
        pass  # (Ensure your backend interaction function stores SMILES in state)

def view_animation(state):
    """Call the Flask API to generate/fetch the animation video."""
    payload = {
        "drug1": state.drug1,
        "drug2": state.drug2,
        "smiles1": state.smiles1 if hasattr(state, "smiles1") else "",
        "smiles2": state.smiles2 if hasattr(state, "smiles2") else "",
        "sideEffects": "No specific side effects provided."
    }
    try:
        response = requests.post("http://localhost:3000/generate-video", json=payload)
        if response.ok:
            data = response.json()
            video_url = data.get("videoUrl")
            if video_url:
                state.animation_url = video_url
                notify(state, "success", "Animation video is ready!")
            else:
                notify(state, "error", "Animation video URL not received.")
        else:
            notify(state, "error", f"Failed to generate animation: {response.text}")
    except Exception as e:
        notify(state, "error", f"Error: {str(e)}")

# Define the Taipy GUI layout.
page = """
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

<|View Animation|button|on_action=view_animation|>

## Animation Video URL:
<|{animation_url}|text|>
"""

if __name__ == "__main__":
    print("🚀 Starting Drug Interaction Checker...")
    
    # Populate MongoDB if needed and create indexes
    populate_mongodb(db)
    create_indexes(db)
    
    try:
        Gui(page).run(port=5001)
    except OSError as e:
        if "Address already in use" in str(e):
            print("Port 5001 is in use, trying port 5002...")
            try:
                Gui(page).run(port=5002)
            except OSError:
                print("❌ Multiple ports are in use. Please try these solutions:")
                print("1. Kill existing processes:")
                print("   lsof -i :5001")
                print("   kill -9 <PID>")
                print("2. Or specify a different port:")
                print("   Gui(page).run(port=8080)")
        else:
            raise e
