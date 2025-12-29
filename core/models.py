from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class MaintenanceTeam(models.Model):
    name = models.CharField(max_length=255, unique=True)
    members = models.ManyToManyField(User, related_name="maintenance_teams")

    def __str__(self):
        return self.name

    def get_least_loaded_member(self):
        tech_loads = []
        for tech in self.members.all():
            count = tech.maintenance_requests.filter(
                state__in=["new", "in_progress"]
            ).count()
            tech_loads.append((count, tech))

        if not tech_loads:
            return None

        tech_loads.sort(key=lambda x: x[0])
        return tech_loads[0][1]


class Equipment(models.Model):
    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255, unique=True)

    department = models.CharField(max_length=100)
    assigned_to = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_equipment"
    )

    team = models.ForeignKey(
        MaintenanceTeam,
        on_delete=models.CASCADE,
        related_name="equipment"
    )
    default_technician = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="default_tech_equipment"
    )

    purchase_date = models.DateField(null=True, blank=True)
    warranty_end_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255)

    is_scrapped = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.serial_number})"

    def open_requests_count(self):
        return self.requests.filter(state__in=["new", "in_progress"]).count()


class MaintenanceRequest(models.Model):
    TYPE_CORRECTIVE = "corrective"
    TYPE_PREVENTIVE = "preventive"
    TYPE_CHOICES = [
        (TYPE_CORRECTIVE, "Corrective"),
        (TYPE_PREVENTIVE, "Preventive"),
    ]

    STATE_NEW = "new"
    STATE_IN_PROGRESS = "in_progress"
    STATE_REPAIRED = "repaired"
    STATE_SCRAP = "scrap"
    STATE_CHOICES = [
        (STATE_NEW, "New"),
        (STATE_IN_PROGRESS, "In Progress"),
        (STATE_REPAIRED, "Repaired"),
        (STATE_SCRAP, "Scrap"),
    ]

    subject = models.CharField(max_length=255)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name="requests")
    request_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default=STATE_NEW)

    assigned_technician = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="maintenance_requests"
    )
    scheduled_date = models.DateField(null=True, blank=True)
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_requests")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} ({self.get_state_display()})"

    def auto_assign_technician(self):
        team = self.equipment.team
        if self.equipment.default_technician:
            return self.equipment.default_technician
        return team.get_least_loaded_member()

    def save(self, *args, **kwargs):
        if self.equipment and self.equipment.is_scrapped:
            raise ValidationError("You cannot create a maintenance request for scrapped equipment.")

        if self.state == self.STATE_NEW and not self.assigned_technician:
            tech = self.auto_assign_technician()
            if tech:
                self.assigned_technician = tech

        if self.state == self.STATE_SCRAP:
            self.equipment.is_scrapped = True
            self.equipment.save()

        super().save(*args, **kwargs)
