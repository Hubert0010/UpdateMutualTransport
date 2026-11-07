from django.urls import path

from .views import auth

app_name = 'accounts'

urlpatterns = [
    path('', auth.login_view, name='home'),
    path('connexion/', auth.login_view, name='login'),
    path('deconnexion/', auth.logout_view, name='logout'),
]
