"""Logique métier des compagnies."""
from django.db import transaction

from apps.accounts.models import User
from apps.accounts.services.users import generate_password

from ..models import Company


def create_company_account(*, email, **company_fields):
    """Crée le compte et la compagnie. Renvoie la compagnie et le mot de passe généré."""
    password = generate_password()
    with transaction.atomic():
        user = User.objects.create_user(email=email, password=password, role=User.Role.COMPANY)
        company = Company.objects.create(user=user, **company_fields)
    return company, password
