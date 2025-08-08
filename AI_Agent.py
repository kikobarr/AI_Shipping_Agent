import streamlit as st
from services.langchain_agent import LangChainFedExAgent
from datetime import datetime
import time

# Professional font styling with high contrast accessibility
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* High contrast status boxes */
    .status-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        border: 2px solid;
    }
    
    .status-connected {
        background-color: #000000;
        border-color: #00ff00;
        color: #00ff00;
    }
    
    .status-disconnected {
        background-color: #000000;
        border-color: #ff0000;
        color: #ff0000;
    }
    
    /* High contrast message bubbles */
    .user-message, .assistant-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        border: 2px solid;
        font-weight: 500;
    }
    
    .user-message {
        background-color: #000080;
        border-color: #ffffff;
        color: #ffffff;
    }
    
    .assistant-message {
        background-color: #000000;
        border-color: #00ff00;
        color: #ffffff;
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .status-connected {
            background-color: #000000;
            border-color: #00ff00;
            color: #00ff00;
        }
        
        .status-disconnected {
            background-color: #000000;
            border-color: #ff0000;
            color: #ff0000;
        }
        
        .user-message {
            background-color: #000080;
            border-color: #ffffff;
            color: #ffffff;
        }
        
        .assistant-message {
            background-color: #000000;
            border-color: #00ff00;
            color: #ffffff;
        }
    }
    
    /* Light mode high contrast */
    @media (prefers-color-scheme: light) {
        .status-connected {
            background-color: #ffffff;
            border-color: #008000;
            color: #008000;
        }
        
        .status-disconnected {
            background-color: #ffffff;
            border-color: #cc0000;
            color: #cc0000;
        }
        
        .user-message {
            background-color: #ffffff;
            border-color: #000080;
            color: #000080;
        }
        
        .assistant-message {
            background-color: #ffffff;
            border-color: #008000;
            color: #008000;
        }
    }
    
    /* High contrast text and links */
    .stMarkdown p, .stMarkdown li {
        color: var(--text-color) !important;
        font-weight: 500;
    }
    
    /* High contrast buttons */
    .stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }
    
    /* High contrast form inputs */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        font-weight: 500 !important;
    }
    
    /* High contrast expander */
    .streamlit-expanderHeader {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* High contrast success/error messages */
    .stSuccess {
        background-color: #000000 !important;
        color: #00ff00 !important;
        border: 2px solid #00ff00 !important;
    }
    
    .stError {
        background-color: #000000 !important;
        color: #ff0000 !important;
        border: 2px solid #ff0000 !important;
    }
    
    .stWarning {
        background-color: #000000 !important;
        color: #ffff00 !important;
        border: 2px solid #ffff00 !important;
    }
    
    /* High contrast headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color) !important;
        font-weight: 700 !important;
    }
    
    /* Ensure good contrast for small text */
    small, .caption {
        color: var(--text-color) !important;
        font-weight: 500 !important;
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
if 'langchain_agent' not in st.session_state:
    st.session_state.langchain_agent = LangChainFedExAgent()
    success, message = st.session_state.langchain_agent.initialize_connection()
    st.session_state.connected = success
    st.session_state.connection_message = message
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'connected' not in st.session_state:
    st.session_state.connected = False

st.header("AI Shipping Assistant with Live FedEx API")

# Status box
status_class = "status-connected" if st.session_state.connected else "status-disconnected"
status_text = "🟢 Connected to OpenAI + FedEx API" if st.session_state.connected else "🔴 Not Connected"
st.markdown(f"""
<div class="status-box {status_class}">
    {status_text}
</div>
""", unsafe_allow_html=True)

if not st.session_state.connected:
    st.error(f"Connection Error: {st.session_state.connection_message}")
    if st.button("🔄 Retry Connection"):
        success, message = st.session_state.langchain_agent.initialize_connection()
        st.session_state.connected = success
        st.session_state.connection_message = message
        st.rerun()

# Example prompts for users
if not st.session_state.messages:
    st.markdown("""
    ### 💡 Try asking me:
    How much does it cost to ship a 5lb package (4 x 5 x 7in) from 913 Paseo Camarillo, Camarillo, CA 93010 to 1 Harpst St, Arcata, CA 95521?
    """)

# Chat history
for message in st.session_state.messages:
    msg_type = "user-message" if message["role"] == "user" else "assistant-message"
    label = "You" if message["role"] == "user" else "AI Assistant"
    icon = "👤" if message["role"] == "user" else "🤖"
    
    # Check if this is a tool-calling response
    content = message["content"]
    
    st.markdown(f"""
    <div class="{msg_type}">
        <strong>{label}:</strong> {content}
        <small style="float: right; color: #666;">{message["timestamp"]}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Show debug information for assistant messages if available
    if message["role"] == "assistant" and "debug_info" in message:
        debug_info = message["debug_info"]
        if debug_info.get("tool_calls_made", False):
            with st.expander(f"🔍 Debug Info - Tools Used ({len(debug_info.get('tools_used', []))})"):
                st.success("✅ AI Agent successfully called FedEx API tools")
                for i, tool_info in enumerate(debug_info.get('tools_used', []), 1):
                    st.write(f"**Tool {i}: {tool_info['tool']}**")
                    st.json(tool_info['input'])
                    st.text_area(f"Tool Output {i}:", tool_info['output'], height=100)
        else:
            with st.expander("⚠️ Debug Info - No Tools Used"):
                st.warning("AI did not call any tools for this response. This might indicate hallucination.")
                if "error" in debug_info:
                    st.error(f"Error: {debug_info['error']}")

# Chat input
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    user_input = col1.text_input(
        "Ask about shipping rates, compare services, or get FedEx quotes...", 
        label_visibility="collapsed",
        placeholder="e.g., How much to ship 5lbs from LA to NYC?"
    )
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
            
            # Get AI response with tool calling and debug info
            with st.spinner("🤖 AI is thinking and may call FedEx API..."):
                response, debug_info = st.session_state.langchain_agent.send_message(user_input)
            
            # Add AI response
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response, 
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "debug_info": debug_info  # Store debug info
            })
            
            st.rerun()

# Clear chat button and memory info
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("Clear Chat", use_container_width=False):
        st.session_state.messages = []
        st.session_state.langchain_agent.clear_memory()
        st.rerun()

# Footer
st.markdown("---")
st.markdown("*Powered by OpenAI GPT + LangChain + Live FedEx API • Built with Streamlit*")
