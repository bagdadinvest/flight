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
