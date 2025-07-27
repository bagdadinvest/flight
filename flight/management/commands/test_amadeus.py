"""
Django management command to test Amadeus API integration
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from flight.amadeus_service import amadeus_service
from flight.models import Place
import json


class Command(BaseCommand):
    help = 'Test Amadeus API integration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-search',
            action='store_true',
            help='Test flight search functionality',
        )
        parser.add_argument(
            '--test-airports',
            action='store_true', 
            help='Test airport search functionality',
        )
        parser.add_argument(
            '--origin',
            type=str,
            default='NYC',
            help='Origin airport code for flight search test',
        )
        parser.add_argument(
            '--destination',
            type=str,
            default='LAX',
            help='Destination airport code for flight search test',
        )
        parser.add_argument(
            '--date',
            type=str,
            default='2025-08-15',
            help='Departure date for flight search test (YYYY-MM-DD)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Testing Amadeus API Integration...\n')
        )
        
        # Check configuration
        self.check_config()
        
        if options['test_airports']:
            self.test_airport_search()
        
        if options['test_search']:
            self.test_flight_search(
                options['origin'],
                options['destination'],
                options['date']
            )

    def check_config(self):
        """Check Amadeus configuration"""
        self.stdout.write('Checking Amadeus configuration...')
        
        client_id = settings.AMADEUS_CLIENT_ID
        client_secret = settings.AMADEUS_CLIENT_SECRET
        hostname = settings.AMADEUS_HOSTNAME
        
        if client_id == 'your_client_id_here':
            self.stdout.write(
                self.style.WARNING(
                    'Warning: Using default client ID. Please set AMADEUS_CLIENT_ID environment variable.'
                )
            )
        
        if client_secret == 'your_client_secret_here':
            self.stdout.write(
                self.style.WARNING(
                    'Warning: Using default client secret. Please set AMADEUS_CLIENT_SECRET environment variable.'
                )
            )
        
        self.stdout.write(f'Hostname: {hostname}')
        self.stdout.write('')

    def test_airport_search(self):
        """Test airport search functionality"""
        self.stdout.write('Testing airport search...')
        
        test_queries = ['New York', 'London', 'Paris', 'Tokyo']
        
        for query in test_queries:
            self.stdout.write(f'Searching for: {query}')
            
            try:
                results = amadeus_service.get_airport_suggestions(query)
                
                if results:
                    self.stdout.write(
                        self.style.SUCCESS(f'Found {len(results)} airports:')
                    )
                    for airport in results[:3]:  # Show first 3 results
                        self.stdout.write(
                            f"  - {airport.get('code', 'N/A')} - {airport.get('name', 'N/A')} ({airport.get('city', 'N/A')}, {airport.get('country', 'N/A')})"
                        )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'No results found for: {query}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error searching for {query}: {e}')
                )
            
            self.stdout.write('')

    def test_flight_search(self, origin, destination, date):
        """Test flight search functionality"""
        self.stdout.write(f'Testing flight search: {origin} → {destination} on {date}')
        
        try:
            # Search flights
            results = amadeus_service.search_flights(
                origin_code=origin,
                destination_code=destination,
                departure_date=date,
                adults=1,
                travel_class='ECONOMY',
                max_results=5
            )
            
            if results.get('error'):
                self.stdout.write(
                    self.style.ERROR(f'Search failed: {results.get("message")}')
                )
                return
            
            flights = results.get('flights', [])
            
            if flights:
                self.stdout.write(
                    self.style.SUCCESS(f'Found {len(flights)} flights:')
                )
                
                for i, flight in enumerate(flights[:3], 1):  # Show first 3 flights
                    self.stdout.write(f'\nFlight {i}:')
                    self.stdout.write(f'  Airline: {flight.get("airline_name", "N/A")} ({flight.get("airline_code", "N/A")})')
                    self.stdout.write(f'  Flight: {flight.get("flight_number", "N/A")}')
                    self.stdout.write(f'  Departure: {flight.get("departure_time", "N/A")}')
                    self.stdout.write(f'  Arrival: {flight.get("arrival_time", "N/A")}')
                    self.stdout.write(f'  Duration: {flight.get("duration", "N/A")}')
                    self.stdout.write(f'  Price: {flight.get("price", {}).get("currency", "USD")} {flight.get("price", {}).get("total", "N/A")}')
                    self.stdout.write(f'  Aircraft: {flight.get("aircraft", "N/A")}')
                    self.stdout.write(f'  Stops: {flight.get("stops", 0)}')
                    
            else:
                self.stdout.write(
                    self.style.WARNING('No flights found for this route and date')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during flight search: {e}')
            )

    def test_price_analysis(self, origin, destination, date):
        """Test price analysis functionality"""
        self.stdout.write(f'Testing price analysis: {origin} → {destination} on {date}')
        
        try:
            analysis = amadeus_service.get_flight_price_analysis(
                origin_code=origin,
                destination_code=destination,
                departure_date=date
            )
            
            if analysis.get('error'):
                self.stdout.write(
                    self.style.WARNING(f'Price analysis failed: {analysis.get("message")}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('Price analysis successful:')
                )
                self.stdout.write(f'Currency: {analysis.get("currency", "N/A")}')
                
                metrics = analysis.get('price_metrics', [])
                if metrics:
                    self.stdout.write(f'Price metrics available: {len(metrics)} data points')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during price analysis: {e}')
            )
