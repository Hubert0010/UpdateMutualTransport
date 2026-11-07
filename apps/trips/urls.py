from django.urls import path

from .views import imports

app_name = 'trips'

urlpatterns = [
    path('compagnie/import-donnees/', imports.import_planning, name='import'),
    path('compagnie/telecharger-modele/', imports.download_import_template, name='import_template'),
]
