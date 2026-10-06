# Task 019: Frontend and Express hardening

## Metadata
- **ID:** 019
- **Status:** `proposed`
- **Type:** `behaviour-changing`
- **Branch:** `collab/frontend-hardening`  <!-- AngrySenechal2 repo + senechal repo for CORS -->
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** the CORS allow-list is loaded from an env var (new `CORS_ORIGINS`), so the owner must set it, otherwise the web page is blocked. `server.js` needs a canonical host env var. The hosting URL (`environment.prod.ts:3` still points at `senechal.herokuapp.com`) must be confirmed.

## Context
- **Problem / motivation:** token in `localStorage` and logged to the console; no central 401 handling; `server.js` redirects using the unvalidated `Host` header and has no security headers; the CORS list contains codepen, a LAN IP and `http://` origins; the Angular app has no `trackBy` / `OnPush`, leaks subscriptions and polls forever; the default build is unoptimised.
- **Related review finding:** `03-security-audit.md` §7 (rows 15-17, 24) and §8.
- **Definition of done:** token no longer logged; interceptor in place; `server.js` hardened; CORS configurable; the performance items below done on the heaviest components.

## Scope
- **In scope:**
  - Remove `logger.log('token:'+...)` (`app.component.ts:36`); `HttpInterceptor` for the `Authorization` header and 401 handling (shared with Task 015); decide cookie vs in-memory token with the owner.
  - `server.js`: canonical host from env, `trust proxy`, `helmet` (CSP, HSTS), `compression`, 404 for missing assets, cache headers.
  - CORS (`api/app.py:16-27`): origins from env; drop codepen, LAN IP, `http://`.
  - `handleError` (`character.service.ts:370-380`) surfaces errors; `setUser` null-safe (`app.component.ts:83`); guarded `JSON.parse` (`feast-seating.component.ts:22`).
  - Performance: `trackBy` and `OnPush` on `character-detail`, `chargen`, `team`; replace template method calls (`app.component.html:14-45`); `takeUntil` for subscriptions; stop the `interval(5000)` poll once the user is loaded (`app.component.ts:42-50`); lazy-load routes; `defaultConfiguration: production` and tighter budgets in `angular.json`.
  - Maps: validate `url` scheme server-side (`api/views.py:531`).
  - Replace the hardcoded `senechal.herokuapp.com` / duckdns URLs (`environment.prod.ts:3`, `character.service.ts:292`).
- **Out of scope:** removing the webhook from `/base` (needs Task 011 to cover logged-out users first); Angular major upgrade (Task 020).

## Plan
- [ ] Owner confirms the production URL, allowed origins and token storage approach.
- [ ] Backend: CORS from env; maps URL validation.
- [ ] `server.js` hardening.
- [ ] Interceptor + error handling.
- [ ] Performance items, component by component, with the existing specs.

## Respect-the-owner checklist
- [ ] Dedicated branch, not `main`.
- [ ] No unrelated reformatting.
- [ ] No deletion of working code without flagging.
- [ ] Behaviour change and operational impact flagged in the PR.

## DOCUMENTATION — required
- [ ] `documentation/CHANGELOG.md` entry.
- [ ] `pm/STATUS.md` refreshed.
- [ ] *Outcome* filled.
- [ ] *Files touched* filled.
- [ ] README note for the new env vars.

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| `AngrySenechal2/server.js`, `angular.json`, `src/app/*` | see Scope | hardening, performance | |
| `api/app.py`, `api/views.py` | 16-27, 531 | CORS from env, URL check | |

## Before / after
- **Before:** see Context.
- **After:** see Definition of done.
- **Behaviour-changing?** yes (see Operational impact).

## Verification
- **How tested:** `npm run build`, `npm test`; browser network tab (no token in logs, 401 handling); `curl -H "Host: evil.example" -I` against `server.js` does not redirect there; `curl -H "Origin: https://codepen.io"` gets no CORS headers.
- **How the owner can reproduce:** same steps.

## Risk & rollback
- **Risk:** blocking the web page if the CORS env var is wrong; CSP breaking Google Fonts or Material icons.
- **Rollback:** `git revert <sha>` in both repos.

## Outcome  *(fill on completion)*
- **Result:**
- **CHANGELOG entry:**
- **Commit(s):**
