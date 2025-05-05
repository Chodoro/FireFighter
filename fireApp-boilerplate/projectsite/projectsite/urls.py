from django.contrib import admin
from django.urls import path

from fire.views import HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth, MultilineIncidentTop3Country, multipleBarbySeverity
from fire import views


from fire.views import LocationsCreateView, LocationsUpdateView, LocationsDeleteView, LocationsListView 
from fire.views import IncidentCreateView, IncidentUpdateView, IncidentDeleteView, IncidentListView
from fire.views import FireStationListView, FireStationCreateView, FireStationUpdateView, FireStationDeleteView

from fire.views import (
    FirefighterListView, 
    FirefighterCreateView, 
    FirefighterUpdateView, 
    FirefighterDeleteView
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard-charts'),
    path('chart/', PieCountbySeverity, name='charts'),
    path('lineChart/', LineCountbyMonth, name='chart'),
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('multiBarChart/', multipleBarbySeverity, name='chart'),

    path('stations', views.map_station, name='map-station'),
    path('incidents', views.map_incidents, name='map-incidents'),


    #CRUD for Locations
    path('locations_list/', LocationsListView.as_view(), name='locations-list'),
    path('locations_list/add/', LocationsCreateView.as_view(), name='locations-add'),
    path('locations_list/<int:pk>/', LocationsUpdateView.as_view(), name='locations-update'),
    path('locations_list/<int:pk>/delete/', LocationsDeleteView.as_view(), name='locations-delete'),

    #CRUD for Incidents
    path('incident_list/', IncidentListView.as_view(), name='incident-list'),
    path('incident_list/add/', IncidentCreateView.as_view(), name='incident-add'),
    path('incident_list/<int:pk>/', IncidentUpdateView.as_view(), name='incident-update'),
    path('incident_list/<int:pk>/delete/', IncidentDeleteView.as_view(), name='incident-delete'),

    #CRUD for Fire Stations
    path('firestations/', FireStationListView.as_view(), name='firestation-list'),
    path('firestations/add/', FireStationCreateView.as_view(), name='firestation-add'),
    path('firestations/<int:pk>/edit/', FireStationUpdateView.as_view(), name='firestation-edit'),
    path('firestations/<int:pk>/delete/', FireStationDeleteView.as_view(), name='firestation-delete'),

    #CRUD for Firefighters
    path('firefighter_list/', FirefighterListView.as_view(), name='firefighter-list'),
    path('firefighter_list/add/', FirefighterCreateView.as_view(), name='firefighter-add'),
    path('firefighter_list/<int:pk>/', FirefighterUpdateView.as_view(), name='firefighter-edit'),
    path('firefighter_list/<int:pk>/delete/', FirefighterDeleteView.as_view(), name='firefighter-delete'),

]