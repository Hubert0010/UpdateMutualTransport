"""Connexion et déconnexion."""
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST

from ..forms.auth import LoginForm
from ..models import User


def _home_url(user):
    """Espace vers lequel envoyer un utilisateur connecté."""
    return 'core:admin_dashboard' if user.role == User.Role.ADMIN else 'core:compagnie_dashboard'


@never_cache
@sensitive_post_parameters('password')
def login_view(request):
    if request.user.is_authenticated:
        return redirect(_home_url(request.user))

    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            login(request, form.user)
            if not form.cleaned_data['remember']:
                # La session prend fin à la fermeture du navigateur.
                request.session.set_expiry(0)

            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect(_home_url(form.user))
    else:
        form = LoginForm(request)

    return render(request, 'core/login.html', {'form': form})


@require_POST
def logout_view(request):
    """Déconnexion (POST uniquement, pour être protégée par le jeton CSRF)."""
    logout(request)
    return redirect('accounts:login')
