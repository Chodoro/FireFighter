from django.shortcuts import render
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation


class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

def map_station(request):
    fireStations = FireStation.objects.values('name', 'latitude', 'longitude')

    for fs in fireStations:
        fs["latitude"] = float(fs['latitude'])
        fs["longitude"] = float(fs['longitude'])

    fireStations_list = list(fireStations)

    context = {
        'fireStations': fireStations_list,
    }

    return render (request, "map_station.html", context)


def map_incident(request):
    fireIncidents = Incident.objects.select_related('location').values(
        'location__city',
        'location__latitude',
        'location__longitude',
        'description',
        'date_time',
        'severity_level'
    )

    incident_list = []
    for fi in fireIncidents:
        incident_list.append({
            'city': fi['location__city'],
            'latitude': float(fi['location__latitude']),
            'longitude': float(fi['location__longitude']),
            'description': fi['description'],
            'date': fi['date_time'].strftime('%Y-%m-%d %H:%M') if fi['date_time'] else 'N/A',
            'severity': fi['severity_level']
        })

    cities = Incident.objects.select_related('location') \
        .values_list('location__city', flat=True).distinct()

    context = {
        'fireIncidents': incident_list, 
        'cities': cities,
    }

    return render(request, 'map_incident.html', context)