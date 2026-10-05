# Task 011: Web page dice rolls and commands without the webhook

## Metadata
- **ID:** 011
- **Status:** `in-review` (backend merged in PR #8 / `a730ef2`; the logged-out webhook fallback is in the `AngrySenechal2` working tree and not committed yet)
- **Type:** `behaviour-changing`
- **Branch:** `collab/passion-categories` (backend), `AngrySenechal2` `main` (frontend)
- **Created:** 2026-10-05
- **Reviewed via PR:** walakymas/senechal#8
- **Operational impact:** the HTTP API must run **in the bot process** (`server.py`, Procfile `web`); with the standalone `senechal.py` worker the new endpoints answer `"result": "not sent"`. Backend and frontend must be deployed together (the new Angular calls `/roll` and `/command`). Logged-in users no longer need the Discord webhook for these actions; logged-out users still use it.

## Context
- **Problem / motivation:** the dice and commands of the character page were posted by a webhook ("Captain Hook") as `!…` messages. They should appear in the user's own channel and show which command ran.
- **Definition of done:** a logged-in user's dice rolls and `c` / `check` / `team` commands are executed by the server and shown in the user's channel; logged-out users keep the webhook.

## Scope
- **In scope:** `POST /roll`, `POST /command`, `bot_bridge.py`, `dicing.py`, Angular `CharacterService.roll/command/isLoggedIn` and the character-detail / team call sites.
- **Out of scope:** the login handshake `token <id>` (the token is not valid yet, so it stays on the webhook); other commands (extend `WEB_COMMANDS`).

## Behaviour
- Both endpoints need a **valid, non-expired token** (`tokens` joined with `player`), otherwise HTTP 403.
- **Channel:** `<prefix>channel<player id>` → `<prefix>channel` → `Config.mainChannel`.
- `POST /roll` (`token`, `dice`, `id` = character): `dicePattern` must match fully, at most 100 dice, die size 1–1000 (else 400). It rolls with `dicing.roll_dice`, stores the result in `checks` (so the page's last-roll view keeps working) and posts ``<character name> (`!4d20`): 12+2+1+6= 21``.
- `POST /command` (`token`, `command` without the prefix, e.g. `c Sword 0 cid:5`): only commands named in `WEB_COMMANDS = ('check', 'team')` (aliases resolved through `message_handler.COMMAND_ALIASES`), otherwise 400. The real handler runs on the bot loop with a message stand-in (`WebMessage` / `WebAuthor`); before its output the channel shows ``<character name>: `!c Sword 0` `` (the `cid:` / `<@!…>` target is stripped).
- **Frontend:** `CharacterService.isLoggedIn()` = token present and `userName` set (`AppComponent` sets it after the token is validated). Logged in → `roll` / `command`; otherwise the old webhook call (`bot()`) with the old `cid:` / `<@!id>` target.
- The dice code moved from `message_handler.py` to `dicing.py` (`roll_dice`); the output of the `!4d20` command is unchanged.

## Files touched
| File | Change |
|------|--------|
| `api/views.py`, `api/app.py` | `roll`, `command` views and routes, channel lookup |
| `bot_bridge.py` (new) | thread-safe bridge from API threads to the Discord client (`send`, `run_command`) |
| `dicing.py` (new), `message_handler.py` | dice helper extracted; the dispatcher uses it |
| `server.py` | hands the client and its loop to `bot_bridge` |
| `AngrySenechal2/src/app/character.service.ts` | `roll`, `command`, `isLoggedIn` |
| `AngrySenechal2/.../character-detail.component.ts`, `team.component.ts` | API when logged in, webhook otherwise |

## Before / after
- **Before:** every dice button and command was a webhook message `!…`, answered by the bot in the webhook's channel.
- **After:** as under *Behaviour*.

## Verification
- **Done:** `py_compile`; `roll_dice` and `dicePattern` exercised with a stubbed `utils` (`4d20`, `d6`, `2d6-1`, invalid specs).
- **Not done:** a live Discord/DB run, the Angular build and spec (empty `node_modules`).
- **How the owner can reproduce:** log in on the web page, press D20 or click a skill → a message with the command appears in the channel set by `!me setChannel` (else `!admin setChannel`, else the main channel); log out → the old webhook message appears.

## Risk & rollback
- **Risk:** authorisation is token validity only (any valid token can roll or run checks for any character id, as `modify` already allows); the whitelist keeps admin/db commands out. If the bot is not connected the web action shows nothing in Discord (`"not sent"` in the response).
- **Rollback:** `git revert a730ef2` (this also reverts Task 010) and the frontend commit.

## DOCUMENTATION
- [x] CHANGELOG entry · [x] `pm/STATUS.md` · [x] this file · [x] `documentation/02-web-to-discord.md`

## Outcome
- **Result:** a logged-in web user's dice and check commands run server-side in their own channel, labelled with the command; the webhook is kept for logged-out users and the login handshake.
- **CHANGELOG entry:** 2026-10-05 — Web commands without the webhook (Task 011)
- **Commit(s):** `a730ef2` (backend); frontend `6881f1c` (+ the uncommitted webhook fallback)
