import streamlit as st

st.set_page_config(page_title="Home", layout="wide")

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
    
    .welcome-content {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        line-height: 1.6;
        color: #4b5563;
        background-color: #f8fafc;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    
    .feature-list {
        font-family: 'Inter', sans-serif;
        color: #374151;
        margin-top: 1rem;
    }
    
    .feature-list li {
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 class="main-title">Home</h2>', unsafe_allow_html=True)

st.markdown("""
<div class="welcome-content">
    <p><strong>Welcome to the Shipping Assistant App!</strong></p>
    
    <div class="feature-list">
        <p>Use the navigation to:</p>
        <ul>
            <li>Connect to your AWS Bedrock agent</li>
            <li>Chat with the assistant</li>
            <li>Get shipping rates or track packages</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)
