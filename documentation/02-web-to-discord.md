# Web → Discord: channels, dice and commands

How the Angular character page talks to the bot since Tasks 010–011. Passion categories
(Task 009) are described in `tasks/009-passion-categories.md`.

## Channels (`properties` table)

| Key | Set by | Meaning |
|-----|--------|---------|
| `<prefix>channel` | `!admin setChannel` (needs `playerrights > 0` and bit 0) | default channel for user-facing messages |
| `<prefix>channel<player id>` | `!me setChannel` | the player's own channel (`player.cid`) |

Lookup order for a web action: player's channel → default channel → `Config.mainChannel`.

## Endpoints (`api/app.py`, `api/views.py`)

Both need a valid token (`token` form field); the bot must run in the same process (`server.py`).

- `POST /roll` — `dice` (`4d20`, `d6`, `2d6+3`), `id` (character). Rolls server-side, saves the roll in `checks`, posts ``<character> (`!4d20`): 12+2= 14``.
- `POST /command` — `command` (e.g. `c Sword 0 cid:5`). Runs the real command handler as if typed in the channel, after a line ``<character>: `!c Sword 0` ``. Only `WEB_COMMANDS` (`check`, `team`) are allowed.

## Moving parts

- `bot_bridge.py` — filled by `server.py` with the Discord client and its loop; API worker threads use `run_coroutine_threadsafe` to send messages / run commands. `WebMessage` and `WebAuthor` mimic the parts of `discord.Message` / `Member` that the whitelisted commands use (`content`, `channel`, `guild`, `author.id/name/display_name/mention`). A command that needs more (DMs, reactions, `add_reaction`) must not be added to `WEB_COMMANDS` without extending them.
- `dicing.py` — `roll_dice(count, size, modifier)`; used by the `!4d20` handling in `message_handler.py` and by `/roll`.

## Logged-out users

The Angular `CharacterService.isLoggedIn()` (token present and `userName` set) decides: logged in → `/roll` and `/command`; logged out → the old webhook post (`CharacterService.bot`). The login handshake (`token <id>`) always uses the webhook, because the token is only enabled by that command.
