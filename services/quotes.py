# services/quotes.py
import json
import requests

# Replace with secure storage in production
FEDEX_CLIENT_ID = "l73e80924b04f249768f45f5767778d0a3"
FEDEX_CLIENT_SECRET = "13dff649cdf6425698db8491ea2e3d8b"


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
    return response.json()['access_token']


def get_fedex_quote(origin, destination, weight):
    token = get_fedex_token()
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    payload = build_fedex_payload(origin, destination, weight)
    response = requests.post("https://api.fedex.com/rate/v2/rates/quotes", headers=headers, json=payload)
    return response.json()


def build_fedex_payload(origin, destination, weight_lbs):
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
                    "value": "207084866"
                },
                "address": {
                    "city": origin["city"],
                    "postalCode": origin["postalCode"],
                    "countryCode": origin.get("countryCode", "US"),
                    "streetLines": [origin.get("street", "")],
                    "residential": False,
                    "stateOrProvinceCode": origin["state"]
                }
            },
            "recipients": [{
                "address": {
                    "city": destination["city"],
                    "postalCode": destination["postalCode"],
                    "countryCode": destination.get("countryCode", "US"),
                    "streetLines": [destination.get("street", "")],
                    "residential": False,
                    "stateOrProvinceCode": destination["state"]
                }
            }],
            "shipTimestamp": "2025-07-31",
            "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
            "packagingType": "FEDEX_SMALL_BOX",
            "shippingChargesPayment": {
                "payor": {
                    "responsibleParty": {
                        "accountNumber": {
                            "key": FEDEX_CLIENT_ID,
                            "value": "207084866"
                        },
                        "address": {
                            "countryCode": "US"
                        }
                    }
                }
            },
            "requestedPackageLineItems": [{
                "groupPackageCount": 1,
                "physicalPackaging": "FEDEX_SMALL_BOX",
                "insuredValue": {"currency": "USD", "amount": 0},
                "weight": {"units": "LB", "value": weight_lbs}
            }],
            "preferredCurrency": "USD"
        },
        "carrierCodes": ["FDXG", "FDXE"],
        "returnLocalizedDateTime": True,
        "webSiteCountryCode": "US"
    }


def get_all_quotes(origin, destination, weight):
    return {
        "fedex": get_fedex_quote(origin, destination, weight),
        # Future: add UPS and DHL when APIs are ready
    }
