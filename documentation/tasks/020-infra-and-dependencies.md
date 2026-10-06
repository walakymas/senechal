# Task 020: Infrastructure, dependencies and repo hygiene

## Metadata
- **ID:** 020
- **Status:** `in-review`  <!-- implemented and verified in containers; not deployed, not committed -->
- **Type:** `behaviour-preserving` for the application; **changes how it is built, tested and deployed**
- **Branch:** `collab/infra-and-deps` in **both** repos (`senechal` from `collab/frontend-hardening`, `AngrySenechal2` from `collab/frontend-hardening`)
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:**
  - The backend image is now `python:3.12-slim`, runs as user `app` (uid 1000) and installs **pinned** dependencies (`requirements.txt`). Rebuild it: `docker compose build senechal`. `runtime.txt` and `Procfile` are deleted: Heroku is no longer used (owner decision).
  - `aiohttp` goes 3.12.14 → **3.14.3** (64 known advisories in the old version).
  - The Postgres port is published on `127.0.0.1:5432` only (was all interfaces).
  - `package-lock.json` in `AngrySenechal2` is regenerated (in sync with `package.json`); both frontend Dockerfiles use `npm ci`.
  - `senechal.db`, `senechal.db-journal` and the font `*.pkl` files are no longer tracked (the SQLite files stay on disk); `senechal_old.py` and the `.pkl` files are deleted.
  - Frontend: `Dockerfile.dev` runs as `node`; `Dockerfile` is now a production multi-stage image (hardened `server.js`, user `node`, port 8080); the unused `compression` package was dropped again (known DoS advisory).

## Context
- **Problem / motivation:** containers ran as root; Postgres was published to the network; unpinned Python dependencies including a vulnerable `aiohttp`; EOL runtime versions; tracked files that should not be in git; a stale, unused frontend Dockerfile.
- **Related review finding:** `03-security-audit.md` §7 (rows 18-19) and §1.
- **Definition of done:** non-root images, pinned and audited dependencies, complete ignore files, dead files removed. Met except the items under *Left open*.

## Owner decisions used
- Delete `senechal_old.py` and the `.pkl` files (approved); `senechal2/` was already removed by the owner.
- Heroku is no longer supported: remove every Heroku dependency (`Procfile`, `runtime.txt`, the `herokuapp.com` URLs). Remove the tracked stray files. Synchronise `package-lock.json`.

## Scope
- **Done:**
  - **Python dependencies** (pin set corrected in Task 021: `fpdf2` 2.8.3 could not embed the variable font, the file now has the versions of the working container): `requirements.txt` fully pinned (direct + transitive) for Python 3.12; installed in a clean `python:3.12-slim`, all unit tests pass there, `pip-audit`: **no known vulnerabilities** (before: only `aiohttp` 3.12.14, 64 advisories, fixed in 3.14.3). `psycopg2-binary` kept (the slim image has no compiler/libpq headers).
  - **`Dockerfile.senechal`** (workspace root, not in a repo): Python 3.12, user `app`, writable `/var/www/senechalPictures` (the `picturesDir` default), `PYTHONUNBUFFERED=1`; `Dockerfile.senechal.dockerignore` excludes `.env*`, `*.db`, `*.dmp`, `*.zip`, `*.tgz`, `*.pkl`, `.claude`. Verified: `docker build`, `id` = `app`, the pictures directory is writable, `import server` works, and **all 62 tests pass inside the image against a PostgreSQL 14 container, including the 12 database tests**.
  - **`docker-compose.yml`** (workspace root): Postgres on `127.0.0.1:5432`.
  - **Tests**: the `database.database` stub is gone from the test files (the connection has been lazy since Task 017); the stub made the database tests use a fake `Database` when everything ran in one `unittest discover`.
  - **Repo hygiene (backend)**: deleted `senechal_old.py` and 7 `.pkl` files (fpdf 1.x font caches, unused by fpdf2); `git rm --cached senechal.db senechal.db-journal`; `.gitignore` gained `*.pkl`, `*.db`, `*.db-journal`, `*.dmp`, `*.zip`, `*.tgz`, `.claude/`.
  - **Frontend (`AngrySenechal2`)**: `Dockerfile.dev` as user `node` (verified: `ng` 13.3.11 on Node 16.20); `Dockerfile` replaced by a production multi-stage build (verified: user `node`, `/` 200, missing asset 404, CSP-report-only and HSTS headers); removed the misnamed `dockerignore` duplicate; `.dockerignore` gained `.angular`, `.env*`, `*.log`, `__pycache__`; removed the `compression` dependency (`npm audit --omit=dev` of the server's dependencies: **0 vulnerabilities**).
  - **`npm audit` of the whole frontend** (recorded, not fixed): 113 advisories after the lock was synchronised (115 before; 7 critical: `form-data`, `json-schema`, `jsprim`, `piscina`, `request`, `socket.io-parser`, `tar`; 52 high). They come from Angular 14 itself (end of life) and the dev tooling (`protractor`, `karma`, `@angular-devkit/build-angular`); the shipped bundle's attack surface is the Angular runtime.
  - **Heroku removed**: `Procfile`, `runtime.txt` deleted; `static/sheet.js` and `static/team.js` no longer call `https://senechal.herokuapp.com` (they use the same server, `..`); the Heroku mentions in `senechal/CLAUDE.md` and `server.js` are gone (historic CHANGELOG / task / audit text is left as it was). While doing this I found **two more hardcoded Discord webhook URLs** in `static/team.js` (a production and a localhost one): removed; the "bot" buttons of that old page post only when `hurl` is set locally.
  - **Stray files**: `#build#` and `AngrySenechal2.iml` removed from git (the untracked `__pycache__` folder deleted).
  - **`package-lock.json` synchronised** (`npm install --package-lock-only` in `node:16-alpine`, lockfileVersion 2, same Angular 14.3.0 / CLI 13.3.11; `helmet` 7.2.0): the Dockerfiles use `npm ci`; verified by building both images from it (below).
  - Docs: workspace `CLAUDE.md` brought up to date (no Django, no `senechal2`, Python 3.12, tests, Docker).
- **Left open (owner decisions or separate work):**
  - **Python / Node targets**: I chose Python 3.12. Node stayed at 16 only because Angular 14's CLI does not run on newer Node; **Task 022 did the Angular upgrade (14 → 22) and moved the frontend to Node 22**, and replaced `protractor`, `tslint` and `codelyzer`.
  - **`deploy/setup-systemd.sh`** starts the Angular **dev server** (`ng serve`) as the production frontend service `senechal-ng`. Switching it to `npm run build` + `node server.js` (with `REQUIRE_HTTPS=false` behind your own TLS proxy) is an operations change for the host; I did not touch it because I cannot test it there. Also check that the sudoers rule it installs only allows the two `systemctl restart` commands.
  - **`disableHostCheck: true`** (`angular.json`, dev server) kept: replacing it by `allowedHosts` needs the host names you use for development.
  - Ports `8000` / `4200` are still published on all interfaces (you may use them from the LAN).
  - The hardcoded admin Discord ids in migration 14 (Task 017) and the PostgreSQL dump `db/senechal_20260622.dmp` (sensitive; now ignored by `*.dmp`) are unchanged.
- **Out of scope:** secret rotation (manual, Task 013); application code.

## Plan
- [x] Pin and audit the Python dependencies; verify on Python 3.12.
- [x] Backend image (non-root) and compose; verify with the database tests.
- [x] Ignore files and untracking; delete the approved dead files.
- [x] Frontend Dockerfiles (non-root, production multi-stage); verify both.
- [x] Record `npm audit`; drop the vulnerable `compression`.
- [ ] Owner: rebuild and restart the stack (`docker compose build && docker compose up -d`; take a database backup first if you have not run Task 017's migration yet).
- [ ] Owner decisions under *Left open*; follow-up tasks: Angular upgrade series, systemd frontend service.

## Respect-the-owner checklist
- [x] Dedicated branch, not `main`.
- [x] No unrelated reformatting.
- [x] Every deleted file is listed above (`senechal_old.py`, 7 `.pkl`, `dockerignore`; the untracked SQLite files stay on disk).
- [x] Operational impact flagged.

## DOCUMENTATION — required
- [x] `documentation/CHANGELOG.md` entry.
- [x] `pm/STATUS.md` refreshed.
- [x] *Outcome* filled.
- [x] *Files touched* filled.
- [x] `CLAUDE.md` and README run instructions updated (Docker, Python version, tests, frontend server).

## Files touched
| Repo | File | Change |
|------|------|--------|
| senechal | `requirements.txt` | everything pinned, `aiohttp` 3.14.3 |
| senechal | `.gitignore`; deleted `senechal_old.py`, 7 `*.pkl`, `Procfile`, `runtime.txt`; untracked `senechal.db`, `senechal.db-journal` | hygiene, Heroku removed |
| senechal | `static/sheet.js`, `static/team.js`, `CLAUDE.md`, `pm/STATUS.md` | no Heroku URLs, no webhook URLs |
| senechal | `tests/*_test.py` (4 files) | removed the `database.database` stub |
| AngrySenechal2 | `Dockerfile.dev`, `Dockerfile`, `.dockerignore`; deleted `dockerignore` | non-root images, production image |
| AngrySenechal2 | `server.js`, `package.json`, `README.md` | dropped `compression`, no Heroku mention |
| AngrySenechal2 | `package-lock.json`, `Dockerfile`, `Dockerfile.dev`; deleted `#build#`, `AngrySenechal2.iml` | synchronised lock, `npm ci` |
| workspace root (no repo) | `Dockerfile.senechal`, `Dockerfile.senechal.dockerignore`, `docker-compose.yml`, `CLAUDE.md` | see Scope |

## Before / after
- **Before:** root containers, unpinned dependencies with a vulnerable `aiohttp`, Python 3.10 image, database published to the network, SQLite/pickle files in git, an unused dev-like "production" Dockerfile.
- **After:** see Scope.
- **Behaviour-changing?** no for the application; the Python and aiohttp upgrades change the runtime it runs on (all tests pass on it).

## Verification
- **How tested:** see the "Verified" statements in Scope. Commands: `python -m unittest discover -s tests -p "*_test.py"` (62 tests; 12 need `TEST_DATABASE_URL`); `pip-audit -r requirements.txt --no-deps`; `docker build -f ../Dockerfile.senechal .` in `senechal/`; `docker build -f Dockerfile.dev .` and `docker build -f Dockerfile .` in `AngrySenechal2/`; `npm run test:server`.
- **How the owner can reproduce:** the same commands; then `docker compose build && docker compose up -d`, `docker compose exec senechal id` (user `app`), and try the bot and the web page.

## Risk & rollback
- **Risk:** library behaviour changes with `aiohttp` 3.14 / Python 3.12 that the unit tests do not cover (live Discord, PDF, uploads); a non-root container cannot write where a bind mount is owned by another uid (Linux hosts); the dev stack needs a rebuild.
- **Rollback:** `git revert <sha>` in each repo; restore the old root files from the workspace copy if needed.

## Outcome  *(fill on completion)*
- **Result:** implemented as in *Scope — Done*; the *Left open* items need the owner or separate tasks.
- **CHANGELOG entry:** 2026-10-06 — Infrastructure, dependencies and repo hygiene (Task 020)
- **Commit(s):** not committed yet
