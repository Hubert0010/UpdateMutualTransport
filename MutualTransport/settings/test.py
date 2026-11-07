"""Exécution des tests : mots de passe hachés rapidement."""
from .dev import *  # noqa: F403
from .base import REST_FRAMEWORK  # noqa: E402, F401  # API testée avec les réglages de production

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

LOGGING = {**LOGGING, 'root': {'handlers': [], 'level': 'CRITICAL'}}  # noqa: F405
