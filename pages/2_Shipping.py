import streamlit as st
import pandas as pd
from services.shipping_integration import (
    get_fedex_shipping_quotes,
    format_fedex_results,
    display_fedex_summary,
    display_errors
)

st.set_page_config(page_title="FedEx Shipping Rates", layout="wide")

st.title("🚚 FedEx Shipping Rates")

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
