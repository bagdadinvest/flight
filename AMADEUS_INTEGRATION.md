# Amadeus API Integration for Flight Booking System

This document describes the integration of Amadeus Travel API with the Django Flight booking system, providing real-time flight data alongside the existing local database.

## Overview

The integration adds the following capabilities:
- **Real-time flight search** using Amadeus Flight Offers Search API
- **Airport/city suggestions** with global coverage
- **Price analysis and trends** for route planning
- **Combined search results** showing both local and live data
- **Enhanced user experience** with multiple data sources

## Features

### 1. Flight Search Integration
- Search live flights from 500+ airlines worldwide
- Support for one-way and round-trip searches
- Multiple cabin classes (Economy, Business, First)
- Real-time pricing and availability

### 2. Airport Data Enhancement
- Global airport and city suggestions
- IATA code lookup and validation
- Enhanced location search with country information

### 3. Price Intelligence
- Historical price trends and analysis
- Price comparison between sources
- Best time to book recommendations

### 4. Dual Search Capability
- Local database for curated routes
- Live Amadeus data for comprehensive coverage
- Side-by-side comparison of results

## Setup Instructions

### 1. Get Amadeus API Credentials

1. Visit [Amadeus for Developers](https://developers.amadeus.com/)
2. Create a free account
3. Create a new application
4. Note your `Client ID` and `Client Secret`

### 2. Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# Amadeus API Configuration
AMADEUS_CLIENT_ID=your_actual_client_id_here
AMADEUS_CLIENT_SECRET=your_actual_client_secret_here
AMADEUS_HOSTNAME=test  # Use 'production' for live environment
```

### 3. Install Dependencies

The Amadeus Python SDK is already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Test the Integration

Use the management command to test your setup:

```bash
# Test airport search
python manage.py test_amadeus --test-airports

# Test flight search
python manage.py test_amadeus --test-search --origin=JFK --destination=LAX --date=2025-08-15

# Test both
python manage.py test_amadeus --test-airports --test-search
```

## API Endpoints

### Flight Search
```
GET /amadeus/search?Origin=JFK&Destination=LAX&DepartDate=2025-08-15&SeatClass=economy
```

### Airport Suggestions
```
GET /amadeus/airports/new%20york
```

### Price Analysis
```
GET /amadeus/price-analysis?Origin=JFK&Destination=LAX&DepartDate=2025-08-15
```

## Usage Examples

### 1. Enhanced Search Page

Visit `/enhanced-search` for the new search interface that combines both local and Amadeus results.

### 2. JavaScript Integration

```javascript
// Search flights using Amadeus
const results = await amadeusClient.searchFlights({
    origin: 'JFK',
    destination: 'LAX', 
    departDate: '2025-08-15',
    seatClass: 'economy'
});

// Get airport suggestions
const airports = await amadeusClient.getAirportSuggestions('new york');
```

### 3. Template Integration

```html
<!-- Enhanced search button on homepage -->
<button onclick="enhancedSearch()" class="btn btn-success">
    <i class="fas fa-satellite"></i> Live Search
</button>
```

## Code Architecture

### Backend Components

1. **`amadeus_service.py`** - Core service class for API interactions
2. **Views** - Django views for handling API requests
3. **URLs** - Route configuration for Amadeus endpoints
4. **Management Commands** - Testing and maintenance utilities

### Frontend Components

1. **`amadeus.js`** - JavaScript client for API calls
2. **Enhanced Search Page** - Combined search interface
3. **Search Integration** - Homepage enhancements

### Key Classes

```python
# Main service class
class AmadeusService:
    def search_flights(self, origin_code, destination_code, departure_date, ...)
    def get_airport_suggestions(self, keyword)
    def get_flight_price_analysis(self, origin_code, destination_code, departure_date)
```

```javascript
// Frontend client
class AmadeusClient:
    async searchFlights(searchParams)
    async getAirportSuggestions(query) 
    async getPriceAnalysis(origin, destination, departDate)
```

## Data Flow

1. **User Input** → Frontend validation
2. **API Call** → Amadeus service layer
3. **Data Processing** → Normalization and formatting
4. **Response** → JSON data to frontend
5. **Display** → Enhanced search results page

## Error Handling

The integration includes comprehensive error handling:

- **API Rate Limits** - Graceful degradation
- **Network Issues** - Retry logic and fallbacks
- **Invalid Data** - Validation and user feedback
- **Service Unavailable** - Local database fallback

## Performance Considerations

- **Caching** - Airport suggestions cached for 1 hour
- **Pagination** - Limited results per search (configurable)
- **Async Requests** - Non-blocking API calls
- **Fallback Strategy** - Local data when Amadeus unavailable

## Security

- **Environment Variables** - Secure credential storage
- **Input Validation** - Sanitized user inputs
- **Rate Limiting** - Protect against abuse
- **HTTPS Only** - Secure API communications

## Monitoring and Debugging

### Log Files
Check Django logs for Amadeus-related errors:
```bash
tail -f logs/django.log | grep amadeus
```

### Test Commands
```bash
# Comprehensive test
python manage.py test_amadeus --test-airports --test-search

# Specific route test
python manage.py test_amadeus --test-search --origin=NYC --destination=LON --date=2025-09-01
```

### Common Issues

1. **Authentication Errors**
   - Verify `AMADEUS_CLIENT_ID` and `AMADEUS_CLIENT_SECRET`
   - Check account status at Amadeus Developer Portal

2. **No Results Found**
   - Verify airport codes are valid IATA codes
   - Check date format (YYYY-MM-DD)
   - Ensure future dates only

3. **Rate Limit Exceeded**
   - Amadeus Test environment has rate limits
   - Implement request throttling
   - Consider upgrading to production environment

## Production Deployment

### Environment Configuration
```bash
# Production settings
AMADEUS_HOSTNAME=production
AMADEUS_CLIENT_ID=your_production_client_id
AMADEUS_CLIENT_SECRET=your_production_client_secret
```

### Monitoring
- Set up monitoring for API response times
- Track API usage and costs
- Monitor error rates and types

### Scaling Considerations
- Implement Redis caching for frequent requests
- Add request queuing for high traffic
- Consider API response caching strategies

## Future Enhancements

1. **Booking Integration** - Complete booking flow via Amadeus
2. **Seat Selection** - Seat map integration
3. **Fare Rules** - Detailed fare conditions
4. **Multi-city Search** - Complex itineraries
5. **Hotel & Car Integration** - Amadeus Travel APIs
6. **Loyalty Programs** - Airline program integration

## Support

For issues and questions:
- Check the [Amadeus Developer Documentation](https://developers.amadeus.com/self-service)
- Review Django logs for error details
- Use the test management command for debugging
- Verify API credentials and permissions

## API Limits

**Test Environment:**
- 100 requests per hour
- 1,000 requests per month
- Rate limit: 10 requests per minute

**Production Environment:**
- Varies by subscription plan
- Higher limits available
- SLA guarantees included

---

This integration provides a robust foundation for real-time flight data while maintaining the existing local database functionality. The dual-source approach ensures reliability and comprehensive coverage for your flight booking system.
