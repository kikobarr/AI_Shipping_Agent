import streamlit as st
from pathlib import Path

# Set page config
st.set_page_config(page_title="Shipping Assistant", layout="wide", initial_sidebar_state="collapsed")

# Load CSS
with open("styles/chat_ui.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# === NAVBAR ===
st.markdown("""
<div class="navbar">
    <h2>📦 Shipping Assistant</h2>
    <div class="nav-links">
        <a href="/Home" target="_self">Home</a>
        <a href="/Chatbot" target="_self">Chatbot</a>
        <a href="https://aws.amazon.com/bedrock/" target="_blank">AWS Bedrock</a>
        <a href="mailto:support@example.com">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Welcome or redirect logic
st.markdown("""
<div style='padding:2rem; text-align:center'>
    <h3>Welcome to the Shipping Assistant</h3>
    <p>Select a page from the top navigation bar.</p>
</div>
""", unsafe_allow_html=True)