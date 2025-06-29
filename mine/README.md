# Mini Event Management System API

This project provides a simple API for managing events and attendee registrations. It's built with Python, Django, and Django REST Framework, focusing on clean architecture principles, scalability, and data integrity.

## Table of Contents

* [Features](#features)
* [Assumptions](#assumptions)
* [Project Structure](#project-structure)
* [Setup Instructions](#setup-instructions)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
    * [Running Migrations](#running-migrations)
    * [Creating a Superuser](#creating-a-superuser)
    * [Loading Sample Data](#loading-sample-data)
    * [Running the Development Server](#running-the-development-server)
* [API Endpoints](#api-endpoints)
    * [Base URL](#base-url)
    * [Sample API Requests (cURL)](#sample-api-requests-curl)
    * [Sample API Requests (Postman)](#sample-api-requests-postman)
* [Error Handling](#error-handling)
* [Future Enhancements](#future-enhancements)
* [Contributing](#contributing)
* [License](#license)


## Features

* Create new events with details like name, location, start/end times, and max capacity.
* List all upcoming events.
* Register attendees for a specific event.
* Prevent event overbooking based on `max_capacity`.
* Prevent duplicate registrations for the same email on the same event.
* Retrieve a list of all registered attendees for a given event.

## Assumptions

* **Python 3.8+:** The project is developed and tested with Python 3.8 or newer.
* **Database:** Defaults to SQLite for simplicity in development. For production, a more robust database like PostgreSQL is recommended.
* **Timezones:** Dates and times are handled with timezone awareness. API requests and responses for `DateTimeField` should use ISO 8601 format with UTC offset (e.g., `YYYY-MM-DDTHH:MM:SSZ` for UTC). Django stores `DateTimeField` values in UTC by default when `USE_TZ = True` (which is the default in new Django projects).

## Project Structure

event_management_system/
├── manage.py
├── event_management_system/  # Root Django project directory (settings, urls)
│   ├── init.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                     # Django app: Core models and business logic
│   ├── migrations/
│   │   └── init.py
│   ├── init.py
│   ├── admin.py              # Model registration for Django Admin
│   ├── apps.py
│   ├── models.py             # Event and Attendee models
│   ├── tests.py              # Unit tests for models/core logic
│   └── management/           # Custom management commands
│       └── init.py
│       └── commands/
│           ├── init.py
│           └── load_sample_data.py # Custom command to load CSV data
├── api/                      # Django app: API serializers, views, and specific API URLs
│   ├── migrations/
│   │   └── init.py
│   ├── init.py
│   ├── admin.py
│   ├── apps.py
│   ├── serializers.py        # DRF serializers
│   ├── tests.py              # API endpoint tests
│   ├── urls.py               # API-specific URL patterns
│   └── views.py              # DRF API views
├── venv/                     # Python virtual environment
├── .gitignore                # Git ignore file
├── README.md                 # Project README
├── events.csv                # Sample data for events (for load_sample_data command)
├── attendees.csv             # Sample data for attendees (for load_sample_data command)
└── db.sqlite3                # Default SQLite database file


## Setup Instructions

### Prerequisites

* Python 3.8+
* `pip` (Python package installer)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url> # Replace with your actual repository URL if hosted
    cd event-management-system
    ```

2.  **Create a virtual environment:**

    It's highly recommended to use a virtual environment to manage dependencies.

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**

    * **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    * **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install dependencies:**

    ```bash
    pip install Django djangorestframework
    ```

5.  **Create Django Apps:**
    (If not already created, ensure you are in the directory containing `manage.py`)
    ```bash
    python manage.py startapp core
    python manage.py startapp api
    ```

6.  **Update `event_management_system/settings.py`:**
    Add your new apps and `rest_framework` to `INSTALLED_APPS`.

    ```python
    # event_management_system/event_management_system/settings.py

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        # My custom apps
        'core',
        'api',
        # Third-party apps
        'rest_framework',
    ]
    ```

### Running Migrations

After installing dependencies and defining your models, you need to create the necessary database tables.

```bash
python manage.py makemigrations core api
python manage.py migrate
Creating a Superuser
This is needed to access the Django administration panel for manual data entry or inspection.

Bash

python manage.py createsuperuser
Follow the prompts to set up your username, email, and password.

Loading Sample Data
To quickly populate your database with sample events and attendees for testing your API, you can use the provided custom management command.

Ensure events.csv and attendees.csv are in your project root.
(You should have these from previous steps).

Ensure the custom command file is in the correct place:
core/management/commands/load_sample_data.py
And that core/management/__init__.py and core/management/commands/__init__.py also exist.

Run the command:

Bash

python manage.py load_sample_data
This command will clear existing data and then load the sample events and attendees.

Running the Development Server
Bash

python manage.py runserver
The API will now be running at http://127.0.0.1:8000/. You can also access the Django Admin at http://127.0.0.1:8000/admin/ with your superuser credentials.

API Endpoints
Base URL
All API requests should be prefixed with: http://127.0.0.1:8000/api/

Sample API Requests (cURL)
Below are examples using cURL. You can easily adapt these for Postman or Insomnia.

1. Create a New Event (POST /api/events/)
Creates a new event. start_time must be in the future. Times should be in ISO 8601 UTC format.

Endpoint: POST /api/events/

Headers: Content-Type: application/json

Body:

JSON

{
    "name": "Global AI Summit 2026",
    "location": "Bengaluru International Exhibition Centre",
    "start_time": "2026-03-15T09:00:00Z",
    "end_time": "2026-03-17T17:00:00Z",
    "max_capacity": 750
}
cURL Command:

Bash

curl -X POST \
  [http://127.0.0.1:8000/api/events/](http://127.0.0.1:8000/api/events/) \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Global AI Summit 2026",
    "location": "Bengaluru International Exhibition Centre",
    "start_time": "2026-03-15T09:00:00Z",
    "end_time": "2026-03-17T17:00:00Z",
    "max_capacity": 750
  }'
Note: Adjust start_time and end_time to be in the future relative to your current time.

2. List All Upcoming Events (GET /api/events/)
Retrieves a list of all events whose start_time is in the future.

Endpoint: GET /api/events/

cURL Command:

Bash

curl -X GET \
  [http://127.0.0.1:8000/api/events/](http://127.0.0.1:8000/api/events/)
3. Get Event Details (GET /api/events/{event_id}/)
Retrieves details for a specific event by its ID.

Endpoint: GET /api/events/{event_id}/

Example (replace 1 with an actual event ID from your loaded data or a created one):

Bash

curl -X GET \
  [http://127.0.0.1:8000/api/events/1/](http://127.0.0.1:8000/api/events/1/)
4. Register an Attendee for an Event (POST /api/events/{event_id}/register/)
Registers an attendee for the specified event.

Endpoint: POST /api/events/{event_id}/register/

Headers: Content-Type: application/json

Body:

JSON

{
    "name": "Bob The Builder",
    "email": "bob@example.com"
}
cURL Command (replace 1 with an actual event ID):

Bash

curl -X POST \
  [http://127.0.0.1:8000/api/events/1/register/](http://127.0.0.1:8000/api/events/1/register/) \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Bob The Builder",
    "email": "bob@example.com"
  }'
5. Get All Registered Attendees for an Event (GET /api/events/{event_id}/attendees/)
Retrieves a list of all attendees registered for a specific event.

Endpoint: GET /api/events/{event_id}/attendees/

Example (replace 1 with an actual event ID):

Bash

curl -X GET \
  [http://127.0.0.1:8000/api/events/1/attendees/](http://127.0.0.1:8000/api/events/1/attendees/)
Sample API Requests (Postman)
For Postman, you'd create new requests and configure them as follows:

General Postman Setup:
Open Postman.
Click + to create a new request tab.
Set the HTTP Method (GET, POST, etc.) from the dropdown.
Enter the Request URL.
For POST requests, select the Body tab, then choose raw and select JSON from the dropdown. Paste your JSON body there.
For requests requiring headers (like Content-Type), go to the Headers tab and add them.
1. Create a New Event (POST)
Method: POST
URL: http://127.0.0.1:8000/api/events/
Headers:
Content-Type: application/json
Body (raw - JSON):
JSON

{
    "name": "Global AI Summit 2026",
    "location": "Bengaluru International Exhibition Centre",
    "start_time": "2026-03-15T09:00:00Z",
    "end_time": "2026-03-17T17:00:00Z",
    "max_capacity": 750
}
2. List All Upcoming Events (GET)
Method: GET
URL: http://127.0.0.1:8000/api/events/
Headers: (None specific needed, Postman adds defaults)
Body: (None)
3. Get Event Details (GET)
Method: GET
URL: http://127.0.0.1:8000/api/events/1/ (Replace 1 with an actual event ID)
Headers: (None specific needed)
Body: (None)
4. Register an Attendee for an Event (POST)
Method: POST
URL: http://127.0.0.1:8000/api/events/1/register/ (Replace 1 with an actual event ID)
Headers:
Content-Type: application/json
Body (raw - JSON):
JSON

{
    "name": "Bob The Builder",
    "email": "bob@example.com"
}
5. Get All Registered Attendees for an Event (GET)
Method: GET
URL: http://127.0.0.1:8000/api/events/1/attendees/ (Replace 1 with an actual event ID)
Headers: (None specific needed)
Body: (None)









### Running Migrations

After installing dependencies and defining your models, you need to create the necessary database tables.

```bash
python manage.py makemigrations core api
python manage.py migrate



