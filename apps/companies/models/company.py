"""Compagnie de transport."""
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from core.models import TimeStampedModel

validate_phone = RegexValidator(
    regex=r'^\+?[0-9][0-9 .\-]{6,18}$',
    message='Saisissez un numéro de téléphone valide (ex. : +228 90 12 34 56).',
)


class Company(TimeStampedModel):
    """Compagnie rattachée au compte utilisateur créé par l'administrateur."""

    class Region(models.TextChoices):
        MARITIME = 'Maritime', 'Maritime'
        PLATEAUX = 'Plateaux', 'Plateaux'
        CENTRALE = 'Centrale', 'Centrale'
        KARA = 'Kara', 'Kara'
        SAVANES = 'Savanes', 'Savanes'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='company',
        verbose_name='compte de connexion',
    )

    # Renseignés par l'administrateur, en lecture seule pour la compagnie.
    rccm = models.CharField('RCCM', max_length=50, blank=True)
    nif = models.CharField('NIF (OTR)', max_length=50, blank=True)
    license_number = models.CharField('licence de transport', max_length=50, blank=True)
    city = models.CharField('ville du siège', max_length=100, blank=True)
    region = models.CharField('région', max_length=20, choices=Region.choices, blank=True)

    # Modifiables par la compagnie depuis son profil.
    legal_name = models.CharField('raison sociale', max_length=200)
    trade_name = models.CharField('nom commercial', max_length=200, blank=True)
    manager_name = models.CharField('gérant / représentant légal', max_length=150, blank=True)
    support_phone = models.CharField(
        'téléphone principal service client', max_length=20, blank=True, validators=[validate_phone],
    )
    mobile_phone = models.CharField(
        'téléphone mobile / WhatsApp', max_length=20, blank=True, validators=[validate_phone],
    )
    contact_email = models.EmailField('email professionnel', blank=True)
    address = models.CharField('adresse du siège social et gare principale', max_length=255, blank=True)
    description = models.TextField('description', blank=True)
    logo = models.ImageField('logo', upload_to='companies/logos/', blank=True)
    tmoney_account = models.CharField('numéro marchand T-Money', max_length=50, blank=True)
    flooz_account = models.CharField('compte marchand Moov Flooz', max_length=50, blank=True)
    rib = models.CharField('RIB / IBAN', max_length=50, blank=True)

    class Meta:
        verbose_name = 'compagnie'
        ordering = ['-created_at', 'legal_name']

    def __str__(self):
        return self.trade_name or self.legal_name
