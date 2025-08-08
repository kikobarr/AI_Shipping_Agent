import streamlit as st
from services.openai_connector import OpenAIConnector
from datetime import datetime
import time

# Professional font styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .status-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    
    .status-connected {
        background-color: #d1fae5;
        border: 1px solid #a7f3d0;
        color: #065f46;
    }
    
    .status-disconnected {
        background-color: #fee2e2;
        border: 1px solid #fca5a5;
        color: #991b1b;
    }
    
    .user-message, .assistant-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
    }
    
    .user-message {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
    }
    
    .assistant-message {
        background-color: #f9fafb;
        border-left: 4px solid #10b981;
    }
    
    .model-selector {
        background-color: #f8fafc;
        padding: 0.5rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        color: #6b7280;
    }
</style>
""", unsafe_allow_html=True)

# Load CSS
try:
    with open("styles/chat_ui.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass  # CSS file not found, continue with inline styles

# Initialize session state
if 'openai_connector' not in st.session_state:
    st.session_state.openai_connector = OpenAIConnector()
    success, message = st.session_state.openai_connector.initialize_connection()
    st.session_state.connected = success
    st.session_state.connection_message = message
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'connected' not in st.session_state:
    st.session_state.connected = False

st.header("💬 Chat with AI Assistant")

# Model selector
col1, col2 = st.columns([3, 1])
with col2:
    model_option = st.selectbox(
        "Model",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        index=0,
        help="Select the OpenAI model to use"
    )
    if model_option != st.session_state.openai_connector.model:
        st.session_state.openai_connector.set_model(model_option)

# Status box
status_class = "status-connected" if st.session_state.connected else "status-disconnected"
status_text = "🟢 Connected to OpenAI" if st.session_state.connected else "🔴 Not Connected"
st.markdown(f"""
<div class="status-box {status_class}">
    {status_text}
</div>
""", unsafe_allow_html=True)

if not st.session_state.connected:
    st.error(f"Connection Error: {st.session_state.connection_message}")
    if st.button("🔄 Retry Connection"):
        success, message = st.session_state.openai_connector.initialize_connection()
        st.session_state.connected = success
        st.session_state.connection_message = message
        st.rerun()

# Chat history
for message in st.session_state.messages:
    msg_type = "user-message" if message["role"] == "user" else "assistant-message"
    label = "You" if message["role"] == "user" else "AI Assistant"
    icon = "👤" if message["role"] == "user" else "🤖"
    
    st.markdown(f"""
    <div class="{msg_type}">
        <strong>{icon} {label}:</strong> {message["content"]}
        <small style="float: right; color: #666;">{message["timestamp"]}</small>
    </div>
    """, unsafe_allow_html=True)

# Chat input
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    user_input = col1.text_input("Ask me anything about shipping...", label_visibility="collapsed")
    send_button = col2.form_submit_button("Send", use_container_width=True)

    if send_button and user_input:
        if not st.session_state.connected:
            st.error("Please connect to OpenAI first.")
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Add user message
            st.session_state.messages.append({
                "role": "user", 
                "content": user_input, 
                "timestamp": timestamp
            })
            
            # Get AI response
            with st.spinner("🤖 AI is thinking..."):
                response = st.session_state.openai_connector.send_message(
                    user_input, 
                    st.session_state.messages
                )
            
            # Add AI response
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response, 
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            st.rerun()

# Clear chat button
if st.button("🗑️ Clear Chat", use_container_width=False):
    st.session_state.messages = []
    st.rerun()

# Footer
st.markdown("---")
st.markdown("*Powered by OpenAI GPT • Built with Streamlit*")
