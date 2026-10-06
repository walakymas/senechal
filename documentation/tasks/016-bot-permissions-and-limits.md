# Task 016: Bot permission checks, dice limits, mention safety

## Metadata
- **ID:** 016
- **Status:** `in-review`  <!-- implemented, unit-tested, not run on a live Discord server, not committed -->
- **Type:** `behaviour-changing`
- **Branch:** `collab/bot-permissions`  <!-- branched from `collab/sql-injection-fix` (Task 014, uncommitted at the time) -->
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** `!reload`, `!set`, `!info`, `!images` and most of `!db` need `playerrights` with bit 0 set (the same rule as `!admin`, Task 010) — **the owner must have it set, otherwise they lock themselves out of `!reload`**. Dice rolls above 100 dice or a die size above 1000 are refused. The archived-attachment directory can be set with `picturesDir` in the config (default unchanged: `/var/www/senechalPictures`).

## Context
- **Problem / motivation:** only `commands/admin.py` checked rights. Anyone could run `!reload` (restart, `git pull` when `pull` is set), `!set` (rewrite the global config, e.g. `debugdice`), `!db` (read/write `properties`, incl. `hook`), `!info` (all member/channel ids) and `!images`. `!999999999d6` and the damage loops blocked the event loop. Replies could ping `@everyone`.
- **Related review finding:** `03-security-audit.md` §5 (rows 8-9, 13, 25).
- **Definition of done:** the protected commands refuse non-admins; dice/damage input is clamped; user echo cannot ping `@everyone`/roles; the reaction handler is guarded. All met; see Outcome.

## Scope
- **Done:**
  - `permissions.py`: `has_rights(did, bits=ADMIN)` (same rule as `!admin`: `playerrights` with bit 0), `NO_RIGHTS` text.
  - `message_handler.handle_command` enforces an optional `required_rights` class attribute of a command (`getattr(..., 0)`); `help` stays available to everyone. **`BaseCommand` is not modified** (its header says "Do not modify!"), commands just define the attribute.
  - `required_rights = ADMIN` on `Reload`, `Set`, `Info`, `Images`.
  - `!db`: admin for everything except `!db set lord` (a player setting their own lord data, kept open).
  - Dice: `utils.MAX_DICE_COUNT = 100`, `MAX_DIE_SIZE = 1000`, `check_dice_limits()`; `dicing.roll_dice` raises `ValueError` with a Hungarian message, `message_handler` replies with it. Damage dice loops are capped at 100 (`utils.embed_attack`, `commands/weapon.py`). `d1` stays allowed (the web `roll` endpoint allows it too); `d0` is refused instead of crashing.
  - Client: `AllowedMentions(everyone=False, roles=False, users=True)` — no `@everyone` / `@here` / role pings from echoed text; user mentions still notify.
  - `on_message` / `on_message_edit` ignore bot authors.
  - Reaction handler (`senechal.py`) and `!images`: only archive images/pdf/mp4/webm (`utils.PICTURE_EXTENSIONS`; no html/svg/js, which would be served from the web origin), `os.path.basename` on file names, `None` guards (no channel / reaction in a DM), directory from `pictures_dir()` (`picturesDir` config, same default).
- **Left open on purpose (owner decisions needed):**
  - `!event remove|modify` and `!mark remove` take a bare id and work for anyone (`commands/event.py:24-30`, `commands/mark.py:33`). Which branches count as destructive, and who may use them (the owner of the row? admins?), is the owner's call — same open question as the write rules in Task 015.
  - `on_message_edit` still re-runs commands (editing a message re-rolls dice). It looks intentional (typo fixes), so it was not changed; say if it should go.
  - The 👀 / 🗺️ reactions are still open to every member (players use them to get picture links; 🗺️ adds to `maps`). Restricting 🗺️ to admins is a one-line change if wanted.
- **Out of scope:** bug fixes in `weapon.py` / `feast.py` logic (Task 018); data-layer changes (Task 017).

## Plan
- [x] `permissions.py` and enforcement in `message_handler.py`.
- [x] Mark the commands; `!db` special case for `set lord`.
- [x] Clamp dice and damage dice; shared constants in `utils.py`.
- [x] `AllowedMentions`.
- [x] Harden the reaction handler and `!images`.
- [x] Ignore bot authors.
- [x] Tests (`tests/bot_permissions_test.py`).
- [ ] Try it on a test server (see Verification).
- [ ] Owner decides the open points above.

## Respect-the-owner checklist
- [x] Dedicated branch, not `main`.
- [x] No unrelated reformatting.
- [x] No deletion of working code; `BaseCommand` untouched.
- [x] Behaviour change and operational impact flagged (above); the PR is the review gate.

## DOCUMENTATION — required
- [x] `documentation/CHANGELOG.md` entry.
- [x] `pm/STATUS.md` refreshed.
- [x] *Outcome* filled.
- [x] *Files touched* filled.
- [ ] Command help texts mention required rights (not done: the `help` text is built in `BaseCommand`, which is not modified).

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| `permissions.py` | new | `has_rights`, `ADMIN`, `NO_RIGHTS` | one rights rule for all commands |
| `message_handler.py` | imports, 39-48, 58-60 | `required_rights` check; refuse out-of-range dice | enforcement |
| `commands/reload.py`, `set.py`, `info.py`, `images.py` | class attribute | `required_rights = ADMIN` | privilege |
| `commands/db.py` | `handle` | admin check except `set lord` | `properties` / download exposure |
| `commands/weapon.py` | damage loops | cap at `MAX_DICE_COUNT` | DoS |
| `utils.py` | dice section, `embed_attack` | limits, `check_dice_limits`, `pictures_dir`, `is_archivable`, damage cap | shared helpers |
| `dicing.py` | `roll_dice` | validate count and size | DoS, `d0` crash |
| `senechal.py` | client, `common_handle_message`, reaction handler | mentions, bot authors, attachment guard | safety |
| `tests/bot_permissions_test.py` | new | 11 unit tests | regression guard |

## Before / after
- **Before:** any Discord user could reconfigure/restart the bot, read `properties`, or stall it with a huge dice roll; replies could ping `@everyone`.
- **After:** admin-only for those commands; dice bounded; no mass pings; the archiver only stores image/pdf/video files.
- **Behaviour-changing?** yes (see Operational impact). Players also lose `!info`, `!images` and `!db` prop/list/download.

## Verification
- **How tested:** `venv/Scripts/python.exe -m unittest discover -s tests -p "*_test.py"` — 17 tests pass (6 of them Task 014). Not run against a live Discord server.
- **How the owner can reproduce (test server):**
  1. As a user without `playerrights`: `!reload`, `!set debugdice 6`, `!info`, `!images`, `!db list prop` → "Nincs jogosultságod ehhez a parancshoz"; `!reload help` still answers; `!db set lord …` still works.
  2. As an admin (bit 0 set): the same commands work.
  3. `!101d6`, `!d0`, `!5d1001` → refusal text; `!4d20`, `!2d6+1` as before.
  4. A reply containing `@everyone` does not ping; a normal user mention still does.
  5. React 👀 to an image → link DM as before; to an `.html` file → skipped (console: `skipped …`).

## Risk & rollback
- **Risk:** the owner locked out of `!reload` if `playerrights` is not set; players relying on `!info` / `!images`; rare legitimate attachment types (add them to `PICTURE_EXTENSIONS`).
- **Rollback:** `git revert <sha>`.

## Outcome  *(fill on completion)*
- **Result:** implemented as listed under *Scope — Done*; 17 unit tests pass.
- **CHANGELOG entry:** 2026-10-06 — Bot permission checks, dice limits (Task 016)
- **Commit(s):** not committed yet
