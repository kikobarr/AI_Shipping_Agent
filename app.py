# app.py
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Shipping Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional font styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Load custom CSS
custom_css_path = Path("styles/chat_ui.css")
if custom_css_path.exists():
    with open(custom_css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Professional UI Navbar
st.markdown("""
<nav style="background-color:#1f2937; padding:1rem 2rem; display:flex; justify-content:space-between; align-items:center; font-family:'Inter', sans-serif; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <div style="color:#f9fafb; font-size:1.5rem; font-weight:600;">Shipping Assistant</div>
    <div style="display:flex; gap:2rem;">
        <a href="/Home" target="_self" style="color:#f9fafb; text-decoration:none; font-size:1rem; font-weight:500; padding:0.5rem 1rem; border-radius:6px; transition:all 0.2s ease;">Home</a>
        <a href="/Chatbot" target="_self" style="color:#f9fafb; text-decoration:none; font-size:1rem; font-weight:500; padding:0.5rem 1rem; border-radius:6px; transition:all 0.2s ease;">Chatbot</a>
        <a href="/Shipping" target="_self" style="color:#f9fafb; text-decoration:none; font-size:1rem; font-weight:500; padding:0.5rem 1rem; border-radius:6px; transition:all 0.2s ease;">Shipping</a>
        <a href="https://aws.amazon.com/bedrock/" target="_blank" style="color:#f9fafb; text-decoration:none; font-size:1rem; font-weight:500; padding:0.5rem 1rem; border-radius:6px; transition:all 0.2s ease;">AWS Bedrock</a>
        <a href="mailto:support@example.com" style="color:#f9fafb; text-decoration:none; font-size:1rem; font-weight:500; padding:0.5rem 1rem; border-radius:6px; transition:all 0.2s ease;">Contact</a>
    </div>
</nav>
""", unsafe_allow_html=True)

# Professional Welcome Section
st.markdown("""
<div style='text-align:center; padding:4rem 2rem; background:linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; box-shadow: 0px 4px 16px rgba(0,0,0,0.08); margin: 2rem 0; font-family: "Inter", sans-serif;'>
    <h1 style='margin-bottom:1rem; font-weight:600; color:#1f2937; font-size:2.5rem;'>Welcome to the Shipping Assistant</h1>
    <p style='font-size:1.2rem; color:#4b5563; line-height:1.6; max-width:600px; margin:0 auto;'>Streamline your shipping experience by comparing rates and automating logistics with professional efficiency.</p>
</div>
""", unsafe_allow_html=True)
