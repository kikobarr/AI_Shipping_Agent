import os
import requests
from dotenv import load_dotenv

load_dotenv()

FEDEX_CLIENT_ID = os.getenv("FEDEX_CLIENT_ID")
FEDEX_CLIENT_SECRET = os.getenv("FEDEX_CLIENT_SECRET")
FEDEX_ACCOUNT_NUMBER = os.getenv("FEDEX_ACCOUNT_NUMBER")

def get_fedex_token():
    url = "https://apis.fedex.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": FEDEX_CLIENT_ID,
        "client_secret": FEDEX_CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def build_fedex_payload(origin, destination, weight_lbs, dimensions, packaging_type):
    return {
        "rateRequestControlParameters": {
            "rateSortOrder": "COMMITASCENDING",
            "returnTransitTimes": True,
            "servicesNeededOnRateFailure": False
        },
        "requestedShipment": {
            "shipper": {
                "accountNumber": {
                    "key": FEDEX_CLIENT_ID,
                    "value": FEDEX_ACCOUNT_NUMBER
                },
                "address": {
                    "streetLines": [origin.get("street", ""), origin.get("apt", "")],
                    "city": origin["city"],
                    "stateOrProvinceCode": origin["state"],
                    "postalCode": origin["postalCode"],
                    "countryCode": "US",
                    "residential": False
                }
            },
            "recipients": [{
                "address": {
                    "streetLines": [destination.get("street", ""), destination.get("apt", "")],
                    "city": destination["city"],
                    "stateOrProvinceCode": destination["state"],
                    "postalCode": destination["postalCode"],
                    "countryCode": "US",
                    "residential": False
                }
            }],
            "shipTimestamp": "2025-07-31",
            "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
            "packagingType": packaging_type,
            "shippingChargesPayment": {
                "payor": {
                    "responsibleParty": {
                        "accountNumber": {
                            "key": FEDEX_CLIENT_ID,
                            "value": FEDEX_ACCOUNT_NUMBER
                        },
                        "address": {"countryCode": "US"}
                    }
                }
            },
            "requestedPackageLineItems": [{
                "groupPackageCount": 1,
                "physicalPackaging": packaging_type,
                "insuredValue": {"currency": "USD", "amount": 0},
                "weight": {"units": "LB", "value": weight_lbs},
                "dimensions": {
                    "length": dimensions["length"],
                    "width": dimensions["width"],
                    "height": dimensions["height"],
                    "units": "IN"
                }
            }],
            "preferredCurrency": "USD"
        },
        "carrierCodes": ["FDXG", "FDXE"],
        "returnLocalizedDateTime": True,
        "webSiteCountryCode": "US"
    }

def get_all_quotes(origin, destination, weight, dimensions, packaging_type):
    token = get_fedex_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = build_fedex_payload(origin, destination, weight, dimensions, packaging_type)

    response = requests.post(
        "https://apis.fedex.com/rate/v2/rates/quotes",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    return response.json()