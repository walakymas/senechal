# Task 001: Set up collaborator workflow (branch + documentation system)

> Worked example. This task is what established the branch, the `documentation/`
> folder, and the task system itself.

---

## Metadata
- **ID:** 001
- **Status:** `done`
- **Type:** `behaviour-preserving`
- **Branch:** `collab/code-review-and-docs`
- **Created:** 2026-05-25
- **Owner approval required?:** no (documentation only; no source code touched)
- **Approved by / date:** collaborator request, 2026-05-25

## Context
- **Problem / motivation:** This repo is owned by **walakymas**; we are collaborators.
  We need every contribution isolated from `main` and documented in detail, so the
  owner can review before merging.
- **Related review finding:** 01-code-review.md (overall — no automated tests, no CI,
  no contribution process).
- **Definition of done:** A dedicated branch exists, a `documentation/` folder exists,
  and a repeatable task-with-documentation process is written down.

## Scope
- **In scope:** Creating the branch and the documentation/task scaffolding.
- **Out of scope:** Any change to application source code (`*.py`, settings, configs).

## Plan
- [x] Create branch `collab/code-review-and-docs` off `main`.
- [x] Add `documentation/README.md`, `01-code-review.md`, `CHANGELOG.md`.
- [x] Add the task system (`tasks/TASK_TEMPLATE.md`, `tasks/README.md`, this file).

## Respect-the-owner checklist
- [x] Working on a dedicated branch, not `main`.
- [x] No unrelated reformatting, renaming, or import re-ordering.
- [x] No deletion of working code without flagging it.
- [x] No behaviour-changing edits (none made).

## DOCUMENTATION — required
- [x] Added a `documentation/CHANGELOG.md` entry.
- [x] Filled the *Outcome* section below.
- [x] Listed every file in the *Files touched* table.
- [x] No source README/docstrings affected (none existed for this area).
- [x] Introduced a new convention (the task system) and documented it in `tasks/README.md`.

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| `documentation/README.md` | new | add | Folder purpose + ownership/process rules. |
| `documentation/01-code-review.md` | new | add | Read-only review of the codebase. |
| `documentation/CHANGELOG.md` | new | add | Chronological change log. |
| `documentation/tasks/TASK_TEMPLATE.md` | new | add | Reusable task template with built-in doc instructions. |
| `documentation/tasks/README.md` | new | add | How the task system works. |
| `documentation/tasks/001-setup-collaborator-workflow.md` | new | add | This worked example. |

## Before / after
- **Before:** Work would happen directly on `main`; no documentation process.
- **After:** Work happens on `collab/*` branches; every change is captured as a task
  plus a changelog entry.
- **Behaviour-changing?** No — documentation and process only. No source code changed.

## Verification
- **How tested:** `git rev-parse --abbrev-ref HEAD` confirms branch
  `collab/code-review-and-docs`; the `documentation/` files exist and render.
- **How the owner can reproduce:** `git checkout collab/code-review-and-docs` and read
  the `documentation/` folder.

## Risk & rollback
- **Risk:** None to application behaviour — no source code touched.
- **Rollback:** `git checkout main` then `git branch -D collab/code-review-and-docs`,
  or delete `documentation/`.

## Outcome
- **Result:** Branch + documentation folder + task system established.
- **CHANGELOG entry:** 2026-05-25 — "Set up collaborator workflow (docs + branch)".
- **Commit(s):** <pending commit on this branch>
