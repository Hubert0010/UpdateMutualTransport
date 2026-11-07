"""Données de test partagées entre les domaines."""
from apps.accounts.models import User
from apps.companies.models import Company

PASSWORD = 'motdepasse-de-test-42'


def make_company(email='contact@nagode.tg', **fields):
    user = User.objects.create_user(email=email, password=PASSWORD, role=User.Role.COMPANY)
    fields.setdefault('legal_name', 'NAGODE TRANSPORT SARL')
    return Company.objects.create(user=user, **fields)


def make_admin(email='admin@mutualtransport.tg'):
    return User.objects.create_superuser(email=email, password=PASSWORD)
