# Status

> **Snapshot of the current state.** Overwrite this to keep it accurate — it always
> describes "now," not history. For history see `documentation/CHANGELOG.md`.

**Last updated:** 2026-05-25
**Active branch:** `collab/bugfixes` (off `collab/code-review-and-docs`)
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

## In progress

- Task 004: typo + `utils.py` de-duplications done; both files compile. Scoped to avoid
  any file the other PRs touch.

## Next up

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
