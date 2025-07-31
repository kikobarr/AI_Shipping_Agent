import streamlit as st
from services.aws_agent_connector import AWSAgentConnector
from datetime import datetime
import time

# Professional font styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .navbar {
        background-color: #f8fafc;
        padding: 1rem 2rem;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    .navbar h2 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1f2937;
        margin: 0;
        display: inline-block;
    }
    
    .nav-links {
        float: right;
        font-family: 'Inter', sans-serif;
    }
    
    .nav-links a {
        margin-left: 2rem;
        text-decoration: none;
        color: #4b5563;
        font-weight: 500;
        transition: color 0.2s ease;
    }
    
    .nav-links a:hover {
        color: #3b82f6;
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
    
    .user-message, .agent-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
    }
    
    .user-message {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
    }
    
    .agent-message {
        background-color: #f9fafb;
        border-left: 4px solid #6b7280;
    }
</style>
""", unsafe_allow_html=True)

# Load CSS
try:
    with open("styles/chat_ui.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass  # CSS file not found, continue with inline styles

# === NAVBAR ===
st.markdown("""
<div class="navbar">
    <h2>Shipping Assistant</h2>
    <div class="nav-links">
        <a href="/Home" target="_self">Home</a>
        <a href="/Chatbot" target="_self">Chatbot</a>
        <a href="https://aws.amazon.com/bedrock/" target="_blank">AWS Bedrock</a>
        <a href="mailto:support@example.com">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent_connector' not in st.session_state:
    st.session_state.agent_connector = AWSAgentConnector()
    success, message = st.session_state.agent_connector.initialize_connection()
    st.session_state.connected = success
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session-{int(time.time())}"
if 'connected' not in st.session_state:
    st.session_state.connected = False

st.header("Chat with Your Agent")

# # Sidebar config
# with st.sidebar:
#     st.header("AWS Agent Configuration")
#     with st.form("aws_config"):
#         aws_access_key = st.text_input("AWS Access Key ID", type="password")
#         aws_secret_key = st.text_input("AWS Secret Access Key", type="password")
#         region = st.selectbox("AWS Region", ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"])
#         agent_id = st.text_input("Bedrock Agent ID")
#         agent_alias_id = st.text_input("Agent Alias ID", value="TSTALIASID")
#         submit_config = st.form_submit_button("Connect to Agent")

#         if submit_config:
#             if all([aws_access_key, aws_secret_key, region, agent_id]):
#                 with st.spinner("Connecting to AWS Bedrock Agent..."):
#                     success, message = st.session_state.agent_connector.initialize_connection(
#                         aws_access_key, aws_secret_key, region, agent_id, agent_alias_id
#                     )
#                     st.session_state.connected = success
#                     st.success(message) if success else st.error(message)
#             else:
#                 st.error("Please fill in all required fields")

# Status box
st.markdown(f"""
<div class="status-box {'status-connected' if st.session_state.connected else 'status-disconnected'}">
    {'Connected' if st.session_state.connected else 'Not Connected'} 
</div>
""", unsafe_allow_html=True)

# Chat history
for message in st.session_state.messages:
    msg_type = "user-message" if message["role"] == "user" else "agent-message"
    label = "You" if message["role"] == "user" else "Agent"
    st.markdown(f"""
    <div class="{msg_type}">
        <strong>{label}:</strong> {message["content"]}
        <small style="float: right; color: #666;">{message["timestamp"]}</small>
    </div>
    """, unsafe_allow_html=True)

# Chat input
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    user_input = col1.text_input("Ask...", label_visibility="collapsed")
    send_button = col2.form_submit_button("Send")

    if send_button and user_input:
        if not st.session_state.connected:
            st.error("Please connect first.")
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
            with st.spinner("Agent is thinking..."):
                response = st.session_state.agent_connector.send_message(user_input, st.session_state.session_id)
            st.session_state.messages.append({"role": "agent", "content": response, "timestamp": datetime.now().strftime("%H:%M:%S")})
            st.rerun()

# Quick actions
st.markdown("### Quick Actions")
col1, col2, col3 = st.columns(3)
def quick_action(prompt):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": timestamp})
    with st.spinner("Agent is responding..."):
        response = st.session_state.agent_connector.send_message(prompt, st.session_state.session_id)
    st.session_state.messages.append({"role": "agent", "content": response, "timestamp": datetime.now().strftime("%H:%M:%S")})
    st.rerun()

with col1:
    if st.button("Get Shipping Rates", use_container_width=True) and st.session_state.connected:
        quick_action("Can you help me get shipping rates for a package?")
with col2:
    if st.button("Track Package", use_container_width=True) and st.session_state.connected:
        quick_action("I need help tracking a package. What information do you need?")
with col3:
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = f"session-{int(time.time())}"
        st.rerun()
