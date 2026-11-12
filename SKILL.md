# SKILL.md — IT Helpdesk Ticketing System

## When to use this skill

Any task related to this repository: setting up the Django project,
implementing features from the spec, fixing bugs, writing tests, or
preparing material for the final project report.

## Project summary

A web-based IT Helpdesk Ticketing System for a university final project:

- **Reporter** creates tickets for IT problems.
- **Admin** assigns them to technicians and views dashboards/reports.
- **Technician** works on assigned tickets and updates status.
- Every change is recorded (status history), tickets have SLA due dates,
  and overdue tickets are clearly marked.

## Key domain rules

- Ticket status flow: `OPEN → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED`.
- Transitions are strict and role-based; invalid transitions are rejected
  with a clear error.
- `due_at = created_at + priority.target_hours` (High 4h, Medium 48h, Low 120h).
- Overdue = not RESOLVED/CLOSED and now > due_at (computed, never stored).
- A CLOSED ticket is read-only: no status change, no new comments.
- Notifications are in-app only: rows in the `Notification` table created
  in the service layer.

## Essential knowledge

- Source of truth: `docs/PROJECT_SPEC.pdf` — read the relevant section
  before every task.
- Working rules for agents: `AGENTS.md`.
- Tech stack: Python, Django (server-rendered templates), SQLite,
  Bootstrap 5 (local, offline), package manager `uv`, django-environ,
  Pillow.
- Business logic belongs in `tickets/services.py`; views stay thin.
- Permissions are enforced server-side in every view (role decorator),
  never by hiding UI elements only.
- Anonymous or unauthorized access to another user's ticket returns 404.
- All state-changing requests are POST with CSRF protection.

## Common commands

```bash
uv run python manage.py runserver       # dev server
uv run python manage.py test            # full test suite (T-01…T-18)
uv run python manage.py makemigrations  # create migrations
uv run python manage.py migrate         # apply migrations
uv run python manage.py seed_demo       # idempotent demo data
```

## Guardrails

- Do not add features outside the spec's scope; ask the owner first.
- Ask before adding dependencies or changing the data model.
- One milestone/feature at a time; run tests before reporting done.
- Commit style: conventional messages, one feature per commit, English.
