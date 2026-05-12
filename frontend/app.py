import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import time

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION & DUAL-ENDPOINT SETUP
# ============================================================================
# Defaulting to the deployed Render backend URL provided by the user
DEFAULT_BACKEND_URL = "https://tailortalk-drive-ai-agent.onrender.com"
BACKEND_URL = os.getenv("BACKEND_URL", DEFAULT_BACKEND_URL).rstrip("/")

# Configure page settings
st.set_page_config(
    page_title="TailorTalk - AI Google Drive Assistant",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PREMIUM AESTHETICS & CUSTOM STYLING (Google Fonts, Glassmorphism, Animations)
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Apply modern typography globally */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* Main layout container padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1100px !important;
    }
    
    /* Sleek gradient top bar */
    .top-gradient-bar {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        height: 6px;
        border-radius: 6px;
        margin-bottom: 1.5rem;
    }
    
    /* Premium Title Header */
    .app-title {
        font-weight: 700;
        font-size: 2.8rem;
        background: linear-gradient(135deg, #1E1B4B 0%, #4338CA 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        text-align: center;
        letter-spacing: -0.05rem;
    }
    
    .app-subtitle {
        color: #6B7280;
        font-size: 1.1rem;
        font-weight: 400;
        text-align: center;
        margin-bottom: 2.5rem;
    }
    
    /* Chat Message Bubbles with Subtle Shadows & Smooth Borders */
    .stChatMessage {
        border-radius: 16px !important;
        padding: 1.2rem 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02) !important;
        transition: transform 0.2s ease !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* User Message - Premium Tailored HSL Blue Tone */
    .stChatMessage[data-testid="chatMessage"] > div:first-child {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%) !important;
        border-left: 4px solid #3B82F6 !important;
        color: #1E3A8A !important;
    }
    
    /* Assistant Message - Sleek Clean Grey Tone */
    .stChatMessage > div {
        background: #F9FAFB !important;
        border-left: 4px solid #8B5CF6 !important;
        color: #1F2937 !important;
    }
    
    /* Styled Chat Input Container */
    .stChatInputContainer {
        border-radius: 16px !important;
        border: 2px solid #E5E7EB !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05) !important;
        padding: 0.2rem 0.5rem !important;
    }
    
    .stChatInputContainer:focus-within {
        border-color: #6D28D9 !important;
    }
    
    /* Sidebar custom branding */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #F1F5F9 !important;
    }
    
    /* Interactive Button Styling */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 500 !important;
        border: 1px solid #E2E8F0 !important;
        background-color: #FFFFFF !important;
        color: #334155 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    
    .stButton > button:hover {
        background-color: #F1F5F9 !important;
        border-color: #CBD5E1 !important;
        color: #0F172A !important;
        transform: translateY(-1px) !important;
    }
    
    /* Primary action hover glow */
    .stButton > button:active {
        transform: translateY(0px) !important;
    }
</style>
""", unsafe_allow_html=True)

# Top aesthetic border
st.markdown('<div class="top-gradient-bar"></div>', unsafe_allow_html=True)

# App Header
st.markdown('<div class="app-title">📁 TailorTalk AI</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Intelligent Natural Language Discovery for your Google Drive</div>', unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "👋 **Welcome to TailorTalk!** I'm your AI assistant powered by LangChain and the Google Drive API.\n\nAsk me anything about your files, such as:\n- *\"Find finance PDFs\"*\n- *\"Show spreadsheets uploaded recently\"*\n- *\"Search documents containing the word budget\"*"
        }
    ]

# Helper function to clear history
def clear_chat_history():
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "♻️ Chat history cleared. How can I help you discover files today?"
        }
    ]

# ============================================================================
# SIDEBAR CONTROLS & STATUS
# ============================================================================
with st.sidebar:
    st.markdown("### 🚀 Quick Prompts")
    st.caption("Click to automatically test common discovery scenarios:")
    
    sample_queries = [
        "Find finance PDFs",
        "Show spreadsheets uploaded recently",
        "Find documents containing internship",
        "Search image files",
        "Find reports modified last week"
    ]
    
    for query in sample_queries:
        if st.button(f"🔍 {query}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": query})
            st.rerun()
            
    st.divider()
    
    st.markdown("### ⚙️ System Status")
    
    # Endpoint health check display
    status_box = st.empty()
    with status_box.container():
        st.caption("Checking backend connection...")
    
    # Verify backend URL format and accessibility safely
    is_connected = False
    try:
        # Check base URL or root endpoint briefly
        res = requests.get(f"{BACKEND_URL}/", timeout=3)
        if res.status_code in [200, 404]:  # 404 on root is okay if /chat is live
            is_connected = True
    except Exception:
        is_connected = False
        
    with status_box.container():
        if is_connected:
            st.success("🟢 **Backend API Live**", icon="✅")
        else:
            st.warning("🟡 **Backend Connecting...**", icon="⚡")
            
    st.caption(f"**Target URL:** `{BACKEND_URL}`")
    
    st.divider()
    
    st.markdown("### 🛠️ Configuration")
    st.caption("Ensure your backend service has `credentials.json` configured with Google Drive permissions.")
    
    if st.button("🗑️ Reset Conversation", use_container_width=True, on_click=clear_chat_history):
        pass
        
    st.divider()
    st.caption("💼 **Built for Production**\nFastAPI • Streamlit • LangChain")

# ============================================================================
# MAIN CHAT HISTORY RENDERING
# ============================================================================
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        avatar_icon = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])

# ============================================================================
# API CALL HANDLING WITH SMART DUAL-ENDPOINT FALLBACK
# ============================================================================
def send_chat_request(user_prompt, history_payload):
    """
    Sends the request to the backend. Automatically supports both:
    - /chat (Requested Format)
    - /api/chat (Standard repo router path)
    Ensures seamless functionality regardless of backend configuration setup.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "message": user_prompt,
        "history": history_payload
    }
    
    # Candidate endpoints to try seamlessly
    endpoints = [
        f"{BACKEND_URL}/chat",
        f"{BACKEND_URL}/api/chat"
    ]
    
    last_error = None
    last_response = None
    
    for endpoint in endpoints:
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=45)
            last_response = response
            # If endpoint exists (200 or 500 server error logic handled below), return it immediately
            if response.status_code != 404:
                return response
        except requests.exceptions.RequestException as e:
            last_error = e
            continue
            
    # If both resulted in request exception or 404, return the last response or raise
    if last_response is not None:
        return last_response
    if last_error is not None:
        raise last_error
    raise requests.exceptions.ConnectionError("Could not reach backend endpoints.")

# ============================================================================
# CHAT INPUT & EXECUTION
# ============================================================================
if prompt := st.chat_input("Type your Google Drive search query here... (e.g., 'Find presentation slides')"):
    # Append user prompt immediately to chat state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Render user prompt locally
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        
    # Prepare non-duplicative history payload for backend context
    # Keeping role and content mapped cleanly
    history_payload = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages[:-1]
    ]
    
    # Stream/Process assistant response
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        
        # Display modern loading feedback
        with st.spinner("🔍 Consulting AI Agent & Searching Drive API..."):
            start_time = time.time()
            try:
                response = send_chat_request(prompt, history_payload)
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("response", "No files found or empty response returned.")
                    
                    # Optional nice visual touch: render answer with metrics tag
                    message_placeholder.markdown(answer)
                    
                    # Save assistant message to persistent state
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                elif response.status_code == 500:
                    err_detail = response.json().get("detail", response.text)
                    error_markdown = f"""
❌ **Backend API Processing Error (500)**

The backend server encountered an error while executing the Google Drive search tool.

**Technical Details:**
```text
{err_detail}
```

**Quick Troubleshooting Checklist:**
1. Ensure your Google Service Account `credentials.json` file is securely loaded on the backend server.
2. Verify the `DRIVE_FOLDER_ID` environment variable points to a valid folder shared with the service account email.
3. Check the Render application logs for detailed Python traceback.
"""
                    message_placeholder.error(error_markdown)
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Server Error: {err_detail}"})
                    
                else:
                    error_markdown = f"❌ **Server Returned Status Code {response.status_code}**\n\nResponse Content: `{response.text}`"
                    message_placeholder.error(error_markdown)
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ API Error ({response.status_code})"})
                    
            except requests.exceptions.Timeout:
                err_msg = "⏱️ **Request Timed Out.** The search took longer than 45 seconds to complete. Please try narrowing your query parameters."
                message_placeholder.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
                
            except requests.exceptions.ConnectionError:
                err_msg = f"🔌 **Connection Refused.** Unable to communicate with the backend API at `{BACKEND_URL}`. Ensure the service is deployed and accessible."
                message_placeholder.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
                
            except Exception as e:
                err_msg = f"⚠️ **Unexpected Client Error:** `{str(e)}`"
                message_placeholder.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})

# Footer metadata
st.markdown("<br><hr style='opacity: 0.5;'>", unsafe_allow_html=True)
cols = st.columns([1, 1, 1])
cols[0].caption("🔒 Secure Connection • Client-Side Stateless Integration")
cols[1].caption(f"📅 Session Started: {datetime.now().strftime('%b %d, %Y')}")
cols[2].caption("⚡ Built with **Streamlit** & **FastAPI**")

