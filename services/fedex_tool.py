"""
LangChain Tool for FedEx API Integration
Allows the AI agent to call FedEx API directly for shipping quotes
"""

from langchain.tools import BaseTool
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import json

from .fedexAPI import get_fedex_freight_rate


class FedExShippingInput(BaseModel):
    """Input schema for FedEx shipping tool"""
    origin_street: str = Field(description="Origin street address (e.g., '913 Paseo Camarillo')")
    origin_city: str = Field(description="Origin city name")
    origin_state: str = Field(description="Origin state code (e.g., 'CA', 'NY')")
    origin_postal_code: str = Field(description="Origin postal/zip code")
    destination_street: str = Field(description="Destination street address (e.g., '1 Harpst St')")
    destination_city: str = Field(description="Destination city name")
    destination_state: str = Field(description="Destination state code (e.g., 'GA', 'FL')")
    destination_postal_code: str = Field(description="Destination postal/zip code")
    weight: float = Field(description="Package weight in pounds")
    length: float = Field(description="Package length in inches", default=12.0)
    width: float = Field(description="Package width in inches", default=12.0)
    height: float = Field(description="Package height in inches", default=12.0)
    service_type: str = Field(description="FedEx service type", default="FEDEX_GROUND")


class FedExShippingTool(BaseTool):
    """LangChain tool for getting FedEx shipping quotes"""
    
    name: str = "get_fedex_shipping_quote"
    description: str = """
    Get real-time shipping quotes from FedEx API. Use this tool when users ask for shipping rates, 
    costs, or quotes. You need COMPLETE addresses including street addresses, city, state, and postal code 
    for both origin and destination, plus package details (weight, dimensions). Available service types:
    - FEDEX_GROUND: Most economical ground service (4 business days)
    - FEDEX_EXPRESS_SAVER: Express service (3 business days)
    - FEDEX_2_DAY: Fast service (2 business days)
    
    IMPORTANT: Always ask for complete street addresses, not just city/state/zip!
    """
    args_schema: type[BaseModel] = FedExShippingInput
    
    def _run(
        self,
        origin_street: str,
        origin_city: str,
        origin_state: str,
        origin_postal_code: str,
        destination_street: str,
        destination_city: str,
        destination_state: str,
        destination_postal_code: str,
        weight: float,
        length: float = 12.0,
        width: float = 12.0,
        height: float = 12.0,
        service_type: str = "FEDEX_GROUND"
    ) -> str:
        """Execute the FedEx API call"""
        
        try:
            # Prepare the API call parameters with street addresses
            origin = {
                'street': origin_street,
                'city': origin_city,
                'state': origin_state,
                'postal_code': origin_postal_code  # Fixed: use postal_code not postalCode
            }
            
            destination = {
                'street': destination_street,
                'city': destination_city,
                'state': destination_state,
                'postal_code': destination_postal_code  # Fixed: use postal_code not postalCode
            }
            
            shipment = {
                'weight': weight,
                'dimensions': {
                    'length': length,
                    'width': width,
                    'height': height
                },
                'service_type': service_type
            }
            
            # Call the FedEx API
            result = get_fedex_freight_rate(origin, destination, shipment)
            
            if result['success']:
                # Extract and format the response
                if 'output' in result['data'] and 'rateReplyDetails' in result['data']['output']:
                    rates = result['data']['output']['rateReplyDetails']
                    
                    formatted_results = []
                    for rate in rates:
                        if 'ratedShipmentDetails' in rate and rate['ratedShipmentDetails']:
                            rate_detail = rate['ratedShipmentDetails'][0]
                            total_charge = rate_detail.get('totalNetCharge', 0)
                            currency = rate_detail.get('currency', 'USD')
                            
                            # Get transit time
                            transit_time = 'N/A'
                            if 'operationalDetail' in rate:
                                transit_time = rate['operationalDetail'].get('transitTime', 'N/A')
                            
                            # Get service name
                            service_name = rate.get('serviceName', service_type)
                            
                            formatted_results.append({
                                'service': service_name,
                                'cost': f"${total_charge} {currency}",
                                'transit_time': transit_time,
                                'service_type': service_type
                            })
                    
                    if formatted_results:
                        # Format the response for the AI
                        response = f"FedEx Shipping Quote Results:\n"
                        response += f"From: {origin_street}, {origin_city}, {origin_state} {origin_postal_code}\n"
                        response += f"To: {destination_street}, {destination_city}, {destination_state} {destination_postal_code}\n"
                        response += f"Package: {weight} lbs, {length}x{width}x{height} inches\n\n"
                        
                        for result in formatted_results:
                            response += f"• {result['service']}: {result['cost']}"
                            if result['transit_time'] != 'N/A':
                                response += f" (Transit: {result['transit_time']})"
                            response += "\n"
                        
                        return response
                    else:
                        return f"No rates found for {service_type} service from {origin_street}, {origin_city}, {origin_state} to {destination_street}, {destination_city}, {destination_state}"
                else:
                    return f"No rate details returned from FedEx API for the requested shipment."
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                return f"FedEx API Error: {error_msg}. Please check the addresses and package details."
                
        except Exception as e:
            return f"Error calling FedEx API: {str(e)}. Please verify all shipping details are correct."
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version - just call the sync version"""
        return self._run(*args, **kwargs)


class FedExMultiServiceTool(BaseTool):
    """LangChain tool for getting multiple FedEx service quotes at once"""
    
    name: str = "get_fedex_all_services"
    description: str = """
    Get shipping quotes for ALL available FedEx services at once. Use this when users want to 
    compare different shipping options or see all available services. Requires COMPLETE addresses 
    including street addresses, city, state, and postal code for both origin and destination, 
    plus package details (weight, dimensions). Returns quotes for Ground, Express Saver, and 2Day services.
    
    IMPORTANT: Always ask for complete street addresses, not just city/state/zip!
    """
    args_schema: type[BaseModel] = FedExShippingInput
    
    def _run(
        self,
        origin_street: str,
        origin_city: str,
        origin_state: str,
        origin_postal_code: str,
        destination_street: str,
        destination_city: str,
        destination_state: str,
        destination_postal_code: str,
        weight: float,
        length: float = 12.0,
        width: float = 12.0,
        height: float = 12.0,
        service_type: str = "FEDEX_GROUND"  # This parameter is ignored for multi-service
    ) -> str:
        """Get quotes for all FedEx services"""
        
        # List of reliable FedEx services (removed problematic overnight services)
        services = [
            ('FEDEX_GROUND', '🚚 FedEx Ground'),
            ('FEDEX_EXPRESS_SAVER', '⚡ FedEx Express Saver'),
            ('FEDEX_2_DAY', '📦 FedEx 2Day')
        ]
        
        origin = {
            'street': origin_street,
            'city': origin_city,
            'state': origin_state,
            'postal_code': origin_postal_code  # Fixed: use postal_code not postalCode
        }
        
        destination = {
            'street': destination_street,
            'city': destination_city,
            'state': destination_state,
            'postal_code': destination_postal_code  # Fixed: use postal_code not postalCode
        }
        
        all_results = []
        errors = []
        
        for service_code, service_name in services:
            try:
                shipment = {
                    'weight': weight,
                    'dimensions': {
                        'length': length,
                        'width': width,
                        'height': height
                    },
                    'service_type': service_code
                }
                
                result = get_fedex_freight_rate(origin, destination, shipment)
                
                if result['success']:
                    if 'output' in result['data'] and 'rateReplyDetails' in result['data']['output']:
                        rates = result['data']['output']['rateReplyDetails']
                        
                        for rate in rates:
                            if 'ratedShipmentDetails' in rate and rate['ratedShipmentDetails']:
                                rate_detail = rate['ratedShipmentDetails'][0]
                                total_charge = rate_detail.get('totalNetCharge', 0)
                                currency = rate_detail.get('currency', 'USD')
                                
                                # Get transit time
                                transit_time = 'N/A'
                                if 'operationalDetail' in rate:
                                    api_transit = rate['operationalDetail'].get('transitTime', 'N/A')
                                    if api_transit == 'FOUR_DAYS':
                                        transit_time = '4 business days'
                                    else:
                                        transit_time = api_transit
                                
                                # Use fallback transit times if API doesn't provide them
                                if transit_time == 'N/A':
                                    transit_map = {
                                        'FEDEX_GROUND': '4 business days',
                                        'FEDEX_EXPRESS_SAVER': '3 business days',
                                        'FEDEX_2_DAY': '2 business days'
                                    }
                                    transit_time = transit_map.get(service_code, 'N/A')
                                
                                all_results.append({
                                    'service': service_name,
                                    'cost': total_charge,
                                    'currency': currency,
                                    'transit_time': transit_time,
                                    'service_code': service_code
                                })
                                break  # Only take the first rate for each service
                else:
                    errors.append(f"{service_name}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                errors.append(f"{service_name}: {str(e)}")
        
        # Format the response
        if all_results:
            # Sort by cost
            all_results.sort(key=lambda x: x['cost'])
            
            response = f"FedEx Shipping Quote Comparison:\n"
            response += f"From: {origin_street}, {origin_city}, {origin_state} {origin_postal_code}\n"
            response += f"To: {destination_street}, {destination_city}, {destination_state} {destination_postal_code}\n"
            response += f"Package: {weight} lbs, {length}x{width}x{height} inches\n\n"
            response += "Available Services (sorted by price):\n"
            
            for i, result in enumerate(all_results, 1):
                response += f"{i}. {result['service']}: ${result['cost']:.2f} {result['currency']}"
                if result['transit_time'] != 'N/A':
                    response += f" ({result['transit_time']})"
                response += "\n"
            
            # Add summary
            cheapest = all_results[0]
            most_expensive = all_results[-1]
            response += f"\n💰 Cheapest: {cheapest['service']} - ${cheapest['cost']:.2f}"
            response += f"\n💸 Most Expensive: {most_expensive['service']} - ${most_expensive['cost']:.2f}"
            
            # Find fastest overnight service
            overnight_services = [r for r in all_results if 'Overnight' in r['service']]
            if overnight_services:
                fastest = min(overnight_services, key=lambda x: x['cost'])
                response += f"\n⚡ Fastest: {fastest['service']} - ${fastest['cost']:.2f}"
            
            if errors:
                response += f"\n\n⚠️ Some services unavailable: {', '.join(errors)}"
            
            return response
        else:
            return f"Unable to get FedEx quotes. Errors: {', '.join(errors) if errors else 'No rates returned'}"
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async version - just call the sync version"""
        return self._run(*args, **kwargs)


# Create tool instances
fedex_single_tool = FedExShippingTool()
fedex_multi_tool = FedExMultiServiceTool()
