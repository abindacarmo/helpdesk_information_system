from django.contrib.auth import views as auth_views
from django.shortcuts import render


class LoginView(auth_views.LoginView):
    """Show and process the login form (Django's built-in logic)."""

    template_name = "accounts/login.html"

class LogoutView(auth_views.LogoutView):
    """Log the user out (POST-only via the base class)."""

def dashboard(request):
    """Role-based dashboard placeholder, fully filled in later milestones."""
    return render(request, "accounts/dashboard.html")

