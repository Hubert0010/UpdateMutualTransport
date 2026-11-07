"""Profil de la compagnie connectée."""
from django.contrib import messages
from django.shortcuts import redirect, render

from apps.accounts.decorators import company_required

from ..forms.company import CompanyProfileForm


@company_required
def company_profile(request):
    company = request.user.company

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('companies:profile')
        # La validation a modifié l'instance en mémoire : le reste de la page
        # doit continuer d'afficher les valeurs enregistrées.
        company.refresh_from_db()
    else:
        form = CompanyProfileForm(instance=company)

    return render(request, 'core/compagnie/profil.html', {'form': form, 'company': company})
