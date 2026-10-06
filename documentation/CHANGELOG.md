# Changelog

A detailed, chronological log of every change made by collaborators. Newest entries
at the top. See `README.md` for the entry format and the "respect the owner's code"
principles.

Each entry states whether it is **behaviour-preserving** (no observable runtime
difference) or **behaviour-changing** (requires owner/collaborator approval).

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
