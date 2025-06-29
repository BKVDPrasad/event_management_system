import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import Event, Attendee

class Command(BaseCommand):
    help = 'Loads sample event and attendee data from events.csv and attendees.csv'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("--- Starting Data Load ---"))

        # Define CSV file paths relative to where manage.py is run
        events_csv_path = 'events.csv'
        attendees_csv_path = 'attendees.csv'

        # --- Clear existing data (optional, for clean re-runs) ---
        try:
            with transaction.atomic(): # Ensure atomicity for clearing data too
                Attendee.objects.all().delete()
                Event.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing Event and Attendee data cleared."))
        except Exception as e:
            raise CommandError(f"Error clearing existing data: {e}")

        # --- Load Events ---
        self.stdout.write("\nLoading Events...")
        event_mapping = {} # To store name -> id mapping for attendees lookup
        try:
            with open(events_csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        # Parse dates, handling 'Z' for UTC
                        start_time_str = row['start_time'].replace('Z', '+00:00')
                        end_time_str = row['end_time'].replace('Z', '+00:00')

                        event = Event.objects.create(
                            name=row['name'],
                            location=row['location'],
                            start_time=datetime.fromisoformat(start_time_str),
                            end_time=datetime.fromisoformat(end_time_str),
                            max_capacity=int(row['max_capacity'])
                        )
                        event_mapping[row['name']] = event.id # Store for attendee lookup
                        self.stdout.write(self.style.SUCCESS(f"Created Event: {event.name} (ID: {event.id})"))
                    except ValueError as ve:
                        self.stdout.write(self.style.ERROR(f"Data conversion error for event {row.get('name', 'N/A')}: {ve}. Row: {row}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error loading event {row.get('name', 'N/A')}: {e}. Row: {row}"))
        except FileNotFoundError:
            raise CommandError(f"{events_csv_path} not found. Please ensure it's in the project root.")
        except Exception as e:
            raise CommandError(f"An unexpected error occurred during event loading: {e}")

        # --- Load Attendees ---
        self.stdout.write("\nLoading Attendees...")
        try:
            with open(attendees_csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        # Use event_id from CSV directly IF you're sure they match already loaded IDs
                        # OR, better: if you used event_name in attendees.csv:
                        # event_name_from_csv = row['event_name']
                        # event_obj = Event.objects.get(name=event_name_from_csv)

                        # For the provided CSV, we rely on event_id, so ensure these match
                        event_id = int(row['event_id'])
                        event_obj = Event.objects.get(id=event_id)

                        attendee = Attendee.objects.create(
                            event=event_obj,
                            name=row['name'],
                            email=row['email']
                        )
                        self.stdout.write(self.style.SUCCESS(f"Registered Attendee: {attendee.name} for {event_obj.name}"))
                    except Event.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Warning: Event with ID {row['event_id']} not found for attendee {row['name']}. Skipping."))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error loading attendee {row.get('name', 'N/A')}: {e}. Row: {row}"))
        except FileNotFoundError:
            raise CommandError(f"{attendees_csv_path} not found. Please ensure it's in the project root.")
        except Exception as e:
            raise CommandError(f"An unexpected error occurred during attendee loading: {e}")

        self.stdout.write(self.style.SUCCESS("\n--- Data Load Complete ---"))