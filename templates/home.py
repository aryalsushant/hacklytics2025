import streamlit as st
import json
import os
import requests

# Check if user session exists in file
def load_user_session():
    if os.path.exists("user_session.json"):
        with open("user_session.json", "r") as f:
            return json.load(f)
    return None

# Streamlit Page Config
st.set_page_config(page_title="Auth0 Example", page_icon="🔑", layout="wide")

st.title("🔑 Auth0 Login Example")

user_info = load_user_session()

if user_info:
    st.session_state["user"] = user_info
    st.write(f"### Welcome, {user_info['userinfo']['name']}!")
    
    if st.button("Go to Profile"):
        # Redirect to profile page
        st.experimental_rerun()  # Optional, if you need to reload
        st.markdown(
            '<meta http-equiv="refresh" content="0; url=/templates/profile/profile.py">',
            unsafe_allow_html=True
        )
    if st.button("Logout"):
        # Trigger Flask logout
        requests.get("http://127.0.0.1:3000/logout")
        if os.path.exists("user_session.json"):
            os.remove("user_session.json")  # Remove session file
        del st.session_state["user"]
        st.experimental_rerun()

else:
    st.write("### Welcome Guest")
    if st.button("Login"):
        # Redirect to Flask login
        st.markdown(
            '<meta http-equiv="refresh" content="0; url=http://127.0.0.1:3000/login">',
            unsafe_allow_html=True
        )
