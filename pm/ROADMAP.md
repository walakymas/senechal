# Roadmap

> Forward-looking direction. Items are grouped **Now / Next / Later** by priority, not
> by date. Everything here is a *proposal* pending owner approval unless marked
> otherwise. Sourced largely from `documentation/01-code-review.md`.

## Now (in flight)

- **Collaborator workflow & documentation** — branch policy, `documentation/`, task
  system, `pm/`. *(mostly done — Task 001)*

## Next (highest value, smallest risk)

- **Security hardening** — env-based `SECRET_KEY`, `DEBUG=False`, re-enable CSRF, real
  token validation. *(Task 002, proposed — behaviour-changing, needs owner approval)*
- **Clear bug fixes** — broken `cleanupTokens` SQL (`web/views.py:339`), doubled embed
  fields (`utils.py:451+`), `message.channelsend` typo (`commands/base_command.py:32`).

## Later (larger or lower-urgency)

- **Dependency & runtime upgrade** — pin `requirements.txt`; move off EOL Django 3.1
  and Python 3.9.5.
- **Testing & CI** — add `pytest` around the pure logic (dice/check/feast) + GitHub
  Actions; add `ruff`/`black`.
- **Code hygiene** — de-duplicate `utils.py`; remove secret-leaking `print()`s.
- **Data-layer consolidation** — the web app uses raw `psycopg2` while the Django ORM
  and migrations sit unused; pick one path.
- **Repo cleanup** — remove the committed `senechal.db` from version control.

## Explicitly out of scope (for now)

- Rewriting the architecture or the command/plugin system (it works well).
- Changing game rules / domain behaviour.
