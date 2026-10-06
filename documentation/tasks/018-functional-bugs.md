# Task 018: Functional bug fixes (weapon, feast, parsing, character)

## Metadata
- **ID:** 018
- **Status:** `in-review`  <!-- implemented, unit-tested, not run on a live Discord server, not committed -->
- **Type:** `behaviour-changing`  <!-- game results change where the old code was wrong -->
- **Branch:** `collab/functional-bugs`  <!-- branched from `collab/data-layer-stability` (Task 017) -->
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** none for deployment. `!weapon` results change where the old logic crashed or used the wrong damage roll; `!c <name> …` / `!pc <name>` now really filter by name; `!lord stewardship|horses` store the value.

## Context
- **Problem / motivation:** logic bugs found in `03-security-audit.md` §6. (The audit's line numbers for `character.py` were wrong; the real locations are below.)
- **Related review finding:** `03-security-audit.md` §5-6 (rows 22-23, 25).
- **Definition of done:** each bug below is fixed or explicitly deferred with the reason. Met; see Outcome.

## Owner decisions used
- **`check2` (skill above 20) is intended, not a bug** (2026-10-06): above 20 the check always succeeds, the excess is added to the roll, a total of 20 or more is a critical success (+4d6 damage). Pinned by tests, documented in `utils.check2`; criticals add 4 damage dice in `embed_attack` and `Weapon.embed` (verified).
- **Alias collisions** (2026-10-06): remove `l` from Lord and `tel` from Token.
- **Not yet decided by the owner** (so implemented conservatively and flagged below): the `!weapon` wound rule, `effective_dexterity`.

## Scope
- **Done:**
  - `commands/weapon.py`: the attacker's and the opponent's damage rolls are separate variables (`dmg_sum`, `odmg_sum`). Before, `sum` was shared, so a fumble/fail with a winning opponent and no opponent damage dice raised `UnboundLocalError`, and the wound was computed from the wrong roll. The wound is now the **opponent's** damage minus the character's protection (shield + armor when both succeeded and the opponent rolled higher; armor only when the character failed). Without opponent damage dice no wound is computed. `Weapon.knocked` used to append to a string passed by value (the text was lost); it now returns the text, and `Weapon.wound` builds the wound / major wound / knocked-down text.
  - `feast.py`: the new row's id is used (`FeastTable.insert` returns it with `RETURNING cid`, so `Feast(None)` no longer keeps `id = -1`); round keys are strings everywhere (`set_round_action` could not find its own round after a save/reload, so the "action already set" guard failed and a card could be drawn again); `select_card` used the builtin `round`; `setAction` used a non-existent `round` key; `add_participiant` ignores an unknown character; `card_enabled` crashed (iterated over int card ids, undefined variable) and now implements the evident rule: a Host card is always enabled, a card mandatory for one of the character's significant stats is enabled and disables the other cards of the round.
  - `commands/feast.py` (`!lakoma`): `randint(1, 154)` (there are 154 cards; 155 would be an image that does not exist).
  - `character.py`: `Character.pcs(name)` now filters by name (`!c <name> <spec>` rolled for **every** PC; `check.py` / `login.py` pass `None` for the `---` default so the no-argument behaviour is unchanged); bare `except` in `get_weapon` narrowed; removed the `"stewardship_": 13` default (the trailing underscore made it harmless; without it `winterData` still uses the character's own stewardship, as documented).
  - Parsing: modern mentions `<@id>` are stripped like `<@!id>` (`utils.strip_mention`, used by `senechal.py` and `bot_bridge.py`); `get_me` no longer crashes on an empty command, `cid:abc` or a role mention, and a lone `!` is not a name (`ILIKE '%%'` matched the first character). `message_handler` catches `ValueError` / `IndexError` from a command and replies with a hint instead of dying silently (covers the unchecked `params[N]` / `int()` spots in `db`, `mark`, `event`, `attack`, `images`, `token`); `!db` checks its parameter count.
  - Stale `Config.characters` code: removed `Config.pcs` / `Config.npcs`; `!winter <arg>` uses `Character.pcs()`; `!me` for an unknown user answers instead of crashing; `!db list lord|mark` and `!mark` (no character) use the current table columns and `Character` objects; `!lord` stores `params[1]` (horses: the comma-joined rest), checks the value is given, and its `list` uses the right columns and `LordTable.list(lord=…)`.
  - Library drift: `emojize(language='alias')`; `client.send_message` → `channel.send` (`send_in_channel`, `try_upload_file`).
  - `winter.py`: `randint` → `dice()` (so `debugdice` applies, like the other rolls).
  - Alias collisions (owner decision: remove them): `Lord` lost its `l` alias (`!l` is the Feast command, also `!lakoma`; Lord is `!lord`) and `Token` lost its `tel` alias (a copy-paste leftover; `!tel` is Winter, the web page uses `!token <id>`). `message_handler` also prints a warning at start-up if a clash ever reappears; `AliasTest` checks there is none.
- **Left open (owner decisions):**
  - `Character.effective_dexterity` (`character.py:77`) is `str + armor red + shield red`, which looks wrong, but nothing uses it. Delete it, or fix once the rule is known?
  - The `!weapon` wound rule above (opponent's damage minus the character's protection) is my reading of the code's intent; please confirm.
  - `Feast.card_enabled` rule above is my reading of the card text ("Discard this card when you draw a Host card or a mandatory card"); nothing calls it yet.
  - `pdf/test_sheet.py` still uses `Config.characters` (a manual script, not a test) — remove in Task 020.
- **Out of scope:** dead-code removal (`senechal_old.py`, Task 020).

## Plan
- [x] Owner confirmed the `check2` rule.
- [x] Fix per module, with tests for the pure logic (`tests/functional_bugs_test.py`).
- [x] Remove or repair the `Config.characters` leftovers.
- [ ] Owner decisions listed under *Left open*.

## Respect-the-owner checklist
- [x] Dedicated branch, not `main`.
- [x] No unrelated reformatting.
- [x] Deleted code flagged: `Config.pcs` / `Config.npcs` (referenced the removed `Config.characters`), the `"stewardship_"` default key.
- [x] Behaviour change flagged.

## DOCUMENTATION — required
- [x] `documentation/CHANGELOG.md` entry.
- [x] `pm/STATUS.md` refreshed.
- [x] *Outcome* filled.
- [x] *Files touched* filled.

## Files touched
| File | Change |
|------|--------|
| `commands/weapon.py` | separate damage sums, `wound()` / `knocked()` return text |
| `feast.py`, `database/feasttable.py`, `commands/feast.py` | id from `RETURNING cid`, string round keys, `select_card`, `setAction`, `card_enabled`, card range |
| `character.py` | `pcs(name)` filter, narrowed `except`, removed `stewardship_` |
| `utils.py` | `strip_mention`, hardened `get_me`, `check2` comment, emoji / `send_message` drift |
| `senechal.py`, `bot_bridge.py` | mention stripping, empty command guard |
| `message_handler.py` | alias clash warning, `ValueError` / `IndexError` reply |
| `commands/lord.py`, `commands/token.py` | removed the clashing aliases `l` and `tel` |
| `config.py` | removed stale `pcs` / `npcs` |
| `commands/check.py`, `login.py`, `winter.py`, `me.py`, `db.py`, `mark.py`, `lord.py` | see Scope |
| `tests/functional_bugs_test.py` (new), `tests/database_integration_test.py` | 25 unit tests, 1 integration test |

## Before / after
- **Before:** `!weapon` could crash or use the wrong roll; `!c <name> <spec>` rolled for all PCs; feast actions could be repeated; `!db list lord|mark`, `!mark` (no character), `!me` (unknown user), `!winter <arg>` crashed; malformed parameters died silently.
- **After:** see Scope.
- **Behaviour-changing?** yes (see Operational impact).

## Verification
- **How tested:** `venv/Scripts/python.exe -m unittest discover -s tests -p "*_test.py"` — 54 tests pass (12 skipped without a database); with a throwaway PostgreSQL 14 the 12 integration tests pass, including the new feast id test. Not run on a live Discord server.
- **How the owner can reproduce (test server):** `!w <weapon> 0 <opponent skill>` with and without opponent damage dice; `!c <name part> <skill>` as a GM; `!tel`/`!l` still run Winter/Lord; `!db set prop`, `!mark remove`, `!event 5` (missing parameters) answer with a hint; `!lord stewardship 15`; a roll with `<@id>` mention.

## Risk & rollback
- **Risk:** changing results the group got used to (`!weapon` wounds); `!db list …` output format; the `RETURNING` insert needs the fresh Task 017 data layer.
- **Rollback:** `git revert <sha>`.

## Outcome  *(fill on completion)*
- **Result:** implemented as in *Scope — Done*; 54 unit tests pass (12 more with a database).
- **CHANGELOG entry:** 2026-10-06 — Functional bug fixes (Task 018)
- **Commit(s):** not committed yet
