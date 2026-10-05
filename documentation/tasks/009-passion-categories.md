# Task 009: Passion categories (Fidelitas / Fervor / Adoratio / Civilitas)

## Metadata
- **ID:** 009
- **Status:** `done` (merged: PR #7; the frontend part is in the `AngrySenechal2` repo, commit `Passion kategóriák`)
- **Type:** `behaviour-changing` (display only)
- **Branch:** `collab/passion-categories`
- **Created:** 2026-10-05
- **Reviewed via PR:** walakymas/senechal#7
- **Operational impact:** none — no DB, API, env var or stored-data change. Discord embeds, the PDF sheet, the static sheet and the Angular views change their passion layout. The Angular part must be deployed for the web UI to change.

## Context
- **Problem / motivation:** passions were shown as one flat list everywhere; the campaign uses the Pendragon passion categories.
- **Related review finding:** none
- **Definition of done:** every passion display groups the passions by category, stored data unchanged.

## Scope
- **In scope:** a derived category (first word of the passion name + alias table for existing misspellings), grouped display in `!me passions`, `!check`, `!login`, the PDF sheet, the static `sheet.js`, and the Angular character-detail, npc-detail, npc-detail2 and team views.
- **Out of scope:** DB/API/`character.py`, stored passion names, `senechal_old.py`, `chargen`, the Angular `PassionDialog` (a type/target picker is a possible follow-up), `feast.json` guest `passion:` traits.

## Rules (as delivered)
- Category = first word of the name, case-insensitive: Fidelitas `duty, fealty, homage, loyalty`; Fervor `hate, love`; Adoratio `adoration, devotion`; Civilitas `chivalry, hospitality, station`. Aliases: `fealthy→fealty`, `hospitability→hospitality`, `amor→adoration`.
- **Everything else is `Other`** (e.g. `Honor`, `Directed Trait …`, `Heritage (Place)`). `Other` is shown **first and without a heading**; then Fidelitas, Fervor, Adoratio, Civilitas.
- Each category heading shows the **sum of its passions in brackets**, e.g. `Fervor (27)`. A sum **above 40** is highlighted red (`PASSION_WARN_TOTAL = 40`): red text in the PDF/web, `:red_circle:` + bold on Discord (embeds have no colours). The team view shows the sum per character column.
- The stored name is never changed (marks, checks, `modifyProp('passions.<name>')`, history keep working).

## Files touched
| File | Change | Rationale |
|------|--------|-----------|
| `passions.py` (new) | `PASSION_CATEGORIES`, aliases, `passion_category`, `group_passions`, `passion_total` | single source of the rules |
| `tests/passions_test.py` (new) | unit tests with real passion names | |
| `utils.py` | `!me passions` grouped | |
| `commands/check.py`, `commands/login.py` | Passions embed field grouped | |
| `pdf/sheet.py` | category sub-headings with total in `passions()` | |
| `static/sheet.js`, `static/css/senechal.css` | grouped list, `.passion-cat`, `.passion-warn` | |
| `AngrySenechal2/src/app/passion-category.ts` (+ `.spec.ts`) (new) | TS mirror of the rules + `passionGroups` pipe | |
| `AngrySenechal2/.../app.module.ts` | declare the pipe | |
| `AngrySenechal2/.../character-detail`, `npc-detail`, `npc-detail2`, `team` templates (+ `team.component.ts`) | grouped rendering | |
| `AngrySenechal2/src/styles.css` | `.passion-cat`, `.passion-warn` | |

## Before / after
- **Before:** flat passion list (alphabetical on Discord, JSON order elsewhere).
- **After:** grouped as described under *Rules*. The rules exist in three places (Python, TS, and a JS copy in `static/sheet.js`) and must be kept in sync.

## Verification
- **Done:** `python tests/passions_test.py` (3 tests OK); `py_compile` of the edited Python files; `node --check static/sheet.js`.
- **Not done:** the Angular build/spec (`AngrySenechal2/node_modules` is empty and `package-lock.json` is out of sync with `package.json`, so `npm ci` fails), PDF rendering (`fpdf` not installed locally), a live bot run.
- **How the owner can reproduce:** `npm install && npx ng test --include='**/passion-category.spec.ts'`; `!me passions`, `!c`; open a character, an NPC and the team view; check a character with a category above 40.

## Risk & rollback
- **Risk:** the PDF passion column gets taller (one heading line per category); the Discord Passions field is longer (embed field limit 1024 chars).
- **Rollback:** `git revert` commit `8e7865c` (backend) and the matching frontend commit.

## DOCUMENTATION
- [x] `documentation/CHANGELOG.md` entry · [x] `pm/STATUS.md` refreshed · [x] this file

## Outcome
- **Result:** passions are grouped by category on every display, with per-category totals.
- **CHANGELOG entry:** 2026-10-05 — Passion categories (Task 009)
- **Commit(s):** `8e7865c` (merged in `782d288`)
