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
        """
        Check that start_time is before end_time and in the future.
        """
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("End time must be after start time.")
        if data['start_time'] < timezone.now():
            raise serializers.ValidationError("Start time must be in the future.")
        return data

class AttendeeRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendee
        fields = ['name', 'email']

class AttendeeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = ['id', 'name', 'email', 'registered_at']