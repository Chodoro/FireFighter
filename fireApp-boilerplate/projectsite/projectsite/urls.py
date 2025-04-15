from django.contrib import admin
from django.urls import path

from fire.views import HomePageView
from fire import views
from fire.models import Locations, Incident, FireStation

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('stations', views.map_station, name='map-station'),
    path('incidents', views.map_incident, name='map-incident'),

]
