# Task 010: Admin rights, `setChannel`, remove `!admin save`

## Metadata
- **ID:** 010
- **Status:** `done` (merged: PR #8, commit `a730ef2` "noHook")
- **Type:** `behaviour-changing`
- **Branch:** `collab/passion-categories`
- **Created:** 2026-10-05
- **Reviewed via PR:** walakymas/senechal#8
- **Operational impact:** (1) `!admin save` and the `!save` alias are **gone** — the bot no longer takes the yearly history snapshot. (2) `!admin` now needs `player.playerrights > 0` with bit 0 set; the two admins seeded by the migration (`1023`) keep access. (3) Two new `properties` key families (below), written only by the new commands.

## Context
- **Problem / motivation:** user-facing messages should appear in a configurable channel; the yearly save task was no longer wanted; `!admin` was open to everyone (`hidden` only hides it from help).
- **Definition of done:** channels can be set per bot and per player; `!admin` is rights-protected.

## Scope
- **In scope:** `!admin setChannel`, `!me setChannel`, the rights check, removal of `save`.
- **Out of scope:** *reading* the stored channel (Task 011), other commands' authorisation.

## Behaviour
- `!admin setChannel` → `properties` key `<prefix>channel` = id of the current channel (the bot's default channel).
- `!me setChannel` → key `<prefix>channel<player id>` (`player.cid`, found by the author's Discord id; if the author is not in `player` the bot says it does not know them). No special rights needed.
- Any `!admin …`: `PlayerTable().rights(author id)` must be `> 0` and `rights & 1`, otherwise the bot answers that the user lacks permission.
- `<prefix>` is `Config.prefix` (default `!`), e.g. the keys `!channel` and `!channel12`.

## Files touched
| File | Change |
|------|--------|
| `commands/admin.py` | `save` task and `save` alias removed; `setChannel`; rights check; description updated |
| `commands/me.py` | `setChannel` task + help line |
| `database/playertable.py` | `rights(did)` helper |

## Before / after
- **Before:** `!admin save` stored the year's stats/traits/passions/skills into `history` for every PC; anyone could call `!admin`.
- **After:** as under *Behaviour*. Existing `history` data in characters is untouched; nothing writes it any more.

## Verification
- **Done:** `py_compile` of the three files. **Not done:** a live run against Discord/PostgreSQL.
- **How the owner can reproduce:** as an admin run `!admin setChannel` in a channel and as a player `!me setChannel`; `!db list prop` shows the keys; a user without rights is refused by `!admin setChannel`.

## Risk & rollback
- **Risk:** anything relying on `!admin save` (a yearly routine) stops working; the meaning of `playerrights` (bit 0 = admin) is assumed from the `1023` seed.
- **Rollback:** `git revert a730ef2` (this also reverts Task 011).

## DOCUMENTATION
- [x] CHANGELOG entry · [x] `pm/STATUS.md` · [x] this file · [x] `documentation/02-web-to-discord.md`

## Outcome
- **Result:** per-bot and per-player channel keys, rights-protected `!admin`, `save` removed.
- **CHANGELOG entry:** 2026-10-05 — Admin rights, setChannel (Task 010)
- **Commit(s):** `a730ef2` (merged in `431bdd7`)
