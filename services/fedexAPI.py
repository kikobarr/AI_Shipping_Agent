import json
import requests
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FedEx API Configuration
FEDEX_SANDBOX_BASE_URL = "https://apis-sandbox.fedex.com"
FEDEX_AUTH_URL = f"{FEDEX_SANDBOX_BASE_URL}/oauth/token"
FEDEX_RATES_URL = f"{FEDEX_SANDBOX_BASE_URL}/rate/v1/rates/quotes"

def get_fedex_access_token() -> Optional[str]:
    """
    Get FedEx API access token using client credentials from .env file.
    
    Returns:
        Access token string or None if authentication fails
    """
    client_id = os.getenv('FEDEX_CLIENT_ID')
    client_secret = os.getenv('FEDEX_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("Error: FedEx credentials not found in .env file")
        return None
    
    auth_payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.post(FEDEX_AUTH_URL, data=auth_payload, headers=headers)
        response.raise_for_status()
        
        auth_data = response.json()
        return auth_data.get('access_token')
        
    except requests.exceptions.RequestException as e:
        print(f"Error getting FedEx access token: {e}")
        return None

def get_fedex_freight_rate(
    origin: Dict[str, str],
    destination: Dict[str, str], 
    shipment: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get FedEx freight rate quotes by calling the FedEx API sandbox directly.
    
    This function is designed to be used by AI agents with the OpenAI function schema.
    
    Args:
        origin: Origin address with keys: city, state, postal_code, country (optional)
        destination: Destination address with keys: city, state, postal_code, country (optional)
        shipment: Shipment details with keys: weight, dimensions, service_type (optional), 
                 pickup_type (optional), ship_date (optional)
        options: Additional options with keys: rate_request_type, currency, include_transit_times
    
    Returns:
        Dict containing the FedEx rate quote response
        
    Example:
        result = get_fedex_freight_rate(
            origin={
                "city": "Memphis",
                "state": "TN", 
                "postal_code": "38118"
            },
            destination={
                "city": "Dallas",
                "state": "TX",
                "postal_code": "75063"
            },
            shipment={
                "weight": 500,
                "dimensions": {
                    "length": 48,
                    "width": 40,
                    "height": 36
                },
                "service_type": "FEDEX_GROUND"
            }
        )
    """
    
    # Set defaults
    if options is None:
        options = {}
    
    # Default values
    origin.setdefault('country', 'US')
    destination.setdefault('country', 'US')
    shipment.setdefault('service_type', 'FEDEX_GROUND')
    shipment.setdefault('pickup_type', 'DROPOFF_AT_FEDEX_LOCATION')
    
    if 'ship_date' not in shipment:
        # Default to tomorrow
        shipment['ship_date'] = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    options.setdefault('rate_request_type', ['ACCOUNT'])
    options.setdefault('currency', 'USD')
    options.setdefault('include_transit_times', True)
    
    # Validate required fields
    required_origin_fields = ['city', 'state', 'postal_code']
    required_destination_fields = ['city', 'state', 'postal_code'] 
    required_shipment_fields = ['weight', 'dimensions']
    
    for field in required_origin_fields:
        if field not in origin:
            return {
                'success': False,
                'error': f'Missing required origin field: {field}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    for field in required_destination_fields:
        if field not in destination:
            return {
                'success': False,
                'error': f'Missing required destination field: {field}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    for field in required_shipment_fields:
        if field not in shipment:
            return {
                'success': False,
                'error': f'Missing required shipment field: {field}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    # Validate dimensions
    if 'dimensions' in shipment:
        required_dim_fields = ['length', 'width', 'height']
        for field in required_dim_fields:
            if field not in shipment['dimensions']:
                return {
                    'success': False,
                    'error': f'Missing required dimension field: {field}',
                    'timestamp': datetime.utcnow().isoformat()
                }
    
    # Get access token
    access_token = get_fedex_access_token()
    if not access_token:
        return {
            'success': False,
            'error': 'Failed to authenticate with FedEx API',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # For sandbox testing, use FedEx provided test account numbers
    # The account number from .env might be for production
    sandbox_account = "740561073"  # FedEx sandbox test account
    account_number = sandbox_account  # Use sandbox account for testing
    
    # Prepare the FedEx API payload
    fedex_payload = {
        "accountNumber": {
            "value": account_number
        },
        "rateRequestControlParameters": {
            "returnTransitTimes": options.get('include_transit_times', True),
            "servicesNeededOnRateFailure": True,
            "rateSortOrder": "SERVICENAMETRADITIONAL"
        },
        "requestedShipment": {
            "shipper": {
                "address": {
                    "streetLines": ["1234 Test Street"],
                    "city": origin.get('city', 'Memphis'),
                    "stateOrProvinceCode": origin.get('state', 'TN'),
                    "postalCode": origin['postal_code'],
                    "countryCode": origin.get('country', 'US'),
                    "residential": False
                }
            },
            "recipient": {
                "address": {
                    "streetLines": ["5678 Test Avenue"],
                    "city": destination.get('city', 'Dallas'),
                    "stateOrProvinceCode": destination.get('state', 'TX'),
                    "postalCode": destination['postal_code'],
                    "countryCode": destination.get('country', 'US'),
                    "residential": False
                }
            },
            "shipDateStamp": shipment['ship_date'],
            "rateRequestType": ["ACCOUNT", "LIST"],
            "serviceType": shipment.get('service_type', 'FEDEX_GROUND'),
            "packagingType": "YOUR_PACKAGING",
            "pickupType": shipment.get('pickup_type', 'DROPOFF_AT_FEDEX_LOCATION'),
            "requestedPackageLineItems": [
                {
                    "groupPackageCount": 1,
                    "weight": {
                        "units": "LB",
                        "value": shipment['weight']
                    },
                    "dimensions": {
                        "length": shipment['dimensions']['length'],
                        "width": shipment['dimensions']['width'],
                        "height": shipment['dimensions']['height'],
                        "units": "IN"
                    }
                }
            ]
        }
    }
    
    # Set up headers
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-locale': 'en_US'
    }
    
    try:
        # Make the API call
        response = requests.post(FEDEX_RATES_URL, json=fedex_payload, headers=headers)
        
        # Handle response
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'data': result,
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            error_data = response.json() if response.content else {}
            return {
                'success': False,
                'error': f'FedEx API error: {response.status_code}',
                'error_details': error_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'Failed to call FedEx API: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'timestamp': datetime.utcnow().isoformat()
        }

# Example usage for testing
if __name__ == "__main__":
    # Test the wrapper function
    test_result = get_fedex_freight_rate(
        origin={
            "city": "Memphis",
            "state": "TN",
            "postal_code": "38118"
        },
        destination={
            "city": "Dallas", 
            "state": "TX",
            "postal_code": "75063"
        },
        shipment={
            "weight": 500,
            "dimensions": {
                "length": 48,
                "width": 40,
                "height": 36
            },
            "service_type": "FEDEX_GROUND"
        }
    )
    
    print("Test Result:")
    print(json.dumps(test_result, indent=2))
