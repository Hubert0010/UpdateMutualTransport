"""Routage de la version 1 de l'API REST : chaque domaine déclare ses routes dans api/urls.py."""
from django.urls import include, path

app_name = 'api_v1'

urlpatterns = [
    path('auth/', include('apps.accounts.api.urls')),
    path('companies/', include('apps.companies.api.urls')),
    path('trips/', include('apps.trips.api.urls')),
    path('bookings/', include('apps.bookings.api.urls')),
    path('payments/', include('apps.payments.api.urls')),
    path('notifications/', include('apps.notifications.api.urls')),
    path('assistant/', include('apps.assistant.api.urls')),
    path('supervision/', include('apps.supervision.api.urls')),
]
