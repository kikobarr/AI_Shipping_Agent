import streamlit as st
import pandas as pd
from services.shipping_integration import (
    get_fedex_shipping_quotes,
    format_fedex_results,
    display_fedex_summary,
    display_errors
)

st.set_page_config(page_title="FedEx Shipping Rates", layout="wide")

# --- CSS Styling with High Contrast Accessibility ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stForm > div {
    background-color: #000000;
    color: #ffffff;
    padding: 2rem;
    border-radius: 12px;
    border: 3px solid #ffffff;
}

.main-title {
    font-weight: 700;
    font-size: 2.3rem;
    margin-bottom: 1rem;
    color: var(--text-color);
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
}

.section-header {
    font-weight: 700;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
    color: var(--text-color);
}

.quote-result {
    background-color: #000000;
    border: 3px solid #00ff00;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
    color: #ffffff;
}

.metric-box {
    border: 3px solid #ffffff;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    background-color: #000000;
    color: #ffffff;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #00ff00;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
}

.metric-label {
    color: #ffffff;
    font-size: 1rem;
    font-weight: 600;
}

.fedex-badge {
    background-color: #ff0000;
    color: #ffffff;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
    border: 1px solid #ffffff;
}

/* Light mode high contrast */
@media (prefers-color-scheme: light) {
    .stForm > div {
        background-color: #ffffff;
        color: #000000;
        border: 3px solid #000000;
    }
    
    .quote-result {
        background-color: #ffffff;
        border: 3px solid #008000;
        color: #000000;
    }
    
    .metric-box {
        border: 3px solid #000000;
        background-color: #ffffff;
        color: #000000;
    }
    
    .metric-value {
        color: #008000;
    }
    
    .metric-label {
        color: #000000;
    }
}

/* High contrast form inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stNumberInput > div > div > input {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 2px solid #000000 !important;
    font-weight: 600 !important;
}

/* High contrast buttons */
.stButton > button {
    background-color: #000000 !important;
    color: #ffffff !important;
    border: 2px solid #ffffff !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
}

.stButton > button:hover {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 2px solid #000000 !important;
}

/* High contrast dataframes */
.stDataFrame {
    border: 3px solid var(--text-color) !important;
}

.stDataFrame table {
    border-collapse: collapse !important;
}

.stDataFrame th, .stDataFrame td {
    border: 1px solid var(--text-color) !important;
    font-weight: 600 !important;
}

/* High contrast success/error messages */
.stSuccess {
    background-color: #000000 !important;
    color: #00ff00 !important;
    border: 2px solid #00ff00 !important;
    font-weight: 600 !important;
}

.stError {
    background-color: #000000 !important;
    color: #ff0000 !important;
    border: 2px solid #ff0000 !important;
    font-weight: 600 !important;
}

.stInfo {
    background-color: #000000 !important;
    color: #00ffff !important;
    border: 2px solid #00ffff !important;
    font-weight: 600 !important;
}

/* High contrast text */
.stMarkdown p, .stMarkdown li {
    font-weight: 500 !important;
}

h1, h2, h3, h4, h5, h6 {
    font-weight: 700 !important;
}

/* High contrast labels */
.stSelectbox label, .stTextInput label, .stNumberInput label {
    font-weight: 700 !important;
    color: var(--text-color) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🚚 FedEx Shipping Rates</h1>', unsafe_allow_html=True)

# Add info about the FedEx integration
st.info("🔴 **Live FedEx API Integration** - Get real-time shipping rates directly from FedEx sandbox!")

# --- Form Section ---
with st.form("fedex_shipping_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📍 Origin Address")
        origin = {
            "street": st.text_input("Street", value="913 Paseo Camarillo"),
            "apt": st.text_input("Apt / Suite", value="", key="origin_apt"),
            "city": st.text_input("City", value="Camarillo"),
            "state": st.text_input("State", value="CA"),
            "postalCode": st.text_input("Postal Code", value="93010")
        }
    with col2:
        st.subheader("📍 Destination Address")
        destination = {
            "street": st.text_input("Street", value="302 Baldwin Park Dr"),
            "apt": st.text_input("Apt / Suite", value="", key="dest_apt"),
            "city": st.text_input("City", value="LaGrange"),
            "state": st.text_input("State", value="GA"),
            "postalCode": st.text_input("Postal Code", value="30241")
        }

    st.markdown('<h3 class="section-header">📦 Package Details</h3>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        weight = st.number_input("Weight (lbs)", min_value=0.1, step=0.1, format="%.2f", value=9.0)
        length = st.number_input("Length (in)", min_value=1.0, step=0.5, format="%.1f", value=4.0)
        packaging_type = st.selectbox("Packaging Type", ["YOUR_PACKAGING", "FEDEX_BOX", "FEDEX_ENVELOPE"])
    with col4:
        width = st.number_input("Width (in)", min_value=1.0, step=0.5, format="%.1f", value=5.0)
        height = st.number_input("Height (in)", min_value=1.0, step=0.5, format="%.1f", value=7.0)

    submit = st.form_submit_button("🔍 Get FedEx Shipping Quotes", use_container_width=True)

# --- Handle Submission ---
if submit:
    dimensions = {"length": length, "width": width, "height": height}

    with st.spinner("🔄 Fetching live FedEx rates..."):
        # Use the FedEx-only shipping integration
        results = get_fedex_shipping_quotes(
            origin, destination, weight, dimensions, packaging_type
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
        st.error("❌ No FedEx shipping quotes were retrieved. Please check your addresses and try again.")

# --- Footer ---
st.markdown("---")
st.markdown("*Powered by live FedEx API integration • Built with Streamlit*")
