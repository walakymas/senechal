# Task 008: Character ownership ("My character" / "Activate")

## Metadata
- **ID:** 008
- **Status:** `in-review`
- **Type:** `behaviour-changing`
- **Branch:** `collab/character-ownership`
- **Created:** 2026-10-05
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** none (no env vars, no migration). `POST /user` gets an extra `did` field; `characters.player` is now actually written by `modify`.

## Context
- **Problem / motivation:** the web UI needs to let a logged-in user claim a character (`characters.player`) and make it their active one (`player.character`). `CharacterTable.set_json` computed `player` but never stored it, so the column could not be set from the UI.
- **Related review finding:** none
- **Definition of done:** the character-sheet menu has "My character" (only if the character has no owner) and "Activate" (only for own or unowned characters); both persist.

## Scope
- **In scope:** persist `characters.player` in `set_json`; expose `player` in the character response; `did` in `/user`; two Angular menu items + service method.
- **Out of scope:** server-side authorisation (`hasRight` is still token-presence only), un-claiming a character.

## Plan
- [x] Backend: write `characters.player`, return it from `Character`, add `did` to `/user`.
- [x] Frontend: `setCharPlayer`, `claim()`, `activate()`, menu items.

## Respect-the-owner checklist
- [x] Working on a dedicated branch, not `main`.
- [x] No unrelated reformatting, renaming, or import re-ordering.
- [x] No deletion of working code.
- [x] Behaviour-changing edits flagged below; the PR is the review gate.

## DOCUMENTATION — required
- [x] `documentation/CHANGELOG.md` entry.
- [x] `pm/STATUS.md` refreshed.
- [x] Outcome filled.
- [x] Files touched listed.

## Files touched
| File | Change | Rationale |
|------|--------|-----------|
| `database/charactertable.py` | `set_json` also `UPDATE characters SET player` when `player` is in the JSON | the column was never written |
| `character.py` | `data['player']` from `characters.player` column | frontend needs the owner |
| `api/views.py` | `user()` returns `did` (string, Discord ids exceed JS safe ints) | `updatePlayer` needs the user's did |
| `AngrySenechal2/src/app/character.service.ts` | `setCharPlayer()` | modify with only `player` |
| `AngrySenechal2/src/app/character-detail/character-detail.component.{ts,html}` | `claim()`, `activate()`, `canClaim()`, `canActivate()`, two menu items | feature |

## Before / after
- **Before:** `characters.player` could not be set from the UI; no way to claim/activate a character.
- **After:** "My character" sets `characters.player` = user id. "Activate" sets the owner if empty, then `player.character` = character id (via `updatePlayer`). Activate is hidden when another user owns the character or another Discord member is already linked to it.
- **Behaviour-changing?** yes (see Operational impact).

## Verification
- **How tested:** `py_compile` on the Python files. Angular build / manual UI test **not run** (no `node_modules` here).
- **How the owner can reproduce:** log in via Discord, open an unowned character, use the menu next to the name.

## Risk & rollback
- **Risk:** `modify` accepts any token; `player` from JSON is now persisted to the column for every `set_json` call that carries it.
- **Rollback:** `git revert <sha>`.

## Outcome
- **Result:** implemented, unverified in the browser.
- **CHANGELOG entry:** 2026-10-05
- **Commit(s):** <!-- pending -->
