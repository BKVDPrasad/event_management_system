from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Event, Attendee
import datetime

class EventAndAttendeeAPITest(APITestCase):
    def setUp(self):
        # reference “now”
        self.now = timezone.now()

        # Past event (start_time <= now): cannot register, not listed
        self.past_event = Event.objects.create(
            name="Past Event",
            location="Hall Past",
            start_time=self.now - datetime.timedelta(days=1),
            end_time=self.now + datetime.timedelta(hours=2),
            max_capacity=2
        )

        # Upcoming events for listing
        self.future1 = Event.objects.create(
            name="Future 1",
            location="Hall 1",
            start_time=self.now + datetime.timedelta(days=1),
            end_time=self.now + datetime.timedelta(days=1, hours=3),
            max_capacity=2
        )
        self.future2 = Event.objects.create(
            name="Future 2",
            location="Hall 2",
            start_time=self.now + datetime.timedelta(days=2),
            end_time=self.now + datetime.timedelta(days=2, hours=4),
            max_capacity=1
        )

        # pre-register one attendee on future1
        self.att1 = Attendee.objects.create(
            event=self.future1,
            name="Alice",
            email="alice@example.com"
        )

        # URLs
        self.list_create_url = reverse('event-list-create')
        self.detail_url = lambda pk: reverse('event-detail', kwargs={'pk': pk})
        self.register_url = lambda eid: reverse('event-register-attendee', kwargs={'event_id': eid})
        self.attendees_url = lambda eid: reverse('event-attendee-list', kwargs={'event_id': eid})


    def test_list_upcoming_events(self):
        resp = self.client.get(self.list_create_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [e['name'] for e in resp.data['results']]
        # past_event excluded, future1 and future2 included
        self.assertListEqual(names, ["Future 1", "Future 2"])

    def test_create_event_valid(self):
        payload = {
            "name": "New Event",
            "location": "Hall New",
            "start_time": (self.now + datetime.timedelta(days=3)).isoformat(),
            "end_time":   (self.now + datetime.timedelta(days=3, hours=2)).isoformat(),
            "max_capacity": 10
        }
        resp = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Event.objects.filter(name="New Event").exists())

    def test_create_event_start_in_past(self):
        payload = {
            "name": "Bad Event",
            "location": "Hall Bad",
            "start_time": (self.now - datetime.timedelta(hours=1)).isoformat(),
            "end_time":   (self.now + datetime.timedelta(hours=1)).isoformat(),
            "max_capacity": 5
        }
        resp = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Start time must be in the future", str(resp.data))

    def test_create_event_end_before_start(self):
        payload = {
            "name": "Weird Event",
            "location": "Hall Weird",
            "start_time": (self.now + datetime.timedelta(days=1)).isoformat(),
            "end_time":   (self.now + datetime.timedelta(days=1)).isoformat(),
            "max_capacity": 5
        }
        resp = self.client.post(self.list_create_url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("End time must be after start time", str(resp.data))


    def test_retrieve_event(self):
        resp = self.client.get(self.detail_url(self.future1.pk))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['name'], "Future 1")

    def test_update_event(self):
        payload = {"name": "Future 1 Updated"}
        resp = self.client.patch(self.detail_url(self.future1.pk), payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.future1.refresh_from_db()
        self.assertEqual(self.future1.name, "Future 1 Updated")

    def test_delete_event(self):
        resp = self.client.delete(self.detail_url(self.future2.pk))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(pk=self.future2.pk).exists())


    def test_register_valid_attendee(self):
        url = self.register_url(self.future2.pk)
        payload = {"name": "Bob", "email": "bob@example.com"}
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Attendee.objects.filter(email="bob@example.com", event=self.future2).exists())

    def test_overbooking_prevention(self):
        # future2.max_capacity == 1, already has 0. Register one -> OK
        url = self.register_url(self.future2.pk)
        self.client.post(url, {"name": "Bob", "email": "bob@example.com"}, format='json')
        # second registration should fail
        resp2 = self.client.post(url, {"name": "Charlie", "email": "charlie@example.com"}, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Event is full", str(resp2.data))

    def test_duplicate_registration(self):
        url = self.register_url(self.future1.pk)
        # Alice already registered in setUp
        resp = self.client.post(url, {"name": "Alice", "email": "alice@example.com"}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("already registered", str(resp.data))

    def test_cannot_register_past_event(self):
        url = self.register_url(self.past_event.pk)
        payload = {"name": "Dave", "email": "dave@example.com"}
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already started or ended", str(resp.data))

    def test_register_invalid_event(self):
        url = self.register_url(9999)
        resp = self.client.post(url, {"name": "Eve", "email": "eve@example.com"}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_list_attendees(self):
        # only Alice on future1
        url = self.attendees_url(self.future1.pk)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        emails = [a['email'] for a in resp.data['results']]
        self.assertListEqual(emails, ["alice@example.com"])

    def test_list_attendees_empty(self):
        url = self.attendees_url(self.future2.pk)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['results'], [])

    def test_list_attendees_invalid_event(self):
        url = self.attendees_url(9999)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
