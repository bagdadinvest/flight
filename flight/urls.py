from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register_view, name="register"),
    path("query/places/<str:q>", views.query, name="query"),
    path("amadeus/search", views.amadeus_flight_search, name="amadeus_search"),
    path("amadeus/airports/<str:q>", views.amadeus_airport_suggestions, name="amadeus_airports"),
    path("amadeus/price-analysis", views.amadeus_flight_price_analysis, name="amadeus_price_analysis"),
    path("flight", views.unified_flight_search, name="flight"),  # Updated to use unified search
    path("unified-search", views.unified_flight_search, name="unified_search"),
    path("enhanced-search", views.enhanced_search, name="enhanced_search"),
    path("enhanced-flight-search", views.enhanced_flight_search, name="enhanced_flight_search"),
    path("review", views.review, name="review"),
    path("flight/ticket/book", views.book, name="book"),
    path("flight/ticket/payment", views.payment, name="payment"),
    path('flight/ticket/api/<str:ref>', views.ticket_data, name="ticketdata"),
    path('flight/ticket/print',views.get_ticket, name="getticket"),
    path('flight/bookings', views.bookings, name="bookings"),
    path('flight/ticket/cancel', views.cancel_ticket, name="cancelticket"),
    path('flight/ticket/resume', views.resume_booking, name="resumebooking"),
    path('contact', views.contact, name="contact"),
    path('privacy-policy', views.privacy_policy, name="privacypolicy"),
    path('terms-and-conditions', views.terms_and_conditions, name="termsandconditions"),
    path('about-us', views.about_us, name="aboutus"),
    path('flight-time', views.flighttime, name='flighttime'),
]
