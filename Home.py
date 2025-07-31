import streamlit as st
from streamlit_extras.switch_page_button import switch_page

# Set up the page
st.set_page_config(page_title="Shipping Assistant - Home", layout="wide", initial_sidebar_state="expanded")

# Sidebar menu
page = st.sidebar.selectbox("📚 Navigate to a Page", ["Home", "Chatbot", "Shipping"])

# Redirect based on sidebar selection
if page == "Chatbot":
    switch_page("2_Chatbot")
elif page == "Shipping":
    switch_page("3_Shipping")

# HOME PAGE UI
st.title("🏠 Welcome to the Shipping Assistant Dashboard")
st.markdown("Use the quick actions below or navigate using the sidebar.")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📦 Get Shipping Rates", use_container_width=True):
        switch_page("3_Shipping")

with col2:
    if st.button("🚚 Track a Package", use_container_width=True):
        switch_page("3_Shipping")  # Assuming same page handles both

with col3:
    if st.button("💬 Talk to Chatbot", use_container_width=True):
        switch_page("2_Chatbot")

st.divider()

st.info("Tip: You can also use the sidebar to explore all features.")