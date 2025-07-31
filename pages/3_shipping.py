import streamlit as st
import pandas as pd
from services.shippingAPI import compare_all_quotes

st.set_page_config(page_title="Shipping Rate Comparison", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stForm > div {
    background-color: var(--background-secondary);
    padding: 2rem;
    border-radius: 12px;
    border: 1px solid var(--border-color);
}
.main-title {
    font-weight: 700;
    font-size: 2.3rem;
    margin-bottom: 1rem;
}
.section-header {
    font-weight: 600;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
}
.quote-result {
    background-color: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
}
.carrier-header {
    font-weight: 600;
    font-size: 1.2rem;
    color: #1e3a8a;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Shipping Rate Comparison</h1>', unsafe_allow_html=True)

# --- FORM ---
with st.form("shipping_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Origin Address")
        origin_street = st.text_input("Street", value="913 Paseo Camarillo")
        origin_apt = st.text_input("Apt / Suite", value="", key="origin_apt")
        origin_city = st.text_input("City", value="Camarillo")
        origin_state = st.text_input("State", value="CA")
        origin_postal = st.text_input("Postal Code", value="93010")
    with col2:
        st.subheader("Destination Address")
        dest_street = st.text_input("Street", value="302 Baldwin Park Dr")
        dest_apt = st.text_input("Apt / Suite", value="", key="dest_apt")
        dest_city = st.text_input("City", value="LaGrange")
        dest_state = st.text_input("State", value="GA")
        dest_postal = st.text_input("Postal Code", value="30241")

    st.markdown('<h3 class="section-header">Package Details</h3>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        weight = st.number_input("Weight (lbs)", min_value=0.1, step=0.1, format="%.2f", value=9.0)
        length = st.number_input("Length (in)", min_value=1.0, step=0.5, format="%.1f", value=4.0)
        packaging_type = st.selectbox("Packaging Type", ["YOUR_PACKAGING", "package", "tube", "soft_pack"])
    with col4:
        width = st.number_input("Width (in)", min_value=1.0, step=0.5, format="%.1f", value=5.0)
        height = st.number_input("Height (in)", min_value=1.0, step=0.5, format="%.1f", value=7.0)

    submit = st.form_submit_button("Compare Shipping Quotes")

# --- SUBMIT HANDLER ---
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

    with st.spinner("Fetching shipping quotes..."):
        quotes = compare_all_quotes(origin, destination, weight, dimensions, packaging_type)

    if "error" in quotes:
        st.error(quotes["error"])
    else:
                 # ---- TABLES: Cheapest and Fastest ----
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(quotes, orient='index').reset_index().rename(columns={"index": "service_name"})
        df["shipping_amount_usd"] = df["shipping_amount"].str.replace(" USD", "").astype(float)

        # Top 5 Cheapest
        cheapest = df.sort_values("shipping_amount_usd").head(5)
        st.markdown("### Top 5 Cheapest Shipping Options")
        st.dataframe(cheapest[["service_name", "carrier_code", "shipping_amount"]], use_container_width=True, hide_index=True)

        # Top 5 Fastest (based on label match)
        fast_keywords = ["Overnight", "Next Day", "Express", "Early"]
        fast_df = df[df["service_name"].str.contains("|".join(fast_keywords), case=False)]
        fastest = fast_df.sort_values("shipping_amount_usd").head(5)

        st.markdown("### Top 5 Fastest Shipping Options (by label)")
        st.dataframe(fastest[["service_name", "carrier_code", "shipping_amount"]], use_container_width=True, hide_index=True)
        
        

