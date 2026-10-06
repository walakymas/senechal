# Task 015: API authentication and authorisation

## Metadata
- **ID:** 015
- **Status:** `blocked`  <!-- waiting: do not change access rules until login is confirmed working for every player -->
- **Type:** `behaviour-changing`
- **Branch:** `collab/api-auth`
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** **client-breaking for writes.** Write routes now return 401/403 without a valid token, so the Angular frontend must send the token on every write call and the old `/token` login is removed; backend and frontend deploy together. Reads are unaffected.

## Context
- **Problem / motivation:** most routes need no token (`api/app.py:36-47`); `hasRight()` (`api/views.py:299`) accepts any string; `modify` skips the check when `Config.authorization` is false (the default, `config.py:8`, `api/views.py:216`); `/token` (`api/views.py:110-130`) mints a token for any character id; `adminList` (`api/views.py:375`) dumps live session tokens.
- **Related review finding:** `03-security-audit.md` §2 (rows 5-7, 10, 14).
- **Definition of done:** every non-public route validates the token and applies a rights rule; unauthenticated callers get 401; a test per rule class passes.

## Owner decisions (2026-10-06)
- **Blocker:** access must not be tightened until the owner has confirmed that the login works correctly for **every player** (Discord OAuth, `api/auth.py`). Until then this task stays `blocked`; only preparation that changes no behaviour (tests, the decorator behind a switch that is off) may be done.
- **Reads stay open:** everyone, logged in or not, may see all characters. Read routes (`json`, `npc`, `pdf`, `pdfs`, `list`, `players`, `checks`, `connections`) keep working without a token.
- **Write rules come later:** the owner will specify who may modify what. Do not invent ownership/admin rules until then.

## Scope
- **In scope** (applies once unblocked, and only for write routes):
  - One decorator/middleware: `TokenTable().get_info_by_token`, `state == 1`, not expired.
  - Rules: to be defined by the owner. Candidates from the audit: *owner* (character belongs to the token's player; `modify`, `newchar`, `event`, `mark`, `feast`, `addC2C`), *admin* (`playerrights` bit 0; `updatePlayer`, `cleanupTokens`, `add_map` / `update_map` / `delete_map`).
  - `adminList` dumps live session tokens, so it is not a normal read route: protect it (admin) or drop the `tokens` table from it even while reads stay open. Needs the owner's confirmation.
  - Delete `hasRight()`; make authorization non-optional (drop `Config.authorization`).
  - Remove the unauthenticated `/token` issuer; Discord OAuth (`api/auth.py`) stays the only login.
  - `modify`: field allow-list and ownership; fix `set_json` (`if 'player' in j: role = j['player']`).
  - Stop returning exception text to clients; catch `Exception`, not `BaseException`.
- **Out of scope:** the webhook URL that `/base` returns (kept for now, see Task 011); token hashing at rest and OAuth state store (Task 019); frontend token storage (Task 019) — only the minimal change to keep it working.

## Plan
- [ ] Owner confirms the login works for every player (blocker).
- [ ] Owner defines the write rules (who may modify what).
- [ ] Implement the decorator and apply it to the write routes only.
- [ ] Remove `/token` and its use in `app.component.ts` `loginBase()`.
- [ ] Allow-list `modify` fields; fix `set_json`.
- [ ] Frontend: send the token on all calls (a single `HttpInterceptor`).
- [ ] Tests: 401 without token, 403 for another player's character, 403 for non-admin on admin routes.

## Respect-the-owner checklist
- [ ] Dedicated branch, not `main`.
- [ ] No unrelated reformatting.
- [ ] No deletion of working code without flagging (`/token`, `hasRight()`, `Config.authorization`).
- [ ] Behaviour change and operational impact flagged in the PR.

## DOCUMENTATION — required
- [ ] `documentation/CHANGELOG.md` entry.
- [ ] `pm/STATUS.md` refreshed.
- [ ] *Outcome* filled.
- [ ] *Files touched* filled.
- [ ] `documentation/02-web-to-discord.md` updated if the token rules change.

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| `api/app.py` | 36-47 | route table with rules | central enforcement |
| `api/views.py` | 110-130, 202-231, 299, 375, 408-422 | auth, allow-list, removals | see Context |
| `database/charactertable.py` | `set_json` | fix `role`/`player` | bug |
| `config.py` | 8 | drop `authorization` | no optional auth |
| `AngrySenechal2/src/app/*.ts` | — | interceptor, remove `/token` login | keep the UI working |

## Before / after
- **Before:** anyone can read/modify any character, mint tokens and read all tokens.
- **After:** reads stay open; writes follow the owner's rules; tokens come only from Discord OAuth.
- **Behaviour-changing?** yes (see Operational impact).

## Verification
- **How tested:** `curl` each route without/with a foreign token; run the Angular app logged in and logged out.
- **How the owner can reproduce:** the new tests.

## Risk & rollback
- **Risk:** locking out legitimate flows (e.g. NPC reads for logged-out visitors); breaking the web page if the frontend deploy lags.
- **Rollback:** `git revert <sha>` on both repos.

## Outcome  *(fill on completion)*
- **Result:**
- **CHANGELOG entry:**
- **Commit(s):**
