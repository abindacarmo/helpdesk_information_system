from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def role_required(*roles):
    """Allow the view only to logged-in users whose role is in ``roles``.

    Unauthenticated users are redirected to the login page; authenticated
    users with a different role receive 403 Forbidden.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            if roles and request.user.role not in roles:
                return HttpResponseForbidden(
                    "You do not have permission to access this pages."
                    
                )
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator

def admin_required(view_func):
    """Shortcut for views that only the Admin role may use."""
    from apps.accounts.models import User

    return role_required(User.Roles.ADMIN)(view_func)