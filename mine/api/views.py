from django.shortcuts import render

# Create your views here.

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from core.models import Event, Attendee
from api.serializers import EventSerializer, AttendeeRegistrationSerializer, AttendeeListSerializer
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination



class EventPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100

class EventListCreateAPIView(generics.ListCreateAPIView):
    queryset = Event.objects.filter(start_time__gt=timezone.now()).order_by('start_time')
    serializer_class = EventSerializer
    pagination_class = EventPagination # Add this line

    def get_queryset(self):
        return Event.objects.filter(start_time__gt=timezone.now()).order_by('start_time')

# Similarly for AttendeeListAPIView
class AttendeeListAPIView(generics.ListAPIView):
    serializer_class = AttendeeListSerializer
    pagination_class = EventPagination # Can reuse or define a new one

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        event = get_object_or_404(Event, pk=event_id)
        return event.attendees.all().order_by('registered_at')



class EventRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_queryset(self):
        # For retrieve/update/delete, we don't strictly need to filter by upcoming,
        # but it's good practice to ensure consistency if modifying past events isn't allowed.
        # For this exercise, we'll allow retrieving past events but creation/listing is for upcoming.
        return Event.objects.all()




class RegisterAttendeeAPIView(generics.CreateAPIView):
    serializer_class = AttendeeRegistrationSerializer
    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)

        # Check if the event is full
        if event.is_full():
            return Response({"detail": "Event is full. Cannot register more attendees."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if the event has already started/ended
        if not event.is_upcoming():
             return Response({"detail": "Cannot register for an event that has already started or ended."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = AttendeeRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # Attempt to create the attendee
                    # This leverages unique_together constraint in the Attendee model for duplicate email check
                    attendee = Attendee.objects.create(
                        event=event,
                        name=serializer.validated_data['name'],
                        email=serializer.validated_data['email']
                    )
                    return Response({"detail": "Attendee registered successfully.",
                                     "attendee_id": attendee.id}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"detail": "Attendee with this email is already registered for this event."},
                                status=status.HTTP_409_CONFLICT) # Conflict status for duplicate
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

