# Task 025: Feast card data in `feast.yml` (cards 10, 12–154)

- **ID / Status / Type:** 025 · `in-review` · `behaviour-changing` (a few keys are read by the engine)
- **Branch:** `collab/feast-rules` · **Created:** 2026-10-10 · **Reviewed via PR:** (not opened)

## Context
Task 024 left "card effects in `feast.yml`" open. Only cards 1–9 and 11 had `check:` data.

## Scope
Fill `check:` (declarative), `keep:` and `mandatory:` for the remaining cards from their `full` text, add a short `text:` where missing, and leave a `# TODO(feast-check): …` comment wherever the card is doubtful or incomplete. Not in scope: engine code that evaluates `check:`.

## Operational / behaviour impact
- `keep: {geniality, draw}` on cards 37, 44, 56, 58, 66, 67, 68, 118 and `mandatory: indulgent` on cards 92–107 **are read by the engine** (`feast.py`) and change a running feast.
- `text:` added to every card that lacked it.
- Everything else is inert data.

## Documentation (required)
- [x] `documentation/feast-cards.md` (conventions, impact, list of doubtful cards).
- [x] `documentation/CHANGELOG.md` entry added.
- [ ] `pm/STATUS.md` refreshed.

## Verification & rollback
- **Checked:** `feast.yml` loads with PyYAML; every pre-existing field of every card is identical before/after; unit tests unchanged (4 import errors for the missing `discord` package exist with and without the change). Not run in a live feast.
- **Rollback:** `git checkout -- feast.yml`.
