# Task 017: Data layer stability (connections, errors, event loop, broken SQL)

## Metadata
- **ID:** 017
- **Status:** `proposed`
- **Type:** `behaviour-changing`  <!-- failures that were silent now surface -->
- **Branch:** `collab/data-layer-stability`
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** failed writes now raise or report an error instead of silently succeeding; a fresh database initialises cleanly. A schema migration adds UNIQUE constraints — **back up the database first** (`db/` dump) and check for existing duplicates in `c2c` / `p2c`.

## Context
- **Problem / motivation:** one global connection opened at import time with no reconnect (`database/database.py:12-21`); `execute` prints and swallows errors (`database/base_table_handler.py:42-58`); synchronous DB/PDF/subprocess calls run on the Discord event loop; many table methods contain invalid SQL that fails silently; migrations break on a fresh install; `getValue` crashes at startup.
- **Related review finding:** `03-security-audit.md` §4 (rows 11-12, 20-21).
- **Definition of done:** the bot and API survive a dropped connection; errors are visible to callers; the broken SQL is fixed; a fresh DB initialises and starts.

## Scope
- **In scope:**
  - `ThreadedConnectionPool` (or reconnect on `InterfaceError` / `OperationalError`); `psycopg2.connect(dsn)` so `sslmode` is kept; fail early when `DATABASE_URL` is missing; remove the unused `sqlite3.connect('senechal.db')` (and rethink `!db download`).
  - `execute`: re-raise (or return an explicit failure); commit/rollback in `finally`.
  - `asyncio.to_thread` for DB calls in `message_handler.py:44`, `utils.py:218`, `Character.__init__` (`character.py:547`), `commands/me.py:39`, `commands/reload.py:21-22`, `senechal.py:47-48`.
  - Fix invalid SQL: `lordtable.py:16,19`, `markstable.py:20`, `p2ctable.py:16,19`, `p2ptable.py:24,31,34-35`, `checktable.py:16`, `tokenstable.py:24,27`, `feasttable.py:15,30`, `playertable.py:13` (deletes from `properties`!), `api/views.py:422` (`INTERVALL`, missing `WHERE`).
  - Migrations (`database/database.py:129-173`): duplicate `ALTER` / `INSERT`, UNIQUE on `c2c(c0,c1)` and `p2c(player,character)`, rollback in `initiate()`, remove hardcoded ids (`:173`).
  - Startup: `PropertiesTable.getValue` returns `None` for a missing row; initialise the DB before `Config.reload()` (`config.py:73`); `yaml.safe_load` (`config.py:53,69,71`).
  - `senechal.py:111` `datetime.time.sleep` and the `running` flag (`:33-37`).
- **Out of scope:** query batching and caching (Task 021); auth (Task 015).

## Plan
- [ ] Back up the database.
- [ ] Connection pool + `execute` error handling (one commit).
- [ ] Fix each broken SQL statement, with a test where possible.
- [ ] Migrations and startup order, verified on an empty database (`docker compose up`).
- [ ] `asyncio.to_thread` changes, one module at a time.

## Respect-the-owner checklist
- [ ] Dedicated branch, not `main`.
- [ ] No unrelated reformatting.
- [ ] No deletion of working code without flagging (`sqlite3` leftover, `!db download`).
- [ ] Behaviour change and operational impact flagged in the PR.

## DOCUMENTATION — required
- [ ] `documentation/CHANGELOG.md` entry.
- [ ] `pm/STATUS.md` refreshed.
- [ ] *Outcome* filled.
- [ ] *Files touched* filled.
- [ ] `CLAUDE.md` gotcha about import-time connection updated.

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| `database/database.py`, `database/base_table_handler.py` | see Scope | pool, errors, migrations | stability |
| `database/*table.py` | see Scope | SQL fixes | silent failures |
| `config.py`, `database/proptable.py` | 53-73, 22 | startup, `safe_load` | fresh DB |
| `message_handler.py`, `utils.py`, `commands/me.py`, `commands/reload.py`, `senechal.py` | see Scope | `to_thread` | event loop |

## Before / after
- **Before:** one dead connection = permanently broken bot; failed writes still reply "Updated".
- **After:** reconnects; errors surface; fresh DB works.
- **Behaviour-changing?** yes (see Operational impact).

## Verification
- **How tested:** restart Postgres while the bot runs; empty-DB start; each fixed command (`!lord`, `!mark`, `!token`, feast) once.
- **How the owner can reproduce:** same steps.

## Risk & rollback
- **Risk:** the UNIQUE migration fails if duplicates exist; callers that relied on a silent `None`.
- **Rollback:** `git revert <sha>`; restore the DB from the backup if a migration ran.

## Outcome  *(fill on completion)*
- **Result:**
- **CHANGELOG entry:**
- **Commit(s):**
