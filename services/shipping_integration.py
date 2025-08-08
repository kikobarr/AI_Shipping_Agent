"""
FedEx-Only Shipping Integration Service
Provides FedEx shipping quotes using the direct FedEx API
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd

from .fedexAPI import get_fedex_freight_rate


def get_fedex_shipping_quotes(
    origin: Dict[str, str],
    destination: Dict[str, str],
    weight: float,
    dimensions: Dict[str, float],
    packaging_type: str = "YOUR_PACKAGING"
) -> Dict[str, Any]:
    """
    Get FedEx shipping quotes using the direct FedEx API
    
    Args:
        origin: Origin address with keys: street, city, state, postalCode
        destination: Destination address with keys: street, city, state, postalCode
        weight: Package weight in pounds
        dimensions: Package dimensions with keys: length, width, height (in inches)
        packaging_type: Type of packaging
    
    Returns:
        Dictionary containing FedEx quotes and metadata
    """
    
    results = {
        'quotes': {},
        'fedex_response': None,
        'errors': [],
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Get FedEx quotes directly from FedEx API
    try:
        fedex_origin = {
            'city': origin.get('city', ''),
            'state': origin.get('state', ''),
            'postal_code': origin.get('postalCode', '')
        }
        
        fedex_destination = {
            'city': destination.get('city', ''),
            'state': destination.get('state', ''),
            'postal_code': destination.get('postalCode', '')
        }
        
        fedex_shipment = {
            'weight': weight,
            'dimensions': {
                'length': dimensions.get('length', 12),
                'width': dimensions.get('width', 12),
                'height': dimensions.get('height', 12)
            },
            'service_type': 'FEDEX_GROUND'
        }
        
        # Try different FedEx services
        # Use the same reliable FedEx services as the AI agent tools
        fedex_services = [
            ('FEDEX_GROUND', '🚚 FedEx Ground'),
            ('FEDEX_EXPRESS_SAVER', '⚡ FedEx Express Saver'),
            ('FEDEX_2_DAY', '📦 FedEx 2Day')
        ]
        
        for service_code, service_name in fedex_services:
            try:
                fedex_shipment['service_type'] = service_code
                fedex_result = get_fedex_freight_rate(
                    fedex_origin, fedex_destination, fedex_shipment
                )
                
                if fedex_result['success']:
                    # Extract rate information
                    if 'output' in fedex_result['data'] and 'rateReplyDetails' in fedex_result['data']['output']:
                        rates = fedex_result['data']['output']['rateReplyDetails']
                        
                        for rate in rates:
                            if 'ratedShipmentDetails' in rate and rate['ratedShipmentDetails']:
                                rate_detail = rate['ratedShipmentDetails'][0]
                                total_charge = rate_detail.get('totalNetCharge', 0)
                                currency = rate_detail.get('currency', 'USD')
                                
                                # Get transit time - use API response or fallback to service mapping
                                transit_time = 'N/A'
                                if 'operationalDetail' in rate:
                                    api_transit = rate['operationalDetail'].get('transitTime', 'N/A')
                                    # Convert API response to readable format
                                    if api_transit == 'FOUR_DAYS':
                                        transit_time = '4 business days'
                                    else:
                                        transit_time = api_transit
                                
                                # If API doesn't provide transit time, use service-specific mapping
                                if transit_time == 'N/A':
                                    transit_time_map = {
                                        'FEDEX_GROUND': '4 business days',
                                        'FEDEX_EXPRESS_SAVER': '3 business days',
                                        'FEDEX_2_DAY': '2 business days'
                                    }
                                    transit_time = transit_time_map.get(service_code, 'N/A')
                                
                                # Add to results
                                results['quotes'][service_name] = {
                                    'shipping_amount': f"{total_charge} {currency}",
                                    'carrier_code': 'fedex',
                                    'service_type': service_code,
                                    'transit_time': transit_time,
                                    'source': 'fedex_api_direct'
                                }
                                
                                # Store the first successful result as primary
                                if results['fedex_response'] is None:
                                    results['fedex_response'] = fedex_result
                                    
                else:
                    results['errors'].append(f"FedEx API error for {service_name}: {fedex_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                results['errors'].append(f"Error getting FedEx {service_name}: {str(e)}")
                
    except Exception as e:
        results['errors'].append(f"Error calling FedEx API: {str(e)}")
    
    return results


def format_fedex_results(results: Dict[str, Any]) -> pd.DataFrame:
    """
    Format FedEx results into a pandas DataFrame for display
    
    Args:
        results: Results from get_fedex_shipping_quotes
        
    Returns:
        Formatted DataFrame with FedEx shipping options
    """
    
    if not results['quotes']:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(results['quotes'], orient='index').reset_index()
    df = df.rename(columns={"index": "service_name"})
    
    # Extract numeric shipping amount
    def extract_price(price_str):
        try:
            # Remove currency symbols and extract numeric value
            import re
            price_match = re.search(r'[\d.]+', str(price_str))
            return float(price_match.group()) if price_match else 0.0
        except:
            return 0.0
    
    df["shipping_amount_usd"] = df["shipping_amount"].apply(extract_price)
    
    # Use service name as display name (already formatted with emojis)
    df["display_name"] = df["service_name"]
    
    # Add FedEx indicator
    df["is_fedex_api"] = True
    
    return df


def display_fedex_summary(df: pd.DataFrame):
    """
    Display FedEx shipping summary with metrics and tables
    
    Args:
        df: Formatted DataFrame with FedEx shipping options
    """
    
    if df.empty:
        st.warning("No FedEx shipping quotes available")
        return
    
    # Display all FedEx options
    st.markdown("### 🔴 Live FedEx API Results")
    
    # Create a display dataframe - sort first, then select columns
    sorted_df = df.sort_values("shipping_amount_usd")
    display_df = sorted_df[["display_name", "shipping_amount", "transit_time"]].copy()
    display_df = display_df.rename(columns={
        "display_name": "Service",
        "shipping_amount": "Price",
        "transit_time": "Transit Time"
    })
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


def display_errors(errors: List[str]):
    """
    Display any errors that occurred during quote retrieval
    
    Args:
        errors: List of error messages
    """
    
    if errors:
        with st.expander("⚠️ Errors and Warnings", expanded=False):
            for error in errors:
                st.warning(error)
