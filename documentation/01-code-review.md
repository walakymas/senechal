# Code Review — senechal

**Date:** 2026-05-25
**Reviewer:** collaborator (read-only analysis; no code was modified)
**Branch:** `collab/code-review-and-docs`

**About this review.** This is a constructive review meant to help, not to criticise.
senechal is a real, working tool that its owner has built and kept running for a live
gaming group — that is genuinely impressive, and the design gets a lot right (see
*Strengths* first). The notes below are framed as **opportunities**, prioritised, each
with an exact `path:line` so they are easy to act on. They describe the code as found
at this date so that later changes can be justified against concrete observations —
they are not a judgement of the author.

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

## 2. Structure & strengths

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

What stands out positively:

- **The command plugin system is genuinely nice.** Command classes subclass
  `BaseCommand`, and `message_handler.py:18` auto-registers every subclass plus its
  aliases. Adding a feature is a matter of dropping one file into `commands/` — clean
  and easy to extend.
- **The data layer uses parameterized queries** (e.g. `database/markstable.py:10`), so
  the SQL layer is well-protected against injection. That is a good habit already in
  place.
- **Clear separation** between bot, web, data layer, and domain model. `character.py`
  in particular is a coherent, well-organised module.
- **Real, broad functionality** — character sheets, trait/skill/passion checks, marks,
  glory/events, feasts, PDF export, and a web companion — all working in production.

---

## 3. Opportunities: code quality

These are mostly small, localised items — the kind that accumulate in any actively
developed project. Several are quick wins.

### 3.1 Duplicated lines (likely copy/paste or merge duplications)
- `utils.py:451-452`, `utils.py:455-456`, `utils.py:464-465` — an embed field is added
  twice, so it renders doubled.
- `utils.py:444-445` — `dice(6)` is rolled twice and the first result is discarded.
- Harmless echoes: `utils.py:298-299`, `utils.py:304-305`,
  `database/database.py:11-12`, `database/database.py:73-74`.

### 3.2 Small bugs and unreachable code
- `config.py:81` — `Config.characters` is never defined, so `pcs`/`npcs` would raise
  `AttributeError` if called.
- `commands/base_command.py:32` — typo `message.channelsend` (should be
  `message.channel.send`); the fallback help path would raise an error.
- `web/views.py:339` — the `cleanupTokens` SQL has a typo (`INTERVALL`) and is missing a
  `WHERE` clause, so this endpoint currently errors.
- `utils.py:120-123` — a duplicated, unreachable `elif` branch in `get_me`.

### 3.3 Logging and secrets in logs
- A few `print()` calls aid debugging but currently emit secrets: the bot token at
  `senechal.py:17` and `config.py:60`, and DB credentials at `web/settings.py:137` and
  `database/database.py:10`. Worth removing or guarding so they don't reach host logs.
- `print()` debugging is used widely (including player and token records); a logging
  level/flag would let it be quietened in production.

### 3.4 Other observations
- `database/database.py:8-20` opens the DB connection at import time and depends on
  `DATABASE_URL` being set; there is also a vestigial unused SQLite handle
  (`database.py:8`).
- The hand-rolled migration stepper (`database.py`) works, though its skipped version
  numbers (`v=1` then `v=3`, `v=4` then `v=7`) make it a little hard to follow.
- Builtins are shadowed (`list`, `type`, `id`, `sum`) in places in `web/views.py`.
- No type hints, and identifiers/strings mix English and Hungarian; `character.py` is
  the cleanest module to model the rest on.

---

## 4. Opportunities: security

Because the app is internet-facing, these are the highest-priority items.

| Item | Location |
|------|----------|
| `DEBUG = True` in production | `web/settings.py:28` |
| `SECRET_KEY` hardcoded in the committed settings | `web/settings.py:25` |
| CSRF middleware commented out | `web/settings.py:55` |
| `hasRight()` is currently a placeholder — it returns `token != 'null'` rather than checking the DB | `web/views.py:215` |
| Mutating endpoints reachable without auth (`modify`, `newchar`, `mark`, `event`, `updatePlayer`, `cleanupTokens`, `adminList`, `token`) | `web/urls.py:22-50` |
| `senechal.db` (SQLite containing Discord IDs) is tracked in git | tracked in git |

Because these combine, the mutating endpoints are, as configured, reachable without
authentication. Addressing the settings (secret key, `DEBUG`, CSRF) and giving
`hasRight()` a real check would close most of the exposure with a fairly small change.

---

## 5. Testing & operations
- There is little automated test coverage today. `tests/deck_test.py` has one method
  that isn't prefixed `test_` (so `unittest` skips it) and has no assertions.
- No CI configuration and no linter/formatter config yet.
- Dependencies are unpinned (`requirements.txt` has no versions), which makes builds
  hard to reproduce. Django 3.1 and Python 3.9.5 are both past end-of-life, so they no
  longer receive upstream security patches.

---

## 6. SWOT

**Strengths**
- Clean, extensible command-plugin architecture; clear bot / web / data / domain
  separation.
- A genuinely working, domain-rich tool (sheets, checks, marks, glory, feasts, PDF
  export, web companion) in real use.
- Parameterized SQL in the data layer; a coherent domain model with sensible defaults.

**Weaknesses**
- Security items worth prioritising (DEBUG, secret key, CSRF, the auth placeholder) —
  see §4.
- Some accumulated cleanup: duplicated lines, a few small bugs, debug prints, no types.
- Little automated testing, CI, or lint/format gating yet.
- End-of-life runtime/framework and unpinned dependencies.

**Opportunities**
- A small, contained security pass (env-based secret key, `DEBUG=False`, re-enable
  CSRF, real token validation) removes the highest-severity risks with a modest diff.
- Pin dependencies; add `pytest` + GitHub Actions + `ruff`/`black`.
- The dice/check/feast logic is pure and highly testable — an ideal first test target.
- The two DB access paths (web uses raw `psycopg2`; the Django ORM and migrations are
  present but largely unused) could be consolidated; `utils.py` could be de-duplicated.

**Threats**
- Internet-facing mutating endpoints are currently unauthenticated (§4).
- EOL Django 3.1 / Python 3.9 — no upstream security patches.
- Maintainability: more docs and tests would make it easier for additional people to
  contribute and reduce reliance on the original author's context.
- Secrets currently reach host logs, so log access could expose the bot token.

---

## 7. Suggested priorities (for discussion)

1. **Security hardening** (highest severity, modest diff): secrets to env,
   `DEBUG=False`, re-enable CSRF, real token validation in `hasRight`.
2. **Small bug fixes** from §3.2 / §3.1 (the `cleanupTokens` SQL, the doubled embed
   fields, the `base_command.py:32` typo).
3. **Cleanup**: remove secret-leaking prints; de-duplicate `utils.py`.
4. **Tooling**: pin dependencies, add tests + CI.

Each would be its own branch and PR, recorded in `documentation/CHANGELOG.md` with a
before/after and rollback note. The owner reviews and approves each via its PR.
