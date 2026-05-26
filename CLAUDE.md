# CLAUDE.md — guidance for AI agents working in this repo

This file tells Claude Code (and any AI agent) how to work in the **senechal**
repository. Read it before making changes.

## Project in one line

A *King Arthur Pendragon* tabletop-RPG campaign assistant: a **Discord bot**
(`senechal.py`, run as the Heroku `worker`) plus a **Django web app** (`web/`, run as
the `web` process via gunicorn), sharing a domain/data layer.

- Entry points: `senechal.py` (bot), `manage.py` / `web/wsgi.py` (web).
- Dispatcher: `message_handler.py`; commands are plugins under `commands/`.
- Domain/core: `character.py`, `config.py`, `utils.py`, `feast.py`.
- Data layer: `database/` (handler-per-table over `psycopg2`; parameterized queries).
- Config: `config.py` reads `config.yml` / `senechal.yml` / `feast.json`.

## Ownership — read this first

This repository is owned by **walakymas** (`github.com/walakymas/senechal`).
Work here is done by **collaborators**, not the owner. Therefore:

- **Respect the owner's code.** No wholesale reformatting, no mass renames, no
  re-ordering imports, no deleting working code without flagging it first.
- **Never commit directly to `main`.** All work happens on `collab/*` branches.
- **The PR is the review/approval gate.** Implement freely on a `collab/*` branch —
  nothing reaches `main` without the owner reviewing and merging the PR, so no
  pre-approval is needed to write code on a branch.
- **Flag behaviour-changing work loudly.** A behaviour-changing edit (anything
  observable at runtime: bot/web responses, stored data, config semantics) must be
  called out in the task file and the PR description, including any **operational
  impact** the owner must act on (new env vars, changes that could break existing
  clients). Documentation and comments are not behaviour.
- **Keep `.claude/` out of commits** (local tooling).

## The task system — how all work is organised

Work is tracked as **tasks** in `documentation/tasks/`. Each task is one branch, one
focused change, and **is not complete until its documentation is written**.

To do any non-trivial work:

1. Copy `documentation/tasks/TASK_TEMPLATE.md` to
   `documentation/tasks/<NNN>-<slug>.md` (next free number).
2. Fill in *Context*, *Scope*, *Plan*; set Status to `proposed`.
3. If the task is behaviour-changing, flag the runtime change and any **operational
   impact** in the task file (and later the PR). No pre-approval is needed — the PR is
   the review/approval gate.
4. Implement on the task's branch.
5. Complete the template's **`DOCUMENTATION — required`** checklist: add an entry to
   `documentation/CHANGELOG.md` (append-only *history*) **and** refresh `pm/STATUS.md`
   (a *snapshot of now*). Only then set Status to `done`.

See `documentation/README.md` and `documentation/tasks/README.md` for details, and
`documentation/01-code-review.md` for known issues and their `path:line` locations.
Project status, roadmap, and the decision log live in `pm/`.

## Running it locally

- **Bot:** `python senechal.py` (Procfile `worker`). Needs the Discord bot token in the
  `token` environment variable (or in `config.yml`, which is gitignored).
- **Web:** `python manage.py runserver` for development, or `gunicorn web.wsgi`
  (Procfile `web`).
- **Database:** both processes expect a PostgreSQL `DATABASE_URL` env var. The data
  layer connects on import, so it must be set before importing anything in `database/`.
- Config is read from `config.yml` (optional, gitignored), `senechal.yml`, and
  `feast.json`.

## Gotchas worth knowing

- `database/database.py` opens its PostgreSQL connection at **import time** from
  `DATABASE_URL` — importing `database/` without it set will fail.
- `senechal.py` reads `os.environ['token']` directly at startup (no graceful fallback).
- `web/views.py` uses raw `psycopg2`; the Django ORM/migrations exist but are largely
  unused — match the existing data-layer style within a file rather than mixing.
- Known issues with exact `path:line` locations are catalogued in
  `documentation/01-code-review.md`.

## Quick conventions

- The data layer already uses parameterized SQL — keep it that way; never build SQL
  with string interpolation of user input.
- Secrets (bot token, DB URL) come from environment / `config.yml` (gitignored). Do
  not print secrets to logs and do not commit them.
- Code and many UI strings are mixed English/Hungarian; match the surrounding style.
