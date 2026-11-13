from django.urls import path

from apps.tickets import views

app_name = "tickets"

urlpatterns = [
    path("", views.ticket_list, name="ticket_list"),
]