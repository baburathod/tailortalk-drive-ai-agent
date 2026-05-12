import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Drive File Assistant",
    page_icon="📁",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .user-msg {
        background-color: #e6f3ff;
    }
    .assistant-msg {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

st.title("📁 Google Drive File Assistant")
st.markdown("Ask me to find files, filter by type, or search content in your Google Drive!")

with st.sidebar:
    st.header("💡 Try these queries:")
    st.markdown("""
    - Find finance PDFs
    - Show spreadsheets uploaded recently
    - Find documents containing internship
    - Search image files
    - Find reports modified last week
    """)
    st.info("Remember to add your credentials.json file to the backend folder so the agent can execute these searches!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("E.g., Find finance PDFs uploaded last week"):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        with st.spinner("Searching your Drive..."):
            try:
                # Exclude the current prompt from history payload to avoid duplication
                # Although our backend is stateless, it accepts history
                history_payload = st.session_state.messages[:-1]
                
                response = requests.post(
                    f"{BACKEND_URL}/api/chat",
                    json={
                        "message": prompt,
                        "history": history_payload
                    },
                    timeout=30 # 30 seconds timeout
                )
                
                if response.status_code == 200:
                    answer = response.json().get("response", "No response received.")
                    message_placeholder.markdown(answer)
                    # Add assistant response to state
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error from server: {response.status_code} - {response.text}"
                    message_placeholder.error(error_msg)
            except requests.exceptions.RequestException as e:
                message_placeholder.error(f"Could not connect to the backend server. Please ensure it's running. Error: {str(e)}")
