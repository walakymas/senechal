# Changelog

A detailed, chronological log of every change made by collaborators. Newest entries
at the top. See `README.md` for the entry format and the "respect the owner's code"
principles.

Each entry states whether it is **behaviour-preserving** (no observable runtime
difference) or **behaviour-changing** (requires owner/collaborator approval).

---

## 2026-10-06 — Performance and logging (Task 021)

- **Branch:** `collab/performance` (from `collab/infra-and-deps`)
- **Type:** behaviour-preserving (same answers, fewer queries), plus three small flagged changes
- **Summary:** measured first (`tests/query_count_test.py`), then removed the N+1 queries. SQL statements per call, 6 / 24 characters: `/players` 5 / 14 → **2 / 2**; `Character.pcs()` 4 / 13 → **1 / 1**; `/connections` (hub) 17 / 71 → **4 / 4**; `/pdfs` 19 / 73 → **5 / 5**; `/json?id=` 5 → 4; an unregistered Discord user's 5 commands 5 → **1**. How: `CharacterTable` records carry the player's `did` (no query per `Character`), `Character.get_many_by_id`, batch marks/events/glory, `CharacterTable.list_summary()` (no JSON blob) for the lists, a cached game year (`PropertiesTable.set/remove` drop it), a locked character cache with one key per kind and a 10 s negative entry. PDF: project-relative fonts/images, in-memory `/pdf` and `/pdfs` (no temp files), one team-zip build at a time reused for 30 s, sanitised zip names, safe `Content-Disposition` (ASCII `filename` + RFC 5987 `filename*`). Logging: `logs.setup_logging()` (`LOG_LEVEL`), every `print()` became a log call or was removed; message content, command arguments (at INFO), token and player records are no longer logged.
- **Behaviour changes:** `/pdfs` selects the team from the `player` table (the legacy `characters.memberid` column selected nobody for newer data); the team zip can be 30 s old; `get_by_name` / `get_by_id` pick the first player deterministically.
- **Found while testing:** the Task 020 pins (`fpdf2` 2.8.3, from the dev venv) cannot embed the sheet's variable font (`KeyError: 'fvar'`: every PDF would have failed). `requirements.txt` is re-pinned to the versions the working container ran (`fpdf2` 2.8.9, `fonttools` 4.65.0, `discord.py` 2.7.1, …); `pip check` / `pip-audit` clean, tests pass on Python 3.12.
- **Files touched:** `character.py`, `database/{charactertable,base_table_handler,proptable,markstable,eventstable}.py`, `api/views.py`, `api/compat.py`, `pdf/sheet.py`, `commands/me.py`, `logs.py` (new), `server.py`, `senechal.py`, `message_handler.py`, `utils.py`, `config.py`, `feast.py`, other `database/*.py` and `commands/*.py` (logging), `requirements.txt`, `tests/query_count_test.py` (new), `tests/performance_test.py` (new).
- **Left open:** fonts are still parsed per sheet; cached `Character` objects are still mutated in place by a few callers; the synchronous DB calls on the event loop; the Angular `trackBy` / `OnPush` (after the Angular upgrade).
- **Risk & rollback:** 91 tests pass in the Python 3.12 image against PostgreSQL 14 (none skipped); not run on a live Discord session. `git revert`.

---

## 2026-10-06 — Infrastructure, dependencies and repo hygiene (Task 020)

- **Branch:** `collab/infra-and-deps` in `senechal` and in `AngrySenechal2` (both from `collab/frontend-hardening`)
- **Type:** behaviour-preserving for the application, but it changes the build / runtime (Python 3.12, `aiohttp` 3.14.3, non-root containers)
- **Summary:** `requirements.txt` fully pinned for Python 3.12 (`pip-audit`: no known vulnerabilities; the old `aiohttp` 3.12.14 had 64; **the pin set was corrected in Task 021**: `fpdf2` 2.8.3 broke the PDFs); `Dockerfile.senechal` on `python:3.12-slim` as user `app`; Postgres published on `127.0.0.1` only; deleted `senechal_old.py` and the `.pkl` font caches (owner-approved), untracked `senechal.db*`, extended the ignore files; test stubs for `database.database` removed (they made the database tests use a fake when everything ran together). Frontend: `Dockerfile.dev` as `node`, `Dockerfile` is now a production multi-stage image serving `dist` with `server.js` (user `node`), dropped the `compression` package (known DoS advisory), removed the misnamed `dockerignore`. `npm audit` of the whole frontend recorded: 113 advisories, almost all Angular 14 (EOL) and dev tooling. Workspace `CLAUDE.md` updated.
- **Files touched:** `senechal`: `requirements.txt`, `.gitignore`, `tests/*_test.py`, deleted files; `AngrySenechal2`: `Dockerfile`, `Dockerfile.dev`, `.dockerignore`, `server.js`, `package.json`, `README.md`; workspace root: `Dockerfile.senechal`, `Dockerfile.senechal.dockerignore`, `docker-compose.yml`, `CLAUDE.md`.
- **Follow-up (owner: Heroku is gone, remove its leftovers; remove stray files; sync the lock):** deleted `Procfile` and `runtime.txt`; `static/sheet.js` / `static/team.js` use the same server instead of `senechal.herokuapp.com`, and two more hardcoded Discord webhook URLs in `static/team.js` were removed; Heroku mentions removed from `senechal/CLAUDE.md` and `server.js`; `#build#` and `AngrySenechal2.iml` removed from git; `package-lock.json` regenerated and in sync, the Dockerfiles use `npm ci`.
- **Operational impact:** rebuild the images (`docker compose build`); the old Heroku deployment files are gone.
- **Left open:** Python/Node targets and the Angular upgrade series, the systemd frontend service that runs `ng serve`, `disableHostCheck` — see the task file.
- **Risk & rollback:** verified in containers only: backend image + 62 tests including the database tests, frontend dev and production images, server tests; not deployed. `git revert` in each repo.

---

## 2026-10-06 — Frontend and Express hardening (Task 019)

- **Branch:** `collab/frontend-hardening` in `senechal` (from `collab/functional-bugs`) and in `AngrySenechal2` (from `main`)
- **Type:** **behaviour-changing** (CORS / login-return origins, map URL validation, `server.js` behaviour, build defaults)
- **Summary:** backend: allowed origins from `CORS_ORIGINS` (default list without codepen / cdpn / LAN IP; it also limits where the Discord login may return the token); the maps endpoints refuse non-http(s) URLs. Frontend: token no longer logged, failed calls show a snackbar (throttled), null-safe `setUser`, guarded `JSON.parse`, subscriptions released. `server.js`: `trust proxy`, no redirect to an unvalidated host, `helmet` with a report-only CSP, `compression`, long cache only for hashed bundles, 404 for missing assets, tests (`npm run test:server`). `ng build` defaults to production; budgets 2.2 / 3 MB.
- **Files touched:** `api/app.py`, `api/views.py`, `tests/api_hardening_test.py` (new); `AngrySenechal2`: `server.js`, `server.test.js`, `package.json`, `angular.json`, `README.md`, `src/app/app.component.ts`, `character.service.ts`, `feast-seating/feast-seating.component.ts`, `src/environments/environment.prod.ts.example`; workspace root: `docker-compose.yml`, `.env.example`.
- **Operational impact:** run `npm install` (new `helmet`, `compression`; the lockfile was not regenerated); the production build needs a local `environment.prod.ts` (git-ignored, copy the `.example`); set `CORS_ORIGINS` if a removed origin is still needed.
- **Left open:** production API URL, token storage / `Authorization` header (after Task 015), CSP enforcement, Angular performance (`trackBy` / `OnPush` / lazy routes) — see the task file.
- **Risk & rollback:** 62 backend tests pass; `server.js` tested in a `node:16-alpine` container; the production build succeeds in a container (1.96 MB initial); not run in a browser. `git revert` in both repos.

---

## 2026-10-06 — Functional bug fixes (Task 018)

- **Branch:** `collab/functional-bugs` (branched from `collab/data-layer-stability`)
- **Type:** **behaviour-changing** (`!weapon` wounds, `!c <name> …` / `!pc <name>` filtering, `!lord` values, `!lakoma` card range, aliases `!l` → Feast only, `!tel` → Winter only)
- **Summary:** `!weapon` keeps the attacker's and the opponent's damage separate (no more `UnboundLocalError`; wound = opponent's damage minus the character's protection; knocked-down / major-wound text is no longer lost). Feast: the new row's id is used, round keys are strings (an action could be repeated after a reload), `select_card` / `setAction` / `card_enabled` fixed, `!lakoma` draws 1..154. `Character.pcs(name)` filters by name; removed the harmless-by-accident `"stewardship_"` default. Mentions `<@id>` are stripped, `get_me` survives empty commands / `cid:abc` / role mentions / a lone `!`; a command that raises `ValueError` / `IndexError` answers with a hint. Stale `Config.characters` code repaired (`!db list lord|mark`, `!mark`, `!me`, `!winter <arg>`, `!lord`; removed `Config.pcs` / `Config.npcs`). discord.py 2 / emoji 2 drift fixed; `winter` uses `dice()`. The clashing aliases were removed (`l` from Lord, `tel` from Token; owner decision) and a clash is logged at start-up. The `check2` rule (skill above 20 always succeeds; total ≥ 20 is a critical, +4d6) is pinned by tests.
- **Files touched:** `commands/weapon.py`, `feast.py`, `database/feasttable.py`, `commands/feast.py`, `character.py`, `utils.py`, `senechal.py`, `bot_bridge.py`, `message_handler.py`, `config.py`, `commands/check.py`, `login.py`, `winter.py`, `me.py`, `db.py`, `mark.py`, `lord.py`, `tests/functional_bugs_test.py` (new), `tests/database_integration_test.py`.
- **Open (owner):** unused `Character.effective_dexterity` (`str` + armor + shield looks wrong), confirm the `!weapon` wound rule and the `card_enabled` rule.
- **Risk & rollback:** 54 unit tests pass (12 more with a database); not run on a live Discord server. `git revert`.

---

## 2026-10-06 — Data layer stability (Task 017)

- **Branch:** `collab/data-layer-stability` (branched from `collab/bot-permissions`)
- **Type:** **behaviour-changing** (database errors now raise instead of returning `None`; the connection is opened lazily; schema migration 18 adds unique indexes)
- **Summary:** `Database` opens the PostgreSQL connection on first use from the whole `DATABASE_URL` (keeps `?sslmode=`), reconnects when it is closed or dead (ping after 60 s idle), and fails with a clear error when `DATABASE_URL` is missing; the unused `sqlite3.connect('senechal.db')` is gone. `BaseTableHandler.execute` rolls back and re-raises. `initiate()` rolls back a failed migration; fresh installs no longer break at v13/v14 (`player.name`, duplicate `did`); migration 18 collapses duplicate `c2c` / `p2c` rows (newest kept) and adds the unique indexes the `ON CONFLICT` upserts need. Invalid SQL fixed in `lordtable`, `markstable`, `p2ctable`, `c2ctable`, `checktable`, `tokenstable`, `feasttable`, `playertable`, and `cleanupTokens` (`api/views.py`). `PropertiesTable.getValue` returns `None` for a missing key; `Config.reload` tolerates an empty schema, uses `yaml.safe_load` and UTF-8, and converts the `mainChannel` env var to int. `senechal.py`: `time.sleep` bug, the `running` flag is set only after the schema step succeeded, the schema step runs before `Config.reload()` and off the event loop. `!reload` (`git pull`) and `!me pdf` no longer block the event loop; `!db download` explains when there is no SQLite file.
- **Removed:** `database/p2ptable.py` (`P2PTable`; owner approved: its table `p2p` was never created and nothing used it).
- **Files touched:** `database/*.py` (see Task 017), `config.py`, `senechal.py`, `commands/reload.py`, `commands/me.py`, `commands/db.py`, `api/views.py`, `tests/database_integration_test.py` (new), `CLAUDE.md`s.
- **Operational impact:** **back up the database before the first start** (migration 18 deletes duplicate `c2c` / `p2c` rows). `DATABASE_URL` is now passed to libpq as is: a password with special characters must be percent-encoded. Failed writes now surface as errors in the console / HTTP 500 instead of a fake "ok".
- **Not changed:** hardcoded admin Discord ids in migration 14 (fresh installs only; owner's call), the many short synchronous DB calls on the event loop (needs an async data layer).
- **Risk & rollback:** tested against a throwaway PostgreSQL 14 (11 integration tests, plus a startup smoke test on an empty database); not run against the production data or a live Discord server. `git revert`; migration 18 is not reverted automatically (drop `idx_c2c_c0_c1`, `idx_p2c_player_character`, set `dbversion` back to 17).

---

## 2026-10-06 — Bot permission checks, dice limits, mention safety (Task 016)

- **Branch:** `collab/bot-permissions` (branched from `collab/sql-injection-fix`)
- **Type:** **behaviour-changing** (`!reload`, `!set`, `!info`, `!images` and most of `!db` need admin rights; out-of-range dice are refused; the archiver skips non-image files)
- **Summary:** `permissions.has_rights()` plus an optional `required_rights` command attribute enforced in `message_handler.handle_command` (`BaseCommand` untouched). Dice count/size limits (100 / 1000) in `dicing.roll_dice`, damage dice capped at 100. `AllowedMentions` blocks `@everyone` / roles; bot authors are ignored; the 👀/🗺️ handler and `!images` only archive image/pdf/video files, guard `None`, and read the directory from `picturesDir` (same default).
- **Files touched:** `permissions.py` (new), `message_handler.py`, `dicing.py`, `utils.py`, `senechal.py`, `commands/reload.py`, `set.py`, `info.py`, `images.py`, `db.py`, `weapon.py`, `tests/bot_permissions_test.py` (new).
- **Operational impact:** the owner needs `playerrights` with bit 0 to keep using `!reload`.
- **Open (owner decisions):** `!event remove|modify` / `!mark remove` for anyone; `on_message_edit` re-running commands; 🗺️ reaction open to all.
- **Risk & rollback:** not run on a live Discord server (17 unit tests pass). `git revert`.

---

## 2026-10-06 — Fix SQL injection in `get_by_name` (Task 014)

- **Branch:** `collab/sql-injection-fix`
- **Type:** **behaviour-changing** (a name search containing `%`, `_`, `\` or `'` now matches those characters literally)
- **Summary:** `CharacterTable.get_by_name` no longer builds the SQL with an f-string; the name is a bound parameter and LIKE wildcards are escaped (`CharacterTable.like_pattern`). The `dbversion` update in `database/database.py` is parameterised too.
- **Motivation:** `03-security-audit.md` §3 — the name came unauthenticated from `GET /json?ch=`, from `newchar` and from Discord (`!c … !name`).
- **Files touched:** `database/charactertable.py`, `database/database.py`, `tests/character_table_test.py` (new).
- **Verification:** `python -m unittest tests.character_table_test` (3 tests, stubbed driver). Not run against a live DB.
- **Risk & rollback:** a player relying on `%` as a wildcard in a name search. `git revert`.

---

## 2026-10-06 — Remove stale secrets, add audit tasks (Task 013; tasks 014-021 proposed)

- **Branch:** `main` (not committed yet)
- **Type:** behaviour-preserving
- **Summary:** removed the commented bot token from `settings.py` and the `hook` webhook URL from `AngrySenechal2/src/environments/environment.prod.ts` (both stale, confirmed by the collaborator; `environment.hook` was not referenced anywhere). `/base` still returns `Config.hook` on purpose, because the web page needs it for now. Added task files 013-021 for the audit's fix steps.
- **Files touched:** `settings.py`, `AngrySenechal2/src/environments/environment.prod.ts`, `documentation/tasks/013-…021-*.md` (new), `pm/STATUS.md`.
- **Not done:** the values remain in git history; verify that the live token and `properties.hook` differ from the removed ones, and rotate them if not.
- **Risk & rollback:** none expected. `git revert`; the Angular build needs a rebuild to drop the webhook from `dist/`.

---

## 2026-10-06 — Security, bug and performance audit (docs only)

- **Branch:** `main` (not committed yet)
- **Type:** behaviour-preserving (documentation only; no source code touched)
- **Summary:** added `documentation/03-security-audit.md`, a read-only audit of the API, the bot and data layer, the Angular frontend, Express and the Docker/deploy files, with `path:line` references and a suggested order of fixes.
- **Motivation:** collaborator asked for a review for vulnerabilities, potential bugs and optimisation opportunities. Fixes are not made here; they should become separate tasks.
- **Files touched:** `documentation/03-security-audit.md` (new), `documentation/README.md` (table row), `pm/STATUS.md`, `pm/ROADMAP.md`.
- **Headlines:** SQL injection in `database/charactertable.py:37`; most API routes unauthenticated (`hasRight()`, `/token`, `adminList`); `reload` / `set` / `db` bot commands without permission checks; unbounded dice loops; a Discord webhook URL committed in the frontend and exposed by `/base`; a bot token in a comment in `settings.py`. **Rotate** the exposed secrets.
- **Risk & rollback:** none to application behaviour. Delete the new file and revert the README / pm edits.

---

## 2026-10-06 — systemd services and deploy script (Task 012)

- **Branch:** `main`
- **Type:** behaviour-preserving (ops scripts only; no application code touched)
- **Summary:** `deploy/setup-systemd.sh` replaces the crontab `@reboot` + `run.sh` startup with systemd units (`senechal`, `senechal-ng`), moves the secrets to `/etc/senechal.env`; `deploy/deploy.sh` does `git pull` + restart without a reboot.
- **Files touched:** `deploy/setup-systemd.sh`, `deploy/deploy.sh`.
- **Operational impact:** run the setup script once on the host as the service user (sudo needed); `run.sh` becomes `run.sh.old`; rotate the Discord token/secret.
- **Risk & rollback:** not run on the host yet (`bash -n` only). `git revert`; host: disable the units, restore `run.sh` and the crontab backup.

---

## 2026-10-06 — Fix: `Character.memberid` / memberId handling

- **Branch:** `main` (not committed yet) + `AngrySenechal2`
- **Type:** **behaviour-changing** (bug fix; the PDF sheet, `!me events`/`!me pdf`, `!lord`, `!db set lord` worked again)
- **Summary:** Task 008 dropped `Character.memberid` (the `characters.memberid` column moved to the `player` table) but left its users behind: `pdf/sheet.py` (HTTP 500 on `/pdf`), `utils.embed_char` (`!me events`), `Character.npcs`, `get_memberid`, `commands/lord.py`, `commands/db.py`. `Character` now sets `memberid` from `PlayerTable.did_by_character` (an explicit `SELECT did`, instead of the fragile `player[8]` index) and `data['memberId']` from it (`None` when nobody plays the character). Also: `!me pdf` passed a data dict to `Sheet` (now the character), `!lord` read `me.memberid` before checking `me`, `me['name']` / `me['memberId']` on a `Character`, `/json` and `/players` turned a missing `memberId` into the string `'None'`; the Angular `bot()` treated `'None'` as a real member id (`<@!None>`) — it now uses `activeMemberId()`.
- **Files touched:** `character.py`, `database/playertable.py`, `api/views.py`, `commands/me.py`, `commands/lord.py`, `commands/db.py`; `AngrySenechal2`: `character-detail.component.ts`.
- **Not fixed:** `!lord stewardship|horses` store the word `stewardship`/`horses` (`params[0]`) as the value instead of `params[1]`.
- **Risk & rollback:** untested against the database. `git revert`.

---

## 2026-10-05 — Web commands without the webhook (Task 011)

- **Branch:** `collab/passion-categories` (+ `AngrySenechal2` `main`)
- **Type:** **behaviour-changing** (new endpoints `/roll`, `/command`; the web page no longer posts through the webhook when the user is logged in)
- **Summary:** a logged-in user's dice rolls and `c` / `check` / `team` commands from the character page are executed by the server and shown in the user's channel (player channel → default channel → main channel), preceded by the command that ran. Logged-out users and the login handshake keep the webhook. Dice code moved to `dicing.py`; `bot_bridge.py` connects API threads to the Discord client.
- **Files touched:** `api/views.py`, `api/app.py`, `bot_bridge.py`, `dicing.py`, `message_handler.py`, `server.py`; `AngrySenechal2`: `character.service.ts`, `character-detail.component.ts`, `team.component.ts`. See `documentation/02-web-to-discord.md`.
- **Operational impact:** the API must run in the bot process (`server.py`); backend and frontend deploy together.
- **Risk & rollback:** token validity is the only authorisation; only `check` / `team` are whitelisted. `git revert a730ef2` (also reverts Task 010) and the frontend commit.

---

## 2026-10-05 — Admin rights, setChannel (Task 010)

- **Branch:** `collab/passion-categories`
- **Type:** **behaviour-changing** (`!admin save` removed, `!admin` rights-protected, new `properties` keys)
- **Summary:** removed the `save` task and alias from `!admin`; added `!admin setChannel` (`<prefix>channel`) and `!me setChannel` (`<prefix>channel<player id>`); `!admin` now requires `playerrights > 0` with bit 0 set (`PlayerTable.rights`).
- **Files touched:** `commands/admin.py`, `commands/me.py`, `database/playertable.py`.
- **Risk & rollback:** nothing writes the yearly `history` snapshot any more. `git revert a730ef2`.

---

## 2026-10-05 — Passion categories (Task 009)

- **Branch:** `collab/passion-categories`
- **Type:** **behaviour-changing** (display only; stored data unchanged)
- **Summary:** passions are grouped by Fidelitas / Fervor / Adoratio / Civilitas (derived from the first word of the name, with aliases); everything else, including `Honor`, is `Other`, shown first without a heading. Headings show the category sum in brackets, red above 40. Discord, PDF, static sheet and the Angular character, NPC and team views.
- **Files touched:** `passions.py`, `tests/passions_test.py`, `utils.py`, `commands/check.py`, `commands/login.py`, `pdf/sheet.py`, `static/sheet.js`, `static/css/senechal.css`; `AngrySenechal2`: `passion-category.ts` (+ spec), `app.module.ts`, the four passion templates, `team.component.ts`, `styles.css`.
- **Risk & rollback:** the PDF passion column is taller; the rules live in three places (Python, TS, `sheet.js`). `git revert 8e7865c` + the frontend commit.

---

## 2026-10-05 — Character ownership: "My character" / "Activate" (Task 008)

- **Branch:** `collab/character-ownership`
- **Type:** **behaviour-changing** (`characters.player` is now written; `/user` returns `did`)
- **Summary:** two new items in the character-sheet menu. "My character" sets the owner of an unowned character; "Activate" sets the owner if empty and links the character to the user in `player.character`.
- **Files touched:** `database/charactertable.py`, `character.py`, `api/views.py`, `AngrySenechal2/src/app/character.service.ts`, `character-detail.component.{ts,html}`.
- **Risk & rollback:** `modify` authorisation is still token-presence only. `git revert`.

---

## 2026-10-03 — Remove Django (Task 007)

- **Branch:** `collab/single-process`
- **Type:** **behaviour-changing** (database tables dropped, Django admin gone)
- **Summary:** deleted `web/` and `manage.py`, moved `web/static/` to `static/`, removed
  the five Django-only packages from `requirements.txt`, dropped the 10 Django tables from
  the local database (backup taken first).
- **Files touched:** `web/*`, `manage.py`, `static/*`, `api/app.py`, `api/compat.py`,
  `requirements.txt`, `CLAUDE.md`.
- **Risk & rollback:** `git revert` restores the code; the tables can be recreated with
  Django `migrate`. **Heroku DB not touched** — owner drops the tables there.

- **Follow-up (2026-10-03):** removed `print`s that logged secrets: `DATABASE_URL` (`database/database.py`), the bot token (`config.py`), session tokens (`api/views.py` `hasRight`, `database/tokenstable.py`).

---

## 2026-10-02 — Single process: API + bot on one loop (Task 005)

- **Branch:** `collab/single-process` (off `main`)
- **Type:** **behaviour-changing** (new start command, Procfile, aiohttp instead of Django)
- **Summary:** added `server.py` and `api/` (aiohttp port of `web/views.py`); the bot client
  is built by `senechal.build_client()`; DB access serialised by `Database.lock`.
- **Files touched:** `server.py`, `api/*`, `senechal.py`, `database/database.py`,
  `database/base_table_handler.py`, `Procfile`.
- **Risk & rollback:** restore the old `Procfile`; not yet verified against a live DB.

---

## 2026-05-25 — Bug fixes: base_command typo + utils.py de-duplication (Task 004)

- **Branch:** `collab/bugfixes` (off `collab/code-review-and-docs`)
- **Type:** **behaviour-changing** (corrects doubled embed output / a crash path)
- **Approved by:** collaborator
- **Summary:** Fixed `message.channelsend` → `message.channel.send` and removed
  copy/paste duplications in `utils.py` (doubled embed fields, a double `paginator.run`,
  a doubled die roll, a dead `elif`). **Scoped to files no other open PR touches**
  (`commands/base_command.py`, `utils.py`) — no overlap with the security PR.
- **Files touched:** `commands/base_command.py`, `utils.py`.
- **Before / after:** some embeds rendered a field twice and the paginator ran twice;
  the help fallback crashed. Now each renders once and the fallback works. No game-logic
  change (the duplicate die roll only ever used the second value).
- **Risk & rollback:** low; `git revert <sha>`.

---

## 2026-05-25 — Review & refine the workflow docs (respectful review, CLAUDE.md fixes, task-lite)

- **Branch:** `collab/code-review-and-docs`
- **Type:** behaviour-preserving (docs only)
- **Approved by:** collaborator
- **Summary:** Reviewed the documentation/workflow before pushing. Rewrote the code
  review in a respectful, constructive tone (same findings and `path:line` locations,
  none removed); fixed a contradiction in `CLAUDE.md` and added run/gotcha guidance;
  added a slim "lite" task template.
- **Files changed:**
  - `documentation/01-code-review.md` — respectful rewrite; leads with strengths;
    findings reframed as opportunities (no findings dropped).
  - `CLAUDE.md` — fixed stale "approval before coding" line to match the PR-as-gate
    rule; added "Running it locally" and "Gotchas worth knowing" sections.
  - `documentation/tasks/TASK_TEMPLATE.md` — fixed stale "restate the approval" wording.
  - `documentation/tasks/README.md` — documented the full-vs-lite template choice.
- **Files added:**
  - `documentation/tasks/TASK_TEMPLATE_LITE.md` — slim template for small, low-risk,
    behaviour-preserving changes.
- **Source code touched:** none.
- **Risk & rollback:** none to application behaviour. Revert this commit.

---

## 2026-05-25 — Workflow change: the PR is the approval gate (no pre-implementation approval)

- **Branch:** `collab/code-review-and-docs`
- **Type:** behaviour-preserving (process/docs only)
- **Approved by:** collaborator
- **Summary:** Replaced the "behaviour-changing edits require owner approval before
  implementing" rule with "implement on a `collab/*` branch; the PR is the review and
  approval gate." Behaviour-changing tasks must instead flag runtime + operational impact.
- **Motivation:** Nothing reaches `main` without the owner merging the PR, so
  pre-approval was redundant. See `pm/DECISIONS.md` D06.
- **Files changed:**
  - `CLAUDE.md` — ownership rules updated (PR-as-gate; flag behaviour-changing work).
  - `documentation/tasks/README.md` — lifecycle now
    `proposed → in-progress → in-review → done`; conventions/steps updated.
  - `documentation/tasks/TASK_TEMPLATE.md` — replaced approval metadata with
    *Reviewed via PR* + *Operational impact*; updated status vocabulary and checklist.
  - `documentation/tasks/002-security-hardening.md` — no longer "awaiting approval";
    operational impact recorded; ready to implement.
  - `pm/DECISIONS.md` — added D06.
  - `pm/STATUS.md` — removed the approval blocker; updated next steps.
- **Source code touched:** none.
- **Risk & rollback:** none to application behaviour. Revert this commit to restore the
  prior approval rule.

---

## 2026-05-25 — Add pm/ folder (status, roadmap, decisions) + template STATUS step

- **Branch:** `collab/code-review-and-docs`
- **Type:** behaviour-preserving (project-management docs + template wording; no source code touched)
- **Approved by:** collaborator request
- **Summary:** Added a top-level `pm/` folder holding a current-state snapshot
  (`STATUS.md`), a `ROADMAP.md`, and an append-only `DECISIONS.md`; wired a
  "refresh `pm/STATUS.md`" step into the task template's documentation checklist.
- **Motivation:** The CHANGELOG records *history*; we also need a *snapshot of now*
  (STATUS) and forward direction (ROADMAP). STATUS is overwritten; CHANGELOG is not.
- **Files added:**
  - `pm/README.md` — explains the folder and the STATUS-vs-CHANGELOG distinction.
  - `pm/STATUS.md` — current-state snapshot (overwrite to keep current).
  - `pm/ROADMAP.md` — now / next / later priorities (sourced from the review).
  - `pm/DECISIONS.md` — append-only decision log (lightweight ADRs).
- **Files changed:**
  - `documentation/tasks/TASK_TEMPLATE.md` — added a `pm/STATUS.md` refresh item to the
    required documentation checklist.
  - `documentation/README.md`, `CLAUDE.md` — cross-link `pm/` and the snapshot-vs-history rule.
- **Source code touched:** none.
- **Risk & rollback:** none to application behaviour. To undo: `rm -r pm/` and revert
  the template/README/CLAUDE.md wording.

---

## 2026-05-25 — Add CLAUDE.md guidance + seed security task

- **Branch:** `collab/code-review-and-docs`
- **Type:** behaviour-preserving (a guidance doc + a proposed task; no source code touched)
- **Approved by:** collaborator (CLAUDE.md guidance; security task seeded as `proposed`)
- **Summary:** Added a root `CLAUDE.md` pointing agents at the task system and the
  respect-the-owner rules, and seeded Task 002 (security hardening) as `proposed`.
- **Motivation:** Make the workflow self-enforcing for AI agents, and capture the
  highest-severity review findings (`01-code-review.md §4`) as an approvable task.
- **Files added:**
  - `CLAUDE.md` (repo root) — agent guidance: ownership rules, branch policy, task system.
  - `documentation/tasks/002-security-hardening.md` — proposed, behaviour-changing,
    **not implemented** and pending owner approval.
- **Source code touched:** none.
- **Risk & rollback:** none to application behaviour. To undo: delete `CLAUDE.md` and
  `documentation/tasks/002-security-hardening.md`.

---

## 2026-05-25 — Set up collaborator workflow (docs + branch)

- **Branch:** `collab/code-review-and-docs`
- **Type:** behaviour-preserving (documentation only; no code touched)
- **Approved by:** collaborator request
- **Summary:** Created an isolated working branch off `main` and added this
  `documentation/` folder.
- **Motivation:** The collaborator wants all work isolated from the owner's `main`
  branch and every change documented in detail.
- **Files added:**
  - `documentation/README.md` — ownership notes and the change-documentation process.
  - `documentation/01-code-review.md` — read-only review of the codebase.
  - `documentation/CHANGELOG.md` — this file.
  - `documentation/tasks/TASK_TEMPLATE.md` — reusable task template with built-in
    documentation instructions.
  - `documentation/tasks/README.md` — how the task system works (lifecycle, numbering).
  - `documentation/tasks/001-setup-collaborator-workflow.md` — first task / worked example.
- **Source code touched:** none.
- **Risk & rollback:** zero risk to application behaviour. To remove entirely:
  `git checkout main` and delete the branch (`git branch -D collab/code-review-and-docs`),
  or `rm -r documentation/`.

---

<!--
TEMPLATE for future entries — copy below this line:

## YYYY-MM-DD — <short title>

- **Branch:** <branch name>
- **Type:** behaviour-preserving | behaviour-changing
- **Approved by:** <who, and when>
- **Summary:** <one line>
- **Motivation:** <why; link to a finding in 01-code-review.md if relevant>
- **Files touched:** <path:line ...>
- **Before / after:** <the concrete difference>
- **Risk & rollback:** <how to undo: git revert <sha> or the inverse edit>
-->
