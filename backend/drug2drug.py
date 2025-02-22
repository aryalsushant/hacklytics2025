import pandas as pd
import requests
import os
from taipy.gui import Gui, State

# Define CSV file path
csv_file_path = os.path.join(os.path.dirname(__file__), "../dataset/twosides_aggregated.csv")

# Load the CSV file into memory
def load_csv():
    if os.path.exists(csv_file_path):
        return pd.read_csv(csv_file_path)
    return None

# Load data globally
data = load_csv()

# Function to fetch Canonical SMILES from PubChem
def fetch_smiles(drug_name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/property/CanonicalSMILES/JSON"
    response = requests.get(url)

    if response.status_code != 200:
        return None
    
    data = response.json()
    properties = data.get("PropertyTable", {}).get("Properties", [])
    
    if properties:
        return properties[0].get("CanonicalSMILES")
    return None

# Function to check for drug interactions
def get_interaction(state: State, drug1: str, drug2: str):
    if not drug1 or not drug2:
        state.result = "⚠️ Please provide both drug names!"
        return

    # Fetch SMILES for both drugs
    smiles1 = fetch_smiles(drug1)
    smiles2 = fetch_smiles(drug2)

    if not smiles1 or not smiles2:
        state.result = "❌ Could not retrieve SMILES for one or both drugs."
        return

    # Check for an interaction in the dataset
    match = data[
        ((data["X1"] == smiles1) & (data["X2"] == smiles2)) |
        ((data["X1"] == smiles2) & (data["X2"] == smiles1))
    ]

    if not match.empty:
        state.result = f"✅ Interaction Found!\n\n**Side Effects:** {match.iloc[0]['Top_5_Side_Effects']}"
    else:
        state.result = "⚠️ No known interaction found in the dataset."

# Taipy GUI for user input and results display
page = """
# Drug Interaction Checker 💊

Enter two drug names to check for interactions:

<|input|value=drug1|label=Drug 1|>
<|input|value=drug2|label=Drug 2|>

<|button|label=Check Interaction|on_action=get_interaction|>

### **Results:**
<|text|value={result}|>
"""

# Run the Taipy app
if __name__ == "__main__":
    Gui(page).run(title="Drug Interaction Finder", port=5001)
