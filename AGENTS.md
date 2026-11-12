# AGENTS.md — Instructions for AI Agents

This file guides any AI coding agent working in this repository.
The full project specification is `docs/PROJECT_SPEC.pdf` (source of truth).
Read it before writing code.

## Project Overview

IT Helpdesk Ticketing System — a web-based information system for a university
final project. Reporters create tickets, Admins assign them to Technicians,
Technicians work on them, and every change is tracked with status history,
SLA due dates, and overdue markers.

## Tech Stack (fixed)

- Python + Django (server-rendered templates)
- SQLite (Django default)
- Bootstrap 5 served locally from `static/` (no CDN at runtime)
- Package manager: `uv` (`uv add <pkg>`, `uv run <cmd>`)
- Settings via `django-environ`, images via `Pillow`

## Hard Rules

1. Do not invent features. If it is not in the spec's Scope section, ask first.
2. Ask before: adding a dependency, changing the data model, changing the
   stack, or deviating from the spec.
3. Work in small steps: one milestone at a time, finish it, run the tests,
   then stop and report.
4. Keep code simple and readable. The owner must be able to explain every
   line in a written report. No over-engineering.
5. Do not touch unrelated code. No drive-by refactors.
6. Never fabricate results. Test results and timings must come from real runs.
7. If the spec and a user request conflict, stop and ask the owner.

## Coding Rules

- Business logic lives in `tickets/services.py` (transitions, SLA, history,
  notifications). Views stay thin; templates contain no business rules.
- Function-based views preferred. Check permissions at the start of every
  view (server-side, via a shared role-check decorator/mixin).
- Custom user model `accounts.User` (extends `AbstractUser`, adds `role`)
  must exist before the first migration. `AUTH_USER_MODEL` is set first.
- Follow PEP 8. Use `select_related`/`prefetch_related` on list pages.
- All state-changing actions use POST with `{% csrf_token %}`.
- No secrets in Git. `db.sqlite3`, `media/`, and `.env` stay git-ignored.
- Never use `mark_safe`/`|safe` on user-provided content.
- Never delete tickets/comments/history through the UI; deactivate users
  instead of deleting them.

## Testing

- Django `TestCase`; run everything with `uv run python manage.py test`.
- Minimum test cases are defined in the spec (T-01 … T-18).
- Log real results in `docs/TEST_LOG.md`. Never write unobserved results.

## Workflow

- Milestone order: setup → auth/roles → models/admin → tickets → assign &
  status → comments → SLA → notifications → search/reports → seed & polish.
- One feature per Git commit with a clear conventional message,
  e.g. `feat(tickets): add assign ticket view`.
- After each task, report: what changed, which files, how to run it, which
  tests were added, and anything the owner must decide.

## Command Reference

```bash
uv run python manage.py runserver      # dev server at http://127.0.0.1:8000
uv run python manage.py test           # run all tests
uv run python manage.py makemigrations # create migrations (commit them)
uv run python manage.py migrate        # apply migrations
uv run python manage.py seed_demo      # seed demo data (idempotent)
```
