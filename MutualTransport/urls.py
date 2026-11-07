"""Routage principal : chaque domaine déclare ses routes dans son propre urls.py."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/v1/', include('MutualTransport.api_v1')),
    path('', include('apps.accounts.urls')),
    path('', include('apps.companies.urls')),
    path('compagnie/vehicules/', include('apps.companies.vehicle_urls')),
    path('', include('apps.trips.urls')),
    path('', include('apps.bookings.urls')),
    path('', include('apps.payments.urls')),
    path('', include('apps.notifications.urls')),
    path('', include('apps.assistant.urls')),
    path('', include('apps.supervision.urls')),
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # actif seulement si DEBUG=True
