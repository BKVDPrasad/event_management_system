from django.utils import timezone
from rest_framework import serializers
from core.models import Event, Attendee

class EventSerializer(serializers.ModelSerializer):
    # Add read-only fields for current_attendees_count and available_capacity
    current_attendees_count = serializers.IntegerField(read_only=True)
    available_capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'name', 'location', 'start_time', 'end_time', 'max_capacity',
                  'current_attendees_count', 'available_capacity', 'attendee_name_and_eamil']
        read_only_fields = ['id']

    def validate(self, data):
        # Only do this validation if at least one of the times is changing
        if 'start_time' in data or 'end_time' in data:
            # for PATCH, fill in missing values from the instance
            start = data.get('start_time', getattr(self.instance, 'start_time', None))
            end   = data.get('end_time',   getattr(self.instance, 'end_time',   None))

            # Now do the sanity checks
            if start >= end:
                raise serializers.ValidationError("End time must be after start time.")
            if start < timezone.now():
                raise serializers.ValidationError("Start time must be in the future.")

        return data

class AttendeeRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendee
        fields = ['name', 'email']

class AttendeeListSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)

    class Meta:
        model = Attendee
        fields = ['id', 'name', 'email', 'registered_at', 'event_name']

