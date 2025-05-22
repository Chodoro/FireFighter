from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db import connection
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from datetime import datetime

from fire.models import Locations, Incident, FireStation, Firefighters, FireTruck, WeatherConditions
from fire.forms import LocationsForm, IncidentForm, FireStationForm, FirefightersForm, FireTruckForm, WeatherConditionsForm

# === GENERAL VIEWS ===

class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

class ChartView(ListView):
    template_name = 'chart.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    def get_queryset(self, *args, **kwargs):
        pass

# === JSON CHART VIEWS ===

def PieCountbySeverity(request):
    query = '''
        SELECT severity_level, COUNT(*) as count
        FROM fire_incident
        GROUP BY severity_level
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    data = {severity: count for severity, count in rows} if rows else {}
    return JsonResponse(data)

def LineCountbyMonth(request):
    current_year = datetime.now().year
    result = {month: 0 for month in range(1, 13)}
    incidents_per_month = Incident.objects.filter(date_time__year=current_year).values_list('date_time', flat=True)
    for date_time in incidents_per_month:
        result[date_time.month] += 1
    month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    result_named = {month_names[k]: v for k, v in result.items()}
    return JsonResponse(result_named)

def map_station(request):
    stations = FireStation.objects.values('name', 'latitude', 'longitude')
    for fs in stations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])
    return render(request, 'map_station.html', {'fireStations': list(stations)})

def map_incidents(request):
    fireIncidents = Incident.objects.select_related('location').values(
        'location__city', 'location__latitude', 'location__longitude',
        'description', 'date_time', 'severity_level'
    )
    incident_list = [{
        'city': fi['location__city'],
        'latitude': float(fi['location__latitude']),
        'longitude': float(fi['location__longitude']),
        'description': fi['description'],
        'date': fi['date_time'].strftime('%Y-%m-%d %H:%M') if fi['date_time'] else 'N/A',
        'severity': fi['severity_level']
    } for fi in fireIncidents]

    cities = Incident.objects.select_related('location').values_list('location__city', flat=True).distinct()
    return render(request, 'map_incidents.html', {'fireIncidents': incident_list, 'cities': cities})

def MultilineIncidentTop3Country(request):
    query = '''
        SELECT fl.country, strftime('%m', fi.date_time) AS month, COUNT(fi.id) AS incident_count
        FROM fire_incident fi
        JOIN fire_locations fl ON fi.location_id = fl.id
        WHERE fl.country IN (
            SELECT fl_top.country
            FROM fire_incident fi_top
            JOIN fire_locations fl_top ON fi_top.location_id = fl_top.id
            WHERE strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY fl_top.country
            ORDER BY COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
        GROUP BY fl.country, month
        ORDER BY fl.country, month;
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))
    for country, month, count in rows:
        result.setdefault(country, {m: 0 for m in months})[month] = count
    while len(result) < 3:
        result[f"Country {len(result)+1}"] = {m: 0 for m in months}
    for country in result:
        result[country] = dict(sorted(result[country].items()))
    return JsonResponse(result)

def multipleBarbySeverity(request):
    query = '''
        SELECT fi.severity_level, strftime('%m', fi.date_time) AS month, COUNT(fi.id)
        FROM fire_incident fi
        GROUP BY fi.severity_level, month
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))
    for level, month, count in rows:
        result.setdefault(str(level), {m: 0 for m in months})[month] = count
    for level in result:
        result[level] = dict(sorted(result[level].items()))
    return JsonResponse(result)

# === SHARED MESSAGE MIXIN ===

class MessageMixin:
    success_message = ""

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# === CRUD VIEWS FOR EACH MODEL ===

# LOCATIONS
class LocationsCreateView(MessageMixin, CreateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'locations_add.html'
    success_url = reverse_lazy('locations-list')
    success_message = "Location successfully added."

class LocationsUpdateView(MessageMixin, UpdateView):
    model = Locations
    form_class = LocationsForm
    template_name = 'locations_edit.html'
    success_url = reverse_lazy('locations-list')
    success_message = "Location successfully updated."

class LocationsDeleteView(MessageMixin, DeleteView):
    model = Locations
    template_name = 'locations_del.html'
    success_url = reverse_lazy('locations-list')
    success_message = "Location successfully deleted."

class LocationsListView(ListView):
    model = Locations
    template_name = 'locations_list.html'
    context_object_name = 'locations'

# INCIDENT
class IncidentCreateView(MessageMixin, CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incident_add.html'
    success_url = reverse_lazy('incident-list')
    success_message = "Incident successfully added."

class IncidentUpdateView(MessageMixin, UpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'incident_edit.html'
    success_url = reverse_lazy('incident-list')
    success_message = "Incident successfully updated."

class IncidentDeleteView(MessageMixin, DeleteView):
    model = Incident
    template_name = 'incident_del.html'
    success_url = reverse_lazy('incident-list')
    success_message = "Incident successfully deleted."

class IncidentListView(ListView):
    model = Incident
    template_name = 'incident_list.html'
    context_object_name = 'incidents'

# FIRE STATION
class FireStationCreateView(MessageMixin, CreateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation_add.html'
    success_url = reverse_lazy('firestation-list')
    success_message = "Fire Station successfully added."

class FireStationUpdateView(MessageMixin, UpdateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation_edit.html'
    success_url = reverse_lazy('firestation-list')
    success_message = "Fire Station successfully updated."

class FireStationDeleteView(MessageMixin, DeleteView):
    model = FireStation
    template_name = 'firestation_del.html'
    success_url = reverse_lazy('firestation-list')
    success_message = "Fire Station successfully deleted."

class FireStationListView(ListView):
    model = FireStation
    template_name = 'firestation_list.html'
    context_object_name = 'stations'

# FIREFIGHTERS
class FirefighterCreateView(MessageMixin, CreateView):
    model = Firefighters
    form_class = FirefightersForm
    template_name = 'firefighter_add.html'
    success_url = reverse_lazy('firefighter-list')
    success_message = "Firefighter successfully added."

class FirefighterUpdateView(MessageMixin, UpdateView):
    model = Firefighters
    form_class = FirefightersForm
    template_name = 'firefighter_edit.html'
    success_url = reverse_lazy('firefighter-list')
    success_message = "Firefighter successfully updated."

class FirefighterDeleteView(MessageMixin, DeleteView):
    model = Firefighters
    template_name = 'firefighter_del.html'
    success_url = reverse_lazy('firefighter-list')
    success_message = "Firefighter successfully deleted."

class FirefighterListView(ListView):
    model = Firefighters
    template_name = 'firefighter_list.html'
    context_object_name = 'firefighters'

# FIRE TRUCK
class FireTruckCreateView(MessageMixin, CreateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'firetruck_add.html'
    success_url = reverse_lazy('firetruck-list')
    success_message = "Fire Truck successfully added."

class FireTruckUpdateView(MessageMixin, UpdateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'firetruck_edit.html'
    success_url = reverse_lazy('firetruck-list')
    success_message = "Fire Truck successfully updated."

class FireTruckDeleteView(MessageMixin, DeleteView):
    model = FireTruck
    template_name = 'firetruck_del.html'
    success_url = reverse_lazy('firetruck-list')
    success_message = "Fire Truck successfully deleted."

class FireTruckListView(ListView):
    model = FireTruck
    template_name = 'firetruck_list.html'
    context_object_name = 'firetrucks'

# WEATHER CONDITIONS
class WeatherConditionsCreateView(MessageMixin, CreateView):
    model = WeatherConditions
    form_class = WeatherConditionsForm
    template_name = 'weatherconditions_add.html'
    success_url = reverse_lazy('weatherconditions-list')
    success_message = "Weather condition successfully added."

class WeatherConditionsUpdateView(MessageMixin, UpdateView):
    model = WeatherConditions
    form_class = WeatherConditionsForm
    template_name = 'weatherconditions_edit.html'
    success_url = reverse_lazy('weatherconditions-list')
    success_message = "Weather condition successfully updated."

class WeatherConditionsDeleteView(MessageMixin, DeleteView):
    model = WeatherConditions
    template_name = 'weatherconditions_del.html'
    success_url = reverse_lazy('weatherconditions-list')
    success_message = "Weather condition successfully deleted."

class WeatherConditionsListView(ListView):
    model = WeatherConditions
    template_name = 'weatherconditions_list.html'
    context_object_name = 'weather_conditions'
