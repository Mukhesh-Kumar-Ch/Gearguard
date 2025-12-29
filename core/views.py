from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django import forms
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse

from .models import Equipment, MaintenanceRequest


def calendar_view(request):
    return render(request, "core/calendar.html")


def calendar_events(request):
    preventive = MaintenanceRequest.objects.filter(request_type="preventive")
    today = timezone.now().date()
    events = []
    for req in preventive:
        if not req.scheduled_date:
            continue
        overdue = req.scheduled_date < today and req.state != MaintenanceRequest.STATE_REPAIRED
        events.append({
            "id": req.id,
            "title": f"{req.subject} ({req.equipment.name})",
            "start": str(req.scheduled_date),
            "url": reverse("request_detail", args=[req.id]),
            "color": "#dc3545" if overdue else "#0d6efd"
        })
    return JsonResponse(events, safe=False)


class MaintenanceRequestForm(ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['subject', 'request_type', 'equipment', 'scheduled_date']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'request_type': forms.Select(attrs={'class': 'form-select'}),
            'equipment': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


def home(request):
    return render(request, 'core/home.html')


def equipment_list(request):
    equipment = Equipment.objects.all()
    search_query = request.GET.get('q', '')
    if search_query:
        equipment = equipment.filter(
            Q(name__icontains=search_query) |
            Q(serial_number__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(assigned_to__username__icontains=search_query)
        )
    return render(request, 'core/equipment_list.html', {
        'equipment': equipment,
        'search_query': search_query,
    })


def equipment_detail(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    open_requests = equipment.requests.filter(state__in=["new", "in_progress"])
    return render(request, 'core/equipment_detail.html', {
        'equipment': equipment,
        'open_requests': open_requests,
    })


def request_list(request):
    today = timezone.now().date()
    requests = MaintenanceRequest.objects.select_related("equipment", "assigned_technician")
    return render(request, "core/request_list.html", {
        "requests": requests,
        "today": today
    })



def request_detail(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    technicians = req.equipment.team.members.all()
    if request.method == "POST":
        new_state = request.POST.get("state")
        tech_id = request.POST.get("assigned_technician")
        duration = request.POST.get("duration_hours")

        if tech_id:
            from django.contrib.auth.models import User
            req.assigned_technician = User.objects.get(pk=tech_id)
        else:
            if not req.assigned_technician:
                assigned = req.auto_assign_technician()
                if assigned:
                    req.assigned_technician = assigned

        if new_state in dict(MaintenanceRequest.STATE_CHOICES):
            req.state = new_state

        if req.state == MaintenanceRequest.STATE_REPAIRED:
            if duration:
                req.duration_hours = duration

        req.save()
        messages.success(request, "Request updated.")
        return redirect("request_detail", pk=req.id)

    return render(request, "core/request_detail.html", {
        "req": req,
        "technicians": technicians
    })


def create_request(request, equipment_id=None):
    equipment = get_object_or_404(Equipment, pk=equipment_id) if equipment_id else None
    initial_date = request.GET.get("date")
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            try:
                req = form.save(commit=False)
                req.created_by = request.user
                req.save()
                messages.success(request, 'Request created successfully.')
                return redirect('request_list')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Fix form errors and try again.')
    else:
        initial = {}
        if equipment:
            initial['equipment'] = equipment
        if initial_date:
            initial['scheduled_date'] = initial_date
        form = MaintenanceRequestForm(initial=initial)
    form.fields['equipment'].queryset = Equipment.objects.filter(is_scrapped=False)
    return render(request, 'core/create_request.html', {
        'form': form,
        'equipment': equipment,
        'is_scrapped': equipment.is_scrapped if equipment else False,
    })


def kanban_board(request):
    today = timezone.now().date()
    requests = MaintenanceRequest.objects.select_related("equipment", "assigned_technician")
    grouped = {
        "new": requests.filter(state="new"),
        "in_progress": requests.filter(state="in_progress"),
        "repaired": requests.filter(state="repaired"),
        "scrap": requests.filter(state="scrap"),
    }
    return render(request, "core/kanban.html", {
        "grouped": grouped,
        "today": today
    })


def update_request_state(request, pk):
    if request.method == "POST":
        new_state = request.POST.get("state")
        if new_state not in dict(MaintenanceRequest.STATE_CHOICES):
            return JsonResponse({"success": False, "error": "invalid state"}, status=400)
        req = get_object_or_404(MaintenanceRequest, pk=pk)
        req.state = new_state
        req.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)
