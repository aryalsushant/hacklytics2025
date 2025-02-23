import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)

# Set Streamlit theme to dark
st.markdown(
    """
    <style>
       body {
            background-color: #2c2f33;
            color: white;
        }
        .stChatMessage {
            background-color: #99aab5;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            color: black;
        }
        .stTextInput input {
            background-color: #99aab5;
            color: black;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize Streamlit app with a robot emoji in the title
st.title("🤖 LLM Chatbot using OpenAI")

# Session state to store chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# System message to guide the chatbot's behavior
system_prompt = {
    "role": "system",
    "content": (
        "You are a medical assistant chatbot. The user will provide two drug names, "
        "and you should analyze their interaction. Provide a short description of their interaction, "
        "and state whether it is safe to consume them together. If they are not safe together, suggest "
        "a safer alternative drug. Keep responses concise."
    )
}

# # Add system message if not already present
# if not st.session_state["messages"]:
#     st.session_state["messages"].append(system_prompt)

# User input
user_input = st.chat_input("Enter two drug names to check their interaction...")
if user_input:
    # Display user message
    st.chat_message("user").write(user_input)
    
    # Add user message to chat history
    st.session_state["messages"].append({"role": "user", "content": user_input})
    
    # Call OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state["messages"]
        )
        bot_reply = response.choices[0].message.content
    except Exception as e:
        bot_reply = f"Error: {str(e)}"
    
    # Display bot response
    with st.chat_message("assistant"):
        st.write(bot_reply)
    
    # Add bot response to chat history
    st.session_state["messages"].append({"role": "assistant", "content": bot_reply})

