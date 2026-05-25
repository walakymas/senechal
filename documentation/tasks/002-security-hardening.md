# Task 002: Security hardening (web app)

> **Status is `proposed`. This is behaviour-changing and NOT yet approved or
> implemented.** No source code has been touched for this task. It documents the
> intended work so the owner can approve (and adjust) before anything changes.

---

## Metadata
- **ID:** 002
- **Status:** `proposed`
- **Type:** `behaviour-changing`
- **Branch:** `collab/security-hardening` *(to be created on approval)*
- **Created:** 2026-05-25
- **Owner approval required?:** **yes** — required before implementing.
- **Approved by / date:** <pending owner approval>

## Context
- **Problem / motivation:** The Django web app is internet-facing and has several
  high-severity security gaps. See `01-code-review.md §4`.
- **Related review findings:**
  - `DEBUG = True` in production — `web/settings.py:28`
  - Hardcoded `SECRET_KEY` committed to git — `web/settings.py:25`
  - CSRF middleware disabled — `web/settings.py:55`
  - Authorization stub — `hasRight()` returns `token != 'null'`, never checks the DB —
    `web/views.py:215`
  - Unauthenticated mutating endpoints — `web/urls.py:22-50`
  - Secret leakage to logs — token at `senechal.py:17`, `config.py:60`; DB creds at
    `web/settings.py:137`, `database/database.py:10`
- **Definition of done:** Secrets are read from the environment, `DEBUG` defaults to
  off in production, CSRF protection is active, and token validation actually checks
  the database — without breaking the existing front-end clients.

## Scope
- **In scope (proposed):**
  1. `SECRET_KEY` → read from env (`os.environ`), keep a dev fallback only when
     `DEBUG` is on.
  2. `DEBUG` → driven by an env var, defaulting to `False`.
  3. Re-enable `django.middleware.csrf.CsrfViewMiddleware`; reconcile with the
     external (CodePen/duckdns) clients — likely via explicit CSRF tokens or a
     reviewed, minimal `@csrf_exempt` allowlist. **This is the riskiest item for the
     existing front-end and needs the most care.**
  4. Implement real token validation in `hasRight()` against `TokenTable`
     (expiry + rights), replacing the `token != 'null'` stub.
  5. Remove secret-printing `print()` statements (token, DB creds).
- **Out of scope:** Rewriting the data layer, adding a full auth framework, dependency
  upgrades (Django/Python EOL — that is a separate task), refactoring `views.py`.

## Plan *(to refine on approval)*
- [ ] Confirm with owner which endpoints the external front-end calls, so CSRF / auth
      changes don't break it.
- [ ] Introduce env-based `SECRET_KEY` and `DEBUG`.
- [ ] Re-enable CSRF; verify each front-end call path still works.
- [ ] Implement `hasRight()` against `TokenTable`.
- [ ] Strip secret-leaking prints.
- [ ] Manual verification of bot + web against a dev environment.

## Respect-the-owner checklist
- [ ] Working on a dedicated branch (`collab/security-hardening`), not `main`.
- [ ] No unrelated reformatting / renames.
- [ ] No deletion of working code without flagging it here.
- [ ] **Behaviour-changing — explicit owner approval obtained before implementing.**

## DOCUMENTATION — required (complete before marking `done`)
- [ ] `documentation/CHANGELOG.md` entry added.
- [ ] *Outcome* section below filled.
- [ ] *Files touched* table filled with `path:line` + rationale.
- [ ] Note any new env vars the owner must set in their deploy (e.g. `SECRET_KEY`,
      `DJANGO_DEBUG`) — these are operational changes the owner needs to know about.

## Files touched
*(to be filled during implementation)*

| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
|      |       |        |           |

## Before / after
- **Before:** Secrets in source/logs; `DEBUG=True`; CSRF off; auth effectively bypassed.
- **After:** Secrets from env; `DEBUG=False` by default; CSRF active; token checks real.
- **Behaviour-changing?** **Yes.** Clients that relied on no-CSRF / no-auth may need to
  send CSRF tokens or valid tokens. This must be coordinated with the owner.

## Verification
*(to be filled during implementation — manual test of each affected endpoint + bot.)*

## Risk & rollback
- **Risk:** Re-enabling CSRF or real auth could break the existing external front-end
  if it doesn't send tokens. Mitigation: map front-end calls first; stage changes.
- **Rollback:** `git revert` the relevant commits, or restore `web/settings.py` and
  `web/views.py` from `main`.

## Outcome  *(fill on completion)*
- **Result:** <pending>
