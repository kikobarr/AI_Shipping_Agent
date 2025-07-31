# pages/Shipping.py
import streamlit as st
from services.quotes import get_all_quotes

st.set_page_config(page_title="Shipping", layout="wide")

# Professional font styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .stForm > div {
        background-color: #f8fafc;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 2.5rem;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    .section-header {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        transition: background-color 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #2563eb;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        font-family: 'Inter', sans-serif;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
    }
    
    .quote-result {
        background-color: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
    }
    
    .carrier-header {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1e40af;
        font-size: 1.25rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Shipping Rate Comparison</h1>', unsafe_allow_html=True)
st.write("Use the form below to compare shipping rates from FedEx.")

with st.form("shipping_form"):
    st.markdown('<h3 class="section-header">From Address</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Origin Address**")
        origin_street = st.text_input("Street Address", key="origin_street")
        origin_apt = st.text_input("Apartment/Suite/House", key="origin_apt")
        origin_city = st.text_input("City", key="origin_city")
        origin_state = st.text_input("State", key="origin_state")
        origin_postal = st.text_input("Postal Code", key="origin_postal")
    with col2:
        st.markdown("**Destination Address**")
        dest_street = st.text_input("Street Address", key="dest_street")
        dest_apt = st.text_input("Apartment/Suite/House", key="dest_apt")
        dest_city = st.text_input("City", key="dest_city")
        dest_state = st.text_input("State", key="dest_state")
        dest_postal = st.text_input("Postal Code", key="dest_postal")

    st.markdown('<h3 class="section-header">Package Details</h3>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        weight = st.number_input("Weight (lbs)", min_value=1, step=1, key="weight")
        length = st.number_input("Length (in)", min_value=1, step=1, key="length")
        packaging_type = st.selectbox(
            "Packaging Type",
            ["FEDEX_ENVELOPE", "FEDEX_PAK", "FEDEX_BOX", "FEDEX_TUBE", "FEDEX_10KG_BOX", "FEDEX_25KG_BOX", "YOUR_PACKAGING"],
            key="packaging_type"
        )
    with col4:
        width = st.number_input("Width (in)", min_value=1, step=1, key="width")
        height = st.number_input("Height (in)", min_value=1, step=1, key="height")

    submit = st.form_submit_button("Get FedEx Quote")

if submit:
    origin = {
        "street": origin_street,
        "apt": origin_apt,
        "city": origin_city,
        "state": origin_state,
        "postalCode": origin_postal
    }
    destination = {
        "street": dest_street,
        "apt": dest_apt,
        "city": dest_city,
        "state": dest_state,
        "postalCode": dest_postal
    }
    dimensions = {
        "length": length,
        "width": width,
        "height": height
    }

    try:
        quotes = get_all_quotes(origin, destination, weight, dimensions, packaging_type)
        st.success("Quotes retrieved successfully!")
        for carrier, data in quotes.items():
            st.markdown(f'<div class="quote-result">', unsafe_allow_html=True)
            st.markdown(f'<h4 class="carrier-header">{carrier.upper()}</h4>', unsafe_allow_html=True)
            if isinstance(data, dict):
                for k, v in data.items():
                    st.write(f"**{k}:** {v}")
            else:
                st.write(data)
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error fetching quotes: {e}")
