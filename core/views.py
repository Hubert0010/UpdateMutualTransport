"""
Pages encore statiques, en attente de leur domaine.

Quand un domaine est développé, sa vue et sa route rejoignent son app dans apps/.
"""
from django.shortcuts import render

from apps.accounts.decorators import admin_required, company_required


# ============================================================
# Espace Administrateur
# ============================================================

@admin_required
def admin_dashboard(request):
    """Tableau de bord administrateur."""
    return render(request, 'core/admin/dashboard.html')


@admin_required
def admin_utilisateurs(request):
    """Supervision des utilisateurs (BF-38, BF-39)."""
    return render(request, 'core/admin/utilisateurs.html')


@admin_required
def admin_reservations(request):
    """Supervision des réservations et paiements (BF-39)."""
    return render(request, 'core/admin/reservations.html')


@admin_required
def admin_collecte(request):
    """Couverture réseau mutualisé (BF-57)."""
    return render(request, 'core/admin/collecte.html')


# ============================================================
# Espace Compagnie
# ============================================================

@company_required
def compagnie_dashboard(request):
    """Tableau de bord compagnie (BF-35)."""
    return render(request, 'core/compagnie/dashboard.html')


@company_required
def compagnie_trajets(request):
    """Gestion des trajets (BF-31)."""
    return render(request, 'core/compagnie/trajets.html')


@company_required
def compagnie_reservations(request):
    """Réservations reçues et paiements (BF-34)."""
    return render(request, 'core/compagnie/reservations.html')


@company_required
def compagnie_regles(request):
    """Règles d'annulation et de remboursement (BF-32)."""
    return render(request, 'core/compagnie/regles.html')
