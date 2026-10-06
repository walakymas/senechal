# Security, Bug and Performance Audit

**Date:** 2026-10-06
**Method:** read-only static review (three parallel passes: API, bot + data layer, frontend + infra). Nothing was run and no source code was changed.
**Scope:** `senechal/` (aiohttp API, Discord bot, data layer), `AngrySenechal2/` (Angular 14 + Express), the Docker/deploy files, and the legacy `senechal2/` copy where it differs.

**About this audit.** Like `01-code-review.md`, this is meant to help. The project works and
is in real use; the points below are opportunities, ordered by impact, each with a
`path:line` so they can be turned into tasks. Paths are relative to `senechal/` (the
backend) unless they start with `AngrySenechal2/`. Line numbers describe the code as found on
this date and may drift.

**Secrets:** no secret *values* are reproduced here, only where they live. Several of them
should be treated as exposed and rotated (see section 1).

---

## Summary

| # | Severity | Finding | Where |
|---|----------|---------|-------|
| 1 | Critical | Discord bot token present in a comment | `settings.py:8` |
| 2 | Critical | Discord webhook URL hardcoded in the production frontend (and in git history) | `AngrySenechal2/src/environments/environment.prod.ts:5` |
| 3 | Critical | Backend hands the webhook URL to anyone via `/base` | `api/views.py:48` |
| 4 | Critical | SQL injection in the character-name lookup | `database/charactertable.py:37` |
| 5 | Critical | Most API routes need no authentication; `hasRight()` accepts any string | `api/app.py:36-47`, `api/views.py:299` |
| 6 | Critical | `/token` issues a session token for any character id | `api/views.py:110-130` |
| 7 | Critical | `adminList` dumps player/token/check tables incl. live session tokens | `api/views.py:375` |
| 8 | Critical | Bot commands `reload`, `set`, `db` have no permission check | `commands/reload.py`, `commands/set.py`, `commands/db.py` |
| 9 | Critical | Unbounded dice loop stalls the bot | `dicing.py:9-29`, `message_handler.py:36-45`, `utils.py:505,519` |
| 10 | High | `modify` is a mass-assignment: any field, any character | `api/views.py:202-231` |
| 11 | High | Single global DB connection, no reconnect, errors swallowed | `database/database.py`, `database/base_table_handler.py` |
| 12 | High | Blocking DB/PDF/subprocess calls on the Discord event loop | `message_handler.py:44`, `commands/me.py:39`, `commands/reload.py:21` |
| 13 | High | Reaction handler downloads any attachment to disk, unauthenticated | `senechal.py:75-97` |
| 14 | High | `Config.authorization` defaults to off, `modify` then skips the check | `config.py:8`, `api/views.py:216` |
| 15 | High | Session tokens kept in `localStorage` and logged to the console | `AngrySenechal2/src/app/app.component.ts:36` |
| 16 | High | `server.js`: Host-header redirect, no `helmet`, no `trust proxy` | `AngrySenechal2/server.js` |
| 17 | High | Permissive CORS list (codepen, LAN IP, http origins) | `api/app.py:16-27` |
| 18 | High | Containers run as root, Postgres port published, dev servers in prod images | `Dockerfile.senechal`, `docker-compose.yml`, `AngrySenechal2/Dockerfile*` |
| 19 | High | Angular 14 / Node 16 / Python 3.9–3.10 end of life; deps unpinned | `AngrySenechal2/package.json`, `requirements.txt`, `runtime.txt` |
| 20 | Medium | Broken SQL in many table handlers (errors are swallowed) | see 4.3 |
| 21 | Medium | Startup crash on a fresh DB (`getValue` on a missing row) | `config.py:73`, `database/proptable.py:22` |
| 22 | Medium | `weapon.py` `UnboundLocalError`, wrong wound logic | `commands/weapon.py:35,74,89` |
| 23 | Medium | `feast.py` logic bugs (round key, `id=-1`, str/int keys) | `feast.py:11,20,148-194` |
| 24 | Medium | N+1 queries, no `trackBy`/`OnPush`, polling that never stops | see 8 |
| 25 | Low | Mention injection, alias collisions, log noise, stale code | see 5, 7 |

---

## 1. Secrets and credentials

- **Bot token in a comment** — `settings.py:8`. A comment is still a leak. Rotate the token
  in the Discord Developer Portal, delete the line, and check git history and backups.
- **Webhook URL in the frontend** — `AngrySenechal2/src/environments/environment.prod.ts:5`.
  Tracked in git and present in at least three commits, so deleting the line is not enough.
  Revoke/regenerate the webhook; rewrite history (`git filter-repo`) if you want it gone.
  The same URL is exposed at runtime by `/base` (`api/views.py:48`, `Config.hook`) and used
  by `character.service.ts` (~l.132, ~285-300). Since Task 011 added `/roll` and `/command`,
  the webhook path can be removed from the browser entirely.
- **Local secret files** — `.env` holds the bot token, DB password and Discord client secret.
  It is gitignored in `senechal/`, but the parent folder contains `senechal*.zip` /
  `senechal.tgz`; check them for embedded copies. `db/senechal_20260622.dmp` is a real
  database dump and should be treated as sensitive.
- **Legacy `senechal2/web/settings.py`** hardcodes a Django `SECRET_KEY` and `DEBUG = True`,
  and prints DB credentials. Delete `senechal2/` or make sure it is never deployed.
- **Rotate** (to be safe): Discord bot token, client secret, webhook, DB password.

## 2. Authentication and authorisation (API)

- **No authentication on most routes** — `api/app.py:36-47`. Only `roll` and `command`
  validate a token. `modify`, `newchar`, `event`, `mark`, `updatePlayer`, `addC2C`,
  `add_map` / `update_map` / `delete_map`, `feast`, `pdf` / `pdfs`, `connections`, `adminList`
  and `cleanupTokens` do not.
- **`hasRight()`** (`api/views.py:299`) returns `token != 'null'`, so any string counts as
  authorised. `modify` additionally skips the check when `Config.authorization` is false,
  which is the default (`config.py:8`, `api/views.py:216`).
- **`/token`** (`api/views.py:110-130`) creates a session token for any character id with no
  credentials, bypassing the Discord OAuth flow in `api/auth.py`. The frontend still calls it
  (`app.component.ts` `loginBase()`).
- **`adminList`** (`api/views.py:375`) returns the `player`, `tokens`, `checks` and `c2c`
  tables, including live session tokens and Discord ids. Combined with the above, anyone can
  impersonate any user.
- **`updatePlayer`** (`api/views.py:408-415`) passes the raw POST data to `execute()`, so a
  caller can change `did` / `character` for any player.
- **`modify` mass assignment** (`api/views.py:202-231`): every key except `id` / `token` is
  written into the character JSON, so a caller can overwrite `role`, `memberId`, `player`,
  `name`. `set_json` then copies those into DB columns. Related bug in `set_json`
  (`database/charactertable.py`): `if 'player' in j: role = j['player']` overwrites `role`.
- **Reads are open too** (`json`, `npc`, `pdf`, `pdfs`, `connections`, `list`, `players`,
  `checks`): IDOR, including `memberId` (Discord id).
- **Angular `/admin` route** (`app-routing.module.ts:17`) has no guard (UX layer only; the
  real fix is server-side).
- **Suggested fix:** one decorator/middleware that validates the token
  (`TokenTable().get_info_by_token`, `state == 1`, not expired) and applies per-route rules
  (owner of the character, or `playerrights` bit for admin routes); delete `hasRight()`;
  make `authorization` non-optional; remove the unauthenticated `/token` issuer.
- **Tokens**: plain `uuid4`, stored in cleartext, and logged in places. Prefer
  `secrets.token_urlsafe(32)`, hashed at rest, with revocation and a working cleanup.
- **Discord OAuth** (`api/auth.py`) is sound (state nonce with TTL, origin allow-list), but the
  state store is in-memory and unbounded by count, and the origin allow-list includes
  `http://` and codepen hosts that receive the token in the URL fragment.

## 3. Injection and input validation

- **SQL injection** — `database/charactertable.py:37`:
  `f"SELECT * FROM characters WHERE name ILIKE '%{name}%'"`. Reachable without auth from
  `GET /json?ch=` (`api/views.py:147`), from `newchar` (`api/views.py:199`), and from Discord
  through `utils.py:121-123` (`get_me`, any last argument starting with `!`). Use
  `execute("... WHERE name ILIKE %s", ['%' + name + '%'], fetch='one')` and escape `%` / `_`.
  Everything else in the data layer is parameterised, which is a real strength.
- **Unvalidated input**: `int()` on user text without handling (`utils.py:398`,
  `commands/attack.py:19`, `commands/images.py:19`, `commands/event.py:24`),
  `request.POST['c0']*1` in `addC2C` repeats the string instead of converting it, `feast`
  accepts arbitrary `seat` / `roundAction`, `request.POST['id']` is not validated.
- **Stored URLs**: `add_map` / `update_map` store a user-supplied `url` verbatim
  (`api/views.py:531`); validate the scheme (http/https) and consider a host allow-list.
- **`Content-Disposition`** (`api/compat.py:261`): the character name is interpolated
  unescaped into the filename; sanitise and use RFC 5987 encoding. PDF temp files use the
  private `tempfile._get_candidate_names()` and are never deleted (`api/views.py:315,329`).
- **Mention injection**: commands echo user input without `AllowedMentions.none()`
  (`npc.py:27`, `pc.py:25`, `bot_bridge.py:58`; set it at `senechal.py:27`).
- **Error leakage**: `api/views.py:126` and map handlers (`:538,552,562`) return exception
  text; `except BaseException` at `:124,245`. Return generic messages and log server-side.
- `yaml.load(..., Loader=yaml.FullLoader)` in `config.py:53,69,71`: use `yaml.safe_load`.

## 4. Data layer and stability

### 4.1 Connection handling
- `database/database.py:12-21` opens one module-level connection at import time and never
  reconnects. After a network drop `rollback()` raises on the closed connection and the bot
  stays broken until restart. Use `ThreadedConnectionPool` (or reconnect on
  `InterfaceError` / `OperationalError`) and pass the full DSN to `psycopg2.connect(dsn)`
  so `sslmode` is kept; fail early when `DATABASE_URL` is missing.
- `database/base_table_handler.py:42-58` prints and swallows `psycopg2.Error`, returns `None`,
  and non-psycopg exceptions skip the rollback. Callers then report "Updated" for failed
  writes. Re-raise (or return an explicit failure) and always commit/rollback in `finally`.
- The single `Database.lock` serialises the API and the bot; a slow query can delay Discord
  heartbeats.

### 4.2 Event loop
- Synchronous psycopg2 calls run inside the Discord event loop for every command
  (`message_handler.py:44`, `utils.py:218`, `Character.__init__` at `character.py:547`), as do
  `pdf.output()` (`commands/me.py:39`) and `subprocess` (`commands/reload.py:21-22`). Wrap in
  `asyncio.to_thread`.

### 4.3 Broken SQL (silently swallowed)
`lordtable.py:16,19` · `markstable.py:20` · `p2ctable.py:16,19` · `p2ptable.py:24,31,34-35` ·
`checktable.py:16` · `tokenstable.py:24,27` · `feasttable.py:15,30` ·
`api/views.py:422` (`DELETE FROM tokens expires < ... INTERVALL`) ·
`playertable.py:13` (`remove` deletes from `properties`, the wrong table).
Typical causes: comma instead of `AND`, wrong table/column names, typos.

### 4.4 Schema and migrations (`database/database.py`)
- `:171-172` re-add `did` (already created at `:129`) and insert a `name` column that was
  commented out at `:134`: a fresh install fails.
- `c2c` and `p2c` have no UNIQUE constraint on the columns used by `ON CONFLICT`
  (`c2ctable.py:13`, `p2ctable.py:12`).
- `initiate()` has no rollback on failure; `:173` hardcodes two Discord ids with full rights.
- `!db download` sends a stale, unused `senechal.db` (SQLite) as the "backup"
  (`sqlite3.connect('senechal.db')` in `database.py`).

### 4.5 Startup
- `config.py:73` calls `PropertiesTable().getValue('hook')` before the DB is initialised, and
  `proptable.py:22` indexes `value[0]` on `None`: crash on a fresh or partial database.
- `senechal.py:111` uses `datetime.time.sleep(10)` (`AttributeError`); `senechal.py:33-37`
  sets `running = True` before initialisation succeeds.

## 5. Discord bot

- **Missing permission checks**: `commands/reload.py:19-23` (anyone can restart the bot and
  trigger `git pull` when `pull` is set), `commands/set.py:14-20` (anyone can rewrite global
  config, e.g. `debugdice` to force or break every roll), `commands/db.py:20-65` (read/write
  `properties`, including `hook`), `commands/info.py` (DMs all member and channel ids),
  `commands/images.py`. Only `commands/admin.py:26-29` checks rights correctly. Suggest a
  `required_rights` attribute on `BaseCommand` enforced in `message_handler.handle_command`.
- **Dice DoS**: `!999999999d6` loops on the event loop (`dicing.py:9-29`,
  `message_handler.py:36-45`), as do the damage loops (`utils.py:505,519`,
  `commands/weapon.py:39,56`). `!d0` raises `ValueError`. The web `roll` already clamps
  (≤100 dice, size ≤1000, `api/views.py:258`); apply the same limits in the bot.
- **Reaction handler** (`senechal.py:75-97`): any user adding 👀 / 🗺️ makes the bot download all
  attachments to a hardcoded Linux path with no size/type check (disk fill; files are served
  from the web origin, so an uploaded HTML/SVG is a stored-XSS risk); `event.member` can be
  `None` (DMs). `commands/images.py:15-24` fetches an entire channel history for `!im None`.
- **Authorisation of edits**: `event.py:24-30` and `mark.py:33` remove/modify rows by bare id
  for anyone; `get_me` lets any user act as any character via `cid:N` / `!name`.
- **Message edits**: `on_message_edit` (`senechal.py:70-73`) re-runs commands (re-rolls,
  re-inserts); `on_message` does not skip bots.
- **Argument parsing**: modern mentions `<@id>` are not stripped (`senechal.py:55` only strips
  `<@!`); empty input raises `IndexError` (`message_handler.py:36`, `bot_bridge.py:55`);
  several `params[N]` accesses are unchecked (`db.py:24-39`, `token.py:15`, `mark.py:33`,
  `event.py:34,38`).
- **Alias collisions** (`message_handler.py:21-25`): `tel` (Token/Winter) and `l` (Feast/Lord);
  the last one registered wins silently.
- **Token command** (`commands/token.py`): scans all guild members instead of
  `guild.get_member`, `record[1]` can be `None`, unhandled `Forbidden` on DM, approval DMs
  can be spammed by guessing sequential ids.

## 6. Functional bugs

- `commands/weapon.py:35,74,89`: `sum` is local for the whole function and only set in some
  branches (`UnboundLocalError` on fumble/fail with no opponent damage); the success branch
  computes the wound from the attacker's `sum`; `Weapon.knocked(embed.description, ...)`
  appends to a string passed by value, so the result is discarded.
- `feast.py`: `:154` uses the builtin `round` instead of `self.data['round']`; `:11,:20` leave
  `self.id = -1` after insert so later updates silently do nothing; `:181-183` use `'round'`
  where the data has `'rounds'`; `:194` int keys vs `str(round)` in `draw_card` (JSON turns int
  keys into strings, so the "already set" guard fails after reload); `:35-37` `AttributeError`
  on a `None` character; read-modify-write of the JSON blob has no locking;
  `commands/feast.py:17` `randint(1, 155)` vs `Deck.shuffle` `range(1, 155)` (off-by-one).
- `character.py`: `Character.pcs(name)` ignores `name` (`:709`, used by `check.py:28`,
  `login.py:22`, so `!c <name> <spec>` rolls for every PC); `effective_dexterity` uses
  `str` + armor/shield `red` (`:609`); typo `stewardship_` (`:565`); bare `except:` (`:621`);
  `Character.cache` (`:648-700`) is shared without a lock, mixes key types and mutates cached
  objects in place (`utils.py:228`).
- Stale `Config.characters` references (attribute no longer exists): `commands/db.py:28,33`,
  `config.py:80,87`, `commands/me.py:44`, `commands/winter.py:24`, `commands/lord.py`,
  `commands/mark.py:51-52`; `lord.py:22-26` stores the keyword instead of the value.
- `utils.py`: `client.send_message` (`:75`) and `emojize(use_aliases=True)` (`:31`) do not
  exist in current library versions; `get_checkable` with an empty/short spec matches many
  skills and floods the channel.
- `winter.py:117` uses `randint` directly and bypasses `dice()` / `debugdice`.
- Dead/duplicated code: `senechal_old.py`, `senechal2/`, duplicate `glorys`
  (`eventstable.py:31,34`), unused `events/` scheduler, `test_sheet.py` using removed APIs.
- `check2` (`utils.py:395-412`): with a target above 20 the adjusted roll can exceed 20 and
  count as a critical. **Confirmed as the intended rule** (owner, 2026-10-06): a skill raised
  above 20 by a modifier always succeeds, the excess is added to the roll, and a total of 20 or
  more is a critical success (+4d6 damage). Not a bug; Task 018 only pins it with a test.

> **Owner decisions (2026-10-06):** read access stays open to everyone (all characters visible);
> API write rules will be set later and Task 015 is blocked until login is confirmed to work for
> every player; `senechal2/` is removed, `senechal_old.py` and the `.pkl` files may be deleted.

## 7. Frontend, Express and infrastructure

### Frontend (`AngrySenechal2/`)
- Token in `localStorage` (`app.component.ts:35,70,153,162`, `character.service.ts:306,384`),
  logged via `logger.log('token:'+...)` (`app.component.ts:36`), sent in POST bodies with no
  `HttpInterceptor` (no central 401 handling). Prefer an `HttpOnly; Secure; SameSite=Lax`
  cookie or an in-memory token, plus a CSP.
- No direct XSS sinks were found (`innerHTML`, `bypassSecurityTrust*`, `eval` are unused). Map
  image URLs come from the API, so they are untrusted if `add_map` stays open.
- `app.component.ts:42-50`: `listChanged` subscription never unsubscribed and `interval(5000)`
  polls `getUser()` forever. About 60 `.subscribe(` calls, few with `takeUntil`.
- `handleError` (`character.service.ts:370-380`) logs and returns `of(result)`, hiding failures;
  `setUser` assumes a non-null user (`app.component.ts:83`); `feast-seating.component.ts:22`
  does `JSON.parse(localStorage.getItem('list'))` with no guard.
- `environment.prod.ts:3` points at `https://senechal.herokuapp.com/` (likely dead); a
  duckdns URL is hardcoded at `character.service.ts:292`.
- `angular.json`: base options have `optimization: false`, `sourceMap: true`,
  `defaultConfiguration: ""`; budgets are very loose; all seven routes load eagerly.

### Express (`AngrySenechal2/server.js`)
- HTTPS redirect uses the unvalidated `Host` header (open redirect), trusts
  `x-forwarded-proto` without `trust proxy`, no `helmet`/CSP/HSTS, no `compression`, and the
  `/*` catch-all serves `index.html` (status 200) for missing assets.

### Infra
- `Dockerfile.senechal` and the Angular Dockerfiles run as root; the Angular images use
  `node:16-alpine` (EOL), `npm install` (not `npm ci`) and `ng serve` (dev server) with
  `disableHostCheck: true` (`angular.json`). `docker-compose.yml` publishes Postgres on
  `5432:5432` and bind-mounts `./senechal:/app`.
- `requirements.txt`: no versions at all (14 packages); `runtime.txt` says Python 3.9.5 while
  the Dockerfile uses 3.10 (both EOL); `psycopg2-binary` is not recommended for production;
  `Procfile`/`runtime.txt` are Heroku leftovers.
- `package.json`: Angular `~14.3` (no security fixes since late 2023) but `@angular/cli ~13.3`;
  rxjs 6, protractor/tslint/codelyzer deprecated, several abandoned UI packages. Run
  `npm audit` / `pip-audit` for exact CVEs (not run here).
- Ignore files: tracked files that should not be in git — `senechal.db`, `senechal.db-journal`,
  `*.pkl` font caches, `AngrySenechal2/.../environment.prod.ts`. `.pkl` files load via
  `pickle`; they belong to fpdf 1.x and are unused with fpdf2, so delete them. The
  top-level `.gitignore` (`.env` only) protects nothing outside a repo; there is also a
  misnamed `AngrySenechal2/dockerignore` duplicate.
- `deploy/setup-systemd.sh` runs the Angular dev server as a production service and installs a
  sudoers rule: confirm it is limited to the two exact restart commands. `deploy.sh` does
  `git pull` + `npm ci` on the host.
- Transport: no TLS or security headers in `server.py` (expected behind a proxy; verify one
  exists), no rate limiting on `/token` / `/auth/login`.

## 8. Performance and optimisation

- **N+1 queries**: `Character.__init__` runs a query per instance (`character.py:547`), so
  `pcs` / `npcs` / `team` / `list_by_name` multiply it; `connectionsByCid`
  (`api/views.py:447-456`); `pdfs`; `pcresponse` re-reads marks, events and config on every
  call; an O(n×m) scan over `glorys` in `pcs`. Batch with `WHERE dbid = ANY(%s)` and select only
  needed columns (not `SELECT *` with the JSON blob).
- **Cache**: `Character.cache` is cleared every 60 s, unlocked, mixed keys, and misses are never
  cached (every roll by an unregistered user hits the DB). `force=True` bypasses it on most
  reads.
- **PDF**: fonts are re-parsed for every `Sheet` (`pdf/sheet.py:13-15,39`), relative font and
  image paths break if the working directory changes, `pdfs` renders every PC in-process on
  the request thread and leaves temp files behind. Cache fonts, build the zip in memory,
  rate-limit.
- **Frontend**: zero `OnPush` and zero `trackBy` across ~100 `*ngFor`s; template method calls
  (`myCharacters()`, `isLord()` in `app.component.html:14-45`); eager routes; unoptimised
  default build.
- **Logging**: `print()` of payloads, tokens and every message's content
  (`senechal.py:66,71`, `message_handler.py:48`) — move to `logging` and drop tokens/PII.

## 9. What looks fine

- Almost all SQL uses parameter binding; `get_by_name` is the only user-influenced f-string
  query (`database.py:208` formats an int).
- No `eval`, `exec`, `os.system`, `shell=True` or `pickle.load` in project code; the only
  subprocess is the fixed `["git", "pull"]`.
- `admin.py` checks rights correctly; the web `roll` clamps dice; the Discord OAuth flow uses a
  state nonce; no admin password or credentials are hardcoded in the frontend; no XSS sinks
  found in the Angular templates.
- The Task 007 follow-up already removed the `print`s that leaked `DATABASE_URL`, the bot
  token and session tokens in `senechal/`.

## 10. Suggested order of work

0. **Secrets** (manual): rotate bot token, client secret, webhook, DB password; check the
   zip/tgz archives; clean history if desired.
1. **Critical backend**: parameterise `get_by_name`; add the auth middleware and drop `/token`
   and `hasRight()`; allow-list `modify`; permission checks for `reload` / `set` / `db` /
   `info` / `images`; clamp dice; harden the reaction handler.
2. **Data layer**: connection pool/reconnect, no swallowed errors, `asyncio.to_thread`, fix the
   broken SQL and migrations, `safe_load`.
3. **Functional bugs**: `weapon.py`, `feast.py`, argument parsing, `Character.pcs(name)`,
   `AllowedMentions.none()`, stale `Config.characters` code.
4. **Frontend/Express**: remove the webhook, token handling + interceptor, `server.js`
   hardening, CORS list, `trackBy` / `OnPush` / unsubscribe.
5. **Infra/deps**: non-root multi-stage images, pin dependencies, upgrade Angular / Node /
   Python, ignore files and untrack `senechal.db` / `*.pkl`.
6. **Optimisation**: batch queries, cache, PDF, logging.

Items in steps 1–3 are behaviour-changing (see `CLAUDE.md`); each should be its own task on a
`collab/*` branch with the operational impact flagged in the task file and the PR. Tests do
not exist yet, so start with `pytest` cases for the SQL-injection, auth and dice-limit fixes.
