# Task 007: Remove Django from the codebase and the database

## Metadata
- **ID:** 007
- **Status:** `done`
- **Type:** `behaviour-changing`
- **Branch:** `collab/single-process`
- **Created:** 2026-10-03
- **Reviewed via PR:** <link once opened>
- **Operational impact:** the Django tables are dropped from the database (see below), so
  the Django admin and any `manage.py` command no longer work. **The owner must drop the
  same tables on the Heroku database** (this task only did it on the local Docker DB) and
  remove `DJANGO_SECRET_KEY` / `DJANGO_DEBUG` config vars if set. Static files moved from
  `web/static/` to `static/` (same `/static/` URL).

## Context
- **Problem / motivation:** Task 005 replaced Django with an aiohttp API; Django code,
  dependencies and tables were left behind unused.
- **Definition of done:** no Django code, dependency or table remains.

## Scope
- **In scope:** delete `web/` and `manage.py`; move `web/static/` to `static/`; drop
  Django packages from `requirements.txt`; drop Django tables locally; refresh docs.
- **Out of scope:** `databasechangeloglock` (Liquibase leftover, not Django); the
  historical `documentation/01-code-review.md`, which still describes the Django app.

## Plan
- [x] `pg_dump` backup of the local DB.
- [x] `DROP TABLE` of the 10 Django tables: `django_admin_log`, `auth_user_user_permissions`,
  `auth_user_groups`, `auth_group_permissions`, `auth_user`, `auth_group`,
  `auth_permission`, `django_content_type`, `django_session`, `django_migrations`.
- [x] `git mv web/static static`; `git rm web manage.py`; `api/app.py` serves `static/`.
- [x] Remove `django`, `django-cors-headers`, `gunicorn`, `whitenoise`, `dj-database-url`.
- [x] Update `CLAUDE.md`, CHANGELOG, STATUS.

## Files touched
| File | Change | Rationale |
|------|--------|-----------|
| `web/*`, `manage.py` | removed | unused since Task 005 |
| `web/static/` -> `static/` | moved | still served by `api/app.py` |
| `api/app.py`, `api/compat.py` | static path, comments | no `web/` references |
| `requirements.txt` | 5 packages removed | Django-only |
| `CLAUDE.md` | updated | reflects the new stack |

## DOCUMENTATION — required
- [x] `documentation/CHANGELOG.md` entry added
- [x] `pm/STATUS.md` refreshed
