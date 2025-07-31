# pages/Shipping.py
import streamlit as st
from services.quotes import get_all_quotes

st.set_page_config(page_title="Shipping", layout="wide")

st.markdown("""
    <style>
        .stForm > div {
            background-color: #f9f9f9;
            padding: 1rem;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Shipping Rate Comparison")
st.write("Use the form below to compare shipping rates from FedEx.")

with st.form("shipping_form"):
    st.subheader("From Address")
    col1, col2 = st.columns(2)
    with col1:
        origin_street = st.text_input("Street Address", key="origin_street")
        origin_apt = st.text_input("Apartment/Suite/House", key="origin_apt")
        origin_city = st.text_input("City", key="origin_city")
        origin_state = st.text_input("State", key="origin_state")
        origin_postal = st.text_input("Postal Code", key="origin_postal")
    with col2:
        dest_street = st.text_input("Street Address", key="dest_street")
        dest_apt = st.text_input("Apartment/Suite/House", key="dest_apt")
        dest_city = st.text_input("City", key="dest_city")
        dest_state = st.text_input("State", key="dest_state")
        dest_postal = st.text_input("Postal Code", key="dest_postal")

    st.subheader("Package Details")
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
            st.subheader(carrier.upper())
            if isinstance(data, dict):
                for k, v in data.items():
                    st.write(f"{k}: {v}")
            else:
                st.write(data)
    except Exception as e:
        st.error(f"Error fetching quotes: {e}")