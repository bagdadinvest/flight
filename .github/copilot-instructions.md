# Flight Booking System - AI Coding Guide

## Architecture Overview
This is a Django 3.1 flight booking application with a single-app architecture (`flight/`) and project configuration in `capstone/`. The system handles flight search, booking, payment processing, and PDF ticket generation.

### Core Components
- **Models**: Custom User, Place (airports), Flight, Passenger, Ticket with status tracking
- **Data Flow**: CSV import → Search → Booking → Payment → PDF generation
- **Frontend**: Server-side templates with AJAX-enhanced search and booking flows

## Key Patterns & Conventions

### Model Relationships
```python
# Central booking model with many-to-many relationships
Ticket.passengers -> ManyToMany(Passenger)
Flight.depart_day -> ManyToMany(Week)  # Days of week flights operate
```

### Data Initialization
The app auto-initializes data on startup via `flight/views.py`:
```python
# Runs on first view load, populates from CSV files in Data/
createWeekDays() → addPlaces() → addDomesticFlights() + addInternationalFlights()
```

### Utility Separation
- `capstone/utils.py`: PDF generation and ticket creation utilities
- `flight/utils.py`: Data import and initialization functions
- `flight/constant.py`: Global fee constants (FEE = 100.0)

### Template Structure
- `layout.html`: Base for authenticated pages
- `layout2.html`: Base for login/register flows
- Templates follow naming: `{action}.html` (book.html, search.html, payment.html)

## Development Workflows

### Initial Setup
```bash
# Required for fresh installation
python manage.py makemigrations
python manage.py migrate
# Data auto-loads from CSV files in Data/ on first run
python manage.py runserver
```

### Static Files Pattern
Static assets organized by type in `flight/static/`:
- CSS: Page-specific stylesheets (e.g., `book_style.css`, `search_style.css`)
- JS: Feature-specific modules with AJAX patterns
- Images: UI assets and logos

### AJAX Implementation
Frontend uses vanilla fetch() for dynamic features:
```javascript
// Search autocomplete pattern (index.js)
fetch('query/places/'+input.value)
// Booking operations (bookings.js, payment_process.js)
fetch('ticket/cancel', {method: 'POST'})
```

## Integration Points

### PDF Generation
Uses `xhtml2pdf` library via `capstone/utils.py`:
```python
render_to_pdf(template_src, context_dict)  # Converts HTML templates to PDF
```

### External Dependencies
- **xhtml2pdf**: Ticket PDF generation (use v0.2.8+ for modern Django/Python compatibility)
- **tqdm**: Progress bars for CSV data import  
- **gunicorn**: Production WSGI server (Heroku deployment)

### Compatibility Notes
- If encountering xhtml2pdf import issues, upgrade to version 0.2.8+: `pip install xhtml2pdf==0.2.8 --upgrade`
- PDF generation can be temporarily disabled in `capstone/utils.py` for development

### Security Considerations
- CSRF protection disabled for specific API endpoints (`@csrf_exempt`)
- DEBUG=True and hardcoded SECRET_KEY (development only)
- ALLOWED_HOSTS=['*'] for deployment flexibility

## Testing & Debugging

### Data Validation
Check model relationships in Django shell:
```python
# Verify flight data loading
Flight.objects.filter(origin__code='NYC')
# Check ticket status transitions
Ticket.objects.filter(status='PENDING')
```

### Common Issues
1. **CSV Import Failures**: Check file paths in `Data/` directory
2. **PDF Generation**: Ensure template paths match in `templates/flight/`
3. **Static Files**: Run `collectstatic` for production deployment

## Business Logic

### Fare Calculation
Three-tier pricing: `economy_fare`, `business_fare`, `first_fare`
Total fare = flight_fare + FEE (constant) + coupon_discount

### Booking Flow
Search → Review → Book (passenger details) → Payment → Confirmation → PDF ticket
Status transitions: PENDING → CONFIRMED (or CANCELLED)
