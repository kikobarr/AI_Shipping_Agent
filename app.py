# app.py
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Shipping Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
custom_css_path = Path("styles/chat_ui.css")
if custom_css_path.exists():
    with open(custom_css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Modern UI Navbar
st.markdown("""
<nav style="background-color:#1f2937; padding:1rem; display:flex; justify-content:space-between; align-items:center;">
    <div style="color:#f9fafb; font-size:1.5rem; font-weight:600;">Shipping Assistant</div>
    <div style="display:flex; gap:2rem;">
        <a href="/Home" target="_self" style="color:#f9fafb; text-decoration:none; font-size:1rem;">Home</a>
        <a href="/Chatbot" target="_self" style="color:#f9fafb; text-decoration:none; font-size:1rem;">Chatbot</a>
        <a href="/Shipping" target="_self" style="color:#f9fafb; text-decoration:none; font-size:1rem;">Shipping</a>
        <a href="https://aws.amazon.com/bedrock/" target="_blank" style="color:#f9fafb; text-decoration:none; font-size:1rem;">AWS Bedrock</a>
        <a href="mailto:support@example.com" style="color:#f9fafb; text-decoration:none; font-size:1rem;">Contact</a>
    </div>
</nav>
""", unsafe_allow_html=True)

# Welcome Section
st.markdown("""
<div style='text-align:center; padding:4rem 2rem; background:linear-gradient(to right, #f3f4f6, #e5e7eb); border-radius: 12px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05);'>
    <h1 style='margin-bottom:0.5rem;'>Welcome to the Shipping Assistant</h1>
    <p style='font-size:1.1rem; color:#4b5563;'>Streamline your shipping experience by comparing rates and automating logistics effortlessly.</p>
</div>
""", unsafe_allow_html=True)
