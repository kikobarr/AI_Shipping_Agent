import streamlit as st
import requests
import json
import os

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
        padding: 0.75rem 1.5rem;
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
    
    .stForm > div {
        background-color: #f8fafc;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Load FedEx token (assumes you have a helper function or .env setup)
def get_token():
    try:
        url = "https://apis.fedex.com/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": os.getenv("FEDEX_CLIENT_ID"),
            "client_secret": os.getenv("FEDEX_CLIENT_SECRET")
        }
        r = requests.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        return r.json()["access_token"]
    except:
        return None

token = get_token()
if token:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
else:
    headers = {}

st.set_page_config(page_title="FedEx DevKit Demo", layout="wide")
st.markdown('<h1 class="main-title">FedEx API Developer Toolkit Playground</h1>', unsafe_allow_html=True)

tool = st.sidebar.selectbox("Choose API Tool", [
    "Rate Lookup",
    "Address Validation",
    "Pickup Scheduler",
    "Service Availability",
    "Tracking",
    "Location Finder"
])

# Tool: Rate Lookup
if tool == "Rate Lookup":
    st.markdown('<h3 class="section-header">Rate & Transit Time</h3>', unsafe_allow_html=True)
    with st.form("rate_form"):
        origin = st.text_input("Origin Postal Code")
        destination = st.text_input("Destination Postal Code")
        weight = st.number_input("Weight (lbs)", value=2)
        submitted = st.form_submit_button("Get Rates")
        if submitted and token:
            payload = {
                "accountNumber": {"value": "207084866"},
                "requestedShipment": {
                    "shipper": {"address": {"postalCode": origin, "countryCode": "US"}},
                    "recipient": {"address": {"postalCode": destination, "countryCode": "US"}},
                    "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
                    "rateRequestType": ["ACCOUNT"],
                    "requestedPackageLineItems": [{"weight": {"units": "LB", "value": weight}}]
                }
            }
            try:
                r = requests.post("https://apis.fedex.com/rate/v1/rates/quotes", headers=headers, json=payload)
                st.json(r.json())
            except Exception as e:
                st.error(f"Error: {e}")
        elif submitted and not token:
            st.error("FedEx API credentials not configured")

# Tool: Address Validation
elif tool == "Address Validation":
    st.markdown('<h3 class="section-header">Address Validator</h3>', unsafe_allow_html=True)
    address = st.text_input("Enter address to validate")
    if st.button("Validate") and token:
        payload = {
            "addressesToValidate": [{
                "address": {
                    "streetLines": [address],
                    "city": "San Jose",
                    "stateOrProvinceCode": "CA",
                    "postalCode": "95112",
                    "countryCode": "US"
                }
            }]
        }
        try:
            r = requests.post("https://apis.fedex.com/address/v1/addresses/resolve", headers=headers, json=payload)
            st.json(r.json())
        except Exception as e:
            st.error(f"Error: {e}")
    elif st.button("Validate") and not token:
        st.error("FedEx API credentials not configured")

# Tool: Tracking
elif tool == "Tracking":
    st.markdown('<h3 class="section-header">Track a Package</h3>', unsafe_allow_html=True)
    tracking_number = st.text_input("Tracking Number")
    if st.button("Track") and token:
        payload = {
            "trackingInfo": [{"trackingNumberInfo": {"trackingNumber": tracking_number}}],
            "includeDetailedScans": True
        }
        try:
            r = requests.post("https://apis.fedex.com/track/v1/trackingnumbers", headers=headers, json=payload)
            st.json(r.json())
        except Exception as e:
            st.error(f"Error: {e}")
    elif st.button("Track") and not token:
        st.error("FedEx API credentials not configured")

# Add placeholder for other tools
else:
    st.markdown(f'<h3 class="section-header">{tool}</h3>', unsafe_allow_html=True)
    st.info(f"{tool} functionality coming soon...")

if not token:
    st.warning("FedEx API credentials not found. Please configure FEDEX_CLIENT_ID and FEDEX_CLIENT_SECRET environment variables.")
