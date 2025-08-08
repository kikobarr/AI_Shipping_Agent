import streamlit as st
from services.langchain_agent import LangChainFedExAgent
from datetime import datetime
import time

# Load CSS
try:
    with open("styles/chat_ui.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass  # CSS file not found, continue with default styling

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
if st.session_state.connected:
    st.success("🟢 Connected to OpenAI + FedEx API")
else:
    st.error("🔴 Not Connected")

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
    role = message["role"]
    content = message["content"]
    timestamp = message["timestamp"]
    
    # Use Streamlit's built-in chat message display
    with st.chat_message(role):
        st.write(content)
        st.caption(f"⏰ {timestamp}")
    
    # Show debug information for assistant messages if available
    if role == "assistant" and "debug_info" in message:
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
