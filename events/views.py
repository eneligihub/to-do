import requests
from django.shortcuts import render, redirect, get_object_or_404
from .models import Location, Event, CartItem
from django.contrib.auth.decorators import login_required
from .forms import EventForm
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime

def landing_page(request):
    return render(request, 'landing.html')

def index(request):
    locations = Location.objects.all()
    return render(request, 'index.html', {'locations': locations})


def location_detail(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    activities = Event.objects.filter(location=location)
    return render(
        request,
        'location_detail.html',
        {'location': location, 'activities': activities}
    )


def all_events(request):
    location_id = request.GET.get('location')
    date = request.GET.get('date')
    start_date_iso8601 = ''
    end_date_iso8601 = ''
    events = Event.objects.all()
    if location_id:
        events = events.filter(location_id=location_id)
    if date:
        events = events.filter(start_date=date)
        start_date_iso8601 = f"{date}T00:00:00Z"
        end_date_iso8601 = f"{date}T23:59:59Z"
    city = get_city(location_id)
    filtered_events = get_ticketmaster_events(request, city, start_date_iso8601, end_date_iso8601)
    return render(request, 'events.html', {'events': events, 'ticketmaster_events': filtered_events})


def get_city(location_id):
    if location_id is None:
        return ''
    try:
        location_id = int(location_id)
    except ValueError:
        return ''  # or handle the error accordingly
    locations = Location.objects.all()
    for location in locations:
        if location.id == location_id:
            city = location.name
    return city


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            form.save_m2m()
            messages.success(request, 'Your event has been created!')
            return redirect('all_events')  ## NEED TO BE CHANGED
    form = EventForm()
    return render(request, 'create_event.html', {'form': form})


# need to add a msg if event created successfully

# @login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST' and request.user.is_authenticated:
        if event.payment_type == Event.PAY_TO_JOIN and event.payment_amount > 0:
            CartItem.objects.get_or_create(event=event, user=request.user)
            return redirect('user_cart')
        elif event.payment_type == Event.PAY_FOR_TASK and request.user == event.creator:
            return redirect('event_detail', event_id=event.id)
        else:
            CartItem.objects.get_or_create(event=event, user=request.user)
            return redirect('user_cart')
    return render(request, 'event_detail.html', {'event': event})


@login_required
def event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_view.html', {'event': event})


@login_required
def add_to_cart(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if CartItem.objects.filter(event=event, user=request.user).exists():
        messages.info(request, 'This event is already in your cart.')
    else:
        CartItem.objects.create(event=event, user=request.user)
        messages.success(request, 'Your event has been added to your cart.')

    return redirect('user_cart')

@login_required
def user_cart(request):
    cart_items = CartItem.objects.filter(user=request.user).order_by('event__start_date')
    return render(request, 'user_cart.html', {'cart_items': cart_items})


def get_ticketmaster_events(request, city, start_date_iso8601, end_date_iso8601):
    url = 'https://app.ticketmaster.com/discovery/v2/events.json'
    params = {
        'apikey': settings.TICKETMASTER_API_KEY,
        'city': city,
        'startDateTime': start_date_iso8601,
        'endDateTime': end_date_iso8601,
        'size': 100,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for 4xx/5xx errors
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
    # response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        events_data = data.get('_embedded', {}).get('events', [])
        filtered_events = []
        for event in events_data:
            # Extract the required fields
            event_name = event.get('name')
            images = event.get('images', [])
            third_image_url = images[2].get('url') if len(images) > 2 else None
            start_date = event.get('dates', {}).get('start', {}).get('localDate')
            start_time = event.get('dates', {}).get('start', {}).get('localTime')
            venue_info = event.get('_embedded', {}).get('venues', [{}])[0]
            venue_name = venue_info.get('name')
            city_name = venue_info.get('city', {}).get('name')
            address_line1 = venue_info.get('address', {}).get('line1')
            longitude = venue_info.get('location', {}).get('longitude')
            latitude = venue_info.get('location', {}).get('latitude')
            event_url = event.get('url')
            # Create a new event dictionary
            filtered_event = {
                'title': event_name,
                'image_url': third_image_url,
                'start_date': start_date,
                'start_time': start_time,
                'location': city_name,
                'address_line1': address_line1,
                'longitude': longitude,
                'latitude': latitude,
                'venue': venue_name,
                'url': event_url
            }
            # print(start_date)
            filtered_events.append(filtered_event)
        return filtered_events
    else:
        return JsonResponse({'error': 'Failed to fetch data from Ticketmaster API'}, status=response.status_code)

# 21.08 maiken:
def ticketmaster_event_detail(request, event_id):
    # Fetch event details from Ticketmaster using the event ID
    url = 'https://app.ticketmaster.com/discovery/v2/events/' + event_id
    params = {'apikey': settings.TICKETMASTER_API_KEY}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

    if response.status_code == 200:
        event_data = response.json()
        event_details = {
            'title': event_data.get('name'),
            'description': event_data.get('info', 'No description available.'),
            'start_date': event_data['dates']['start'].get('localDate'),
            'start_time': event_data['dates']['start'].get('localTime'),
            'end_date': event_data['dates']['end'].get('localDate'),
            'end_time': event_data['dates']['end'].get('localTime'),
            'venue': event_data['_embedded']['venues'][0].get('name'),
            'address': event_data['_embedded']['venues'][0].get('address', {}).get('line1'),
            'city': event_data['_embedded']['venues'][0]['city'].get('name'),
            'url': event_data.get('url'),
        }

        return render(request, 'ticketmaster_event_detail.html', {'event': event_details})

    return JsonResponse({'error': 'Event not found'}, status=404)

# import requests
# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Location, Event, CartItem
# from django.contrib.auth.decorators import login_required
# from .forms import EventForm
# from django.conf import settings
# from django.http import JsonResponse
# from django.contrib import messages
# from .weather_context import weather_context
#
#
# def index(request):
#     if 'weather_location' in request.session:
#         del request.session['weather_location']
#     locations = Location.objects.all()
#     return render(request, 'index.html', {'locations': locations})
#
#
# def location_detail(request, location_id):
#     location = get_object_or_404(Location, id=location_id)
#     activities = Event.objects.filter(location=location)
#     return render(
#         request,
#         'location_detail.html',
#         {'location': location, 'activities': activities}
#     )
#
#
# def all_events(request):
#     location_id = request.GET.get('location')
#     date = request.GET.get('date')
#     start_date_iso8601 = ''
#     end_date_iso8601 = ''
#
#     if location_id:
#         weather_location = Location.objects.filter(id=location_id).first()
#         if weather_location:
#             weather_location = weather_location.name
#             request.session['weather_location'] = weather_location
#         else:
#             weather_location = 'Tallinn'
#     else:
#         weather_location = request.session.get('weather_location', 'Tallinn')
#
#     events = Event.objects.all()
#
#     if location_id:
#         events = events.filter(location__name=weather_location)
#
#     if date:
#         events = events.filter(start_date=date)
#         start_date_iso8601 = f"{date}T00:00:00Z"
#         end_date_iso8601 = f"{date}T23:59:59Z"
#
#     # Integrate weather context
#     weather = weather_context(request, weather_location)
#
#     # Integrate Ticketmaster API
#     city = weather_location  # Use the weather location as the city
#     ticketmaster_events = get_ticketmaster_events(request, city, start_date_iso8601, end_date_iso8601)
#
#     return render(request, 'events.html', {
#         'events': events,
#         'ticketmaster_events': ticketmaster_events,
#         **weather
#     })
#
#
# @login_required
# def create_event(request):
#     if request.method == 'POST':
#         form = EventForm(request.POST, request.FILES)
#         if form.is_valid():
#             event = form.save(commit=False)
#             event.creator = request.user
#             event.save()
#             form.save_m2m()
#             messages.success(request, 'Your event has been created!')
#             return redirect('all_events')
#     form = EventForm()
#     return render(request, 'create_event.html', {'form': form})
#
#
# # @login_required
# def event_detail(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
#     location_name = event.location.name \
#         if event.location \
#         else 'Tallinn'
#
#     if event.location:
#         request.session['weather_location'] = event.location.name
#
#     weather = weather_context(request, location_name)
#
#     participants = event.participants.count()
#     if request.method == 'POST' and request.user.is_authenticated:
#         if event.payment_type == Event.PAY_TO_JOIN and event.payment_amount > 0:
#             CartItem.objects.get_or_create(event=event, user=request.user)
#             return redirect('user_cart')
#         elif event.payment_type == Event.PAY_FOR_TASK and request.user == event.creator:
#             return redirect('event_detail', event_id=event.id)
#     return render(request, 'event_detail.html',
#                   {'event': event,
#                    'participants': participants,
#                    **weather})
#
#
# @login_required
# def event_view(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
#     return render(request, 'event_view.html', {'event': event})
#
#
# @login_required
# def add_to_cart(request, event_id):
#     event = get_object_or_404(Event, id=event_id)
#     if not request.user in event.participants.all():
#         event.participants.add(request.user)
#     CartItem.objects.create(event=event, user=request.user)
#     return redirect('user_cart')
#
#
# @login_required
# def user_cart(request):
#     cart_items = CartItem.objects.filter(user=request.user).order_by('event__start_date')
#     return render(request, 'user_cart.html', {'cart_items': cart_items})
#
#
# def get_ticketmaster_events(request, city, start_date_iso8601=None, end_date_iso8601=None):
#     url = 'https://app.ticketmaster.com/discovery/v2/events.json'
#     params = {
#         'apikey': settings.TICKETMASTER_API_KEY,
#         'city': city,
#         'size': 100
#     }
#
#     if start_date_iso8601 and end_date_iso8601:
#         params.update({
#             'startDateTime': start_date_iso8601,
#             'endDateTime': end_date_iso8601
#         })
#
#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#     except requests.exceptions.RequestException as e:
#         return JsonResponse({'error': str(e)}, status=500)
#
#     if response.status_code == 200:
#         data = response.json()
#         events_data = data.get('_embedded', {}).get('events', [])
#         filtered_events = []
#
#         for event in events_data:
#             event_name = event.get('name')
#             images = event.get('images', [])
#             third_image_url = images[2].get('url') if len(images) > 2 else None
#             start_date = event.get('dates', {}).get('start', {}).get('localDate')
#             start_time = event.get('dates', {}).get('start', {}).get('localTime')
#             venue_info = event.get('_embedded', {}).get('venues', [{}])[0]
#             venue_name = venue_info.get('name')
#             city_name = venue_info.get('city', {}).get('name')
#             address_line1 = venue_info.get('address', {}).get('line1')
#             longitude = venue_info.get('location', {}).get('longitude')
#             latitude = venue_info.get('location', {}).get('latitude')
#             event_url = event.get('url')
#
#             filtered_event = {
#                 'title': event_name,
#                 'image_url': third_image_url,
#                 'start_date': start_date,
#                 'start_time': start_time,
#                 'location': city_name,
#                 'address_line1': address_line1,
#                 'longitude': longitude,
#                 'latitude': latitude,
#                 'venue': venue_name,
#                 'url': event_url
#             }
#             filtered_events.append(filtered_event)
#
#         return filtered_events
#     else:
#         return JsonResponse({'error': 'Failed to fetch data from Ticketmaster API'}, status=response.status_code)