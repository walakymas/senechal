# Status

> **Snapshot of the current state.** Overwrite this to keep it accurate — it always
> describes "now," not history. For history see `documentation/CHANGELOG.md`.

**Last updated:** 2026-10-06 (Tasks 013-021 added)
**Active branch:** `main` (Tasks 009–011 merged via PR #7/#8)
**Pushed?** `collab/code-review-and-docs`, `collab/readme`, and `collab/security-hardening`
are pushed to origin. `collab/bugfixes` is committed locally (not pushed yet). PRs are
not opened yet (the `gh` CLI isn't installed — open them from the GitHub links).

## In one line

Four work-streams on parallel branches off the docs branch; three are pushed and ready
for PRs, the bug-fix branch is committed locally.

## Tasks

| ID | Title | Status | Type | Branch | Pushed |
|----|-------|--------|------|--------|--------|
| 001 | Collaborator workflow (branch + docs) | done | behaviour-preserving | code-review-and-docs | yes |
| 002 | Security hardening (web app) | in-progress (ready for PR) | behaviour-changing | security-hardening | yes |
| 003 | Project-specific README | in-progress (ready for PR) | behaviour-preserving | readme | yes |
| 004 | Bug fixes (base_command, utils) | in-progress (ready for PR) | behaviour-changing | bugfixes | no |
| 005 | Single process (API + bot) | in-progress (unverified) | behaviour-changing | single-process | no |
| 007 | Remove Django (code + local DB tables) | done (Heroku DB pending) | behaviour-changing | single-process | no |
| 008 | Character ownership (My character / Activate) | in-review (UI unverified) | behaviour-changing | character-ownership | no |
| 009 | Passion categories | done (frontend build unverified) | behaviour-changing | passion-categories | yes |
| 010 | Admin rights, `setChannel`, remove `!admin save` | done (not run live) | behaviour-changing | passion-categories | yes |
| 011 | Web dice/commands without the webhook | in-review (frontend fallback uncommitted, not run live) | behaviour-changing | passion-categories | partly |
| 012 | systemd services + deploy script (`deploy/`) | done (not run on the host yet) | behaviour-preserving | main | no |
| 013 | Remove stale secrets (`settings.py`, `environment.prod.ts`) | in-review (not committed) | behaviour-preserving | remove-stale-secrets | no |
| 014 | SQL injection in `get_by_name` | in-review (unit tests pass; not run on a live DB) | behaviour-changing | sql-injection-fix | no |
| 015 | API authentication and authorisation (blocked: confirm login for all players first; reads stay open) | blocked | behaviour-changing | api-auth | no |
| 016 | Bot permission checks, dice limits | in-review (17 unit tests pass; not run on a live server) | behaviour-changing | bot-permissions | no |
| 017 | Data layer stability | in-review (11 integration tests on a throwaway PostgreSQL; not run on production data) | behaviour-changing | data-layer-stability | no |
| 018 | Functional bug fixes | in-review (54 unit tests pass; not run on a live server) | behaviour-changing | functional-bugs | no |
| 019 | Frontend and Express hardening | proposed | behaviour-changing | frontend-hardening | no |
| 020 | Infra, dependencies, repo hygiene | proposed | behaviour-preserving | infra-and-deps | no |
| 021 | Performance and logging | proposed | behaviour-preserving | performance | no |

## In progress

- Task 004: typo + `utils.py` de-duplications done; both files compile. Scoped to avoid
  any file the other PRs touch.

## Next up

- Read `documentation/03-security-audit.md` (2026-10-06) and **rotate the exposed secrets**
  (bot token, client secret, Discord webhook, DB password). Then turn the audit's fix steps
  1–3 into tasks (SQL injection, API auth, bot permission checks, dice limits, data layer).

- Commit the `AngrySenechal2` webhook fallback (Task 011) and run its build/spec after `npm install` (the lockfile is out of sync).
- Try Tasks 010–011 live: `!admin setChannel`, `!me setChannel`, a web dice roll and a skill check while logged in and logged out.

- Open the PRs (links in the chat / `git ls-remote`): PR1 docs → `main`; PR2 readme,
  PR3 security, PR4 bugfixes — all based on the docs branch (they retarget to `main`
  after PR1 merges + its branch is deleted).
- Push `collab/bugfixes` when ready for its PR.
- On the security merge/deploy, owner sets `DJANGO_SECRET_KEY` / `DJANGO_DEBUG`.

## Blockers / waiting on

- None blocking. PRs must be opened manually (no `gh` CLI).

## Health notes (from `documentation/01-code-review.md`)

- No automated tests, no CI, unpinned deps, EOL Django 3.1 / Python 3.9.5 (GitHub
  Dependabot reports 21 vulnerabilities on the default branch).
- Web security log-leaks / `SECRET_KEY` / `DEBUG` / `hasRight()` addressed in Task 002;
  CSRF intentionally left off (D07). Bug fixes in Task 004.
