# Test Log

Real test results only (per spec Section 13.2). Never write results that were
not actually observed. Manual commands: `uv run python manage.py test`.

## M1 — Auth & roles

**Date:** 2026-11-13
**Branch:** `feat/m1-auth-roles` (merged via PR #2)
**Command:** `uv run python manage.py test`
**Result:** `Ran 3 tests in 1.685s` — **OK (3 passed, 0 failed)**

| ID  | Test                                                  | Result | Notes                                                        |
| --- | ----------------------------------------------------- | ------ | ------------------------------------------------------------ |
| T-01 | Login with valid credentials redirects to dashboard | Pass   | Redirects to `dashboard`                                     |
| T-02 | Login with wrong password shows error               | Pass   | Error message shown, no session established                  |
| T-03 | Anonymous user opens `/tickets/`                    | Pass   | 302 redirect to `/login/?next=/tickets/`; view is a stub (real list in M3) |
