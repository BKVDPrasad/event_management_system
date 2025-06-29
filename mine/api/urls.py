# api/urls.py
from django.urls import path
from .views import (
    EventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
    RegisterAttendeeAPIView,
    AttendeeListAPIView
)

urlpatterns = [
    path('events/', EventListCreateAPIView.as_view(), name='event-list-create'),
    path('events/<int:pk>/', EventRetrieveUpdateDestroyAPIView.as_view(), name='event-detail'),
    path('events/<int:event_id>/register/', RegisterAttendeeAPIView.as_view(), name='event-register-attendee'),
    path('events/<int:event_id>/attendees/', AttendeeListAPIView.as_view(), name='event-attendee-list'),
]