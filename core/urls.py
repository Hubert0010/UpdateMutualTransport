"""Routes des pages encore statiques, et noms de routes utilisés par les gabarits."""
from django.urls import path

from apps.accounts.views import auth
from apps.companies.views import admin, profile, vehicles
from apps.trips.views import imports

from . import views

app_name = 'core'

urlpatterns = [
    # --- Espace Administrateur ---
    path('admin/tableau-de-bord/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/utilisateurs/', views.admin_utilisateurs, name='admin_utilisateurs'),
    path('admin/reservations/', views.admin_reservations, name='admin_reservations'),
    path('admin/collecte/', views.admin_collecte, name='admin_collecte'),

    # --- Espace Compagnie ---
    path('compagnie/tableau-de-bord/', views.compagnie_dashboard, name='compagnie_dashboard'),
    path('compagnie/trajets/', views.compagnie_trajets, name='compagnie_trajets'),
    path('compagnie/reservations/', views.compagnie_reservations, name='compagnie_reservations'),
    path('compagnie/regles/', views.compagnie_regles, name='compagnie_regles'),

    # --- Noms utilisés par les gabarits pour des routes qui appartiennent aux apps ---
    # Les requêtes sont traitées par les urls.py des apps, inclus avant celui-ci.
    # À retirer quand les gabarits utiliseront les noms des apps.
    path('', auth.login_view, name='login'),
    path('admin/compagnies/', admin.company_list, name='admin_compagnies'),
    path('compagnie/profil/', profile.company_profile, name='compagnie_profil'),
    path('compagnie/vehicules/', vehicles.vehicle_list, name='compagnie_vehicules'),
    path('compagnie/import-donnees/', imports.import_planning, name='compagnie_import'),
    path('compagnie/telecharger-modele/', imports.download_import_template, name='telecharger_modele_import'),
]
