# Task 018: Functional bug fixes (weapon, feast, parsing, character)

## Metadata
- **ID:** 018
- **Status:** `proposed`
- **Type:** `behaviour-changing`  <!-- game results change where the old code was wrong -->
- **Branch:** `collab/functional-bugs`
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** none to deployment. Some roll results change where the old logic was wrong; ask the owner to confirm the intended Pendragon rules before changing them.

## Context
- **Problem / motivation:** a set of logic bugs found in `03-security-audit.md` §6.
- **Related review finding:** `03-security-audit.md` §5-6 (rows 22-23, 25).
- **Definition of done:** each bug below is fixed or explicitly deferred with the owner's reason.

## Scope
- **In scope:**
  - `commands/weapon.py:35,74,89`: `sum` shadowing / `UnboundLocalError`, wound computed from the wrong value, `Weapon.knocked` return value ignored.
  - `feast.py`: `:154` builtin `round`; `:11,20` `id = -1` after insert; `:181-183` `'round'` vs `'rounds'`; `:194` int vs str keys; `:35-37` `None` character; `commands/feast.py:17` `randint(1, 155)` vs `range(1, 155)`.
  - `character.py`: `Character.pcs(name)` ignores `name` (`:709`; users `check.py:28`, `login.py:22`); `effective_dexterity` (`:609`); typo `stewardship_` (`:565`); bare `except` (`:621`).
  - Argument parsing: `<@id>` mentions (`senechal.py:55`), empty input `IndexError` (`message_handler.py:36`, `bot_bridge.py:55`), unchecked `params[N]` (`db.py:24-39`, `token.py:15`, `mark.py:33`, `event.py:34,38`), `int()` on user text (`utils.py:398`, `attack.py:19`, `images.py:19`, `event.py:24`).
  - Stale `Config.characters` code: `commands/db.py:28,33`, `config.py:80,87`, `commands/me.py:44`, `commands/winter.py:24`, `commands/lord.py`, `commands/mark.py:51-52`; the known `!lord stewardship|horses` bug (stores the keyword instead of the value).
  - Library API drift: `utils.py:75` (`client.send_message`), `utils.py:31` (`emojize(use_aliases=True)`); `winter.py:117` uses `randint` instead of `dice()`.
  - Alias collisions (`tel`, `l`): log duplicates at registration (`message_handler.py:21-25`).
  - `check2` (`utils.py:395-412`): **keep the current behaviour — it is the intended rule** (owner, 2026-10-06). When a skill grows above 20 through a modifier, using it always succeeds; the part above 20 is added to the rolled value, and if the sum is 20 or more it is a critical success, which deals 4d6 extra damage. Only add a `pytest` case that pins this rule and a comment in the code stating it; verify the 4d6 extra damage is applied wherever a critical is evaluated (`utils.py`, `commands/weapon.py`).
- **Out of scope:** dead-code removal (`senechal_old.py`, Task 020).

## Plan
- [x] Owner confirmed the `check2` rule (see Scope).
- [ ] Owner confirms intended rules for `weapon` wounds and the alias collisions.
- [ ] Pin the `check2` rule with a test; check that critical successes add 4d6 damage in `weapon.py`.
- [ ] Fix per module, one commit each, with a `pytest` case for the pure logic (`weapon`, `feast`, argument parsing).
- [ ] Remove or repair the `Config.characters` leftovers.

## Respect-the-owner checklist
- [ ] Dedicated branch, not `main`.
- [ ] No unrelated reformatting.
- [ ] No deletion of working code without flagging.
- [ ] Behaviour change flagged.

## DOCUMENTATION — required
- [ ] `documentation/CHANGELOG.md` entry.
- [ ] `pm/STATUS.md` refreshed.
- [ ] *Outcome* filled.
- [ ] *Files touched* filled.

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| see Scope | | | |

## Before / after
- **Before:** crashes and wrong results in the cases listed.
- **After:** correct results or a clear error message.
- **Behaviour-changing?** yes.

## Verification
- **How tested:** `pytest`; manual runs of `!attack`, `!feast`, `!c <name> <skill>`, empty and malformed commands on a test server.
- **How the owner can reproduce:** same steps.

## Risk & rollback
- **Risk:** changing results the group got used to.
- **Rollback:** `git revert <sha>` per commit.

## Outcome  *(fill on completion)*
- **Result:**
- **CHANGELOG entry:**
- **Commit(s):**
