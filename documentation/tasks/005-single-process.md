# Task 005: Single process — HTTP API and Discord bot on one asyncio loop

## Metadata
- **ID:** 005
- **Status:** `in-progress`
- **Type:** `behaviour-changing`
- **Branch:** `collab/single-process`
- **Created:** 2026-10-02
- **Reviewed via PR:** <link once opened>
- **Operational impact:** one process instead of two. New start command `python3 server.py`
  (Procfile now has only `web:`; the `worker` process type is removed — scale it to 0 on
  Heroku). Listens on `$PORT` (default 8000). Needs `DATABASE_URL` and `token` as before.
  The API is served by aiohttp, not Django/gunicorn.

## Context
- **Problem / motivation:** bot and web were separate processes sharing only PostgreSQL, so
  in-memory state (`Config.config`, `Character.cache`) diverged between them.
- **Definition of done:** one process serves the same API routes and runs the bot.

## Scope
- **In scope:** `server.py`, `api/` (aiohttp port of `web/views.py`), `senechal.py`
  (`build_client()` split), DB lock + commit-after-fetch, `Procfile`.
- **Out of scope:** removing `web/` (done later in Task 007), DB pool, async DB driver,
  wrapping bot-command DB calls in threads, auth changes.

## Plan
- [x] `Database.lock` around the shared connection; commit after fetch.
- [x] `senechal.build_client()`; `main()` still runs the standalone bot.
- [x] `api/views.py` (copy of `web/views.py` on a small `django.http` shim), `api/app.py`.
- [x] `server.py`, `Procfile`.
- [ ] Verify against a real DB / Angular frontend.

## Files touched
| File | Change | Rationale |
|------|--------|-----------|
| `server.py` | new | single entry point |
| `api/__init__.py`, `api/compat.py`, `api/views.py`, `api/app.py` | new | aiohttp API, same routes/format |
| `senechal.py` | `build_client()` split; `Database.initiate()` under lock; removed two `print`s of the bot token | reuse client; avoid logging secrets |
| `database/database.py` | `Database.lock` | thread safety |
| `database/base_table_handler.py` | lock; commit after SELECT | thread safety; no dangling transactions |
| `Procfile` | only `web: python3 server.py` | one process |

## Before / after
- **Before:** `worker: senechal.py` + `web: gunicorn web.wsgi`.
- **After:** `web: python3 server.py`. `python senechal.py` still works standalone.
- **Behaviour-changing?** yes — see Operational impact. Missing form fields now give 400;
  `/admin/` is gone; known bugs (e.g. `/cleanupTokens` SQL) are copied as-is.

## Verification
- Run in Docker (compose in the workspace root): bot logs in; `/`, `/base`, `/list`, `/players`,
  `/feastConfig`, `/maps`, `/checks`, `/adminList`, `/json` answer 200; CORS preflight OK.
  Found and fixed: `JsonResponse` must serialise datetimes like Django (`api/compat.py`).
  Not yet tested: Angular UI, POST endpoints, PDF, token login.
- Reproduce: set `DATABASE_URL`, `token`; `python server.py`; open `/base`, `/list`; use the
  Angular app; send a bot command.

## Risk & rollback
- **Risk:** blocking DB calls in bot handlers still run on the loop (as before); `os.execv`
  in `commands/reload.py` would restart the API too.
- **Rollback:** restore the old two-line `Procfile`; `web/` and `senechal.py main()` are intact.
