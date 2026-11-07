"""Obtention et renouvellement des jetons JWT."""
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class AuthThrottleMixin:
    """Limite les tentatives de connexion, sans partager le quota du reste de l'API."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'


class TokenView(AuthThrottleMixin, TokenObtainPairView):
    pass


class TokenRefreshThrottledView(AuthThrottleMixin, TokenRefreshView):
    pass
