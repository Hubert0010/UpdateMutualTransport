"""Environnement de développement local."""
from .base import *  # noqa: F403

SECRET_KEY = 'django-insecure-mutualtransport-dev-key'  # réservée au développement
DEBUG = True
ALLOWED_HOSTS = ['*']

# Interface de test de l'API dans le navigateur, avec la session Django.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    'DEFAULT_AUTHENTICATION_CLASSES': [
        *REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'],  # noqa: F405
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        *REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'],  # noqa: F405
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}
