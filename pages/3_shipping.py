# pages/Shipping.py
import streamlit as st
from services.quotes import get_all_quotes

st.set_page_config(page_title="Shipping", layout="centered")

st.markdown("""
    <style>
        .stForm > div {
            background-color: #f9f9f9;
            padding: 1rem;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📬 Shipping Rate Comparison")
st.write("Use the form below to compare shipping rates from FedEx.")

with st.form("shipping_form"):
    col1, col2 = st.columns(2)
    with col1:
        origin_city = st.text_input("Origin City", "Santa Margarita")
        origin_state = st.text_input("Origin State", "CA")
        origin_postal = st.text_input("Origin Postal Code", "93453")
    with col2:
        dest_city = st.text_input("Destination City", "San Jose")
        dest_state = st.text_input("Destination State", "CA")
        dest_postal = st.text_input("Destination Postal Code", "95112")

    weight = st.number_input("Package Weight (lbs)", value=2.0)
    submit = st.form_submit_button("Get FedEx Quote")

if submit:
    origin = {"city": origin_city, "state": origin_state, "postalCode": origin_postal}
    destination = {"city": dest_city, "state": dest_state, "postalCode": dest_postal}
    try:
        quotes = get_all_quotes(origin, destination, weight)
        st.success("Quotes retrieved successfully!")
        for carrier, data in quotes.items():
            st.subheader(carrier.upper())
            if isinstance(data, dict):
                for k, v in data.items():
                    st.write(f"{k}: {v}")
            else:
                st.write(data)
    except Exception as e:
        st.error(f"Error fetching quotes: {e}")
