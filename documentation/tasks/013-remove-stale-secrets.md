# Task 013: Remove stale secrets from tracked files

## Metadata
- **ID:** 013
- **Status:** `in-review`  <!-- edits made, not committed yet -->
- **Type:** `behaviour-preserving`
- **Branch:** `collab/remove-stale-secrets`
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** none for the running app. The removed values were stale (confirmed by the collaborator). The webhook that `/base` returns (`Config.hook`, from the `properties` table) is **kept on purpose** for now.

## Context
- **Problem / motivation:** `03-security-audit.md` §1 found a Discord bot token in a comment and a Discord webhook URL in the production frontend environment. Both are stale but still readable in tracked files and git history.
- **Related review finding:** `03-security-audit.md` §1 (rows 1-2).
- **Definition of done:** neither value is present in the working tree; nothing in the code referenced them.

## Scope
- **In scope:** delete the commented `BOT_TOKEN` line in `settings.py`; delete the `hook` field in `AngrySenechal2/src/environments/environment.prod.ts`.
- **Out of scope:** `/base` still returns `Config.hook` (the web page needs it for logged-out users, see Task 011); git history rewrite; `.gitignore` changes (Task 020).

## Plan
- [x] Confirm nothing reads `environment.hook` (the frontend takes `hook` from the `/base` response: `character.service.ts:132`).
- [x] Remove the `BOT_TOKEN` comment from `settings.py`.
- [x] Remove `hook` from `environment.prod.ts`.
- [ ] Owner decides whether to rewrite history (`git filter-repo`) — optional, since the values are stale.
- [ ] Verify the live webhook in `properties.hook` and the live bot token are *different* from the removed ones; rotate them if not.

## Respect-the-owner checklist
- [ ] Working on a dedicated branch, not `main`.
- [x] No unrelated reformatting, renaming, or import re-ordering.
- [x] No deletion of working code (a comment and an unused field only).
- [x] Behaviour-changing edits are flagged — none.

## DOCUMENTATION — required
- [ ] Added a `documentation/CHANGELOG.md` entry.
- [ ] Refreshed `pm/STATUS.md`.
- [ ] Filled the *Outcome* section.
- [x] Listed every file touched.

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| `settings.py` | 7-8 | removed the commented bot token | stale secret in a tracked file |
| `AngrySenechal2/src/environments/environment.prod.ts` | 5 | removed `hook` | stale webhook in the production bundle |

## Before / after
- **Before:** both values were in tracked files (and in the built `dist/` bundle of the frontend).
- **After:** removed from the working tree. The Angular build no longer embeds the webhook; a rebuild is needed for `dist/` to change.
- **Behaviour-changing?** no.

## Verification
- **How tested:** `Grep` for `BOT_TOKEN` and `hook` under `AngrySenechal2/src`; `npm run build` after `npm install`.
- **How the owner can reproduce:** `git grep -n "discord.com/api/webhooks"` returns nothing in the working tree.

## Risk & rollback
- **Risk:** none expected; `environment.hook` was unused.
- **Rollback:** `git revert <sha>`.

## Outcome  *(fill on completion)*
- **Result:**
- **CHANGELOG entry:**
- **Commit(s):**
