# Task 027: Storyteller roll log page

- **ID / Status / Type:** 027 · `in-review` · `behaviour-changing`
- **Branch:** `collab/gm-roll-log` (backend) · `main` of `AngrySenechal2`, uncommitted (frontend) · **Created:** 2026-10-16 · **Reviewed via PR:** (not opened)

## Context
The roll results show only as a popup (Task 023) on the character page, and only the last one of the user's own / current character. The storyteller wants to see the last 100 rolls at once, in the same look, optionally only those of one player.

## Scope
- `GET /checks` accepts `limit` (1..100, default stays 10) and `player` (id; only the rolls of that player's characters). Bad numbers → 400.
- New frontend page `/rolls` ("Rolls" in the menu): the last 100 rolls one under the other, a *Player* filter (All / one player, labelled by their characters), refreshed every 5 s, the filter is remembered in `localStorage`.
- The popup card became the shared `check-card` component (`CheckCardComponent`), used by the popup (`CheckResultDialog`) and the new page. No look change in the popup.
- Not in scope: access control (the page, like `/checks`, is open — task 015 covers API auth), filtering by a single character.

## Operational / behaviour impact
- `/checks` without parameters answers exactly as before. New optional parameters only.
- New route `/rolls` and menu item for everybody (there is no storyteller role in the frontend).
- No new env vars or migrations.

## Documentation (required)
- [x] `documentation/CHANGELOG.md` entry added.
- [x] `pm/STATUS.md` refreshed.

## Verification & rollback
- **Checked:** `tests/checks_view_test.py` (4 tests) pass; `ng build --configuration development` succeeds. Not seen in a browser, not run against a live database.
- **Rollback:** `git revert` the backend commit; `git checkout` the frontend files (`app.module.ts`, `app-routing.module.ts`, `app.component.html`, `character.service.ts`, `character-detail.component.ts`) and delete `check-card/`, `rolls/`.
