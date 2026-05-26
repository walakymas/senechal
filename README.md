# Senechal

A Discord bot and web companion for running **King Arthur Pendragon** tabletop-RPG
campaigns. Built for an active Hungarian-speaking gaming group, so much of the in-chat
text is in Hungarian.

## What it does

- **Character sheets** — stats, traits, passions, skills, combat gear, and the winter
  phase, viewable in Discord and exportable to PDF.
- **Dice & checks** — inline dice rolls (`2d6+1`) and trait / skill / passion / stat
  checks with criticals, fumbles, and opposed rolls.
- **Campaign tracking** — marks (*pipák*), glory and events, and the feast card-deck
  mechanic.
- **Web companion** — a JSON API (plus PDF export) consumed by an external front-end for
  browsing and editing characters.

## Architecture

| Part | Where | Notes |
|------|-------|-------|
| Discord bot | `senechal.py` | `discord.py`; runs as the Heroku `worker`. |
| Web app | `web/` | Django + gunicorn; JSON API and PDF export. |
| Shared core | `character.py`, `config.py`, `utils.py`, `feast.py` | Domain model, config, dice/checks, feast logic. |
| Data layer | `database/` | PostgreSQL via `psycopg2` (handler-per-table). |
| Commands | `commands/` | Plugin pattern — drop a `BaseCommand` subclass in to add one. |

Adding commands and events follows the original template's plugin pattern, documented in
[`documentation/original-template-readme.md`](documentation/original-template-readme.md).

## Requirements

- Python 3.9 (see [`runtime.txt`](runtime.txt))
- PostgreSQL
- A Discord bot token

## Configuration

Configuration comes from environment variables and YAML/JSON files:

- `token` — Discord bot token *(required)*
- `DATABASE_URL` — PostgreSQL connection URL *(required; the data layer connects on import)*
- `prefix`, `mainChannel` — optional overrides (default prefix is `!`)
- `config.yml` — optional local config (gitignored); may hold the above
- `senechal.yml`, `feast.json` — game data (rules, weapons, armours, feast deck)

> Keep secrets in the environment or `config.yml` (gitignored) — do not commit them.

## Running locally

```bash
# Discord bot
python senechal.py

# Web app (development)
python manage.py runserver
# or, as in production:
gunicorn web.wsgi
```

## Deployment

Heroku, via the [`Procfile`](Procfile): a `worker` process (the bot) and a `web` process
(gunicorn serving the Django app).

## Repository docs

- [`CLAUDE.md`](CLAUDE.md) — guidance for AI agents and contributors (how to run, gotchas, workflow).
- [`documentation/`](documentation/) — code review, changelog, and the task system used for changes.
- [`pm/`](pm/) — current status, roadmap, and decision log.
- [`documentation/original-template-readme.md`](documentation/original-template-readme.md) — the original template README (command/event guide, `utils` helpers).

## Credits

The bot scaffolding is based on the
[discord-bot-template](https://github.com/agubelu/discord-bot-template) by *agubelu*.

## License

GPL-3.0 — see [`LICENSE`](LICENSE).
