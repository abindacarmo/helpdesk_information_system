# Architecture — IT Helpdesk Ticketing System

This document describes the architecture of the system: how it is
structured, how requests flow through it, and why the structure was chosen.
The functional specification (`docs/PROJECT_SPEC.pdf`) remains the source of
truth for *what* the system does; this document covers *how* it is built.

## 1. High-level overview

The system is a classic server-rendered Django web application:

```
Browser (Bootstrap 5 UI)
        │  HTTP
        ▼
Django development server (single laptop, localhost)
        │
        ▼
Django request/response cycle
  ├── config/urls.py → app urls.py (routing)
  ├── views.py (thin controllers, permission checks)
  ├── forms.py (validation)
  ├── services.py (business logic, the "domain layer")
  ├── models.py (ORM, data access)
        │
        ▼
SQLite database (single file)
```

There is no API layer, no frontend framework, no background worker, and no
external service. Everything runs on one laptop with the Django development
server and SQLite, opened in a desktop browser.

## 2. Project structure

```
helpdesk_information_system/
├── config/            # Django project: settings, root urls, wsgi/asgi
├── apps/              # all project apps live in one package
│   ├── accounts/      # custom User model, login/logout, role checks
│   ├── tickets/       # Ticket, comments, history, notifications
│   │   ├── models.py
│   │   ├── services.py    # business rules (transitions, SLA, notifications)
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── ...
│   └── reports/       # admin dashboard and report views
├── templates/         # base.html + app template folders
├── static/            # local Bootstrap CSS/JS, app.css
├── media/             # uploaded ticket images (git-ignored)
├── docs/              # PROJECT_SPEC.pdf, architecture.md, TEST_LOG.md
└── manage.py
```

### Why this structure

- `accounts`, `tickets`, and `reports` are separate apps so each
  responsibility (identity, ticket domain, reporting) has a clear home.
  They are grouped under one `apps/` package (an owner decision, slightly
  deviating from the spec's Section 11.1 root layout); each app config uses
  `name = "apps.<app>"` with a stable `label` (`accounts`, `tickets`,
  `reports`), so model and URL references stay as in the spec.
- `config` only contains project wiring (settings, root URLconf).
- Templates and static files live at project level so Bootstrap is served
  locally (the system must work offline).

## 3. Django apps and responsibilities

| App         | Responsibility                                                            |
| ----------- | ------------------------------------------------------------------------- |
| `apps.accounts` | Custom user model (`User` with `role`), authentication views, shared role-check decorators used by other apps |
| `apps.tickets`  | Ticket CRUD, assignment, status transitions, comments, status history, notifications, SLA logic, seed command |
| `apps.reports`  | Admin dashboard (status counts, overdue, unassigned) and reports (resolution time, per category, per technician) |
| `config`    | Settings, root URL routing, WSGI/ASGI entry points                          |

## 4. Layering and the service layer

The system follows a deliberate layering rule:

```
Template  (presentation only, no business rules)
   ▲
View      (thin: authenticate, check role permission, call service, render)
   ▲
Service   (all business logic: transitions, SLA, history, notifications)
   ▲
Model     (data persistence via the Django ORM only)
```

`apps/tickets/services.py` is the single home for business rules:

- Ticket creation (code generation, `due_at` calculation, initial history row)
- Assignment and reassignment (including the IN_PROGRESS → ASSIGNED fallback)
- Status transitions (enforcing the allowed-transition table)
- Writing `TicketStatusHistory` rows for every change
- Creating `Notification` rows

**Why:** views stay thin and readable, the owner can explain every rule in one
place, and unit tests can test the rules directly against the service
functions without HTTP overhead.

## 5. Data model

Main entities and relationships:

```
User (role: ADMIN | TECHNICIAN | REPORTER)
  │ 1──N Ticket (as reporter)
  │ 1──N Ticket (as assignee)
  │ 1──N TicketComment, Notification
  ▼
Ticket
  ├── FK → Category (PROTECT)
  ├── FK → Priority (PROTECT, target_hours drives SLA)
  ├── 1──N TicketComment
  ├── 1──N TicketStatusHistory
  └── 1──N Notification
```

Key design decisions:

- **`PROTECT` on category/priority/reporter:** master data and people must
  not silently disappear from tickets; nothing is deleted through the UI.
- **`SET_NULL` on assignee:** a deactivated technician does not break old
  tickets.
- **`TicketStatusHistory`:** every status change (including creation and
  reassignment) writes an audit row — this is the "who changed what" record.
- **`due_at` stored once at creation:** SLA target is frozen even if the
  priority's target hours change later; "overdue" is always *computed*, never
  stored.
- **Code `HD-0001`:** human-readable unique ticket code, generated
  sequentially at creation.

## 6. Request flow for a state-changing action

Example: Admin assigns a ticket (`POST /tickets/<code>/assign/`).

```
1.  config/urls.py → apps/tickets/urls.py matches the route
2.  View: login required, role checked (Admin only) → otherwise 403/redirect
3.  View: loads Ticket with select_related; object-level access check → 404
4.  Form validates the chosen technician
5.  View calls services.assign_ticket(ticket, technician, admin_user)
6.  Service: validates transition (OPEN/ASSIGNED/IN_PROGRESS only),
      sets assignee (status back to ASSIGNED if it was IN_PROGRESS),
      writes TicketStatusHistory ("Reassigned to Technician X"),
      creates a Notification row for the technician
7.  View: success message via Django messages, redirect to ticket detail
8.  Template renders detail page with new status, history, and comment feed
```

The same pattern applies to status changes, comments, and ticket creation.
Every state-changing route accepts POST only, with `{% csrf_token %}` in the
form.

## 7. Permission model

- Authentication is required on every page except `/login/`.
- Role checks are enforced server-side at the start of every view using one
  shared decorator/mixin in `apps.accounts` — hiding buttons in templates is not
  security.
- Object-level scoping: a Reporter may only open tickets they created, a
  Technician only tickets assigned to them; unauthorized object access
  returns **404** (never 403/200, to avoid revealing that the ticket exists).
- Django Admin (`/admin/`) is restricted to Admin users (`is_staff=True`
  only for Admin).

## 8. Static files and templates

- Bootstrap 5 CSS/JS is stored under `static/` — no CDN links, so the
  system works fully offline.
- All templates extend `templates/base.html`, which provides the navbar,
  flash messages, and the unread-notification badge.
- Small vanilla JS snippets are allowed only where necessary (no build
  step, no frontend framework).

## 9. Configuration

- `django-environ` reads settings from `.env` (git-ignored): `DEBUG`,
  `SECRET_KEY`, etc.
- `AUTH_USER_MODEL = "accounts.User"` is set before the first migration.
- `TIME_ZONE = "Asia/Dili"`, `USE_TZ = True`.
- `ALLOWED_HOSTS` limited to local addresses; the dev server runs at
  `http://127.0.0.1:8000`.
- `media/` stores uploaded ticket images (jpg/png, max 2 MB) with generated
  filenames; the folder is git-ignored.

## 10. Testing architecture

- Tests use Django `TestCase` and live in each app's `tests/` package.
- The spec's minimum cases (T-01 … T-18) map to the layers:
  - HTTP-level tests (login, redirects, 404/403) exercise views.
  - Domain tests (transitions, SLA, history, notifications) call
    `services.py` functions directly.
- All results are logged in `docs/TEST_LOG.md` from real runs only.
