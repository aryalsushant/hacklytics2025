import requests
import streamlit as st

def fetch_smiles(drug_name):
    """Fetch SMILES notation from PubChem API for a given drug name."""
    try:
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/property/CanonicalSMILES/JSON"
        response = requests.get(url)
        if response.ok:
            data = response.json()
            properties = data.get('PropertyTable', {}).get('Properties', [])
            if properties:
                return properties[0].get('CanonicalSMILES')
        return None
    except Exception as e:
        st.error(f"Error fetching SMILES for {drug_name}: {e}")
        return None

def get_interaction(state, interactions_collection):
    """Search for a drug interaction in MongoDB and update the state."""
    if interactions_collection is None:
        state.result = "Database connection error. Please check server logs."
        st.error(state.result)  # Display the error in Streamlit UI
        return

    try:
        drug_1 = state.drug1
        drug_2 = state.drug2
        if not drug_1 or not drug_2:
            state.result = "Please enter both drug names"
            st.error(state.result)  # Display the error in Streamlit UI
            return

        # Fetch SMILES for both drugs
        smiles1 = fetch_smiles(drug_1)
        smiles2 = fetch_smiles(drug_2)
        
        # Store the fetched SMILES in state so that they can be passed later
        state.smiles1 = smiles1
        state.smiles2 = smiles2

        if not smiles1 or not smiles2:
            state.result = "Could not retrieve SMILES for one or both drugs."
            st.error(state.result)  # Display the error in Streamlit UI
            return

        # Search for interaction in MongoDB
        interaction = interactions_collection.find_one({
            "$or": [
                {"X1": smiles1, "X2": smiles2},
                {"X1": smiles2, "X2": smiles1}
            ]
        })

        if interaction:
            side_effects = interaction['Top_5_Side_Effects']
            state.result = f"Interaction found between {drug_1} and {drug_2}:\n{side_effects}"
            st.success(f"Interaction found between {drug_1} and {drug_2}!")  # Display success in Streamlit UI
            st.write(f"Side Effects: {side_effects}")
        else:
            state.result = f"No interaction data found between {drug_1} and {drug_2}"
            st.warning(state.result)  # Display warning in Streamlit UI
        
    except Exception as e:
        state.result = f"Error: {str(e)}"
        st.error(f"Error: {str(e)}")  # Display the error in Streamlit UI
