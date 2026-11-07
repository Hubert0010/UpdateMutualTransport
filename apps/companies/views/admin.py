"""Gestion des compagnies par l'administrateur."""
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from apps.accounts.decorators import admin_required

from ..forms.company import CompanyCreateForm
from ..models import Company
from ..services.companies import create_company_account


# La réponse au POST affiche le mot de passe généré : ni redirection, qui
# l'obligerait à transiter par la session, ni mise en cache par le navigateur.
@never_cache
@admin_required
def company_list(request):
    """Liste des compagnies et création d'un compte compagnie."""
    credentials = None

    if request.method == 'POST':
        form = CompanyCreateForm(request.POST)
        if form.is_valid():
            fields = form.cleaned_data.copy()
            company, password = create_company_account(email=fields.pop('email'), **fields)
            credentials = {'email': company.user.email, 'password': password}
            form = CompanyCreateForm()
    else:
        form = CompanyCreateForm()

    return render(request, 'core/admin/compagnies.html', {
        'form': form,
        'companies': Company.objects.select_related('user'),
        'credentials': credentials,
    })
