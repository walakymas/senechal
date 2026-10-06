# Task 017: Data layer stability (connections, errors, event loop, broken SQL)

## Metadata
- **ID:** 017
- **Status:** `in-review`  <!-- implemented, tested on a throwaway PostgreSQL 14, not run on production data, not committed -->
- **Type:** `behaviour-changing`  <!-- failures that were silent now surface -->
- **Branch:** `collab/data-layer-stability`
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** failed writes now raise instead of silently succeeding (console traceback / HTTP 500); a fresh database initialises cleanly. Migration 18 adds UNIQUE indexes to `c2c` / `p2c` and **deletes duplicate rows (newest kept)** — **back up the database first**. `DATABASE_URL` is passed to libpq unchanged: percent-encode special characters in the password.

## Context
- **Problem / motivation:** one global connection opened at import time with no reconnect (`database/database.py:12-21`); `execute` prints and swallows errors (`database/base_table_handler.py:42-58`); synchronous DB/PDF/subprocess calls run on the Discord event loop; many table methods contain invalid SQL that fails silently; migrations break on a fresh install; `getValue` crashes at startup.
- **Related review finding:** `03-security-audit.md` §4 (rows 11-12, 20-21).
- **Definition of done:** the bot and API survive a dropped connection; errors are visible to callers; the broken SQL is fixed; a fresh DB initialises and starts.

## Scope
- **In scope:**
  - `ThreadedConnectionPool` (or reconnect on `InterfaceError` / `OperationalError`); `psycopg2.connect(dsn)` so `sslmode` is kept; fail early when `DATABASE_URL` is missing; remove the unused `sqlite3.connect('senechal.db')` (and rethink `!db download`).
  - `execute`: re-raise (or return an explicit failure); commit/rollback in `finally`.
  - `asyncio.to_thread` for DB calls in `message_handler.py:44`, `utils.py:218`, `Character.__init__` (`character.py:547`), `commands/me.py:39`, `commands/reload.py:21-22`, `senechal.py:47-48`.
  - Fix invalid SQL: `lordtable.py:16,19`, `markstable.py:20`, `p2ctable.py:16,19`, (`p2ptable.py` was removed instead: no `p2p` table exists, nothing used it), `checktable.py:16`, `tokenstable.py:24,27`, `feasttable.py:15,30`, `playertable.py:13` (deletes from `properties`!), `api/views.py:422` (`INTERVALL`, missing `WHERE`).
  - Migrations (`database/database.py:129-173`): duplicate `ALTER` / `INSERT`, UNIQUE on `c2c(c0,c1)` and `p2c(player,character)`, rollback in `initiate()`, remove hardcoded ids (`:173`).
  - Startup: `PropertiesTable.getValue` returns `None` for a missing row; initialise the DB before `Config.reload()` (`config.py:73`); `yaml.safe_load` (`config.py:53,69,71`).
  - `senechal.py:111` `datetime.time.sleep` and the `running` flag (`:33-37`).
- **Out of scope:** query batching and caching (Task 021); auth (Task 015).

## Plan
- [ ] Back up the database before the first start of the new code (owner).
- [x] Lazy, reconnecting connection (one connection under `Database.lock` instead of a `ThreadedConnectionPool`: access is serialised by that lock anyway) + `execute` error handling.
- [x] Fix each broken SQL statement, with integration tests.
- [x] Migrations and startup order, verified on an empty and on a "version 17" database (throwaway PostgreSQL 14 in Docker).
- [x] `asyncio.to_thread` for the blocking calls that are easy to move (`!reload`, `!me pdf`, the schema step).
- [ ] Owner decisions: hardcoded admin ids in migration 14 (kept for now); the remaining short synchronous DB calls on the event loop (needs an async data layer, out of scope here).

## Respect-the-owner checklist
- [x] Dedicated branch, not `main`.
- [x] No unrelated reformatting.
- [x] Deleted code flagged: the `sqlite3.connect('senechal.db')` leftover (nothing used `Database.conn`), the duplicate `EventsTable.glorys`; `!db download` now explains when there is no SQLite file.
- [x] Behaviour change and operational impact flagged.

## DOCUMENTATION — required
- [x] `documentation/CHANGELOG.md` entry.
- [x] `pm/STATUS.md` refreshed.
- [x] *Outcome* filled.
- [x] *Files touched* filled.
- [x] `CLAUDE.md` gotcha about the import-time connection updated (both `CLAUDE.md` files).

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| `database/database.py` | whole `Database` class, `initiate` / `_migrate`, v13, v14, new v17→18 | lazy reconnecting connection, rollback on failed migration, fresh-install fixes, unique indexes | stability |
| `database/base_table_handler.py` | `db`, `execute` | roll back and re-raise | no silent failures |
| `database/p2ptable.py` | removed | `P2PTable` deleted (owner approved) | dead code for a table that never existed |
| `database/lordtable.py`, `markstable.py`, `p2ctable.py`, `c2ctable.py`, `checktable.py`, `tokenstable.py`, `feasttable.py`, `playertable.py`, `eventstable.py`, `proptable.py` | see CHANGELOG | SQL fixes (`AND`, tables/columns, `%s`, `fetch`), `getValue` None-safe, duplicate method removed | silent failures |
| `api/views.py` | `cleanupTokens` | valid `DELETE ... WHERE expires < ...` | broken statement |
| `config.py` | `reload` | `safe_load`, UTF-8, int `mainChannel`, tolerant hook read | startup |
| `senechal.py` | `main`, `on_ready`, `init_database` | `time.sleep`, `running` after init, schema step off the loop and before `Config.reload()` | startup |
| `commands/reload.py`, `commands/me.py`, `commands/db.py` | handlers | `asyncio.to_thread`, `!db download` message | event loop |
| `tests/database_integration_test.py` | new | 11 tests against a real PostgreSQL (skipped without `TEST_DATABASE_URL`) | regression guard |
| `CLAUDE.md` (repo and workspace) | gotchas | lazy connection | docs |

## Before / after
- **Before:** one dead connection = permanently broken bot; failed writes still reply "Updated"; a fresh database could not be created; `cleanupTokens` and several table methods always failed silently.
- **After:** reconnects; errors surface; fresh DB works; the listed statements are valid.
- **Behaviour-changing?** yes (see Operational impact).

## Verification
- **How tested:** throwaway PostgreSQL 14 (`docker run … -p 127.0.0.1:55432:5432 postgres:14`), `TEST_DATABASE_URL=postgresql://t:test@127.0.0.1:55432/t venv/Scripts/python.exe -m unittest tests.database_integration_test` — 11 tests pass: fresh install reaches version 18, idempotent re-run, upgrade from 17 collapses duplicates, a failing migration rolls back, SQL errors raise and the connection stays usable, reconnect after `pg_terminate_backend`, and the fixed table methods. Also a smoke test: `Config.reload()` on an empty database, `import server`, a clear `RuntimeError` without `DATABASE_URL`. All 28 unit tests pass (11 skipped without a database).
- **How the owner can reproduce:** the same commands; then on a copy of the real database: start `python server.py`, watch `PG version: 17` → `18`, restart Postgres while it runs and use the web page and a Discord command; try `!reload`, `!me pdf`, `!lord`, `!mark`, `!token`.

## Risk & rollback
- **Risk:** the UNIQUE migration fails if duplicates exist; callers that relied on a silent `None`.
- **Rollback:** `git revert <sha>`; restore the DB from the backup if a migration ran.

## Outcome  *(fill on completion)*
- **Result:** implemented as in *Plan* (checked items) and the CHANGELOG entry; not yet run against production data.
- **CHANGELOG entry:** 2026-10-06 — Data layer stability (Task 017)
- **Commit(s):** not committed yet
