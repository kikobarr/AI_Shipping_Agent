#!/usr/bin/env python3
"""
Test script to compare AI Agent tool calling vs Direct FedEx API calls
This will help identify if the AI is hallucinating or using real API data
"""

from services.langchain_agent import LangChainFedExAgent
from services.shipping_integration import get_fedex_shipping_quotes, format_fedex_results
import json

def test_ai_vs_direct_comparison():
    print("🧪 Testing AI Agent vs Direct FedEx API Comparison")
    print("=" * 70)
    
    # Test data from your example
    origin = {
        'street': '913 Paseo Camarillo',
        'city': 'Camarillo',
        'state': 'CA',
        'postalCode': '93010'
    }
    
    destination = {
        'street': '1 Harpst St',
        'city': 'Arcata',
        'state': 'CA',
        'postalCode': '95521'
    }
    
    dimensions = {'length': 4.0, 'width': 5.0, 'height': 7.0}
    weight = 9.0
    
    print(f"📦 Test Package:")
    print(f"   From: {origin['street']}, {origin['city']}, {origin['state']} {origin['postalCode']}")
    print(f"   To: {destination['street']}, {destination['city']}, {destination['state']} {destination['postalCode']}")
    print(f"   Weight: {weight} lbs")
    print(f"   Dimensions: {dimensions['length']}x{dimensions['width']}x{dimensions['height']} inches")
    print()
    
    # Test 1: Direct API call (like shipping form)
    print("🔄 Test 1: Direct FedEx API Call (Shipping Form Method)")
    print("-" * 50)
    
    try:
        direct_results = get_fedex_shipping_quotes(
            origin, destination, weight, dimensions, 'YOUR_PACKAGING'
        )
        
        direct_df = format_fedex_results(direct_results)
        
        if not direct_df.empty:
            print("✅ Direct API Results:")
            sorted_df = direct_df.sort_values('shipping_amount_usd')
            for _, row in sorted_df.iterrows():
                print(f"   {row['display_name']}: ${row['shipping_amount_usd']:.2f} ({row['transit_time']})")
        else:
            print("❌ No direct API results")
            
    except Exception as e:
        print(f"❌ Direct API Error: {e}")
    
    print()
    
    # Test 2: AI Agent tool calling
    print("🤖 Test 2: AI Agent Tool Calling")
    print("-" * 50)
    
    try:
        # Initialize AI agent
        agent = LangChainFedExAgent()
        success, message = agent.initialize_connection()
        
        if success:
            print("✅ AI Agent connected")
            
            # Create the exact query with street addresses
            query = f"Get shipping quotes for a {weight}lb package with dimensions {dimensions['length']}x{dimensions['width']}x{dimensions['height']} inches from {origin['street']}, {origin['city']}, {origin['state']} {origin['postalCode']} to {destination['street']}, {destination['city']}, {destination['state']} {destination['postalCode']}"
            
            print(f"Query: {query}")
            print()
            
            # Get AI response with debug info
            response, debug_info = agent.send_message(query)
            
            print("🤖 AI Response:")
            print(response)
            print()
            
            print("🔍 Debug Information:")
            print(f"   Tools called: {debug_info.get('tool_calls_made', False)}")
            print(f"   Number of tools used: {len(debug_info.get('tools_used', []))}")
            
            for i, tool_info in enumerate(debug_info.get('tools_used', []), 1):
                print(f"   Tool {i}: {tool_info['tool']}")
                print(f"   Input: {json.dumps(tool_info['input'], indent=6)}")
                print(f"   Output: {tool_info['output']}")
                print()
                
        else:
            print(f"❌ AI Agent connection failed: {message}")
            
    except Exception as e:
        print(f"❌ AI Agent Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 70)
    print("🔍 Analysis:")
    print("1. Compare the prices from both methods")
    print("2. Check if AI agent actually called tools (debug info)")
    print("3. Verify tool inputs match the query parameters")
    print("4. Look for any discrepancies in pricing or services")
    print("=" * 70)

if __name__ == "__main__":
    test_ai_vs_direct_comparison()
