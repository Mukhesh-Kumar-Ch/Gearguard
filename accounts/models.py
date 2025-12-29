from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_EMPLOYEE = "employee"
    ROLE_TECHNICIAN = "technician"

    ROLE_CHOICES = [
        (ROLE_EMPLOYEE, "Employee"),
        (ROLE_TECHNICIAN, "Technician"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
