# Task 002: Security hardening (web app)

> **Status `in-progress`.** The safe, non-breaking items are implemented on
> `collab/security-hardening` in three scoped commits. **CSRF is deliberately not
> changed yet** — it can break the external front-end and needs the owner's input
> (see *Outcome → CSRF*). This is behaviour-changing; it will be reviewed via the PR.

---

## Metadata
- **ID:** 002
- **Status:** `in-progress`
- **Type:** `behaviour-changing`
- **Branch:** `collab/security-hardening` (stacked on `collab/code-review-and-docs`)
- **Created:** 2026-05-25
- **Reviewed via PR:** <link once opened — the PR is the review/approval gate>
- **Operational impact:** the owner must, in the deploy environment, set
  `DJANGO_SECRET_KEY` (to rotate the now-public key) and `DJANGO_DEBUG` (it defaults to
  off). With `DEBUG=False`, confirm `ALLOWED_HOSTS` covers the live host. Enabling real
  authorization (`Config.authorization`) and/or CSRF later will require the front-end to
  send tokens — not done in this pass.

## Context
- **Problem / motivation:** The Django web app is internet-facing and has several
  high-priority security items. See `01-code-review.md §4`.
- **Related review findings:**
  - `DEBUG = True` in production — `web/settings.py:28`
  - Hardcoded `SECRET_KEY` committed to git — `web/settings.py:25`
  - CSRF middleware disabled — `web/settings.py:55`
  - `hasRight()` placeholder (`token != 'null'`) — `web/views.py:215`
  - Unauthenticated mutating endpoints — `web/urls.py:22-50`
  - Secret leakage to logs — token at `senechal.py:17`, `config.py:60`; DB creds at
    `web/settings.py:137`, `database/database.py:10`; token at `database/tokenstable.py:10`
- **Definition of done:** Secrets read from the environment, `DEBUG` defaults to off,
  real token validation in `hasRight()`, and a decided position on CSRF — all without
  breaking the existing front-end clients.

## Scope
- **In scope:** env-based `SECRET_KEY`/`DEBUG`; stop leaking secrets to logs; real token
  validation in `hasRight()`; a decision on CSRF.
- **Out of scope:** rewriting the data layer, a full auth framework, dependency/runtime
  upgrades (separate task), broad `views.py` refactoring, per-character authorization.

## Plan
- [x] Introduce env-based `SECRET_KEY` and `DEBUG` (with a non-breaking fallback).
- [x] Strip secret-leaking prints (token, DB URL).
- [x] Implement `hasRight()` against `TokenTable` (exists + active + not expired).
- [ ] **CSRF — decision pending** (see *Outcome → CSRF*). Needs to know which endpoints
      the external front-end calls and whether it can send CSRF tokens.
- [ ] Owner sets the new env vars in deploy and verifies the app boots with `DEBUG=False`.

## Respect-the-owner checklist
- [x] Working on a dedicated branch (`collab/security-hardening`), not `main`.
- [x] No unrelated reformatting / renames.
- [x] No deletion of working code without flagging it here.
- [x] **Behaviour-changing — runtime change + operational impact flagged here and (to be) in the PR.**

## DOCUMENTATION — required
- [x] `documentation/CHANGELOG.md` entry added.
- [x] `pm/STATUS.md` refreshed to the new current state.
- [x] *Outcome* section below filled.
- [x] *Files touched* table filled.
- [x] New env vars (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`) noted for the owner's deploy.

## Files touched
| File | Change | Commit | Rationale |
|------|--------|--------|-----------|
| `web/settings.py` | `SECRET_KEY`/`DEBUG` from env; removed DB-config `print` | `8961e25` | Secrets out of source; `DEBUG` off by default. |
| `senechal.py` | removed token from startup `print` | `a611e8a` | Stop leaking the bot token to logs. |
| `config.py` | removed token-leaking `print`; fixed latent `KeyError` | `a611e8a` | Stop leak; avoid crash when `token` env is unset. |
| `database/database.py` | removed `DATABASE_URL` prints; de-duped lookup | `a611e8a` | Stop leaking DB credentials to logs. |
| `database/tokenstable.py` | removed token `print` in `set()` | `a611e8a` | Stop leaking tokens to logs. |
| `web/views.py` | real token validation in `hasRight()` | `dd0b011` | Replace the `token != 'null'` placeholder. |

## Before / after
- **Before:** Secrets printed to logs; `SECRET_KEY` hardcoded; `DEBUG=True`; `hasRight()`
  accepted any non-`'null'` token.
- **After:** No secrets in those log lines; `SECRET_KEY`/`DEBUG` from env (defaults:
  fallback key + `DEBUG=False`); `hasRight()` verifies a real, active, unexpired token.
- **Behaviour-changing?** **Yes** — `DEBUG` defaults off (operational). `hasRight()` is
  stricter only when `Config.authorization` is enabled (default off), so current
  production behaviour is unchanged. CSRF is unchanged (still disabled) pending a decision.

## Verification
- `python -m py_compile` passes on all six edited files.
- `hasRight()` change is gated by `Config.authorization` (default `False`), so it does
  not alter current request handling; the logic was checked against
  `TokenTable.get_info_by_token` (index 3 = `tokenstate`, index 5 = not-expired flag).
- Not run against the live app/front-end (needs `DATABASE_URL`, a bot token, and the
  external front-end) — the owner should smoke-test on a dev/staging environment,
  especially that the site loads with `DEBUG=False`.

## Risk & rollback
- **Risk:** With `DEBUG=False`, an incomplete `ALLOWED_HOSTS` would 400 the site; the
  list already includes the known hosts but should be confirmed. The `hasRight` change
  is inert until authorization is enabled.
- **Rollback:** `git revert` the relevant commit(s) (`8961e25`, `a611e8a`, `dd0b011`).

## Outcome
- **Result:** Secrets removed from logs; `SECRET_KEY`/`DEBUG` env-driven; `hasRight()`
  validates tokens. Implemented in three scoped commits.
- **CSRF (deferred — needs a decision):** Re-enabling `CsrfViewMiddleware` would block
  the external front-end's cross-origin POSTs unless that front-end sends CSRF tokens.
  For a token-authenticated API consumed by a separate SPA, the more natural protection
  is the token check (above) rather than cookie-based CSRF. Options to choose from:
  (a) enable CSRF globally + have the front-end send tokens; (b) enable CSRF but exempt
  the JSON API endpoints and rely on token auth; (c) leave CSRF off and rely on token
  auth + CORS. Pending owner/collaborator input.
- **CHANGELOG entry:** 2026-05-25 — "Security hardening: env secrets, no secret logging,
  real hasRight()".
