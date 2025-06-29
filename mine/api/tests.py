from django.test import TestCase

# Create your tests here.

# api/tests.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from core.models import Event, Attendee
from datetime import datetime, timedelta
from django.utils import timezone  # Important for timezone-aware datetimes


class EventAPITests(APITestCase):
    """
    Tests for Event creation and listing API endpoints.
    GET /api/events/
    POST /api/events/
    GET /api/events/{event_id}/
    """

    def setUp(self):
        # Helper to create an event with default valid data for testing
        self.now = timezone.now()

    def _create_event_payload(self, **kwargs):
        defaults = {
            'name': 'Default Test Event',
            'location': 'Default Test Location',
            'start_time': (self.now + timedelta(days=7)).isoformat(timespec='seconds') + 'Z',
            'end_time': (self.now + timedelta(days=8)).isoformat(timespec='seconds') + 'Z',
            'max_capacity': 100
        }
        defaults.update(kwargs)
        return defaults

    def test_create_valid_event(self):
        """
        Ensure we can create a new event with valid data.
        POST /api/events/
        """
        url = reverse('event-list-create')  # Name from api/urls.py
        data = self._create_event_payload(name='New Tech Conference')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().name, 'New Tech Conference')

    def test_create_event_missing_required_fields(self):
        """
        Ensure we cannot create an event with missing required fields.
        POST /api/events/
        """
        url = reverse('event-list-create')
        # Missing 'name' and 'location'
        data = self._create_event_payload(name='', location='')
        data.pop('name')  # Remove name entirely
        data.pop('location')  # Remove location entirely
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('location', response.data)
        self.assertEqual(Event.objects.count(), 0)

    def test_create_event_start_time_in_past(self):
        """
        Ensure we cannot create an event with a start time in the past.
        POST /api/events/
        """
        url = reverse('event-list-create')
        past_time = (self.now - timedelta(days=1)).isoformat(timespec='seconds') + 'Z'
        data = self._create_event_payload(start_time=past_time)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_time', response.data)
        self.assertEqual(Event.objects.count(), 0)

    def test_create_event_end_time_before_start_time(self):
        """
        Ensure we cannot create an event where end time is before start time.
        POST /api/events/
        """
        url = reverse('event-list-create')
        start_time = (self.now + timedelta(days=10)).isoformat(timespec='seconds') + 'Z'
        end_time = (self.now + timedelta(days=9)).isoformat(timespec='seconds') + 'Z'
        data = self._create_event_payload(start_time=start_time, end_time=end_time)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(Event.objects.count(), 0)

    def test_create_event_invalid_capacity(self):
        """
        Ensure we cannot create an event with non-positive max_capacity.
        POST /api/events/
        """
        url = reverse('event-list-create')
        data = self._create_event_payload(max_capacity=0)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('max_capacity', response.data)

        data = self._create_event_payload(max_capacity=-5)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('max_capacity', response.data)
        self.assertEqual(Event.objects.count(), 0)

    def test_list_upcoming_events_only(self):
        """
        Ensure GET /api/events/ only returns upcoming events.
        """
        self.create_past_event()  # Helper function needed for this.
        upcoming_event_1 = Event.objects.create(
            name='Upcoming Event 1',
            location='Location 1',
            start_time=self.now + timedelta(days=1),
            end_time=self.now + timedelta(days=2),
            max_capacity=50
        )
        upcoming_event_2 = Event.objects.create(
            name='Upcoming Event 2',
            location='Location 2',
            start_time=self.now + timedelta(days=5),
            end_time=self.now + timedelta(days=6),
            max_capacity=70
        )
        url = reverse('event-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should only show 2 upcoming, not past
        self.assertIn(upcoming_event_1.name, [e['name'] for e in response.data])
        self.assertIn(upcoming_event_2.name, [e['name'] for e in response.data])

    def test_list_no_events(self):
        """
        Ensure GET /api/events/ returns an empty list if no events exist.
        """
        url = reverse('event-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_retrieve_event_detail(self):
        """
        Ensure we can retrieve details of a specific event.
        GET /api/events/{event_id}/
        """
        event = Event.objects.create(
            name='Detail Test Event',
            location='Detail Location',
            start_time=self.now + timedelta(days=1),
            end_time=self.now + timedelta(days=2),
            max_capacity=10
        )
        url = reverse('event-detail', args=[event.id])  # Name from api/urls.py
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Detail Test Event')
        self.assertEqual(response.data['location'], 'Detail Location')
        self.assertEqual(response.data['max_capacity'], 10)
        # Check current_attendees is 0 for newly created event
        self.assertEqual(response.data['current_attendees'], 0)

    def test_retrieve_non_existent_event(self):
        """
        Ensure retrieving a non-existent event returns 404.
        GET /api/events/{event_id}/
        """
        url = reverse('event-detail', args=[9999])  # Non-existent ID
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Helper method to create a past event for testing
    def create_past_event(self):
        return Event.objects.create(
            name='Past Event',
            location='Past Location',
            start_time=self.now - timedelta(days=10),
            end_time=self.now - timedelta(days=9),
            max_capacity=50
        )


class AttendeeAPITests(APITestCase):
    """
    Tests for Attendee registration and listing API endpoints.
    POST /api/events/{event_id}/register/
    GET /api/events/{event_id}/attendees/
    """

    def setUp(self):
        self.now = timezone.now()
        self.upcoming_event = Event.objects.create(
            name='Upcoming Event',
            location='Venue A',
            start_time=self.now + timedelta(days=10),
            end_time=self.now + timedelta(days=11),
            max_capacity=5
        )
        self.full_event = Event.objects.create(
            name='Full Event',
            location='Venue B',
            start_time=self.now + timedelta(days=20),
            end_time=self.now + timedelta(days=21),
            max_capacity=1
        )
        Attendee.objects.create(
            event=self.full_event,
            name='Already Registered',
            email='already@example.com'
        )  # This makes the full_event full

        self.past_event = Event.objects.create(
            name='Past Event',
            location='Venue C',
            start_time=self.now - timedelta(days=10),
            end_time=self.now - timedelta(days=9),
            max_capacity=10
        )
        self.event_starting_soon = Event.objects.create(
            name='Event Starting Soon',
            location='Venue D',
            start_time=self.now + timedelta(hours=1),  # Starts in 1 hour
            end_time=self.now + timedelta(hours=2),
            max_capacity=5
        )

    def test_register_attendee_success(self):
        """
        Ensure an attendee can register for an upcoming event.
        POST /api/events/{event_id}/register/
        """
        url = reverse('attendee-register', args=[self.upcoming_event.id])  # Name from api/urls.py
        data = {
            'name': 'Alice Wonderland',
            'email': 'alice@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.upcoming_event.attendees.count(), 1)
        self.assertTrue(self.upcoming_event.attendees.filter(email='alice@example.com').exists())

    def test_register_attendee_non_existent_event(self):
        """
        Ensure registration fails for a non-existent event.
        POST /api/events/{event_id}/register/
        """
        url = reverse('attendee-register', args=[9999])  # Non-existent ID
        data = {
            'name': 'Ghost Person',
            'email': 'ghost@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_register_attendee_event_full(self):
        """
        Ensure registration fails if the event max_capacity is reached.
        POST /api/events/{event_id}/register/
        """
        url = reverse('attendee-register', args=[self.full_event.id])
        data = {
            'name': 'Over Capacity',
            'email': 'over@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'][0], "Event is full.")
        self.assertEqual(self.full_event.attendees.count(), 1)  # Still just the initial attendee

    def test_register_attendee_duplicate_email_for_same_event(self):
        """
        Ensure an attendee cannot register multiple times for the same event with the same email.
        POST /api/events/{event_id}/register/
        """
        url = reverse('attendee-register', args=[self.upcoming_event.id])
        data = {
            'name': 'Duplicate Attendee',
            'email': 'duplicate@example.com'
        }
        response1 = self.client.post(url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.upcoming_event.attendees.count(), 1)

        response2 = self.client.post(url, data, format='json')  # Second attempt with same email
        self.assertEqual(response2.status_code, status.HTTP_409_CONFLICT)  # Conflict status code
        self.assertIn('email', response2.data)
        self.assertEqual(response2.data['email'][0], "This email is already registered for this event.")
        self.assertEqual(self.upcoming_event.attendees.count(), 1)  # Still only one unique registration

    def test_register_attendee_past_event_denied(self):
        """
        Ensure an attendee cannot register for a past event.
        POST /api/events/{event_id}/register/
        """
        url = reverse('attendee-register', args=[self.past_event.id])
        data = {
            'name': 'Past Registrant',
            'email': 'past@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(response.data['non_field_errors'][0], "Cannot register for an event that has already ended.")
        self.assertEqual(self.past_event.attendees.count(), 0)

    def test_register_attendee_event_not_started_yet_allowed(self):
        """
        Ensure an attendee *can* register for an event that hasn't started yet but is in the future.
        POST /api/events/{event_id}/register/
        """
        url = reverse('attendee-register', args=[self.event_starting_soon.id])
        data = {
            'name': 'Early Bird',
            'email': 'earlybird@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.event_starting_soon.attendees.count(), 1)
        self.assertTrue(self.event_starting_soon.attendees.filter(email='earlybird@example.com').exists())

    def test_list_attendees_for_event(self):
        """
        Ensure we can list attendees for a specific event.
        GET /api/events/{event_id}/attendees/
        """
        Attendee.objects.create(event=self.upcoming_event, name='Att1', email='att1@example.com')
        Attendee.objects.create(event=self.upcoming_event, name='Att2', email='att2@example.com')

        url = reverse('attendee-list', args=[self.upcoming_event.id])  # Name from api/urls.py
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn('att1@example.com', [a['email'] for a in response.data])
        self.assertIn('att2@example.com', [a['email'] for a in response.data])

    def test_list_attendees_empty_event(self):
        """
        Ensure listing attendees for an event with no registrations returns an empty list.
        GET /api/events/{event_id}/attendees/
        """
        empty_event = Event.objects.create(
            name='Empty Event',
            location='Empty Venue',
            start_time=self.now + timedelta(days=30),
            end_time=self.now + timedelta(days=31),
            max_capacity=100
        )
        url = reverse('attendee-list', args=[empty_event.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_list_attendees_non_existent_event(self):
        """
        Ensure listing attendees for a non-existent event returns 404.
        GET /api/events/{event_id}/attendees/
        """
        url = reverse('attendee-list', args=[9999])  # Non-existent ID
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)