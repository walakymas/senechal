# Task 009: Passion categories (Fidelitas / Fervor / Adoratio / Civilitas)

## Metadata
- **ID:** 009
- **Status:** `in-progress`
- **Type:** `behaviour-changing`
- **Branch:** `collab/passion-categories` (backend, `senechal/`); the Angular part lives in the separate `AngrySenechal2` repo and needs its own branch/PR there.
- **Created:** 2026-10-05
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** none (no DB, API, env var or stored-data change). Discord embeds, the PDF sheet, the static sheet and the Angular views change their passion layout.

## Context
- **Problem / motivation:** passions were shown as one flat list everywhere. The campaign uses the Pendragon passion categories and wants them shown.
- **Related review finding:** none
- **Definition of done:** every passion display groups the passions under Fidelitas, Fervor, Adoratio, Civilitas, Other; stored data is unchanged.

## Scope
- **In scope:** a derived category (first word of the passion name, with an alias table for existing misspellings), and grouped display in `!me passions`, `!check`, `!login`, the PDF sheet, the static `sheet.js`, and the Angular character-detail, npc-detail, npc-detail2 and team views.
- **Out of scope:** DB/API/`character.py`, stored passion names, `senechal_old.py`, `chargen`, the Angular `PassionDialog` (a type/target picker is a possible follow-up), `feast.json` guest `passion:` traits.

## Plan
- [x] `passions.py` (`passion_category`, `group_passions`) + `tests/passions_test.py`
- [x] Discord embeds, PDF, static sheet
- [x] Angular helper + `passionGroups` pipe, templates, spec
- [ ] Angular build/tests, PDF render and live bot run (not possible yet, see Verification)

## Respect-the-owner checklist
- [x] Working on a dedicated branch, not `main`.
- [x] No unrelated reformatting, renaming, or import re-ordering.
- [x] No deletion of working code.
- [x] Behaviour-changing edits flagged in *Before / after*.

## DOCUMENTATION — required (do not set Status to `done` until all checked)
- [ ] Added a `documentation/CHANGELOG.md` entry.
- [ ] Refreshed `pm/STATUS.md`.
- [ ] Filled the *Outcome* section.
- [x] Listed every file touched.

## Files touched
| File | Change | Rationale |
|------|--------|-----------|
| `passions.py` (new) | category table, aliases, `group_passions` | single source of the rules |
| `tests/passions_test.py` (new) | unit tests with real passion names | |
| `utils.py` | `!me passions` grouped | |
| `commands/check.py`, `commands/login.py` | Passions embed field grouped | |
| `pdf/sheet.py` | category sub-headings in `passions()` | |
| `static/sheet.js`, `static/css/senechal.css` | grouped list, `.passion-cat` | |
| `AngrySenechal2/src/app/passion-category.ts` (+ `.spec.ts`) (new) | TS mirror of the rules + `passionGroups` pipe | |
| `AngrySenechal2/src/app/app.module.ts` | declare the pipe | |
| `AngrySenechal2/.../character-detail`, `npc-detail`, `npc-detail2`, `team` templates (+ `team.component.ts`) | grouped rendering | |
| `AngrySenechal2/src/styles.css` | `.passion-cat` | |

## Before / after
- **Before:** flat passion list (alphabetical on Discord, JSON order elsewhere).
- **After:** grouped by category in fixed order, names sorted inside a group on Discord/PDF-side helper; unmatched names (e.g. `Directed Trait ...`, `Heritage (Place)`) under **Other**. The rules exist twice (Python and TS/JS) and must be kept in sync.
- **Behaviour-changing?** yes (display only).

## Verification
- **Done:** `python tests/passions_test.py` (3 tests OK); `py_compile` on the edited Python files; `node --check static/sheet.js`.
- **Not done:** `AngrySenechal2/node_modules` is empty and `package-lock.json` is out of sync with `package.json`, so `npm ci` fails and the Angular build/spec were not run. `fpdf` is not installed locally, so the PDF was not rendered. The bot was not run against a database.
- **How the owner can reproduce:** `npm install && npx ng test --include='**/passion-category.spec.ts'`; `!me passions`, `!c`; open a character, an NPC and the team view.

## Risk & rollback
- **Risk:** the PDF sheet column gets taller (one extra line per category); the Discord Passions field is longer (embed field limit 1024 chars).
- **Rollback:** `git revert <sha>`.

## Outcome  *(fill on completion)*
- **Result:**
- **CHANGELOG entry:**
- **Commit(s):**
