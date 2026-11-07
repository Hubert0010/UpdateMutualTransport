"""Routes de la flotte, sous le namespace `vehicles` utilisé par les gabarits."""
from django.urls import path

from .api import vehicles as vehicles_api
from .views import vehicles

app_name = 'vehicles'

urlpatterns = [
    path('', vehicles.vehicle_list, name='list'),
    path('ajouter/', vehicles.vehicle_create, name='create'),
    path('<int:pk>/modifier/', vehicles.vehicle_update, name='update'),
    path('<int:pk>/supprimer/', vehicles.vehicle_delete, name='delete'),
    path('<int:pk>/maintenance/', vehicles.vehicle_toggle_maintenance, name='maintenance'),
    path('api/', vehicles_api.vehicle_api, name='api'),
    path('api/<int:pk>/', vehicles_api.vehicle_api_detail, name='api_detail'),
]
