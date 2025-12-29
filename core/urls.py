from django.urls import path
from .views import (
    home,
    equipment_list,
    equipment_detail,
    create_request,
    request_list,
    request_detail,
    kanban_board,
    update_request_state,
    calendar_view,
    calendar_events,
)

urlpatterns = [
    path('', home, name='home'),

    # Equipment
    path('equipment/', equipment_list, name='equipment_list'),
    path('equipment/<int:pk>/', equipment_detail, name='equipment_detail'),

    # Requests
    path('requests/', request_list, name='request_list'),
    path('requests/<int:pk>/', request_detail, name='request_detail'),
    path('requests/new/', create_request, name='create_request'),
    path('requests/new/<int:equipment_id>/', create_request, name='create_request_for_equipment'),

    # Kanban
    path('kanban/', kanban_board, name='kanban'),
    path('kanban/update/<int:pk>/', update_request_state, name='update_request_state'),

    # Calendar
    path('calendar/', calendar_view, name='calendar'),
    path('calendar/events/', calendar_events, name='calendar_events'),
]
