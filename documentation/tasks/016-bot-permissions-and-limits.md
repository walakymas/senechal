# Task 016: Bot permission checks, dice limits, mention safety

## Metadata
- **ID:** 016
- **Status:** `proposed`
- **Type:** `behaviour-changing`
- **Branch:** `collab/bot-permissions`
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** `!reload`, `!set`, `!db`, `!info`, `!images` become rights-protected, so the owner must have `playerrights` set (as for `!admin`, Task 010). Very large dice commands are rejected.

## Context
- **Problem / motivation:** only `commands/admin.py:26-29` checks rights. Anyone can run `!reload` (restart, `git pull` when `pull` is set), `!set` (rewrite global config, e.g. `debugdice`), `!db` (read/write `properties`, incl. `hook`), `!info` (all member/channel ids) and `!images`. `!999999999d6` and damage loops block the event loop. Replies can ping `@everyone`.
- **Related review finding:** `03-security-audit.md` §5 (rows 8-9, 13, 25).
- **Definition of done:** the protected commands refuse non-admins; dice/damage input is clamped; the bot is created with `AllowedMentions.none()`; the reaction handler is guarded.

## Scope
- **In scope:**
  - `required_rights` attribute on `BaseCommand`, enforced in `message_handler.handle_command` (reuse `PlayerTable.rights`).
  - Apply to `reload`, `set`, `db`, `info`, `images`, and the destructive branches of `event` / `mark`.
  - Clamp dice: count ≤ 100, size 2..1000 (as `api/views.py:258`) in `dicing.py:9-29`, `message_handler.py:36-45`, `utils.py:505,519`, `commands/weapon.py:39,56`; reject `d0`.
  - `discord.AllowedMentions.none()` at `senechal.py:27`.
  - Reaction handler (`senechal.py:75-97`): rights/role check, size and extension limit, `None` guards, directory from config.
  - Ignore bot authors in `on_message`; do not re-run commands from `on_message_edit`.
- **Out of scope:** bug fixes in `weapon.py` / `feast.py` logic (Task 018); data-layer changes (Task 017).

## Plan
- [ ] Add `required_rights` and the enforcement check.
- [ ] Mark the commands; ask the owner which `event`/`mark` branches count as destructive.
- [ ] Clamp dice and damage; share one helper.
- [ ] `AllowedMentions.none()`.
- [ ] Harden the reaction handler.
- [ ] `on_message` / `on_message_edit` changes.
- [ ] Tests for the dice limits (`pytest`).

## Respect-the-owner checklist
- [ ] Dedicated branch, not `main`.
- [ ] No unrelated reformatting.
- [ ] No deletion of working code without flagging.
- [ ] Behaviour change and operational impact flagged in the PR.

## DOCUMENTATION — required
- [ ] `documentation/CHANGELOG.md` entry.
- [ ] `pm/STATUS.md` refreshed.
- [ ] *Outcome* filled.
- [ ] *Files touched* filled.
- [ ] Command help texts mention required rights.

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| `commands/base_command.py`, `message_handler.py` | — | rights enforcement | central rule |
| `commands/reload.py`, `set.py`, `db.py`, `info.py`, `images.py` | — | set `required_rights` | privilege |
| `dicing.py`, `utils.py`, `commands/weapon.py` | see Scope | clamps | DoS |
| `senechal.py` | 27, 55-97 | mentions, reaction handler, message events | safety |

## Before / after
- **Before:** any Discord user can reconfigure/restart the bot or stall it with a huge dice roll.
- **After:** admin-only for those commands; dice are bounded.
- **Behaviour-changing?** yes (see Operational impact).

## Verification
- **How tested:** run each command as an admin and a normal user on a test server; `!1000000d6` is rejected; a message containing `@everyone` does not ping.
- **How the owner can reproduce:** same steps.

## Risk & rollback
- **Risk:** locking the owner out if their `playerrights` is not set.
- **Rollback:** `git revert <sha>`.

## Outcome  *(fill on completion)*
- **Result:**
- **CHANGELOG entry:**
- **Commit(s):**
