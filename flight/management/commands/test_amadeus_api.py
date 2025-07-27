"""
Django management command to test Amadeus API integration
Run with: python manage.py test_amadeus_api
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from flight.amadeus_service import AmadeusService
import logging

# Set up logging for test output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Command(BaseCommand):
    help = 'Test Amadeus API integration with debugging'

    def add_arguments(self, parser):
        parser.add_argument(
            '--origin',
            type=str,
            default='LAX',
            help='Origin airport code (default: LAX)'
        )
        parser.add_argument(
            '--destination', 
            type=str,
            default='JFK',
            help='Destination airport code (default: JFK)'
        )
        parser.add_argument(
            '--date',
            type=str,
            default='2025-08-01',
            help='Departure date in YYYY-MM-DD format (default: 2025-08-01)'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting Amadeus API Test...')
        )
        
        # Check configuration
        self.stdout.write("\n=== CONFIGURATION CHECK ===")
        self.stdout.write(f"AMADEUS_CLIENT_ID: {'Set' if settings.AMADEUS_CLIENT_ID and settings.AMADEUS_CLIENT_ID != 'your_client_id_here' else 'NOT SET'}")
        self.stdout.write(f"AMADEUS_CLIENT_SECRET: {'Set' if settings.AMADEUS_CLIENT_SECRET and settings.AMADEUS_CLIENT_SECRET != 'your_client_secret_here' else 'NOT SET'}")
        self.stdout.write(f"AMADEUS_HOSTNAME: {settings.AMADEUS_HOSTNAME}")
        
        if not (settings.AMADEUS_CLIENT_ID and settings.AMADEUS_CLIENT_SECRET):
            self.stdout.write(
                self.style.ERROR(
                    'ERROR: Amadeus credentials not properly configured in environment variables!'
                )
            )
            return
        
        # Test API connection
        self.stdout.write("\n=== API CONNECTION TEST ===")
        try:
            service = AmadeusService()
            self.stdout.write(self.style.SUCCESS('✓ AmadeusService initialized successfully'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to initialize AmadeusService: {e}')
            )
            return
        
        # Test flight search
        self.stdout.write("\n=== FLIGHT SEARCH TEST ===")
        origin = options['origin']
        destination = options['destination']
        date = options['date']
        
        self.stdout.write(f"Testing flight search: {origin} → {destination} on {date}")
        
        try:
            results = service.search_flights(
                origin_code=origin,
                destination_code=destination,
                departure_date=date,
                adults=1,
                travel_class='ECONOMY',
                max_results=5
            )
            
            if results.get('error'):
                self.stdout.write(
                    self.style.ERROR(f"✗ Flight search failed: {results.get('message')}")
                )
                if 'api_error' in results:
                    self.stdout.write(f"API Error Details: {results['api_error']}")
            else:
                flights = results.get('flights', [])
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Flight search successful! Found {len(flights)} flights")
                )
                
                # Display first flight details
                if flights:
                    first_flight = flights[0]
                    self.stdout.write("\n=== SAMPLE FLIGHT DETAILS ===")
                    self.stdout.write(f"Airline: {first_flight.get('airline', 'N/A')}")
                    self.stdout.write(f"Flight Number: {first_flight.get('flight_number', 'N/A')}")
                    self.stdout.write(f"Price: {first_flight.get('price', {}).get('currency', 'N/A')} {first_flight.get('price', {}).get('total', 'N/A')}")
                    self.stdout.write(f"Duration: {first_flight.get('duration', 'N/A')}")
                    self.stdout.write(f"Stops: {first_flight.get('stops', 'N/A')}")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Unexpected error during flight search: {e}")
            )
        
        # Test airport suggestions
        self.stdout.write("\n=== AIRPORT SUGGESTIONS TEST ===")
        try:
            suggestions = service.get_airport_suggestions('new york')
            if suggestions:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Airport suggestions successful! Found {len(suggestions)} airports")
                )
                for suggestion in suggestions[:3]:  # Show first 3
                    self.stdout.write(f"  - {suggestion.get('name', 'N/A')} ({suggestion.get('iata_code', 'N/A')})")
            else:
                self.stdout.write(self.style.WARNING("⚠ No airport suggestions returned"))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Airport suggestions test failed: {e}")
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n=== TEST COMPLETED ===')
        )
