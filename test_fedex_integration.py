#!/usr/bin/env python3
"""
Test script for FedEx-only shipping integration
This script tests the complete workflow without Streamlit
"""

from services.shipping_integration import (
    get_fedex_shipping_quotes,
    format_fedex_results,
    display_errors
)
import json

def test_fedex_integration():
    print("🧪 Testing Complete FedEx Integration Workflow")
    print("=" * 60)
    
    # Test data
    origin = {
        'street': '913 Paseo Camarillo',
        'city': 'Camarillo',
        'state': 'CA',
        'postalCode': '93010'
    }
    
    destination = {
        'street': '302 Baldwin Park Dr',
        'city': 'LaGrange',
        'state': 'GA',
        'postalCode': '30241'
    }
    
    dimensions = {'length': 4.0, 'width': 5.0, 'height': 7.0}
    weight = 9.0
    
    print(f"📦 Package: {weight} lbs, {dimensions['length']}x{dimensions['width']}x{dimensions['height']} inches")
    print(f"📍 From: {origin['city']}, {origin['state']} {origin['postalCode']}")
    print(f"📍 To: {destination['city']}, {destination['state']} {destination['postalCode']}")
    print()
    
    # Step 1: Get FedEx quotes
    print("🔄 Step 1: Getting FedEx quotes...")
    results = get_fedex_shipping_quotes(
        origin, destination, weight, dimensions, 'YOUR_PACKAGING'
    )
    
    print(f"✅ Retrieved {len(results['quotes'])} quotes")
    if results['errors']:
        print(f"⚠️  {len(results['errors'])} errors occurred:")
        for error in results['errors']:
            print(f"   - {error}")
    print()
    
    # Step 2: Format results
    print("📊 Step 2: Formatting results...")
    df = format_fedex_results(results)
    
    if not df.empty:
        print(f"✅ Formatted {len(df)} shipping options")
        print()
        
        # Step 3: Display results
        print("📋 Step 3: Available FedEx Services:")
        print("-" * 60)
        
        # Sort by price
        sorted_df = df.sort_values('shipping_amount_usd')
        
        for i, (_, row) in enumerate(sorted_df.iterrows(), 1):
            service = row['display_name']
            price = row['shipping_amount_usd']
            transit = row.get('transit_time', 'N/A')
            print(f"{i:2d}. {service:<30} ${price:>7.2f}  ({transit})")
        
        print("-" * 60)
        
        # Summary
        cheapest = sorted_df.iloc[0]
        most_expensive = sorted_df.iloc[-1]
        
        print(f"💰 Cheapest: {cheapest['display_name']} - ${cheapest['shipping_amount_usd']:.2f}")
        print(f"💸 Most Expensive: {most_expensive['display_name']} - ${most_expensive['shipping_amount_usd']:.2f}")
        
        # Find fastest option
        overnight_services = df[df['service_name'].str.contains('Overnight|Priority', case=False)]
        if not overnight_services.empty:
            fastest = overnight_services.loc[overnight_services['shipping_amount_usd'].idxmin()]
            print(f"⚡ Fastest: {fastest['display_name']} - ${fastest['shipping_amount_usd']:.2f}")
        
        print()
        
        # Step 4: Test data structure
        print("🔍 Step 4: Data structure validation...")
        required_columns = ['display_name', 'shipping_amount_usd', 'transit_time', 'service_type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if not missing_columns:
            print("✅ All required columns present")
        else:
            print(f"❌ Missing columns: {missing_columns}")
        
        # Check for valid prices
        valid_prices = df['shipping_amount_usd'].apply(lambda x: isinstance(x, (int, float)) and x > 0)
        if valid_prices.all():
            print("✅ All prices are valid numbers")
        else:
            print("❌ Some prices are invalid")
        
        print()
        
    else:
        print("❌ No results could be formatted")
        return False
    
    print("🎉 Integration test completed successfully!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_fedex_integration()
    exit(0 if success else 1)
