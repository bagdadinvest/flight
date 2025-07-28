from django import template
from datetime import datetime
import re

register = template.Library()

@register.filter
def parse_iso_time(value):
    """
    Parse ISO datetime string and return time in HH:MM format
    Example: "2023-12-25T14:30:00" -> "14:30"
    """
    if not value:
        return "--:--"
    
    try:
        # Handle various ISO datetime formats
        if 'T' in str(value):
            # Full ISO format: 2023-12-25T14:30:00 or 2023-12-25T14:30:00Z
            datetime_str = str(value).split('T')[1]
            if '+' in datetime_str:
                datetime_str = datetime_str.split('+')[0]
            if 'Z' in datetime_str:
                datetime_str = datetime_str.replace('Z', '')
            
            # Extract time part (HH:MM)
            time_part = datetime_str.split(':')
            if len(time_part) >= 2:
                return f"{time_part[0]}:{time_part[1]}"
        
        # If it's already in time format
        if ':' in str(value) and len(str(value)) <= 8:
            time_parts = str(value).split(':')
            if len(time_parts) >= 2:
                return f"{time_parts[0]}:{time_parts[1]}"
        
        # Try parsing as datetime object
        if hasattr(value, 'strftime'):
            return value.strftime('%H:%M')
            
        return str(value)[:5] if len(str(value)) >= 5 else str(value)
        
    except Exception:
        return str(value) if value else "--:--"

@register.filter
def parse_iso_date(value):
    """
    Parse ISO datetime string and return date in DD/MM/YYYY format
    """
    if not value:
        return ""
    
    try:
        if 'T' in str(value):
            date_str = str(value).split('T')[0]
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.strftime('%d/%m/%Y')
        return str(value)
    except Exception:
        return str(value) if value else ""

@register.filter
def format_duration(value):
    """
    Format flight duration from ISO 8601 duration format (PT2H30M) to readable format
    """
    if not value:
        return ""
    
    try:
        # Parse ISO 8601 duration format like PT2H30M
        duration_str = str(value)
        if duration_str.startswith('PT'):
            duration_str = duration_str[2:]  # Remove 'PT'
            
            hours = 0
            minutes = 0
            
            # Extract hours
            if 'H' in duration_str:
                hours_part = duration_str.split('H')[0]
                hours = int(hours_part) if hours_part.isdigit() else 0
                duration_str = duration_str.split('H')[1] if 'H' in duration_str else duration_str
            
            # Extract minutes
            if 'M' in duration_str:
                minutes_part = duration_str.split('M')[0]
                minutes = int(minutes_part) if minutes_part.isdigit() else 0
            
            if hours > 0 and minutes > 0:
                return f"{hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h"
            elif minutes > 0:
                return f"{minutes}m"
        
        return str(value)
    except Exception:
        return str(value) if value else ""

@register.filter
def get_airline_logo(carrier_code):
    """
    Get airline logo URL from Google's airline logo service
    """
    if not carrier_code:
        return ""
    
    # Clean the carrier code and make it uppercase
    clean_code = str(carrier_code).strip().upper()
    if clean_code:
        return f"https://www.gstatic.com/flights/airline_logos/70px/{clean_code}.png"
    return ""

@register.filter
def get_airline_logo_fallback(carrier_code):
    """
    Get airline logo URL with fallback to a default airline icon
    """
    if not carrier_code:
        return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNzAiIGhlaWdodD0iNzAiIHZpZXdCb3g9IjAgMCA3MCA3MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjcwIiBoZWlnaHQ9IjcwIiByeD0iMzUiIGZpbGw9IiMwMDdiZmYiLz4KPHN2ZyB4PSIxNSIgeT0iMjAiIHdpZHRoPSI0MCIgaGVpZ2h0PSIzMCIgdmlld0JveD0iMCAwIDQ0MCAzODQiIGZpbGw9IndoaXRlIj4KPHA+CQ=="
    
    # Clean the carrier code and make it uppercase
    clean_code = str(carrier_code).strip().upper()
    if clean_code:
        return f"https://www.gstatic.com/flights/airline_logos/70px/{clean_code}.png"
    return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNzAiIGhlaWdodD0iNzAiIHZpZXdCb3g9IjAgMCA3MCA3MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjcwIiBoZWlnaHQ9IjcwIiByeD0iMzUiIGZpbGw9IiMwMDdiZmYiLz4KPHN2ZyB4PSIxNSIgeT0iMjAiIHdpZHRoPSI0MCIgaGVpZ2h0PSIzMCIgdmlld0JveD0iMCAwIDQ0MCAzODQiIGZpbGw9IndoaXRlIj4KPHA+CQ=="

@register.filter
def get_airline_code_from_name(airline_name):
    """
    Extract or map airline code from airline name for local flights
    """
    if not airline_name:
        return ""
    
    # Map common airline names to codes
    airline_mapping = {
        'Air India': 'AI',
        'IndiGo': '6E',
        'SpiceJet': 'SG',
        'Vistara': 'UK',
        'Go First': 'G8',
        'AirAsia India': 'I5',
        'American Airlines': 'AA',
        'Delta Air Lines': 'DL',
        'United Airlines': 'UA',
        'Southwest Airlines': 'WN',
        'British Airways': 'BA',
        'Lufthansa': 'LH',
        'Air France': 'AF',
        'KLM': 'KL',
        'Emirates': 'EK',
        'Qatar Airways': 'QR',
        'Singapore Airlines': 'SQ',
        'Turkish Airlines': 'TK',
        'Cathay Pacific': 'CX',
        'Japan Airlines': 'JL',
        'All Nippon Airways': 'NH',
        'Korean Air': 'KE',
        'Thai Airways': 'TG',
        'Malaysian Airlines': 'MH',
        'China Airlines': 'CI',
        'Air Canada': 'AC',
        'Air China': 'CA',
        'China Eastern': 'MU',
        'China Southern': 'CZ',
    }
    
    # Clean airline name
    clean_name = str(airline_name).strip()
    
    # Direct mapping
    if clean_name in airline_mapping:
        return airline_mapping[clean_name]
    
    # Try partial matching
    for name, code in airline_mapping.items():
        if name.lower() in clean_name.lower() or clean_name.lower() in name.lower():
            return code
    
    # Fallback: create code from first letters
    words = clean_name.split()
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    elif len(words) == 1:
        return words[0][:2].upper()
    
    return ""

@register.filter  
def get_local_airline_logo(airline_name):
    """
    Get airline logo for local flights using airline name
    """
    if not airline_name:
        return ""
    
    # Get airline code from name
    airline_code = get_airline_code_from_name(airline_name)
    
    if airline_code:
        return f"https://www.gstatic.com/flights/airline_logos/70px/{airline_code}.png"
    
    return ""
