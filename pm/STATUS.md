# Status

> **Snapshot of the current state.** Overwrite this to keep it accurate — it always
> describes "now," not history. For history see `documentation/CHANGELOG.md`.

**Last updated:** 2026-05-25
**Active branch:** `collab/code-review-and-docs`
**Committed?** Yes — workflow scaffolding (`CLAUDE.md`, `documentation/`, `pm/`)
committed to the branch. Not pushed; no PR opened yet.

## In one line

Collaborator workflow and documentation scaffolding are in place; the first real code
task (security hardening) is written up and **awaiting owner approval** before any code
is touched.

## Tasks

| ID | Title | Status | Type |
|----|-------|--------|------|
| 001 | Set up collaborator workflow (branch + docs) | done | behaviour-preserving |
| 002 | Security hardening (web app) | proposed | behaviour-changing |

## In progress

- Nothing actively coding — workflow setup complete; awaiting direction on the next task.

## Next up

- Implement Task 002 (security hardening) on `collab/security-hardening`; the owner
  reviews via the PR (no pre-approval needed — see DECISIONS D06).
- Decide whether to push the branch / open a PR for review.

## Blockers / waiting on

- None right now — behaviour-changing work is reviewed via PR, not pre-approval. The
  owner will need to set new env vars (`SECRET_KEY`, `DJANGO_DEBUG`) when Task 002 merges.

## Health notes (from `documentation/01-code-review.md`)

- No automated tests, no CI, unpinned deps, EOL Django 3.1 / Python 3.9.5.
- Several high-severity web security gaps (see Task 002).
- None of these are addressed yet — documentation/process only so far.
