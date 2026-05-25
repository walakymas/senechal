# Status

> **Snapshot of the current state.** Overwrite this to keep it accurate — it always
> describes "now," not history. For history see `documentation/CHANGELOG.md`.

**Last updated:** 2026-05-25
**Active branch:** `collab/security-hardening` (stacked on `collab/code-review-and-docs`)
**Committed?** Yes — security work in 3 commits here; workflow docs on
`collab/code-review-and-docs`; README on `collab/readme`. Nothing pushed; no PRs yet.

## In one line

The security task is implemented (env secrets, no secret logging, real `hasRight()`) and
**CSRF is decided: left off** (proportionate — D07). Task 002 is ready for a PR; only
owner-side deploy env vars remain. Workflow docs and the new README are ready on their
own branches.

## Tasks

| ID | Title | Status | Type | Branch |
|----|-------|--------|------|--------|
| 001 | Set up collaborator workflow (branch + docs) | done | behaviour-preserving | code-review-and-docs |
| 002 | Security hardening (web app) | in-progress | behaviour-changing | security-hardening |
| 003 | Project-specific README (preserve original) | in-progress | behaviour-preserving | readme |

## In progress

- Task 002: implementation complete (4 commits). CSRF decided (off, D07). Ready for PR;
  only owner-side deploy env-vars remain.

## Next up

- Decide whether to push the branches / open PRs (PR1 docs → main; PR2 readme and
  PR3 security, both based on the docs branch).
- A future bug-fix task will touch `web/views.py` and `utils.py` — overlaps this branch,
  so order/stack it after security to avoid conflicts.

## Blockers / waiting on

- None blocking. On merge/deploy the owner must set `DJANGO_SECRET_KEY` and
  `DJANGO_DEBUG`, and confirm `ALLOWED_HOSTS` with `DEBUG=False`.

## Health notes (from `documentation/01-code-review.md`)

- No automated tests, no CI, unpinned deps, EOL Django 3.1 / Python 3.9.5.
- Web security: the log leaks, `SECRET_KEY`/`DEBUG`, and the `hasRight()` placeholder are
  addressed in Task 002; CSRF and per-character authorization remain open.
