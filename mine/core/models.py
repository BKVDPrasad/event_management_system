from django.db import models

# Create your models here.

from django.core.exceptions import ValidationError
from django.utils import timezone

class Event(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_capacity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def current_attendees_count(self):
        return self.attendees.count()

    @property
    def available_capacity(self):
        return self.max_capacity - self.current_attendees_count

    @property
    def attendee_name_and_eamil(self):
        return self.attendees.all().values('name', 'email')

    def is_full(self):
        return self.current_attendees_count >= self.max_capacity

    def is_upcoming(self):
        return self.start_time > timezone.now()


class Attendee(models.Model):
    event = models.ForeignKey(Event, related_name='attendees', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'email') # Prevents duplicate registration for the same email on the same event


    def __str__(self):
        return f"{self.name} - {self.email} ({self.event.name})"