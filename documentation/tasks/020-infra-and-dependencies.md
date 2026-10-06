# Task 020: Infrastructure, dependencies and repo hygiene

## Metadata
- **ID:** 020
- **Status:** `proposed`
- **Type:** `behaviour-preserving`  <!-- build and ignore-file changes; a runtime upgrade step is flagged below -->
- **Branch:** `collab/infra-and-deps`
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** images are rebuilt on non-root users and newer Node/Python; the Postgres port is no longer published to the network; `senechal.db` and `*.pkl` leave version control (files stay on disk). Redeploy needs the owner to review `deploy/setup-systemd.sh` before re-running it.

## Context
- **Problem / motivation:** containers run as root; Postgres port `5432` is published; dev servers (`ng serve`, `disableHostCheck`) in production images; Angular 14 / Node 16 / Python 3.9–3.10 are end of life; `requirements.txt` has no versions; tracked files that should not be (`senechal.db`, `*.pkl`); stale `dist/`.
- **Related review finding:** `03-security-audit.md` §7 (rows 18-19) and §1.
- **Definition of done:** non-root multi-stage images; pinned Python and npm dependencies; audits run; ignore files complete; dead files removed.

## Scope
- **In scope:**
  - `Dockerfile.senechal`, `AngrySenechal2/Dockerfile*`: non-root `USER`, multi-stage build serving `dist` through the hardened `server.js`, Node 20/22 LTS, Python 3.12+, `npm ci`.
  - `docker-compose.yml`: Postgres `127.0.0.1:5432:5432`, web on loopback if a proxy fronts it, pinned `postgres` minor tag; no secrets in the file (env only).
  - `angular.json`: remove `disableHostCheck`.
  - `requirements.txt`: pin with `pip-compile` / `uv`; run `pip-audit`; update `runtime.txt` / `Procfile` or remove if Heroku is gone; `psycopg2-binary` → `psycopg2`/`psycopg` 3 (owner's choice).
  - `package.json`: align `@angular/cli` with the other Angular packages; replace protractor/tslint/codelyzer; run `npm audit`; Angular upgrade one major at a time (`ng update`) — own sub-tasks.
  - `.gitignore` / `.dockerignore`: `.env*`, `*.db`, `*.pkl`, `*.dmp`, `*.zip`, `environment.prod.ts` pattern, `.angular`; `git rm --cached senechal.db senechal.db-journal` and the `*.pkl` files; remove the misnamed `AngrySenechal2/dockerignore`.
  - Delete (owner approved 2026-10-06): `senechal_old.py` and the fpdf 1.x `.pkl` font caches. `senechal2/` has already been removed by the owner (verify it is gone and nothing references it). Also stray `__pycache__`, `#build#`, `.iml` — confirm those with the owner.
  - `deploy/setup-systemd.sh`: serve the built `dist` instead of `ng serve`; confirm the sudoers rule covers only the two restart commands.
- **Out of scope:** secret rotation (manual, Task 013); application code.

## Plan
- [x] Owner approved deleting `senechal_old.py` and the `.pkl` files; `senechal2/` is gone.
- [ ] Owner confirms the target Python/Node versions.
- [ ] Ignore files and untracking.
- [ ] Dockerfiles and compose.
- [ ] Pin dependencies; run both audits and record the results in the CHANGELOG.
- [ ] Angular upgrade as follow-up sub-tasks (14 → 15 → … one major each).

## Respect-the-owner checklist
- [ ] Dedicated branch, not `main`.
- [ ] No unrelated reformatting.
- [ ] No deletion of working code without flagging (list every deleted file in *Before / after*).
- [ ] Operational impact flagged in the PR.

## DOCUMENTATION — required
- [ ] `documentation/CHANGELOG.md` entry.
- [ ] `pm/STATUS.md` refreshed.
- [ ] *Outcome* filled.
- [ ] *Files touched* filled.
- [ ] `CLAUDE.md` and README run instructions updated (Docker, Python version).

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| `Dockerfile.senechal`, `docker-compose.yml`, `AngrySenechal2/Dockerfile*` | — | hardening | |
| `requirements.txt`, `runtime.txt`, `Procfile`, `package.json` | — | pin / upgrade | |
| `.gitignore`, `.dockerignore` | — | complete | |

## Before / after
- **Before:** see Context.
- **After:** see Definition of done.
- **Behaviour-changing?** no for the application; yes for how it is built and deployed.

## Verification
- **How tested:** `docker compose up` from a clean checkout; `docker compose exec web id` is not root; `pip-audit`, `npm audit`; `git ls-files | grep -E "\.pkl|senechal\.db"` is empty.
- **How the owner can reproduce:** same steps.

## Risk & rollback
- **Risk:** library behaviour changes with new versions (`discord.py`, `fpdf2`, `emoji`); untracking files breaks anyone who relied on the committed copy.
- **Rollback:** `git revert <sha>`; restore pinned old versions from `pip freeze` taken before the change.

## Outcome  *(fill on completion)*
- **Result:**
- **CHANGELOG entry:**
- **Commit(s):**
