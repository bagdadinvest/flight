from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from datetime import datetime
import math
from .models import *
from capstone.utils import render_to_pdf, createticket
from .amadeus_service import amadeus_service


#Fee and Surcharge variable
from .constant import FEE
from flight.utils import createWeekDays, addPlaces, addDomesticFlights, addInternationalFlights

try:
    if len(Week.objects.all()) == 0:
        createWeekDays()

    if len(Place.objects.all()) == 0:
        addPlaces()

    if len(Flight.objects.all()) == 0:
        print("Do you want to add flights in the Database? (y/n)")
        if input().lower() in ['y', 'yes']:
            addDomesticFlights()
            addInternationalFlights()
except:
    pass

# Create your views here.
def flighttime(request):
    return render(request, 'flight/flight-time.html')

def index(request):
    min_date = f"{datetime.now().date().year}-{datetime.now().date().month}-{datetime.now().date().day}"
    max_date = f"{datetime.now().date().year if (datetime.now().date().month+3)<=12 else datetime.now().date().year+1}-{(datetime.now().date().month + 3) if (datetime.now().date().month+3)<=12 else (datetime.now().date().month+3-12)}-{datetime.now().date().day}"
    if request.method == 'POST':
        origin = request.POST.get('Origin')
        destination = request.POST.get('Destination')
        depart_date = request.POST.get('DepartDate')
        seat = request.POST.get('SeatClass')
        trip_type = request.POST.get('TripType')
        if(trip_type == '1'):
            return render(request, 'new/index.html', {
            'origin': origin,
            'destination': destination,
            'depart_date': depart_date,
            'seat': seat.lower(),
            'trip_type': trip_type
        })
        elif(trip_type == '2'):
            return_date = request.POST.get('ReturnDate')
            return render(request, 'new/index.html', {
            'min_date': min_date,
            'max_date': max_date,
            'origin': origin,
            'destination': destination,
            'depart_date': depart_date,
            'seat': seat.lower(),
            'trip_type': trip_type,
            'return_date': return_date
        })
    else:
        return render(request, 'new/index.html', {
            'min_date': min_date,
            'max_date': max_date
        })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
            
        else:
            return render(request, "flight/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "flight/login.html")

def register_view(request):
    if request.method == "POST":
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensuring password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "flight/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            user.save()
        except:
            return render(request, "flight/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "flight/register.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def query(request, q):
    places = Place.objects.all()
    filters = []
    q = q.lower()
    for place in places:
        if (q in place.city.lower()) or (q in place.airport.lower()) or (q in place.code.lower()) or (q in place.country.lower()):
            filters.append(place)
    return JsonResponse([{'code':place.code, 'city':place.city, 'country': place.country} for place in filters], safe=False)

def enhanced_search(request):
    """
    Enhanced search page that shows both local and Amadeus options
    """
    o_place = request.GET.get('Origin')
    d_place = request.GET.get('Destination')
    trip_type = request.GET.get('TripType', '1')
    departdate = request.GET.get('DepartDate')
    depart_date = datetime.strptime(departdate, "%Y-%m-%d") if departdate else datetime.now().date()
    return_date = None
    
    if trip_type == '2':
        returndate = request.GET.get('ReturnDate')
        if returndate:
            return_date = datetime.strptime(returndate, "%Y-%m-%d")
    
    seat = request.GET.get('SeatClass', 'economy')

    try:
        destination = Place.objects.get(code=d_place.upper())
        origin = Place.objects.get(code=o_place.upper())
    except Place.DoesNotExist:
        return HttpResponse("Invalid airport codes provided")

    return render(request, "flight/enhanced_search.html", {
        'origin': origin,
        'destination': destination,
        'seat': seat.capitalize(),
        'trip_type': trip_type,
        'depart_date': depart_date,
        'return_date': return_date,
    })

@csrf_exempt
def flight(request):
    o_place = request.GET.get('Origin')
    d_place = request.GET.get('Destination')
    trip_type = request.GET.get('TripType')
    departdate = request.GET.get('DepartDate')
    depart_date = datetime.strptime(departdate, "%Y-%m-%d")
    return_date = None
    if trip_type == '2':
        returndate = request.GET.get('ReturnDate')
        return_date = datetime.strptime(returndate, "%Y-%m-%d")
        flightday2 = Week.objects.get(number=return_date.weekday())
        origin2 = Place.objects.get(code=d_place.upper())
        destination2 = Place.objects.get(code=o_place.upper())
    seat = request.GET.get('SeatClass')

    flightday = Week.objects.get(number=depart_date.weekday())
    destination = Place.objects.get(code=d_place.upper())
    origin = Place.objects.get(code=o_place.upper())
    available_days = []

    if seat == 'economy':
        flights = Flight.objects.filter(depart_day=flightday,origin=origin,destination=destination).exclude(economy_fare=0).order_by('economy_fare')
        if not flights.exists():
            available_days = Flight.objects.filter(origin=origin, destination=destination).exclude(economy_fare=0).values_list('depart_day__name', flat=True).distinct()
        try:
            max_price = flights.last().economy_fare
            min_price = flights.first().economy_fare
        except:
            max_price = 0
            min_price = 0

        if trip_type == '2':
            flights2 = Flight.objects.filter(depart_day=flightday2,origin=origin2,destination=destination2).exclude(economy_fare=0).order_by('economy_fare')
            if not flights2.exists():
                available_days2 = Flight.objects.filter(origin=origin2, destination=destination2).exclude(economy_fare=0).values_list('depart_day__name', flat=True).distinct()
            try:
                max_price2 = flights2.last().economy_fare
                min_price2 = flights2.first().economy_fare
            except:
                max_price2 = 0
                min_price2 = 0

    elif seat == 'business':
        flights = Flight.objects.filter(depart_day=flightday,origin=origin,destination=destination).exclude(business_fare=0).order_by('business_fare')
        if not flights.exists():
            available_days = Flight.objects.filter(origin=origin, destination=destination).exclude(business_fare=0).values_list('depart_day__name', flat=True).distinct()
        try:
            max_price = flights.last().business_fare
            min_price = flights.first().business_fare
        except:
            max_price = 0
            min_price = 0

        if trip_type == '2':
            flights2 = Flight.objects.filter(depart_day=flightday2,origin=origin2,destination=destination2).exclude(business_fare=0).order_by('business_fare')
            if not flights2.exists():
                available_days2 = Flight.objects.filter(origin=origin2, destination=destination2).exclude(business_fare=0).values_list('depart_day__name', flat=True).distinct()
            try:
                max_price2 = flights2.last().business_fare
                min_price2 = flights2.first().business_fare
            except:
                max_price2 = 0
                min_price2 = 0

    elif seat == 'first':
        flights = Flight.objects.filter(depart_day=flightday,origin=origin,destination=destination).exclude(first_fare=0).order_by('first_fare')
        if not flights.exists():
            available_days = Flight.objects.filter(origin=origin, destination=destination).exclude(first_fare=0).values_list('depart_day__name', flat=True).distinct()
        try:
            max_price = flights.last().first_fare
            min_price = flights.first().first_fare
        except:
            max_price = 0
            min_price = 0

        if trip_type == '2':
            flights2 = Flight.objects.filter(depart_day=flightday2,origin=origin2,destination=destination2).exclude(first_fare=0).order_by('first_fare')
            if not flights2.exists():
                available_days2 = Flight.objects.filter(origin=origin2, destination=destination2).exclude(first_fare=0).values_list('depart_day__name', flat=True).distinct()
            try:
                max_price2 = flights2.last().first_fare
                min_price2 = flights2.first().first_fare
            except:
                max_price2 = 0
                min_price2 = 0

    if trip_type == '2':
        return render(request, "flight/search.html", {
            'flights': flights,
            'origin': origin,
            'destination': destination,
            'flights2': flights2,
            'origin2': origin2,
            'destination2': destination2,
            'seat': seat.capitalize(),
            'trip_type': trip_type,
            'depart_date': depart_date,
            'return_date': return_date,
            'max_price': math.ceil(max_price/100)*100,
            'min_price': math.floor(min_price/100)*100,
            'max_price2': math.ceil(max_price2/100)*100,
            'min_price2': math.floor(min_price2/100)*100,
            'available_days': available_days,
            'available_days2': available_days2
        })
    else:
        return render(request, "flight/search.html", {
            'flights': flights,
            'origin': origin,
            'destination': destination,
            'seat': seat.capitalize(),
            'trip_type': trip_type,
            'depart_date': depart_date,
            'return_date': return_date,
            'max_price': math.ceil(max_price/100)*100,
            'min_price': math.floor(min_price/100)*100,
            'available_days': available_days
        })

def review(request):
    flight_1 = request.GET.get('flight1Id')
    date1 = request.GET.get('flight1Date')
    seat = request.GET.get('seatClass')
    round_trip = False
    if request.GET.get('flight2Id'):
        round_trip = True

    if round_trip:
        flight_2 = request.GET.get('flight2Id')
        date2 = request.GET.get('flight2Date')

    if request.user.is_authenticated:
        flight1 = Flight.objects.get(id=flight_1)
        flight1ddate = datetime(int(date1.split('-')[2]),int(date1.split('-')[1]),int(date1.split('-')[0]),flight1.depart_time.hour,flight1.depart_time.minute)
        flight1adate = (flight1ddate + flight1.duration)
        flight2 = None
        flight2ddate = None
        flight2adate = None
        if round_trip:
            flight2 = Flight.objects.get(id=flight_2)
            flight2ddate = datetime(int(date2.split('-')[2]),int(date2.split('-')[1]),int(date2.split('-')[0]),flight2.depart_time.hour,flight2.depart_time.minute)
            flight2adate = (flight2ddate + flight2.duration)
        #print("//////////////////////////////////")
        #print(f"flight1ddate: {flight1adate-flight1ddate}")
        #print("//////////////////////////////////")
        if round_trip:
            return render(request, "flight/book.html", {
                'flight1': flight1,
                'flight2': flight2,
                "flight1ddate": flight1ddate,
                "flight1adate": flight1adate,
                "flight2ddate": flight2ddate,
                "flight2adate": flight2adate,
                "seat": seat,
                "fee": FEE
            })
        return render(request, "flight/book.html", {
            'flight1': flight1,
            "flight1ddate": flight1ddate,
            "flight1adate": flight1adate,
            "seat": seat,
            "fee": FEE
        })
    else:
        return HttpResponseRedirect(reverse("login"))

def book(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            flight_1 = request.POST.get('flight1')
            flight_1date = request.POST.get('flight1Date')
            flight_1class = request.POST.get('flight1Class')
            f2 = False
            if request.POST.get('flight2'):
                flight_2 = request.POST.get('flight2')
                flight_2date = request.POST.get('flight2Date')
                flight_2class = request.POST.get('flight2Class')
                f2 = True
            countrycode = request.POST.get('countryCode', 'Unknown')
            mobile = request.POST.get('mobile', 'Unknown')
            email = request.POST['email']
            flight1 = Flight.objects.get(id=flight_1)
            if f2:
                flight2 = Flight.objects.get(id=flight_2)
            passengerscount = request.POST['passengersCount']
            passengers=[]
            for i in range(1,int(passengerscount)+1):
                fname = request.POST[f'passenger{i}FName']
                lname = request.POST[f'passenger{i}LName']
                gender = request.POST[f'passenger{i}Gender']
                passengers.append(Passenger.objects.create(first_name=fname,last_name=lname,gender=gender.lower()))
            coupon = request.POST.get('coupon')
            
            try:
                ticket1 = createticket(request.user,passengers,passengerscount,flight1,flight_1date,flight_1class,coupon,countrycode,email,mobile)
                if f2:
                    ticket2 = createticket(request.user,passengers,passengerscount,flight2,flight_2date,flight_2class,coupon,countrycode,email,mobile)

                if(flight_1class == 'Economy'):
                    if f2:
                        fare = (flight1.economy_fare*int(passengerscount))+(flight2.economy_fare*int(passengerscount))
                    else:
                        fare = flight1.economy_fare*int(passengerscount)
                elif (flight_1class == 'Business'):
                    if f2:
                        fare = (flight1.business_fare*int(passengerscount))+(flight2.business_fare*int(passengerscount))
                    else:
                        fare = flight1.business_fare*int(passengerscount)
                elif (flight_1class == 'First'):
                    if f2:
                        fare = (flight1.first_fare*int(passengerscount))+(flight2.first_fare*int(passengerscount))
                    else:
                        fare = flight1.first_fare*int(passengerscount)
            except Exception as e:
                return HttpResponse(e)
            

            if f2:    ##
                return render(request, "flight/payment.html", { ##
                    'fare': fare+FEE,   ##
                    'ticket': ticket1.id,   ##
                    'ticket2': ticket2.id   ##
                })  ##
            return render(request, "flight/payment.html", {
                'fare': fare+FEE,
                'ticket': ticket1.id
            })
        else:
            return HttpResponseRedirect(reverse("login"))
    else:
        return HttpResponse("Method must be post.")

def payment(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            ticket_id = request.POST['ticket']
            t2 = False
            if request.POST.get('ticket2'):
                ticket2_id = request.POST['ticket2']
                t2 = True
            fare = request.POST.get('fare')
            card_number = request.POST.get('cardNumber')
            card_holder_name = request.POST['cardHolderName']
            exp_month = request.POST['expMonth']
            exp_year = request.POST['expYear']
            cvv = request.POST['cvv']

            try:
                ticket = Ticket.objects.get(id=ticket_id)
                ticket.status = 'CONFIRMED'
                ticket.booking_date = datetime.now()
                ticket.save()
                if t2:
                    ticket2 = Ticket.objects.get(id(ticket2_id))
                    ticket2.status = 'CONFIRMED'
                    ticket2.save()
                    return render(request, 'flight/payment_process.html', {
                        'ticket1': ticket,
                        'ticket2': ticket2
                    })
                return render(request, 'flight/payment_process.html', {
                    'ticket1': ticket,
                    'ticket2': ""
                })
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be post.")
    else:
        return HttpResponseRedirect(reverse('login'))


def ticket_data(request, ref):
    ticket = Ticket.objects.get(ref_no=ref)
    return JsonResponse({
        'ref': ticket.ref_no,
        'from': ticket.flight.origin.code,
        'to': ticket.flight.destination.code,
        'flight_date': ticket.flight_ddate,
        'status': ticket.status
    })

@csrf_exempt
def get_ticket(request):
    ref = request.GET.get("ref")
    ticket1 = Ticket.objects.get(ref_no=ref)
    data = {
        'ticket1':ticket1,
        'current_year': datetime.now().year
    }
    pdf = render_to_pdf('flight/ticket.html', data)
    return HttpResponse(pdf, content_type='application/pdf')


def bookings(request):
    if request.user.is_authenticated:
        tickets = Ticket.objects.filter(user=request.user).order_by('-booking_date')
        return render(request, 'flight/bookings.html', {
            'page': 'bookings',
            'tickets': tickets
        })
    else:
        return HttpResponseRedirect(reverse('login'))

@csrf_exempt
def cancel_ticket(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            ref = request.POST['ref']
            try:
                ticket = Ticket.objects.get(ref_no=ref)
                if ticket.user == request.user:
                    ticket.status = 'CANCELLED'
                    ticket.save()
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({
                        'success': False,
                        'error': "User unauthorised"
                    })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': e
                })
        else:
            return HttpResponse("User unauthorised")
    else:
        return HttpResponse("Method must be POST.")

def resume_booking(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            ref = request.POST['ref']
            ticket = Ticket.objects.get(ref_no=ref)
            if ticket.user == request.user:
                return render(request, "flight/payment.html", {
                    'fare': ticket.total_fare,
                    'ticket': ticket.id
                })
            else:
                return HttpResponse("User unauthorised")
        else:
            return HttpResponseRedirect(reverse("login"))
    else:
        return HttpResponse("Method must be post.")

def contact(request):
    return render(request, 'flight/contact.html')

def privacy_policy(request):
    return render(request, 'flight/privacy-policy.html')

def terms_and_conditions(request):
    return render(request, 'flight/terms.html')

def about_us(request):
    return render(request, 'flight/about.html')

# Amadeus API Integration Views

@csrf_exempt
def amadeus_flight_search(request):
    """
    Search flights using Amadeus API
    """
    if request.method == 'GET':
        # Get search parameters
        origin = request.GET.get('Origin')
        destination = request.GET.get('Destination')
        depart_date = request.GET.get('DepartDate')
        return_date = request.GET.get('ReturnDate')
        seat_class = request.GET.get('SeatClass', 'ECONOMY').upper()
        adults = int(request.GET.get('Adults', 1))
        trip_type = request.GET.get('TripType', '1')
        
        # Map seat class to Amadeus format
        seat_class_map = {
            'economy': 'ECONOMY',
            'business': 'BUSINESS', 
            'first': 'FIRST'
        }
        amadeus_class = seat_class_map.get(seat_class.lower(), 'ECONOMY')
        
        # Search flights using Amadeus
        search_result = amadeus_service.search_flights(
            origin_code=origin,
            destination_code=destination,
            departure_date=depart_date,
            return_date=return_date if trip_type == '2' else None,
            adults=adults,
            travel_class=amadeus_class
        )
        
        if search_result.get('error'):
            return JsonResponse({
                'error': True,
                'message': search_result.get('message', 'Flight search failed'),
                'flights': []
            })
        
        # Get place objects for display
        try:
            origin_place = Place.objects.get(code=origin.upper())
            destination_place = Place.objects.get(code=destination.upper())
        except Place.DoesNotExist:
            return JsonResponse({
                'error': True,
                'message': 'Invalid airport codes provided',
                'flights': []
            })
        
        # Return Amadeus results
        return JsonResponse({
            'error': False,
            'source': 'amadeus',
            'flights': search_result['flights'],
            'count': search_result['count'],
            'origin': {
                'code': origin_place.code,
                'city': origin_place.city,
                'country': origin_place.country
            },
            'destination': {
                'code': destination_place.code,
                'city': destination_place.city,
                'country': destination_place.country
            }
        })
    
    return JsonResponse({'error': True, 'message': 'GET method required'})

@csrf_exempt
def unified_flight_search(request):
    """
    Unified flight search that displays results from both database and Amadeus API in the search template
    """
    if request.method == 'POST':
        # Handle form submission from home page
        o_place = request.POST.get('Origin')
        d_place = request.POST.get('Destination')
        trip_type = request.POST.get('TripType', '1')
        departdate = request.POST.get('DepartDate')
        returndate = request.POST.get('ReturnDate')
        seat = request.POST.get('SeatClass', 'economy')
        include_amadeus = request.POST.get('include_amadeus', 'true') == 'true'
    else:
        # Handle GET parameters (for modify search, etc.)
        o_place = request.GET.get('Origin')
        d_place = request.GET.get('Destination')
        trip_type = request.GET.get('TripType', '1')
        departdate = request.GET.get('DepartDate')
        returndate = request.GET.get('ReturnDate')
        seat = request.GET.get('SeatClass', 'economy')
        include_amadeus = request.GET.get('include_amadeus', 'true') == 'true'

    # Validate required parameters
    if not all([o_place, d_place, departdate]):
        messages.error(request, "Please provide all required search parameters.")
        return redirect('home')

    try:
        # Parse dates
        depart_date = datetime.strptime(departdate, "%Y-%m-%d")
        return_date = None
        if trip_type == '2' and returndate:
            return_date = datetime.strptime(returndate, "%Y-%m-%d")

        # Get place objects
        try:
            origin = Place.objects.get(code=o_place.upper())
            destination = Place.objects.get(code=d_place.upper())
        except Place.DoesNotExist:
            messages.error(request, "Invalid airport codes provided.")
            return redirect('home')

        # Initialize result containers
        local_flights = []
        amadeus_flights = []
        local_flights2 = []  # For return flights
        amadeus_error = None
        
        # Search local database flights
        flightday = Week.objects.get(name=depart_date.strftime("%A"))
        
        if seat.lower() == 'economy':
            local_flights = Flight.objects.filter(
                depart_day=flightday,
                origin=origin,
                destination=destination
            ).exclude(economy_fare=0).order_by('economy_fare')
        elif seat.lower() == 'business':
            local_flights = Flight.objects.filter(
                depart_day=flightday,
                origin=origin,
                destination=destination
            ).exclude(business_fare=0).order_by('business_fare')
        elif seat.lower() == 'first':
            local_flights = Flight.objects.filter(
                depart_day=flightday,
                origin=origin,
                destination=destination
            ).exclude(first_fare=0).order_by('first_fare')

        # Search return flights for round trip
        if trip_type == '2' and return_date:
            flightday2 = Week.objects.get(name=return_date.strftime("%A"))
            origin2 = destination  # Return trip reverses origin/destination
            destination2 = origin
            
            if seat.lower() == 'economy':
                local_flights2 = Flight.objects.filter(
                    depart_day=flightday2,
                    origin=origin2,
                    destination=destination2
                ).exclude(economy_fare=0).order_by('economy_fare')
            elif seat.lower() == 'business':
                local_flights2 = Flight.objects.filter(
                    depart_day=flightday2,
                    origin=origin2,
                    destination=destination2
                ).exclude(business_fare=0).order_by('business_fare')
            elif seat.lower() == 'first':
                local_flights2 = Flight.objects.filter(
                    depart_day=flightday2,
                    origin=origin2,
                    destination=destination2
                ).exclude(first_fare=0).order_by('first_fare')

        # Search Amadeus API if requested
        if include_amadeus:
            try:
                # Map seat class to Amadeus format
                seat_class_map = {
                    'economy': 'ECONOMY',
                    'business': 'BUSINESS', 
                    'first': 'FIRST'
                }
                amadeus_class = seat_class_map.get(seat.lower(), 'ECONOMY')
                
                # Search Amadeus flights
                amadeus_result = amadeus_service.search_flights(
                    origin_code=origin.code,
                    destination_code=destination.code,
                    departure_date=depart_date.strftime("%Y-%m-%d"),
                    return_date=return_date.strftime("%Y-%m-%d") if return_date else None,
                    adults=1,
                    travel_class=amadeus_class,
                    max_results=20
                )
                
                if not amadeus_result.get('error'):
                    amadeus_flights = amadeus_result.get('flights', [])
                else:
                    amadeus_error = amadeus_result.get('message', 'Amadeus search failed')
                    
            except Exception as e:
                amadeus_error = f"Amadeus API error: {str(e)}"

        # Calculate price ranges for filters
        max_price = min_price = 0
        max_price2 = min_price2 = 0
        
        if local_flights:
            if seat.lower() == 'economy':
                prices = [f.economy_fare for f in local_flights]
            elif seat.lower() == 'business':
                prices = [f.business_fare for f in local_flights]
            else:
                prices = [f.first_fare for f in local_flights]
            max_price = max(prices)
            min_price = min(prices)
            
        if local_flights2:
            if seat.lower() == 'economy':
                prices2 = [f.economy_fare for f in local_flights2]
            elif seat.lower() == 'business':
                prices2 = [f.business_fare for f in local_flights2]
            else:
                prices2 = [f.first_fare for f in local_flights2]
            max_price2 = max(prices2)
            min_price2 = min(prices2)

        # Include Amadeus prices in range calculation
        if amadeus_flights:
            amadeus_prices = [float(f['price']['total']) for f in amadeus_flights]
            if amadeus_prices:
                if max_price == 0:
                    max_price = max(amadeus_prices)
                    min_price = min(amadeus_prices)
                else:
                    max_price = max(max_price, max(amadeus_prices))
                    min_price = min(min_price, min(amadeus_prices))

        # Prepare context for template
        context = {
            'flights': local_flights,
            'amadeus_flights': amadeus_flights,
            'origin': origin,
            'destination': destination,
            'seat': seat.capitalize(),
            'trip_type': trip_type,
            'depart_date': depart_date,
            'return_date': return_date,
            'max_price': math.ceil(max_price/100)*100 if max_price else 1000,
            'min_price': math.floor(min_price/100)*100 if min_price else 0,
            'include_amadeus': include_amadeus,
            'amadeus_error': amadeus_error,
            'available_days': [],
        }
        
        # Add return flight data for round trips
        if trip_type == '2':
            context.update({
                'flights2': local_flights2,
                'origin2': destination,  # Return trip
                'destination2': origin,
                'max_price2': math.ceil(max_price2/100)*100 if max_price2 else 1000,
                'min_price2': math.floor(min_price2/100)*100 if min_price2 else 0,
                'available_days2': [],
            })

        return render(request, "flight/search.html", context)
        
    except Exception as e:
        messages.error(request, f"Search error: {str(e)}")
        return redirect('home')

@csrf_exempt
def enhanced_flight_search(request):
    """
    Enhanced flight search that combines database and Amadeus results
    """
    o_place = request.GET.get('Origin')
    d_place = request.GET.get('Destination')
    trip_type = request.GET.get('TripType', '1')
    departdate = request.GET.get('DepartDate')
    depart_date = datetime.strptime(departdate, "%Y-%m-%d") if departdate else datetime.now().date()
    return_date = None
    
    if trip_type == '2':
        returndate = request.GET.get('ReturnDate')
        if returndate:
            return_date = datetime.strptime(returndate, "%Y-%m-%d")
    
    seat = request.GET.get('SeatClass', 'economy')
    source = request.GET.get('source', 'both')  # 'database', 'amadeus', or 'both'

    try:
        destination = Place.objects.get(code=d_place.upper())
        origin = Place.objects.get(code=o_place.upper())
    except Place.DoesNotExist:
        return HttpResponse("Invalid airport codes provided")

    # Initialize variables
    flights = []
    flights2 = []
    amadeus_flights = []
    amadeus_flights2 = []
    max_price = 0
    min_price = 0
    max_price2 = 0
    min_price2 = 0
    available_days = []
    available_days2 = []

    # Get database flights if requested
    if source in ['database', 'both']:
        flightday = Week.objects.get(number=depart_date.weekday())
        
        if trip_type == '2':
            flightday2 = Week.objects.get(number=return_date.weekday())
            origin2 = Place.objects.get(code=d_place.upper())
            destination2 = Place.objects.get(code=o_place.upper())

        # Database flight search logic (copied from existing flight view)
        if seat == 'economy':
            flights = Flight.objects.filter(depart_day=flightday,origin=origin,destination=destination).exclude(economy_fare=0).order_by('economy_fare')
            if not flights.exists():
                available_days = Flight.objects.filter(origin=origin, destination=destination).exclude(economy_fare=0).values_list('depart_day__name', flat=True).distinct()
            try:
                max_price = flights.last().economy_fare
                min_price = flights.first().economy_fare
            except:
                max_price = 0
                min_price = 0

            if trip_type == '2':
                flights2 = Flight.objects.filter(depart_day=flightday2,origin=origin2,destination=destination2).exclude(economy_fare=0).order_by('economy_fare')
                if not flights2.exists():
                    available_days2 = Flight.objects.filter(origin=origin2, destination=destination2).exclude(economy_fare=0).values_list('depart_day__name', flat=True).distinct()
                try:
                    max_price2 = flights2.last().economy_fare
                    min_price2 = flights2.first().economy_fare
                except:
                    max_price2 = 0
                    min_price2 = 0

        elif seat == 'business':
            flights = Flight.objects.filter(depart_day=flightday,origin=origin,destination=destination).exclude(business_fare=0).order_by('business_fare')
            if not flights.exists():
                available_days = Flight.objects.filter(origin=origin, destination=destination).exclude(business_fare=0).values_list('depart_day__name', flat=True).distinct()
            try:
                max_price = flights.last().business_fare
                min_price = flights.first().business_fare
            except:
                max_price = 0
                min_price = 0

            if trip_type == '2':
                flights2 = Flight.objects.filter(depart_day=flightday2,origin=origin2,destination=destination2).exclude(business_fare=0).order_by('business_fare')
                if not flights2.exists():
                    available_days2 = Flight.objects.filter(origin=origin2, destination=destination2).exclude(business_fare=0).values_list('depart_day__name', flat=True).distinct()
                try:
                    max_price2 = flights2.last().business_fare
                    min_price2 = flights2.first().business_fare
                except:
                    max_price2 = 0
                    min_price2 = 0

        elif seat == 'first':
            flights = Flight.objects.filter(depart_day=flightday,origin=origin,destination=destination).exclude(first_fare=0).order_by('first_fare')
            if not flights.exists():
                available_days = Flight.objects.filter(origin=origin, destination=destination).exclude(first_fare=0).values_list('depart_day__name', flat=True).distinct()
            try:
                max_price = flights.last().first_fare
                min_price = flights.first().first_fare
            except:
                max_price = 0
                min_price = 0

            if trip_type == '2':
                flights2 = Flight.objects.filter(depart_day=flightday2,origin=origin2,destination=destination2).exclude(first_fare=0).order_by('first_fare')
                if not flights2.exists():
                    available_days2 = Flight.objects.filter(origin=origin2, destination=destination2).exclude(first_fare=0).values_list('depart_day__name', flat=True).distinct()
                try:
                    max_price2 = flights2.last().first_fare
                    min_price2 = flights2.first().first_fare
                except:
                    max_price2 = 0
                    min_price2 = 0

    # Get Amadeus flights if requested
    if source in ['amadeus', 'both']:
        # Map seat class to Amadeus format
        seat_class_map = {
            'economy': 'ECONOMY',
            'business': 'BUSINESS', 
            'first': 'FIRST'
        }
        amadeus_class = seat_class_map.get(seat.lower(), 'ECONOMY')
        
        # Search flights using Amadeus
        search_result = amadeus_service.search_flights(
            origin_code=o_place,
            destination_code=d_place,
            departure_date=departdate,
            return_date=returndate if trip_type == '2' else None,
            adults=1,
            travel_class=amadeus_class
        )
        
        if not search_result.get('error'):
            amadeus_flights = search_result.get('flights', [])

    # Render the search template with both database and Amadeus results
    context = {
        'flights': flights,
        'amadeus_flights': amadeus_flights,
        'origin': origin,
        'destination': destination,
        'seat': seat.capitalize(),
        'trip_type': trip_type,
        'depart_date': depart_date,
        'return_date': return_date,
        'max_price': math.ceil(max_price/100)*100 if max_price else 0,
        'min_price': math.floor(min_price/100)*100 if min_price else 0,
        'available_days': available_days,
        'source': source,
    }

    if trip_type == '2':
        context.update({
            'flights2': flights2,
            'amadeus_flights2': amadeus_flights2,
            'origin2': origin2 if 'origin2' in locals() else None,
            'destination2': destination2 if 'destination2' in locals() else None,
            'max_price2': math.ceil(max_price2/100)*100 if max_price2 else 0,
            'min_price2': math.floor(min_price2/100)*100 if min_price2 else 0,
            'available_days2': available_days2
        })

    return render(request, "flight/search.html", context)

def amadeus_airport_suggestions(request, q):
    """
    Get airport suggestions from Amadeus API
    """
    if len(q) < 2:
        return JsonResponse([], safe=False)
    
    suggestions = amadeus_service.get_airport_suggestions(q)
    
    # Format suggestions to match existing format
    formatted_suggestions = []
    for suggestion in suggestions:
        if suggestion.get('code'):  # Only include results with IATA codes
            formatted_suggestions.append({
                'code': suggestion['code'],
                'city': suggestion.get('city', suggestion.get('name', '')),
                'country': suggestion.get('country', ''),
                'name': suggestion.get('name', ''),
                'type': suggestion.get('type', '')
            })
    
    return JsonResponse(formatted_suggestions, safe=False)

@csrf_exempt
def amadeus_flight_price_analysis(request):
    """
    Get flight price analysis from Amadeus
    """
    if request.method == 'GET':
        origin = request.GET.get('Origin')
        destination = request.GET.get('Destination') 
        depart_date = request.GET.get('DepartDate')
        
        if not all([origin, destination, depart_date]):
            return JsonResponse({
                'error': True,
                'message': 'Missing required parameters'
            })
        
        analysis = amadeus_service.get_flight_price_analysis(
            origin_code=origin,
            destination_code=destination,
            departure_date=depart_date
        )
        
        return JsonResponse(analysis)
    
    return JsonResponse({'error': True, 'message': 'GET method required'})
