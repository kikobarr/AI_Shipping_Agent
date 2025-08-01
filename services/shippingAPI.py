import os
import requests
from dotenv import load_dotenv
import json

# Load .env
load_dotenv()
SHIPENGINE_API_KEY = os.getenv("SHIPENGINE_API_KEY")

if not SHIPENGINE_API_KEY:
    raise EnvironmentError("SHIPENGINE_API_KEY is missing. Check your .env file.")

# Your confirmed active carriers
CARRIER_IDS = [
    "se-2904338",  # Stamps.com (USPS)
    "se-2904339",  # UPS
    "se-2904341",
    "se-2904340"   # GlobalPost
]

def compare_all_quotes(origin, destination, weight, dimensions, packaging_type):
    """
    Fetch shipping quotes from ShipEngine for multiple carriers.
    """

    # Map packaging types to valid ShipEngine codes or None for custom
    package_code_map = {
        "YOUR_PACKAGING": None,
        "package": "package",
        "tube": "tube",
        "soft_pack": "soft_pack"
    }

    url = "https://api.shipengine.com/v1/rates"
    headers = {
        "Content-Type": "application/json",
        "API-Key": SHIPENGINE_API_KEY
    }

    package_code = package_code_map.get(packaging_type, None)

    # Assemble request body
    payload = {
        "rate_options": {
            "carrier_ids": CARRIER_IDS
        },
        "shipment": {
            "validate_address": "no_validation",
            "ship_from": {
                "name": "Sender",
                "phone": "555-555-0000",
                "address_line1": origin.get("street", ""),
                "address_line2": origin.get("apt", ""),
                "city_locality": origin.get("city", ""),
                "state_province": origin.get("state", ""),
                "postal_code": origin.get("postalCode", ""),
                "country_code": "US",
                "address_residential_indicator": "yes"
            },
            "ship_to": {
                "name": "Recipient",
                "phone": "555-555-5555",
                "address_line1": destination.get("street", ""),
                "address_line2": destination.get("apt", ""),
                "city_locality": destination.get("city", ""),
                "state_province": destination.get("state", ""),
                "postal_code": destination.get("postalCode", ""),
                "country_code": "US",
                "address_residential_indicator": "yes"
            },
            "packages": [
                {
                    "package_code": package_code,
                    "weight": {
                        "value": weight,
                        "unit": "pound"
                    },
                    "dimensions": {
                        "unit": "inch",
                        "length": dimensions.get("length", 1),
                        "width": dimensions.get("width", 1),
                        "height": dimensions.get("height", 1)
                    }
                }
            ]
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.ok:
            data = response.json()
            rates = data.get("rate_response", {}).get("rates", [])
            if not rates:
                return {"error": "No shipping rates returned."}

            quotes = {}
            for rate in rates:
                carrier = rate.get("carrier_friendly_name") or rate.get("carrier_code", "Unknown Carrier")
                service = f"{carrier} - {rate.get('service_type', 'Unknown')}"
                quotes[service] = {
                    "carrier_code": rate.get("carrier_code"),
                    "service_code": rate.get("service_code"),
                    "shipping_amount": f"{rate['shipping_amount']['amount']} {rate['shipping_amount']['currency'].upper()}",
                    "delivery_days": f"{rate.get('estimated_delivery_days', 'N/A')} day(s)",
                    "rate_id": rate.get("rate_id")
                }
            print("Quotes JSON:", json.dumps(quotes, indent=2))
            return quotes
        else:
            return {"error": f"{response.status_code}: {response.text}"}
    except requests.RequestException as req_err:
        return {"error": f"Request exception: {str(req_err)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}