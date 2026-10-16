# Task 028: Marks status, winter and mark update

- **ID / Status / Type:** 028 · `in-review` · `behaviour-changing`
- **Branch:** `collab/marks-winter-status` (backend) · `main` of `AngrySenechal2`, uncommitted (frontend) · **Created:** 2026-10-16 · **Reviewed via PR:** (not opened)

## Context
`!winter` only printed d20 rolls for the marked skills / traits / passions; nothing was stored and nothing raised the values. The winter must be repeatable without re-rolling, and the web page must be able to start it and to apply the increases.

## Scope
- `marks.status`: `Unchecked` (new marks), `Failed`, `Increase`, `Updated` (migration v19; existing marks become Unchecked).
- Winter roll per Unchecked mark: d20 ≤ value → Failed; d20 > value, or a 20 when the value is over 20 → Increase. Checked marks are reported from their status. `!winter force` (admin only; checked with `permissions.has_rights`) rolls all but the Updated ones again.
- The whole winter report is stored as a new event (glory 0) of the character in the current year, also by the web Winter.
- Update: `!mark update` (current year of the character) and web *Update* (any year) raise the Increase marks by one in the stored character JSON (raw data, not the fallback-extended one) and set them Updated. A trait's opposite pole raises by lowering the stored value; unknown marks stay Increase.
- API: `GET /marks`, `POST /marks_update`, `POST /winter` (token; owner or admin; `force` admin only).
- Frontend: *Marks* popup (accordion per year, *Update*) and *Winter* dialog in the character menu.
- Not in scope: the economy/horse rolls are not remembered (a repeated winter re-rolls them), the Extra Glory is only reported (as before), the connected characters' marks are rolled (as before) but updated only on their own pages / with `!mark update` for them, access control of the old `mark` / `event` calls (task 015).

## Operational / behaviour impact
- Migration v19 on start. Existing marks become Unchecked → the next `!winter` rolls the current year's marks.
- Each `!winter` run adds an event to the character.
- Winter's main-character marks block no longer shows the Modified date; the check uses the plain d20 rule above instead of `check()`.
- New API calls; the frontend needs the new backend (without it the menu items fail with a "Request failed" message).

## Documentation (required)
- [x] `documentation/CHANGELOG.md` entry added.
- [x] `pm/STATUS.md` refreshed.

## Verification & rollback
- **Checked:** `tests/winter_marks_test.py` (17 tests: status rule, mark resolution, winter, update, force right, API rights) and the DB test `test_mark_status` + the v19 migration on a throwaway PostgreSQL 14 (150 backend tests pass); frontend: 66 tests incl. `marks.spec.ts` and the marks dialog, `ng build --configuration development`. Not run on a live server, not seen in a browser.
- **Rollback:** `git revert` the backend commit and `git checkout` the frontend files; the `status` column can stay.
