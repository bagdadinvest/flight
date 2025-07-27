"""
Amadeus API Integration Service

This module provides integration with the Amadeus Travel API for real-time flight data.
It serves as a bridge between the Django Flight app and Amadeus API services.
"""

from amadeus import Client, ResponseError
from django.conf import settings
from django.core.cache import cache
from datetime import datetime, timedelta
import logging
import json

# Configure logging for detailed debugging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler if it doesn't exist
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class AmadeusService:
    """
    Service class for interacting with Amadeus API
    Provides methods for flight search, airport lookup, and booking operations
    """
    
    def __init__(self):
        """Initialize Amadeus client with credentials from settings"""
        logger.debug("Initializing AmadeusService")
        logger.debug(f"Client ID: {settings.AMADEUS_CLIENT_ID[:10]}..." if settings.AMADEUS_CLIENT_ID else "No Client ID")
        logger.debug(f"Hostname: {settings.AMADEUS_HOSTNAME}")
        
        try:
            self.client = Client(
                client_id=settings.AMADEUS_CLIENT_ID,
                client_secret=settings.AMADEUS_CLIENT_SECRET,
                hostname=settings.AMADEUS_HOSTNAME
            )
            logger.info("Amadeus client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Amadeus client: {str(e)}")
            raise
    
    def search_flights(self, origin_code, destination_code, departure_date, 
                      return_date=None, adults=1, travel_class='ECONOMY', 
                      max_results=20):
        """
        Search for flights using Amadeus Flight Offers Search API
        
        Args:
            origin_code (str): IATA airport code for departure
            destination_code (str): IATA airport code for arrival
            departure_date (str): Departure date in YYYY-MM-DD format
            return_date (str, optional): Return date for round trip
            adults (int): Number of adult passengers
            travel_class (str): Travel class (ECONOMY, BUSINESS, FIRST)
            max_results (int): Maximum number of results to return
            
        Returns:
            dict: Flight search results or error message
        """
        logger.info("=== AMADEUS FLIGHT SEARCH DEBUG ===")
        logger.info(f"Input parameters:")
        logger.info(f"  Origin: {origin_code}")
        logger.info(f"  Destination: {destination_code}")
        logger.info(f"  Departure Date: {departure_date}")
        logger.info(f"  Return Date: {return_date}")
        logger.info(f"  Adults: {adults}")
        logger.info(f"  Travel Class: {travel_class}")
        logger.info(f"  Max Results: {max_results}")
        
        try:
            # Prepare search parameters
            search_params = {
                'originLocationCode': origin_code,
                'destinationLocationCode': destination_code,
                'departureDate': departure_date,
                'adults': adults,
                'travelClass': travel_class,
                'max': max_results
            }
            
            # Add return date for round trip
            if return_date:
                search_params['returnDate'] = return_date
            
            logger.info(f"API Request Parameters: {json.dumps(search_params, indent=2)}")
            
            # Call Amadeus API
            logger.info("Making API call to Amadeus...")
            response = self.client.shopping.flight_offers_search.get(**search_params)
            
            logger.info(f"API Response Status: {response.status_code}")
            
            # Note: Amadeus SDK response headers access varies by version
            try:
                if hasattr(response, 'response') and hasattr(response.response, 'headers'):
                    logger.info(f"API Response Headers: {dict(response.response.headers)}")
                elif hasattr(response, 'headers'):
                    logger.info(f"API Response Headers: {dict(response.headers)}")
                else:
                    logger.info("API Response Headers: Not accessible in this SDK version")
            except Exception as e:
                logger.debug(f"Could not access response headers: {e}")
            
            # Log raw response data (first 1000 chars for brevity)
            raw_data = str(response.data)
            if len(raw_data) > 1000:
                logger.info(f"API Response Data (truncated): {raw_data[:1000]}...")
            else:
                logger.info(f"API Response Data: {raw_data}")
            
            logger.info(f"Number of flight offers returned: {len(response.data) if response.data else 0}")
            
            # Process and normalize the response
            normalized_results = self._normalize_flight_results(response.data)
            logger.info(f"Normalized results: {len(normalized_results.get('flights', []))} flights")
            
            return normalized_results
            
        except ResponseError as error:
            logger.error(f"=== AMADEUS API ERROR ===")
            logger.error(f"Error Code: {error.response.status_code}")
            logger.error(f"Error Body: {error.response.body}")
            logger.error(f"Error Description: {error.description}")
            
            return {
                'error': True,
                'message': f"Flight search failed: {error.description}",
                'flights': [],
                'api_error': {
                    'status_code': error.response.status_code,
                    'body': error.response.body,
                    'description': error.description
                }
            }
        except Exception as e:
            logger.error(f"=== UNEXPECTED ERROR ===")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception message: {str(e)}")
            logger.error(f"Exception details: {repr(e)}")
            
            return {
                'error': True,
                'message': "An unexpected error occurred during flight search",
                'flights': []
            }
    
    def get_airport_suggestions(self, keyword):
        """
        Get airport suggestions based on keyword
        
        Args:
            keyword (str): Search keyword for airports/cities
            
        Returns:
            list: List of airport suggestions
        """
        try:
            # Cache key for airport suggestions (URL safe)
            cache_key = f"amadeus_airports_{keyword.lower().replace(' ', '_')}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                return cached_result
            
            response = self.client.reference_data.locations.get(
                keyword=keyword,
                subType='AIRPORT,CITY'
            )
            
            suggestions = []
            for location in response.data:
                suggestion = {
                    'code': location.get('iataCode', ''),
                    'name': location.get('name', ''),
                    'city': location.get('address', {}).get('cityName', ''),
                    'country': location.get('address', {}).get('countryName', ''),
                    'type': location.get('subType', '')
                }
                suggestions.append(suggestion)
            
            # Cache for 1 hour
            cache.set(cache_key, suggestions, 3600)
            return suggestions
            
        except ResponseError as error:
            logger.error(f"Airport search error: {error}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in airport search: {e}")
            return []
    
    def get_flight_price_analysis(self, origin_code, destination_code, departure_date):
        """
        Get flight price analysis and predictions
        
        Args:
            origin_code (str): IATA airport code for departure
            destination_code (str): IATA airport code for arrival  
            departure_date (str): Departure date in YYYY-MM-DD format
            
        Returns:
            dict: Price analysis data
        """
        try:
            response = self.client.analytics.itinerary_price_metrics.get(
                originIataCode=origin_code,
                destinationIataCode=destination_code,
                departureDate=departure_date
            )
            
            return {
                'error': False,
                'currency': response.data[0].get('currencyCode', 'USD'),
                'price_metrics': response.data[0].get('priceMetrics', [])
            }
            
        except ResponseError as error:
            logger.error(f"Price analysis error: {error}")
            return {'error': True, 'message': str(error)}
        except Exception as e:
            logger.error(f"Unexpected error in price analysis: {e}")
            return {'error': True, 'message': str(e)}
    
    def _normalize_flight_results(self, amadeus_data):
        """
        Normalize Amadeus flight data to match our application format
        
        Args:
            amadeus_data (list): Raw Amadeus flight data
            
        Returns:
            dict: Normalized flight results
        """
        normalized_flights = []
        
        try:
            for offer in amadeus_data:
                for itinerary in offer.get('itineraries', []):
                    for segment in itinerary.get('segments', []):
                        # Extract flight details
                        flight_data = {
                            'offer_id': offer.get('id'),
                            'amadeus_id': segment.get('id'),
                            'airline_code': segment.get('carrierCode'),
                            'airline_name': self._get_airline_name(segment.get('carrierCode')),
                            'flight_number': segment.get('number'),
                            'aircraft': segment.get('aircraft', {}).get('code', ''),
                            
                            # Origin details
                            'origin_code': segment.get('departure', {}).get('iataCode'),
                            'origin_terminal': segment.get('departure', {}).get('terminal'),
                            'departure_time': segment.get('departure', {}).get('at'),
                            
                            # Destination details
                            'destination_code': segment.get('arrival', {}).get('iataCode'),
                            'destination_terminal': segment.get('arrival', {}).get('terminal'),
                            'arrival_time': segment.get('arrival', {}).get('at'),
                            
                            # Duration
                            'duration': segment.get('duration'),
                            
                            # Pricing from the offer
                            'price': self._extract_pricing(offer.get('price', {})),
                            'available_seats': segment.get('numberOfBookableSeats', 0),
                            'booking_class': segment.get('bookingClass'),
                            
                            # Additional info
                            'stops': len(itinerary.get('segments', [])) - 1,
                            'is_direct': len(itinerary.get('segments', [])) == 1
                        }
                        
                        normalized_flights.append(flight_data)
            
            return {
                'error': False,
                'flights': normalized_flights,
                'count': len(normalized_flights)
            }
            
        except Exception as e:
            logger.error(f"Error normalizing flight data: {e}")
            return {
                'error': True,
                'message': f"Error processing flight data: {e}",
                'flights': []
            }
    
    def _extract_pricing(self, price_data):
        """Extract and normalize pricing information"""
        return {
            'total': float(price_data.get('total', 0)),
            'currency': price_data.get('currency', 'USD'),
            'base': float(price_data.get('base', 0)),
            'fees': price_data.get('fees', []),
            'taxes': price_data.get('taxes', [])
        }
    
    def _get_airline_name(self, airline_code):
        """Get airline name from code (could be cached or from a lookup table)"""
        # This is a simplified version - in production you'd want a more comprehensive lookup
        airline_names = {
            'AA': 'American Airlines',
            'DL': 'Delta Air Lines', 
            'UA': 'United Airlines',
            'SW': 'Southwest Airlines',
            'BA': 'British Airways',
            'LH': 'Lufthansa',
            'AF': 'Air France',
            'KL': 'KLM',
            'TK': 'Turkish Airlines',
            'EK': 'Emirates',
            'QR': 'Qatar Airways',
            'SQ': 'Singapore Airlines'
        }
        return airline_names.get(airline_code, airline_code)
    
    def validate_booking_offer(self, offer_id):
        """
        Validate a flight offer before booking
        
        Args:
            offer_id (str): Amadeus offer ID
            
        Returns:
            dict: Validation result
        """
        try:
            # This would validate the offer is still available and pricing is current
            # Implementation depends on specific Amadeus booking flow
            response = self.client.shopping.flight_offers.pricing.post(
                {"data": {"type": "flight-offers-pricing", "flightOffers": [{"id": offer_id}]}}
            )
            
            return {
                'valid': True,
                'offer': response.data
            }
            
        except ResponseError as error:
            logger.error(f"Offer validation error: {error}")
            return {
                'valid': False,
                'error': str(error)
            }


# Global instance
amadeus_service = AmadeusService()
