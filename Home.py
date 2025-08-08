import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# Set up the page
st.set_page_config(page_title="Shipping Assistant - Home", layout="wide", initial_sidebar_state="expanded")

# Professional font styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 2.5rem;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    .professional-button {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        transition: background-color 0.2s ease;
    }
    
    .professional-button:hover {
        background-color: #2563eb;
    }
    
    .sidebar-text {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


# HOME PAGE UI
st.markdown('<h1 class="main-title">Welcome to the Shipping Assistant Dashboard</h1>', unsafe_allow_html=True)
st.markdown("Use the quick actions below or navigate using the sidebar.")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Get Shipping Rates", use_container_width=True):
        switch_page("3_Shipping")

with col2:
    if st.button("Track a Package", use_container_width=True):
        switch_page("3_Shipping")  # Assuming same page handles both

with col3:
    if st.button("Talk to AI Agent", use_container_width=True):
        switch_page("2_AI_Agent")

st.divider()

st.info("Tip: You can also use the sidebar to explore all features.")
