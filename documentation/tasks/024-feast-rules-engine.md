# Task 024: Feast rules engine (Book of Feasts)

## Metadata
- **ID:** 024
- **Status:** `in-progress`  (phases 0, 1, 3 and 4 of the feast rework; Discord is left)
- **Type:** `behaviour-changing`
- **Branch:** `collab/feast-rules` (from `main`)
- **Created:** 2026-10-09
- **Reviewed via PR:** not opened
- **Operational impact:** none (no new env vars, no migration: old `feast` rows get the new fields with defaults on load). The legacy `POST /feast` actions now need a session (host right; `roundAction` also the owner), and `GET /feast` answers 404 instead of creating a feast when there is none: the new frontend (`AngrySenechal2`, branch `collab/feast-ui`) uses the new endpoints; **deploy the backend and that frontend branch together** (the old frontend can no longer run the feast). A feast that is already running changes behaviour: cards are drawn from 1000 Glory (inclusive), unknown actions are refused, and Above the Salt guests cannot draw on the server side either.

## Context
- **Problem / motivation:** the feast was half-finished: seating, Geniality, activity results, leaving and the end-of-feast Glory of the Book of Feasts were missing; the draw restrictions were only hidden in the UI.
- **Related review finding:** none
- **Definition of done (phases 0-1):** the rules are in `feast_rules.py` + `documentation/feast-rules.md`, `Feast` uses them, unit tests pass.

## Scope
- **In scope:** `feast_rules.py`, `feast.py`, `Deck` size from `feast.yml`, `feastConfig` no longer mutates the shared config, tests, docs.
- **Out of scope:** Discord (Phase 5), coding the card effects in `feast.yml`, the optional rules (Stewardship roll, ceding, Honor loss).

## Plan
- [x] Phase 0: rules specification (`documentation/feast-rules.md`)
- [x] Phase 1: rules engine and `Feast` refactor, tests
- [x] Phase 3: explicit API endpoints, authorisation (`api/feast_views.py`, `feast_api_test.py`)
- [x] Phase 4: frontend (`AngrySenechal2`, branch `collab/feast-ui`)

## Respect-the-owner checklist
- [x] Dedicated branch, not `main`.
- [x] No unrelated reformatting, renaming, or import re-ordering.
- [x] Replaced code is listed in *Before / after* (`number_of_cards`, the duplicated draw code, `significant`).
- [x] Behaviour-changing edits flagged above.

## DOCUMENTATION — required
- [x] `documentation/CHANGELOG.md` entry.
- [x] `pm/STATUS.md` refreshed.
- [ ] *Outcome* filled (when the task is done).
- [x] Files touched listed.
- [x] `documentation/feast-rules.md` added.

## Frontend (`AngrySenechal2`, branch `collab/feast-ui`, from `main`)
`feast.component` is now a container with `feast-setup` (new feast, APP roll, seating by hand, next round), `feast-round` (activity, rolls, hand, play/keep/discard, leave/return), `feast-scoreboard` (guests in the order of drawing, seating) and `feast-log`; `feast-util.ts`; `character.service.ts` has the new calls (`feastPost` shows the reason of a refusal) and no longer the legacy `seatGuest`/`setRounds`/`setAction`/`nextState`; `lord.ts` types match the data. The card images base URL is `feastImages` in `environment*.ts` (optional, default as before). Verified: `ng build` (development), `ng test` 66/66 in headless Chrome. **Not run in a browser against the API.**

## Files touched
| File | Change | Rationale |
|------|--------|-----------|
| `feast_rules.py` | new | pure rules of the book |
| `feast.py` | changed | uses the rules; new `seat_by_app`, `record_result`, `keep_card`, `discard_kept`, `leave`, `return_to_feast`, `set_royal`, `end_round`, `finish`; one draw path (`_draw_for`); `Deck` ids from `feast.yml` |
| `api/views.py` | `feast`, `feastConfig` | `feastConfig` works on a copy (it put `loginNeeded` into the shared card config); legacy `feast` actions need a session, GET never creates |
| `api/feast_views.py` | new | the new feast endpoints (session, ownership, server-side rolls) |
| `api/app.py` | routes | registers them |
| `tests/feast_api_test.py` | new | the endpoints with mocked tables |
| `tests/feast_rules_test.py` | new | rules and feast flow |
| `documentation/feast-rules.md` | new | rules <-> code table |

## Before / after
- **Before:** `number_of_cards` used `>` (1000 Glory drew nothing), draws were not restricted on the server, `significant` only looked at `stats` (so `mandatory: lustful` never matched), `next_state` only counted rounds, no Geniality, leaving or final Glory.
- **After:** see `documentation/feast-rules.md`.
- **Behaviour-changing?** yes (see Operational impact).

## Verification
- **How tested:** `venv/Scripts/python.exe -m unittest discover -s tests -p "*_test.py"` -> 128 tests OK (25 skipped: they need `TEST_DATABASE_URL`).
- **How the owner can reproduce:** same command; `python -m unittest tests.feast_rules_test`.

## Risk & rollback
- **Risk:** the server-side draw restriction changes a running feast; a Host card now disables the other cards (`Feast.card_enabled`), as the book says; the legacy frontend does not send the host session for non-hosts (players could seat/start before, now cannot).
- **Rollback:** `git revert` the branch's commits.
