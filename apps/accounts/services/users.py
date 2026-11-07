"""Logique métier des comptes utilisateurs."""
from django.utils.crypto import get_random_string

from ..models import User

# Sans caractères ambigus : le mot de passe est transmis hors ligne.
PASSWORD_ALPHABET = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
PASSWORD_LENGTH = 14


def generate_password():
    return get_random_string(PASSWORD_LENGTH, PASSWORD_ALPHABET)


def email_is_taken(email):
    return User.objects.filter(email__iexact=email).exists()
