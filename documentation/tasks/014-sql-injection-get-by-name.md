# Task 014: Fix SQL injection in `get_by_name`

## Metadata
- **ID:** 014
- **Status:** `in-review`  <!-- implemented, not run against a live DB, not committed -->
- **Type:** `behaviour-changing`  <!-- search input is now treated literally, not as SQL -->
- **Branch:** `collab/sql-injection-fix`
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** none. Searches containing `%`, `_` or `'` now match literally.

## Context
- **Problem / motivation:** `database/charactertable.py:37` builds `f"SELECT * FROM characters WHERE name ILIKE '%{name}%'"`. It is reachable without authentication from `GET /json?ch=` (`api/views.py:147`), from `newchar` (`api/views.py:199`) and from Discord (`utils.py:121-123`, any last argument starting with `!`).
- **Related review finding:** `03-security-audit.md` §3 (row 4). The only user-influenced string-built SQL in the project.
- **Definition of done:** the query is parameterised, `%` / `_` are escaped, and a `pytest` case proves `x'; --` is treated as a name.

## Scope
- **In scope:** `CharacterTable.get_by_name`; a regression test; a quick `Grep` that no other f-string SQL takes user input (`database/database.py:208` formats an int — parameterise it too).
- **Out of scope:** authentication of `/json` (Task 015).

## Plan
- [x] Replace with `execute("SELECT * FROM characters WHERE name ILIKE %s", ['%' + escaped + '%'], fetch='one')`.
- [x] Escape `\`, `%`, `_` in `name` (PostgreSQL's default LIKE escape character is `\`, so no `ESCAPE` clause is needed).
- [x] Add `tests/` case (needs a test DB or a stubbed `execute`).
- [x] Parameterise `database/database.py:208`.

## Respect-the-owner checklist
- [x] Dedicated branch (`collab/sql-injection-fix`), not `main`.
- [x] No unrelated reformatting.
- [x] No deletion of working code.
- [x] Behaviour change flagged.

## DOCUMENTATION — required
- [x] `documentation/CHANGELOG.md` entry.
- [x] `pm/STATUS.md` refreshed.
- [x] *Outcome* filled.
- [x] *Files touched* filled.

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| `database/charactertable.py` | 36-43 | `like_pattern()` helper + parameterised `get_by_name` | remove injection |
| `database/database.py` | 208 | parameterise the `dbversion` update | consistency |
| `tests/character_table_test.py` | new | 3 unit tests (stubbed DB driver) | regression guard |

## Before / after
- **Before:** `!c str !x'…` or `/json?ch=x'…` is executed as SQL.
- **After:** the text is a literal name pattern.
- **Behaviour-changing?** yes, only for names containing wildcards or quotes.

## Verification
- **How tested:** `curl "…/json?ch=x'%20OR%20'1'='1"` returns "not found", not a row; normal name lookups unchanged.
- **How the owner can reproduce:** run the new test.

## Risk & rollback
- **Risk:** a player relying on `%` wildcards in a name search.
- **Rollback:** `git revert <sha>`.

## Outcome  *(fill on completion)*
- **Result:** `get_by_name` passes the name as a query parameter with `\`, `%`, `_` escaped; the `dbversion` update in `database.py` is parameterised; a `Grep` found no other f-string SQL (only `f"SELECT * FROM {table}"` in `base_table_handler.py`, where `table` is a constant). `python -m unittest tests.character_table_test` passes (3 tests). Not yet exercised against a live PostgreSQL.
- **CHANGELOG entry:** 2026-10-06 — Fix SQL injection in `get_by_name` (Task 014)
- **Commit(s):** not committed yet
