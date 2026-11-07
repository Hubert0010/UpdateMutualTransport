"""Environnement de production (Gunicorn derrière Nginx). Les secrets viennent de l'environnement."""
import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403


def required_env(name):
    value = os.environ.get(name)
    if not value:
        raise ImproperlyConfigured(f"La variable d'environnement {name} est obligatoire.")
    return value


SECRET_KEY = required_env('DJANGO_SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = required_env('DJANGO_ALLOWED_HOSTS').split(',')

# Nginx termine le TLS et transmet le protocole d'origine.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Limitation de l'API : seule la dernière adresse de X-Forwarded-For, écrite par Nginx,
# est fiable. Sans ce réglage, un client pourrait falsifier l'en-tête pour contourner la limite.
REST_FRAMEWORK = {**REST_FRAMEWORK, 'NUM_PROXIES': 1}  # noqa: F405
