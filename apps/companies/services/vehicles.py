"""Logique métier des véhicules."""
from django.shortcuts import get_object_or_404

from ..models import Vehicle


def get_owned_vehicle(company, pk):
    """Renvoie un véhicule de la compagnie, ou une erreur 404 s'il appartient à une autre."""
    return get_object_or_404(Vehicle, pk=pk, company=company)
