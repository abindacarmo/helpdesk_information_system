from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user with a role field (Admin, Technician, Reporter)."""

    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TECHNICIAN = "TECHNICIAN", "Technician"
        REPORTER = "REPORTER", "Reporter"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.REPORTER,
    )

    



