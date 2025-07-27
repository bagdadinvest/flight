# Amadeus API Integration - Flight Search Enhancement

This document describes the comprehensive integration of the Amadeus Travel API with the Flight booking application, providing users with real-time flight data alongside the existing database flights.

## Overview

The integration provides:
- **Unified Search Interface**: Single search form that queries both local database and Amadeus API
- **Enhanced Search Results**: Side-by-side display of local and live flight data
- **Real-time Data**: Live flight prices, availability, and schedules from Amadeus
- **Seamless User Experience**: Consistent styling and filtering for both data sources

## Key Features

### 1. Unified Flight Search
- **File**: `flight/views.py` - `unified_flight_search()` function
- **URL**: `/unified-search` (also mapped to `/flight`)
- **Template**: `flight/templates/flight/search.html`

### 2. Enhanced Display
- **Amadeus flights** are clearly marked with "LIVE" badges
- **Visual distinction** with green accents and special styling
- **Consistent formatting** for times, prices, and flight details
- **Error handling** with user-friendly messages

### 3. Smart Filtering
- **Price filtering** works across both local and Amadeus flights
- **Time slot filtering** handles different datetime formats
- **Combined price ranges** include both data sources

## Implementation Details

### Backend Components

#### 1. Unified Search View (`views.py`)
```python
@csrf_exempt
def unified_flight_search(request):
    """
    Unified flight search that displays results from both database and Amadeus API
    """
```

**Features**:
- Handles both POST (from home page) and GET (modify search) requests
- Searches local database flights using existing logic
- Calls Amadeus API for live flight data
- Combines results and price ranges
- Provides comprehensive error handling

#### 2. Amadeus Service Integration
- **File**: `flight/amadeus_service.py`
- **Function**: `search_flights()`
- **Data Normalization**: Converts Amadeus API response to application format

#### 3. Template Filters
- **File**: `flight/templatetags/custom_filters.py`
- **Filters**:
  - `parse_iso_time`: Converts ISO datetime to HH:MM format
  - `parse_iso_date`: Converts ISO date to readable format
  - `format_duration`: Formats flight duration

### Frontend Components

#### 1. Enhanced Search Template
- **File**: `flight/templates/flight/search.html`
- **Features**:
  - Displays both local and Amadeus flights
  - Enhanced styling for live flights
  - Error message display
  - Consistent data formatting

#### 2. Updated Search Form
- **File**: `flight/templates/new/index.html`
- **Features**:
  - Checkbox to include/exclude Amadeus results
  - Form submission to unified search endpoint
  - Enhanced user instructions

#### 3. Improved JavaScript
- **File**: `flight/static/js/search2.js`
- **Enhancements**:
  - Price filtering supports Amadeus flights
  - Time filtering handles ISO datetime formats
  - Visual feedback for different flight types

## Data Structure

### Amadeus Flight Object
```python
{
    'offer_id': 'unique_amadeus_offer_id',
    'amadeus_id': 'segment_id',
    'airline_code': 'LH',
    'airline_name': 'Lufthansa',
    'flight_number': '441',
    'aircraft': 'A320',
    'origin_code': 'FRA',
    'destination_code': 'LHR',
    'departure_time': '2023-12-25T14:30:00',
    'arrival_time': '2023-12-25T15:45:00',
    'duration': 'PT1H15M',
    'price': {
        'total': 299.99,
        'currency': 'EUR',
        'base': 250.00
    },
    'available_seats': 9,
    'is_direct': True,
    'stops': 0
}
```

## User Interface Enhancements

### 1. Search Form
- **Location**: Home page (`new/index.html`)
- **Enhancement**: "Include Live Flight Results" checkbox
- **Submission**: POST to `/unified-search`

### 2. Search Results
- **Local Flights**: Standard styling
- **Amadeus Flights**: 
  - Green left border
  - "LIVE" badge
  - Enhanced hover effects
  - Price highlighting

### 3. Filtering
- **Price Range**: Includes both local and Amadeus prices
- **Time Slots**: Works with both datetime formats
- **Visual Feedback**: Smooth transitions and animations

## Error Handling

### 1. API Errors
- Network connectivity issues
- Invalid API credentials
- API rate limiting
- Data parsing errors

### 2. User-Friendly Messages
```html
{% if amadeus_error %}
    <div class="alert alert-warning">
        <strong>Live Flight Search Notice:</strong> {{amadeus_error}}
    </div>
{% endif %}
```

### 3. Graceful Degradation
- If Amadeus API fails, local flights still display
- Clear indication when live data is unavailable
- Option to retry or search without live data

## Configuration

### 1. Environment Variables
```python
# settings.py
AMADEUS_CLIENT_ID = 'your_client_id'
AMADEUS_CLIENT_SECRET = 'your_client_secret'
AMADEUS_HOSTNAME = 'test'  # or 'production'
```

### 2. URL Configuration
```python
# urls.py
path("unified-search", views.unified_flight_search, name="unified_search"),
path("flight", views.unified_flight_search, name="flight"),
```

## Testing

### 1. Test Search
1. Navigate to home page
2. Enter search criteria
3. Check "Include Live Flight Results"
4. Submit search
5. Verify both local and Amadeus flights display

### 2. Test Filtering
1. Use price range slider
2. Select time slots
3. Verify both flight types filter correctly

### 3. Test Error Handling
1. Disable network connection
2. Perform search
3. Verify graceful error handling

## Performance Considerations

### 1. API Caching
- Consider implementing Redis cache for frequently searched routes
- Cache airport data and airline information

### 2. Async Operations
- Potential for implementing async API calls
- Background processing for large result sets

### 3. Rate Limiting
- Implement request throttling
- Handle API quota limitations

## Future Enhancements

### 1. Booking Integration
- Extend booking flow to handle Amadeus flights
- Implement offer validation and pricing confirmation

### 2. Price Comparison
- Side-by-side price comparison
- Historical price trends
- Price alerts and notifications

### 3. Advanced Filtering
- Airline preferences
- Aircraft type filtering
- Connection time preferences

## Troubleshooting

### 1. Common Issues
- **No Amadeus results**: Check API credentials and network
- **Formatting errors**: Verify template filter implementations
- **Filtering issues**: Ensure JavaScript includes Amadeus flights

### 2. Debug Mode
- Enable Django debug mode
- Check browser console for JavaScript errors
- Review server logs for API call details

## Security Considerations

### 1. API Key Protection
- Store credentials in environment variables
- Never commit API keys to version control
- Use different keys for development and production

### 2. Input Validation
- Validate all user inputs before API calls
- Sanitize search parameters
- Implement rate limiting per user

## Conclusion

This integration provides a seamless experience for users by combining local flight data with real-time information from the Amadeus API. The implementation maintains the existing user interface while significantly enhancing the flight search capabilities with live data, comprehensive filtering, and robust error handling.

The modular design allows for easy maintenance and future enhancements while ensuring backward compatibility with the existing flight booking system.
