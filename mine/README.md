# Mini Event Management System API

This project provides a simple API for managing events and attendee registrations. It's built with Python, Django, and Django REST Framework, focusing on clean architecture principles, scalability, and data integrity.

Table of Contents
Features

Tech Stack

Prerequisites

Installation & Setup

Project Structure

Running the App

API Endpoints

Testing

Swagger / OpenAPI Docs

Load Sample Data

Contributing

License

Features
Create, list, update, and delete events

Register attendees with capacity & duplicate checks

List event attendees with pagination

Read-only fields: current attendee count & available capacity

Prevent registrations for past/started events

Auto-generated Swagger (OpenAPI 3) documentation

Tech Stack
Python 3.7+

Django 3.2

Django REST Framework

drf-spectacular (OpenAPI 3 docs)

SQLite (default)

Prerequisites
Python 3.7

pip

(Optional) virtualenv or venv

Installation & Setup
Clone the repo

bash
git clone https://github.com/yourorg/event_management_system.git
cd event_management_system
Create & activate a virtual environment

bash
python3 -m venv venv
source venv/bin/activate
Install dependencies

bash
pip install -r requirements.txt
Run migrations

bash
python manage.py migrate
(Optional) Create a superuser to access the admin

bash
python manage.py createsuperuser
Project Structure
event_management_system/
├── manage.py
├── event_management_system/         # Project settings, URLs, ASGI/WGI
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                  # Global settings & drf-spectacular config
│   ├── urls.py                      # Root URL routes (incl. schema & docs)
│   └── wsgi.py
├── core/                            # Core app: models & business logic
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py                     # Admin site registration
│   ├── apps.py
│   ├── models.py                    # Event & Attendee models
│   ├── tests.py                     # Model/unit tests
│   └── management/                  # Custom manage.py commands
│       └── commands/
│           └── load_sample_data.py  # Load CSV fixtures
├── api/                             # API app: serializers, views, endpoints
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── serializers.py               # DRF serializers
│   ├── tests.py                     # API endpoint tests
│   ├── urls.py                      # API-specific URL patterns
│   └── views.py                     # DRF view classes
├── venv/                            # Virtual environment
├── .gitignore
├── README.md                        # This file
├── requirements.txt
├── events.csv                       # Sample event data
├── attendees.csv                    # Sample attendee data
└── db.sqlite3                       # Default local SQLite DB
Running the App
bash
# Start development server
python manage.py runserver

# Visit
#  - API root: http://localhost:8000/
#  - Swagger UI: http://localhost:8000/api/docs/swagger/
#  - ReDoc UI:   http://localhost:8000/api/docs/redoc/
API Endpoints
Method	Endpoint	Description
GET	/events/	List upcoming events (paginated)
POST	/events/	Create a new event
GET	/events/{pk}/	Retrieve event details
PATCH	/events/{pk}/	Partially update an event
DELETE	/events/{pk}/	Delete an event
POST	/events/{event_id}/register/	Register an attendee
GET	/events/{event_id}/attendees/	List attendees of an event (paginated)
Refer to the Swagger UI for full request/response schemas and examples.

Testing
bash
# Run all unit & API tests
python manage.py test

# To use a file-based test DB (inspect with SQLite tools):

# Then:
Swagger / OpenAPI Docs
Once the server is running, view:

JSON/FYAML schema: GET /api/schema/

Swagger UI: GET /api/docs/swagger/

ReDoc: GET /api/docs/redoc/

Load Sample Data
We include CSV fixtures for quick demos:

bash
python manage.py load_sample_data --events=events.csv --attendees=attendees.csv
This command will bulk-create Event and Attendee records based on the provided CSVs.

Contributing
Fork the repo

Create a feature branch

Write tests & implement your feature

Submit a pull request

Please adhere to PEP8 and add tests for new functionality.

License
© 2025  BKVDPrasad
