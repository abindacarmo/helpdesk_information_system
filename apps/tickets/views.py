from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def ticket_list(request):
    """Placeholder list view; the real list is built in milestone M3."""
    return render(request, "tickets/ticket_list.html")