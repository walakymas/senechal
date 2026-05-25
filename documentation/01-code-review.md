# Code Review — senechal

**Date:** 2026-05-25
**Reviewer:** collaborator (read-only analysis; no code was modified)
**Branch:** `collab/code-review-and-docs`

This document is analysis only. It records the state of the codebase as found, so
that any later changes can be justified against concrete findings. File references
use `path:line`.

---

## 1. What the project is

**Senechal** is a campaign-management assistant for the *King Arthur Pendragon*
tabletop RPG, used by a Hungarian-speaking group (UI strings such as "próba",
"Eredmény", "Lovak", "pipák"). It is a **hybrid application**:

- A **Discord bot** (`senechal.py`) built on `discord.py` — `!`-prefixed commands,
  inline dice parsing (`2d6+1`), and a 👀-reaction image archiver.
- A **Django web app** (`web/`) served by gunicorn — a JSON API plus PDF
  character-sheet export, consumed by an external front-end (CodePen / duckdns host).
- A **shared core**: `character.py` (domain model), `config.py` (YAML/JSON config),
  `utils.py` (dice/checks/embeds), `feast.py` (card-deck feast mechanic).

Scale: ~63 Python files, ~4,370 tracked lines of code. Runtime: Python 3.9.5 on
Heroku (`Procfile` defines a `worker` and a `web` process).

---

## 2. Structure

```
senechal.py            worker entrypoint (bot)
message_handler.py     command dispatcher
manage.py              Django entrypoint
config.py character.py utils.py feast.py    shared core
commands/   25 command classes + base_command.py   <- plugin pattern
database/   14 table handlers + database.py (connection + migrations)
events/     base_event.py + example (scaffolding)
web/        settings.py urls.py views.py wsgi/asgi + static/
pdf/        sheet.py (FPDF2 sheet generator)
tests/      deck_test.py    pdf/test_sheet.py
```

**Strongest part — the command plugin system.** Command classes subclass
`BaseCommand`, and `message_handler.py:18` auto-registers every subclass plus its
aliases. Adding a feature is a matter of dropping one file into `commands/`.

**Data layer.** A thin handler-per-table pattern over `psycopg2`. Notably it **uses
parameterized queries** (e.g. `database/markstable.py:10`), so the SQL layer itself
is injection-safe.

---

## 3. Code-quality findings

### 3.1 Duplicated lines (merge / find-replace artifacts) — some are real bugs
- `utils.py:451-452`, `utils.py:455-456`, `utils.py:464-465` — the same embed field
  is added twice, so it renders doubled.
- `utils.py:444-445` — `dice(6)` is rolled twice and the first result discarded.
- Harmless echoes: `utils.py:298-299`, `utils.py:304-305`,
  `database/database.py:11-12`, `database/database.py:73-74`.

### 3.2 Dead / broken code
- `config.py:81` — `Config.characters` is never defined, so `pcs`/`npcs` raise
  `AttributeError` if called.
- `commands/base_command.py:32` — typo `message.channelsend` (should be
  `message.channel.send`); the fallback help path would crash.
- `web/views.py:339` — `cleanupTokens` SQL is broken: missing `WHERE`, and `INTERVALL`
  is misspelled. The endpoint always errors.
- `utils.py:120-123` — a duplicated, unreachable `elif` branch in `get_me`.

### 3.3 Debug output and secret leakage to logs
- The **bot token is printed to stdout**: `senechal.py:17`, `config.py:60`.
- **DB credentials are printed**: `web/settings.py:137`, `database/database.py:10`.
- `print()` debugging is scattered widely, including player and token records.

### 3.4 Other
- Import-time DB connection in `database/database.py:8-20` crashes if `DATABASE_URL`
  is unset; there is also a vestigial unused SQLite handle (`database.py:8`).
- Hand-rolled migration stepper (`database.py`) with skipped version numbers
  (`v=1` then `v=3`, `v=4` then `v=7`) — fragile but functional.
- Builtins shadowed (`list`, `type`, `id`, `sum`) throughout `web/views.py`.
- No type hints; mixed-language identifiers/strings; `character.py` is the cleanest
  module.

---

## 4. Security findings (the application is internet-facing)

| Issue | Location |
|-------|----------|
| `DEBUG = True` in production | `web/settings.py:28` |
| Hardcoded `SECRET_KEY` committed to git | `web/settings.py:25` |
| CSRF middleware disabled | `web/settings.py:55` |
| Authorization is a stub — `hasRight()` returns `token != 'null'`, never checks the DB | `web/views.py:215` |
| Mutating endpoints with no auth (`modify`, `newchar`, `mark`, `event`, `updatePlayer`, `cleanupTokens`, `adminList`, `token`) | `web/urls.py:22-50` |
| `senechal.db` (SQLite containing Discord IDs) committed to the repo | tracked in git |

Net effect: anyone who knows the URL can read player data and create/modify/delete
characters and player records. CSRF-off + no-auth + stub-auth compound one another.

---

## 5. Testing & operations
- **Effectively no automated tests.** `tests/deck_test.py` has one method that is not
  prefixed `test_` (so `unittest` skips it) and contains no assertions.
- **No CI** configuration, no linter/formatter config.
- **Unpinned dependencies** (`requirements.txt` has no versions) → non-reproducible
  builds. **Django 3.1 and Python 3.9.5 are both end-of-life** (no security patches).

---

## 6. SWOT

**Strengths**
- Clean, extensible command-plugin architecture; clear bot / web / data / domain
  separation.
- A genuinely working, domain-rich tool (sheets, trait/skill checks, marks, glory,
  feasts, PDF export, web companion) in real use.
- Parameterized SQL in the data layer; coherent domain model with sane defaults.

**Weaknesses**
- Serious security gaps (DEBUG, secret key, CSRF off, no/stub auth).
- Hygiene debt: duplicated lines, dead code, secret-leaking debug prints, shadowed
  builtins, no types.
- Near-zero tests, no CI, no lint/format gating.
- EOL runtime/framework, unpinned deps; fragile import-time bootstrapping.

**Opportunities**
- A small, contained security pass (env-based secret key, `DEBUG=False`, re-enable
  CSRF, real token validation) removes the highest-severity risks with a tiny diff.
- Pin dependencies; add `pytest` + GitHub Actions + `ruff`/`black`.
- The dice/check/feast logic is pure and highly testable — ideal first tests.
- Consolidate the two DB access paths (web uses raw `psycopg2`; the Django ORM and
  migrations sit unused) and de-duplicate `utils.py`.

**Threats**
- Unauthenticated mutating endpoints exposed publicly → data tampering/loss.
- EOL Django 3.1 / Python 3.9 → unpatched CVEs.
- Bus factor: idiosyncratic, sparsely documented, single-author, mixed-language code.
- Token/credentials printed to host logs → bot-account compromise if logs leak.

---

## 7. Suggested priority (for discussion — nothing changed yet)

1. **Security hardening** (highest severity, smallest diff): secrets to env,
   `DEBUG=False`, re-enable CSRF, implement real token validation in `hasRight`.
2. **Bug fixes** from §3.2 / §3.1 that are clearly unintended (broken `cleanupTokens`
   SQL, doubled embed fields, `base_command.py:32` typo).
3. **Hygiene**: remove secret-leaking prints; de-duplicate `utils.py`.
4. **Tooling**: pin dependencies, add tests + CI.

Each of these would be done on its own branch and recorded in `CHANGELOG.md` with a
full before/after and rollback note, pending owner approval.
