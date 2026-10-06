# Task 014: Fix SQL injection in `get_by_name`

## Metadata
- **ID:** 014
- **Status:** `proposed`
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
- [ ] Replace with `execute("SELECT * FROM characters WHERE name ILIKE %s", ['%' + escaped + '%'], fetch='one')`.
- [ ] Escape `\`, `%`, `_` in `name` (add `ESCAPE '\'`).
- [ ] Add `tests/` case (needs a test DB or a stubbed `execute`).
- [ ] Parameterise `database/database.py:208`.

## Respect-the-owner checklist
- [ ] Dedicated branch, not `main`.
- [ ] No unrelated reformatting.
- [ ] No deletion of working code.
- [ ] Behaviour change flagged.

## DOCUMENTATION — required
- [ ] `documentation/CHANGELOG.md` entry.
- [ ] `pm/STATUS.md` refreshed.
- [ ] *Outcome* filled.
- [ ] *Files touched* filled.

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| `database/charactertable.py` | 37 | parameterised query | remove injection |
| `database/database.py` | 208 | parameterise | consistency |
| `tests/…` | new | regression test | no tests exist yet |

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
- **Result:**
- **CHANGELOG entry:**
- **Commit(s):**
