# SmartSeason Field Monitoring System

A simple Django application for tracking crop progress across multiple fields during a growing season.

## Features

- Authentication with two roles: Admin and Field Agent
- Field creation, assignment, and editing for coordinators
- Field stage updates and notes for assigned agents
- Computed field status: Active, At Risk, or Completed
- Role-aware dashboards with summaries and recent updates

## Status Logic

The status is computed from the current stage, planting age, and update freshness.

- `Completed` when the field stage is `Harvested`
- `At Risk` when the field is older than the expected window for its stage or has not been updated for more than 14 days
- `Active` for everything else

Expected stage windows used in the assessment:

- `Planted` up to 14 days
- `Growing` up to 45 days
- `Ready` up to 75 days

Live LINK:
https://smartseason-field-monitoring-5a552aa5141f.herokuapp.com/

## Setup

1. Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

4. Load demo data:

```bash
python manage.py seed_demo
```

5. Start the server:

```bash
python manage.py runserver
```

## Demo Credentials

- Admin: `admin` / `admin123`
- Field Agent: `agent1` / `agent123`

## Assumptions

- SQLite is used for simplicity.
- Demo users are created by the `seed_demo` management command.
- Admin users can view all fields, while field agents only see assigned fields.
- The project keeps the business rules in the Django models and views rather than adding extra services.
