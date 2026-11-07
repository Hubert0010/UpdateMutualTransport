"""Contrôle d'accès aux espaces administrateur et compagnie."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import User


def _restricted_to(has_access):
    """Redirige les anonymes vers la connexion et renvoie 403 aux comptes sans le bon rôle."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not has_access(request.user):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


admin_required = _restricted_to(lambda user: user.role == User.Role.ADMIN)
company_required = _restricted_to(
    lambda user: user.role == User.Role.COMPANY and hasattr(user, 'company')
)
