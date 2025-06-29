# api/urls.py
from django.urls import path
from .views import (
    EventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
    RegisterAttendeeAPIView,
    AttendeeListAPIView
)

from drf_spectacular.views import (
  SpectacularAPIView,
  SpectacularSwaggerView,
  SpectacularRedocView,
)

urlpatterns = [
    path('events/', EventListCreateAPIView.as_view(), name='event-list-create'),
    path('events/<int:pk>/', EventRetrieveUpdateDestroyAPIView.as_view(), name='event-detail'),
    path('events/<int:event_id>/register/', RegisterAttendeeAPIView.as_view(), name='event-register-attendee'),
    path('events/<int:event_id>/attendees/', AttendeeListAPIView.as_view(), name='event-attendee-list'),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('schema/swagger-ui/',
         SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    # ReDoc UI
    path('schema/redoc/',
         SpectacularRedocView.as_view(url_name='schema'),
         name='redoc'),
]
