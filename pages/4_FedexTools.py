import streamlit as st
import requests
import json
import os

# Load FedEx token (assumes you have a helper function or .env setup)
def get_token():
    url = "https://apis.fedex.com/oauth/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("FEDEX_CLIENT_ID"),
        "client_secret": os.getenv("FEDEX_CLIENT_SECRET")
    }
    r = requests.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    return r.json()["access_token"]

token = get_token()
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

2
st.set_page_config(page_title="FedEx DevKit Demo", layout="wide")
st.title("FedEx API Developer Toolkit Playground")

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
    st.subheader("📦 Rate & Transit Time")
    with st.form("rate_form"):
        origin = st.text_input("Origin Postal Code")
        destination = st.text_input("Destination Postal Code")
        weight = st.number_input("Weight (lbs)", value=2)
        submitted = st.form_submit_button("Get Rates")
        if submitted:
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
            r = requests.post("https://apis.fedex.com/rate/v1/rates/quotes", headers=headers, json=payload)
            st.json(r.json())

# Tool: Address Validation
elif tool == "Address Validation":
    st.subheader("🏠 Address Validator")
    address = st.text_input("Enter address to validate")
    if st.button("Validate"):
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
        r = requests.post("https://apis.fedex.com/address/v1/addresses/resolve", headers=headers, json=payload)
        st.json(r.json())

# Tool: Tracking
elif tool == "Tracking":
    st.subheader("📦 Track a Package")
    tracking_number = st.text_input("Tracking Number")
    if st.button("Track"):
        payload = {
            "trackingInfo": [{"trackingNumberInfo": {"trackingNumber": tracking_number}}],
            "includeDetailedScans": True
        }
        r = requests.post("https://apis.fedex.com/track/v1/trackingnumbers", headers=headers, json=payload)
        st.json(r.json())

# Add more tools for Pickup, Location Search, and Availability similarly...