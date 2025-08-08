import streamlit as st
from services.langchain_agent import LangChainFedExAgent
from services.shipping_integration import (
    get_fedex_shipping_quotes,
    format_fedex_results,
    display_fedex_summary,
    display_errors
)
from datetime import datetime
import time

# Configure as single page app
st.set_page_config(
    page_title="AI Shipping Assistant", 
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar completely
st.markdown("""
<style>
    .css-1d391kg {display: none}
    .css-1rs6os {display: none}
    .css-17eq0hr {display: none}
    [data-testid="stSidebar"] {display: none}
    [data-testid="collapsedControl"] {display: none}
</style>
""", unsafe_allow_html=True)

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
    st.success("Connected to OpenAI + FedEx API")
else:
    st.error("Not Connected")

if not st.session_state.connected:
    st.error(f"Connection Error: {st.session_state.connection_message}")
    if st.button("Retry Connection"):
        success, message = st.session_state.langchain_agent.initialize_connection()
        st.session_state.connected = success
        st.session_state.connection_message = message
        st.rerun()

# Example prompts for users
if not st.session_state.messages:
    st.markdown("""
    **Try asking me:** How much does it cost to ship a 5lb package (4 x 5 x 7in) from 913 Paseo Camarillo, Camarillo, CA 93010 
    to 1 Harpst St, Arcata, CA 95521?
    """)

# Chat history
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    timestamp = message["timestamp"]
    
    # Use Streamlit's built-in chat message display
    with st.chat_message(role):
        st.write(content)
        st.caption(f"{timestamp}")
    
    # Show debug information for assistant messages if available
    if role == "assistant" and "debug_info" in message:
        debug_info = message["debug_info"]
        if debug_info.get("tool_calls_made", False):
            with st.expander(f"Debug Info - Tools Used ({len(debug_info.get('tools_used', []))})"):
                st.success("AI Agent successfully called FedEx API tools")
                for i, tool_info in enumerate(debug_info.get('tools_used', []), 1):
                    st.write(f"**Tool {i}: {tool_info['tool']}**")
                    st.json(tool_info['input'])
                    st.text_area(f"Tool Output {i}:", tool_info['output'], height=100)
        else:
            with st.expander("Debug Info - No Tools Used"):
                st.warning("AI did not call any tools for this response. This might indicate hallucination.")
                if "error" in debug_info:
                    st.error(f"Error: {debug_info['error']}")

# Chat input
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    user_input = col1.text_input(
        "Ask about shipping rates, compare services, or get FedEx quotes...", 
        label_visibility="collapsed"
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
            with st.spinner("Agent is working on your request."):
                response, debug_info = st.session_state.langchain_agent.send_message(user_input)
            
            # Add AI response
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response, 
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "debug_info": debug_info  # Store debug info
            })
            
            st.rerun()

# Shipping Form Section
st.markdown("---")
st.header("FedEx Quotes Directly from API")
st.info("To confirm that the AI Agent is not hallucinating, use the form below to get quotes directly from Fedex's sandbox API and compare it to what the AI Agent fetches.")

with st.form("fedex_shipping_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Origin Address")
        origin = {
            "street": st.text_input("Street", value="913 Paseo Camarillo", key="origin_street"),
            "apt": st.text_input("Apt / Suite", value="", key="origin_apt"),
            "city": st.text_input("City", value="Camarillo", key="origin_city"),
            "state": st.text_input("State", value="CA", key="origin_state"),
            "postalCode": st.text_input("Postal Code", value="93010", key="origin_postal")
        }
    with col2:
        st.subheader("📍 Destination Address")
        destination = {
            "street": st.text_input("Street", value="1 Harpst St", key="dest_street"),
            "apt": st.text_input("Apt / Suite", value="", key="dest_apt"),
            "city": st.text_input("City", value="Arcata", key="dest_city"),
            "state": st.text_input("State", value="CA", key="dest_state"),
            "postalCode": st.text_input("Postal Code", value="95521", key="dest_postal")
        }

    st.subheader("Package Details")
    col3, col4 = st.columns(2)
    with col3:
        weight = st.number_input("Weight (lbs)", min_value=0.1, step=0.1, format="%.2f", value=9.0, key="package_weight")
        length = st.number_input("Length (in)", min_value=1.0, step=0.5, format="%.1f", value=4.0, key="package_length")
    with col4:
        width = st.number_input("Width (in)", min_value=1.0, step=0.5, format="%.1f", value=5.0, key="package_width")
        height = st.number_input("Height (in)", min_value=1.0, step=0.5, format="%.1f", value=7.0, key="package_height")

    submit = st.form_submit_button("🔍 Get FedEx Shipping Quotes", use_container_width=True)

# Handle Form Submission
if submit:
    dimensions = {"length": length, "width": width, "height": height}

    with st.spinner("🔄 Fetching live FedEx rates..."):
        # Use the FedEx-only shipping integration with default packaging
        results = get_fedex_shipping_quotes(
            origin, destination, weight, dimensions, "YOUR_PACKAGING"
        )

    # Display any errors
    if results['errors']:
        display_errors(results['errors'])

    # Check if we have any quotes
    if results['quotes']:
        # Format results for display
        df = format_fedex_results(results)
        
        if not df.empty:
            # Display the FedEx results
            display_fedex_summary(df)
        else:
            st.error("No FedEx shipping quotes could be formatted for display")
    else:
        st.error("No FedEx shipping quotes were retrieved. Please check your addresses and try again.")

# Footer
st.markdown("---")
st.markdown("*Powered by OpenAI GPT + LangChain + Live FedEx API • Built with Streamlit*")
