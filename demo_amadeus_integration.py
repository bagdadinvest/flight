#!/usr/bin/env python3
"""
Amadeus Flight Search Demo Script

This script demonstrates the unified flight search functionality
that combines local database flights with live Amadeus API results.
"""

import os
import sys
import django

# Setup Django environment
sys.path.append('/home/lotfikan/apps/Flight')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
django.setup()

from flight.amadeus_service import amadeus_service
from flight.models import Place, Week, Flight
from datetime import datetime, timedelta
import json

def demo_amadeus_search():
    """Demonstrate Amadeus API search functionality"""
    print("=" * 60)
    print("AMADEUS FLIGHT SEARCH DEMONSTRATION")
    print("=" * 60)
    
    # Example search parameters
    search_params = {
        'origin_code': 'LAX',
        'destination_code': 'JFK',
        'departure_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        'adults': 1,
        'travel_class': 'ECONOMY',
        'max_results': 5
    }
    
    print(f"\nSearch Parameters:")
    print(f"From: {search_params['origin_code']}")
    print(f"To: {search_params['destination_code']}")
    print(f"Date: {search_params['departure_date']}")
    print(f"Class: {search_params['travel_class']}")
    print(f"Passengers: {search_params['adults']}")
    
    print(f"\n{'='*40}")
    print("CALLING AMADEUS API...")
    print(f"{'='*40}")
    
    try:
        # Call Amadeus service
        result = amadeus_service.search_flights(**search_params)
        
        if result.get('error'):
            print(f"❌ Error: {result.get('message')}")
            print("\nThis is expected if API credentials are not configured.")
            print("The unified search will gracefully handle this and show only local flights.")
        else:
            print(f"✅ Success! Found {len(result.get('flights', []))} flights")
            
            # Display first few results
            for i, flight in enumerate(result.get('flights', [])[:3]):
                print(f"\n--- Flight {i+1} ---")
                print(f"Airline: {flight.get('airline_name', 'Unknown')}")
                print(f"Flight: {flight.get('airline_code', '')}{flight.get('flight_number', '')}")
                print(f"Departure: {flight.get('departure_time', 'N/A')}")
                print(f"Arrival: {flight.get('arrival_time', 'N/A')}")
                print(f"Price: {flight.get('price', {}).get('currency', 'USD')} {flight.get('price', {}).get('total', 'N/A')}")
                print(f"Direct: {'Yes' if flight.get('is_direct') else 'No'}")
    
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        print("\nThis demonstrates error handling in the unified search.")

def demo_local_search():
    """Demonstrate local database search"""
    print(f"\n{'='*40}")
    print("LOCAL DATABASE SEARCH")
    print(f"{'='*40}")
    
    try:
        # Get sample places
        places = Place.objects.all()[:5]
        print(f"\nAvailable airports in database: {places.count()}")
        for place in places:
            print(f"  {place.code} - {place.city}, {place.country}")
        
        # Get sample flights
        flights = Flight.objects.all()[:3]
        print(f"\nSample flights in database: {flights.count()}")
        for flight in flights:
            print(f"  {flight.origin.code} → {flight.destination.code}")
            print(f"    Airline: {flight.airline}")
            print(f"    Economy: €{flight.economy_fare}")
            
    except Exception as e:
        print(f"❌ Database error: {str(e)}")

def demo_unified_search_flow():
    """Demonstrate the unified search workflow"""
    print(f"\n{'='*40}")
    print("UNIFIED SEARCH WORKFLOW")
    print(f"{'='*40}")
    
    print("""
1. USER SUBMITS SEARCH FORM
   - Origin: LAX (Los Angeles)
   - Destination: JFK (New York)
   - Date: Next week
   - Include Amadeus: ✓ Checked

2. UNIFIED_FLIGHT_SEARCH VIEW PROCESSES:
   ├── Validates input parameters
   ├── Searches local database for matching flights
   ├── Calls Amadeus API for live flights
   ├── Combines and normalizes results
   └── Renders search.html template

3. SEARCH TEMPLATE DISPLAYS:
   ├── Local flights (standard styling)
   ├── Amadeus flights (green "LIVE" badges)
   ├── Combined price filtering
   └── Error messages if API unavailable

4. USER INTERACTION:
   ├── Filter by price range (includes both sources)
   ├── Filter by time slots (handles both formats)
   ├── Select flights for booking
   └── Modify search parameters
""")

def main():
    """Run the demonstration"""
    print("🛩️  AMADEUS FLIGHT SEARCH INTEGRATION DEMO")
    print("   Demonstrating unified search functionality\n")
    
    demo_local_search()
    demo_amadeus_search()
    demo_unified_search_flow()
    
    print(f"\n{'='*60}")
    print("TESTING THE INTEGRATION")
    print(f"{'='*60}")
    print("""
To test the unified search:

1. Open your browser to: http://127.0.0.1:8000/
2. Fill in the search form:
   - From: Any airport code (e.g., LAX, JFK, LHR)
   - To: Any destination
   - Date: Future date
   - Check "Include Live Flight Results"
3. Submit the search
4. View results showing both local and live flights
5. Test filtering and sorting features

The search template (flight/search.html) will display:
✅ Local database flights with standard styling
✅ Amadeus API flights with green "LIVE" badges
✅ Combined price and time filtering
✅ Error handling if API is unavailable
""")
    
    print(f"\n{'='*60}")
    print("INTEGRATION COMPLETE!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
