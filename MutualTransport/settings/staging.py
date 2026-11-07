"""Environnement de recette : identique à la production, avec un HSTS court."""
from .prod import *  # noqa: F403

SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
