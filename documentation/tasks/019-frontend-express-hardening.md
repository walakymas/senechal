# Task 019: Frontend and Express hardening

## Metadata
- **ID:** 019
- **Status:** `in-review`  <!-- implemented; frontend builds, server.js tested in a container; not run in a browser, not committed -->
- **Type:** `behaviour-changing`
- **Branch:** `collab/frontend-hardening` in **both** repos: `senechal` (backend, branched from `collab/functional-bugs`) and `AngrySenechal2` (frontend, branched from `main`)
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:**
  - `npm install` is needed in `AngrySenechal2` (new dependencies `helmet`, `compression`; `package-lock.json` was **not** regenerated here, the lock was already out of sync and a regenerated one changes ~8000 lines — run `npm install` and commit the lock when you want it).
  - The production build needs `src/environments/environment.prod.ts`, which is git-ignored (the owner untracked it): copy `environment.prod.ts.example` and set the API address.
  - The default CORS / login-return origin list lost `https://codepen.io`, `https://cdpn.io` and `http://192.168.1.131`; set `CORS_ORIGINS` (comma separated) to replace the whole list (docker-compose passes it through; empty = default list).
  - `ng build` now defaults to `production`; the initial-bundle budget is warning 2.2 MB / error 3 MB (the build is 1.96 MB).

## Context
- **Problem / motivation:** token logged to the console; `server.js` redirected to the unvalidated `Host`, had no security headers or compression and answered a missing asset with the app shell (status 200); the CORS list contained sandbox and LAN origins; the maps endpoints stored any URL; failures were swallowed silently; a few crashes on bad local data; subscriptions were never released.
- **Related review finding:** `03-security-audit.md` §7 (rows 15-17) and §8.
- **Definition of done:** see Scope; met except the items under *Left open*.

## Scope
- **Done (frontend, `AngrySenechal2`):**
  - `app.component.ts`: the token is no longer logged; `setUser` accepts a failed `getUser` (`undefined`); `ngOnDestroy` releases the poll and the `listChanged` subscription.
  - `character.service.ts`: `handleError` now tells the user (snackbar `Request failed: <operation>`, the same operation at most every 10 s, so the login poll cannot spam) instead of only logging.
  - `feast-seating.component.ts`: guarded `JSON.parse` of the cached list.
  - `server.js`: `trust proxy` (X-Forwarded-Proto is believed for the configured number of proxies only, `TRUST_PROXY`, default 1); the https redirect never uses an unvalidated host (`ALLOWED_HOSTS`, or a plain-host-name pattern → 400); `helmet` (HSTS, nosniff, frame options, referrer policy …) with a **report-only** CSP; `compression`; hashed bundles `immutable` for a year, everything else revalidated; a missing file with an extension is a 404; `x-powered-by` off; `REQUIRE_HTTPS=false` for local use; `DIST_DIR` for tests.
  - `server.test.js` + `npm run test:server` (plain node): redirect, bad hosts, https behind the proxy, headers, 404 vs app shell, cache headers.
  - `angular.json`: `build` defaults to production, budgets 2.2 MB / 3 MB. `ng serve` / `extract-i18n` now use a new `development` build configuration explicitly (otherwise `ng serve` inherited the production default and the docker-compose frontend crashed on the missing `environment.prod.ts`; found and fixed in the running container).
  - `environment.prod.ts.example`, README section.
- **Done (backend, `senechal`):**
  - `api/app.py`: allowed origins from `CORS_ORIGINS`, default list without codepen / cdpn / LAN IP (the same set decides where the Discord login may return the token).
  - `api/views.py`: `add_map` / `update_map` accept only absolute http(s) URLs (400 otherwise).
  - `docker-compose.yml` (workspace root, not in a repo) passes `CORS_ORIGINS`; `.env.example` documents it.
- **Left open:**
  - **Production API URL**: `environment.prod.ts` (now local only) pointed at `https://senechal.herokuapp.com/`, and `character.service.ts:292` hardcodes the duckdns avatar URL. I did not change them: the real addresses are the owner's to give.
  - **Token storage / `Authorization` header / HttpInterceptor**: depends on Task 015 (blocked until the login is confirmed for all players); the token still lives in `localStorage` and travels in POST bodies.
  - **CSP enforcement**: first look for violations in the browser, then `reportOnly: false`.
  - **Performance of the Angular views** (`trackBy` / `OnPush` for ~100 `*ngFor`, template method calls such as `myCharacters()`, lazy-loaded routes): not done. `OnPush` changes when views refresh and the components mutate their data in place, and routes are declared in one NgModule, so this needs a browser to verify; it deserves its own task.
  - Remaining http origins in the default list (`senechalweb`, `senechallocal`, `senechaldev` duckdns, `localhost`): kept because they may be in use; trim with `CORS_ORIGINS`.
- **Out of scope:** removing the webhook from `/base` (Task 011 must cover logged-out users first); Angular major upgrade (Task 020).

## Plan
- [x] Backend: CORS from env; maps URL validation (+ tests).
- [x] `server.js` hardening (+ tests in a node:16 container).
- [x] Interceptor-free error handling, token logging, null-safety, JSON guard, subscriptions.
- [x] `angular.json` defaults and budgets; production build verified.
- [ ] Owner: production API URL; try the app in a browser (login, character page, maps, feast); check the CSP report-only messages.
- [ ] Follow-up tasks: Angular performance (`trackBy` / `OnPush` / lazy routes); interceptor + token storage after Task 015.

## Respect-the-owner checklist
- [x] Dedicated branch (`collab/frontend-hardening` in each repo), not `main`.
- [x] No unrelated reformatting.
- [x] No deletion of working code (the token log line; the old inline `requireHTTPS`).
- [x] Behaviour change and operational impact flagged (above).

## DOCUMENTATION — required
- [x] `documentation/CHANGELOG.md` entry.
- [x] `pm/STATUS.md` refreshed.
- [x] *Outcome* filled.
- [x] *Files touched* filled.
- [x] README note for the new env vars (`AngrySenechal2/README.md`, `.env.example`).

## Files touched
| Repo | File | Change |
|------|------|--------|
| AngrySenechal2 | `server.js`, `server.test.js`, `package.json` | hardened server, tests, `helmet` / `compression` |
| AngrySenechal2 | `src/app/app.component.ts`, `character.service.ts`, `feast-seating/feast-seating.component.ts` | see Scope |
| AngrySenechal2 | `angular.json`, `README.md`, `src/environments/environment.prod.ts.example` | defaults, budgets, docs |
| senechal | `api/app.py`, `api/views.py` | CORS from env, map URL validation |
| senechal | `tests/api_hardening_test.py` (new) | 6 unit tests |
| workspace root (no repo) | `docker-compose.yml`, `.env.example` | `CORS_ORIGINS` |

## Before / after
- **Before:** see Context.
- **After:** see Scope.
- **Behaviour-changing?** yes (see Operational impact).

## Verification
- **How tested:**
  - Backend: `venv/Scripts/python.exe -m unittest discover -s tests -p "*_test.py"` — 62 tests pass (12 skipped without a database).
  - `server.js`: `node server.test.js` in a throwaway `node:16-alpine` container (production dependencies installed there) — passes.
  - Frontend: `ng build --configuration production` in a throwaway `node:16-alpine` container — succeeds, initial 1.96 MB (424 kB transferred), the 16-character bundle hash matches the cache rule. The Karma tests were not run (no Chrome); the existing `app.component.spec.ts` was already outdated (it does not provide the app's dependencies).
  - Not run in a browser.
- **How the owner can reproduce:** `cd AngrySenechal2 && npm install && npm run test:server && npm run build` (after copying the environment example); `curl -I http://localhost:8080/` with `REQUIRE_HTTPS=false`: security headers, `Content-Security-Policy-Report-Only`, no `x-powered-by`; `curl -I -H "Host: a/b" http://…` → 400; `curl -H "Origin: https://codepen.io" -i http://localhost:8000/base` → no CORS headers.

## Risk & rollback
- **Risk:** a legitimate origin missing from the list (the web page shows "Request failed" snackbars and the Discord login redirect is refused) — add it to `CORS_ORIGINS`; the report-only CSP does not block anything; `helmet`'s HSTS makes browsers insist on https for the host (that is the redirect's purpose anyway).
- **Rollback:** `git revert <sha>` in both repos.

## Outcome  *(fill on completion)*
- **Result:** implemented as in *Scope — Done*; the *Left open* items need the owner's input or a browser.
- **CHANGELOG entry:** 2026-10-06 — Frontend and Express hardening (Task 019)
- **Commit(s):** not committed yet
