"""Véhicule de la flotte d'une compagnie."""
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from core.models import TimeStampedModel

from .company import Company


class Vehicle(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "En service"
        MAINTENANCE = "maintenance", "En maintenance"
        INACTIVE = "inactive", "Hors service"

    class Category(models.TextChoices):
        VIP = "vip", "Grand autocar VIP"
        CONFORT = "confort", "Bus confort"
        MINIBUS = "minibus", "Minibus express"
        STANDARD = "standard", "Bus standard"

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name="vehicles", verbose_name="Compagnie"
    )
    registration_number = models.CharField("Immatriculation", max_length=20)
    brand_model = models.CharField("Marque et modèle", max_length=120)
    category = models.CharField("Catégorie", max_length=20, choices=Category.choices, default=Category.CONFORT)
    seats = models.PositiveSmallIntegerField("Nombre de places", validators=[MinValueValidator(1), MaxValueValidator(100)])
    has_ac = models.BooleanField("Climatisation", default=False)
    has_wifi = models.BooleanField("Wi-Fi", default=False)
    has_usb = models.BooleanField("Prises USB", default=False)
    technical_inspection_expiry = models.DateField("Expiration visite technique")
    insurance_policy_number = models.CharField("Numéro de police d'assurance", max_length=80)
    status = models.CharField("Statut", max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField("Observations", blank=True)

    class Meta:
        ordering = ["registration_number"]
        constraints = [
            models.UniqueConstraint(fields=["company", "registration_number"], name="unique_vehicle_plate_per_company")
        ]
        verbose_name = "véhicule"
        verbose_name_plural = "véhicules"

    def __str__(self):
        return f"{self.registration_number} — {self.brand_model}"

    @property
    def inspection_expired(self):
        return self.technical_inspection_expiry < timezone.localdate()
