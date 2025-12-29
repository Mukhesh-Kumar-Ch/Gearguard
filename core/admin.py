from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from urllib.parse import urlencode

from .models import MaintenanceTeam, Equipment, MaintenanceRequest


# ------------------------------
# Maintenance Team Admin
# ------------------------------
@admin.register(MaintenanceTeam)
class MaintenanceTeamAdmin(admin.ModelAdmin):
    list_display = ("name", "member_count")
    search_fields = ("name",)
    filter_horizontal = ("members",)

    def member_count(self, obj):
        return obj.members.count()

    member_count.short_description = "Members"


# ------------------------------
# Equipment Admin
# ------------------------------
@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "serial_number",
        "department",
        "team",
        "assigned_to",
        "is_scrapped",
        "open_requests_badge",
    )
    list_filter = ("department", "team", "is_scrapped")
    search_fields = ("name", "serial_number", "department", "location")
    readonly_fields = ("open_requests_badge",)

    # track current obj so we can filter technician options
    def get_form(self, request, obj=None, **kwargs):
        self._current_obj = obj
        return super().get_form(request, obj, **kwargs)

    # filter DEFAULT TECHNICIAN dropdown based on selected team
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "default_technician":
            obj = getattr(self, "_current_obj", None)
            if obj and obj.team:
                kwargs["queryset"] = User.objects.filter(maintenance_teams=obj.team)
            else:
                kwargs["queryset"] = User.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Badge showing open requests & clickable filter
    def open_requests_badge(self, obj):
        count = obj.open_requests_count()
        color = "#dc3545" if count > 0 else "#198754"

        app_label = MaintenanceRequest._meta.app_label
        model_name = MaintenanceRequest._meta.model_name
        base_url = reverse(f"admin:{app_label}_{model_name}_changelist")
        params = {"equipment__id__exact": obj.id, "state__in": "new,in_progress"}
        url = f"{base_url}?{urlencode(params)}"

        badge = format_html(
            '<span style="display:inline-block;padding:.25em .4em;font-size:75%;font-weight:700;'
            'line-height:1;color:#fff;background-color:{};border-radius:.25rem">{}</span>',
            color,
            count,
        )
        return format_html('<a href="{}">{}</a>', url, badge)

    open_requests_badge.short_description = "Open Requests"


# ------------------------------
# Maintenance Request Admin
# ------------------------------
@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "equipment",
        "assigned_technician",
        "request_type",
        "colored_state",
        "created_at",
    )
    list_filter = ("request_type", "state", "assigned_technician", "equipment")
    search_fields = ("subject", "equipment__name", "assigned_technician__username")
    list_display_links = ("subject",)

    # track selected equipment id
    def get_form(self, request, obj=None, **kwargs):
        self._current_obj = obj
        self._equipment_id_from_get = (
            request.GET.get("equipment") or request.GET.get("equipment__id__exact")
        )
        return super().get_form(request, obj, **kwargs)

    # Filter technician & equipment options
    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        # --- Technicians filtered by equipment.team ---
        if db_field.name == "assigned_technician":
            equipment = None
            obj = getattr(self, "_current_obj", None)

            if obj and getattr(obj, "equipment", None):
                equipment = obj.equipment
            else:
                eq_id = getattr(self, "_equipment_id_from_get", None)
                if eq_id:
                    try:
                        equipment = Equipment.objects.get(pk=eq_id)
                    except Equipment.DoesNotExist:
                        equipment = None

            if equipment and equipment.team:
                kwargs["queryset"] = User.objects.filter(maintenance_teams=equipment.team)
            else:
                kwargs["queryset"] = User.objects.none()

            # auto-default technician when new
            if obj is None and equipment and equipment.default_technician:
                kwargs.setdefault("initial", equipment.default_technician.pk)

        # --- Hide scrapped equipment only when creating ---
        if db_field.name == "equipment":
            obj = getattr(self, "_current_obj", None)
            if obj is None:
                kwargs["queryset"] = Equipment.objects.filter(is_scrapped=False)
            else:
                kwargs["queryset"] = Equipment.objects.all()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Enforce state default to "New" when creating
        if obj is None and 'state' in form.base_fields:
            form.base_fields['state'].initial = MaintenanceRequest.STATE_NEW
        return form

    # colored status tag
    def colored_state(self, obj):
        mapping = {
            obj.STATE_NEW: ("New", "#0d6efd"),
            obj.STATE_IN_PROGRESS: ("In Progress", "#ffc107"),
            obj.STATE_REPAIRED: ("Repaired", "#198754"),
            obj.STATE_SCRAP: ("Scrap", "#dc3545"),
        }
        label, color = mapping.get(obj.state, (obj.get_state_display(), "#6c757d"))
        return format_html(
            '<span style="display:inline-block;padding:.25em .4em;font-size:75%;font-weight:700;'
            'line-height:1;color:#000;background-color:{};border-radius:.25rem">{}</span>',
            color,
            label,
        )

    colored_state.short_description = "State"
    colored_state.admin_order_field = "state"