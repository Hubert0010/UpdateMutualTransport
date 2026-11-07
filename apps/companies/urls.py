from django.urls import path

from .views import admin, profile

app_name = 'companies'

urlpatterns = [
    # --- Administrateur ---
    path('admin/compagnies/', admin.company_list, name='admin_list'),

    # --- Compagnie ---
    path('compagnie/profil/', profile.company_profile, name='profile'),
]
