# Documentation

This folder tracks analysis and changes contributed by collaborators to the
**senechal** project.

## Important: ownership and intent

This repository is owned by **walakymas** (remote: `github.com/walakymas/senechal`).
Contributions recorded here are made by a **collaborator**, not the owner. The
working principle is:

- **Respect the owner's code.** No wholesale reformatting, no deletion of working
  code without flagging it first, no behavioural changes without explicit approval.
- **Isolate work.** All changes happen on dedicated branches (never directly on
  `main`), so the owner can review before anything is merged.
- **Document everything.** Every change is described here in enough detail that the
  owner can understand *what* changed, *why*, and *how to revert it* without reading
  the diff line by line.

## Folder contents

| File | Purpose |
|------|---------|
| `README.md` | This file — conventions and ownership notes. |
| `01-code-review.md` | A read-only review of the codebase (structure, quality, security, SWOT). No code was changed to produce it. |
| `CHANGELOG.md` | A running, detailed log of every change made on a collaborator branch. |
| `tasks/` | The **task system**: a reusable task template (with built-in documentation instructions) and one file per unit of work. See `tasks/README.md`. |

## Workflow at a glance

Work is organised as **tasks**. Each task is one branch, one focused change, and is
**not complete until its documentation is written**. To start a piece of work:

1. Copy `tasks/TASK_TEMPLATE.md` to `tasks/<NNN>-<slug>.md` and fill it in.
2. Get approval if the task is behaviour-changing.
3. Do the work on the task's branch.
4. Complete the template's *Documentation* checklist: add a `CHANGELOG.md` entry
   **and** refresh `../pm/STATUS.md`.

See `tasks/README.md` for the full lifecycle, and `../pm/` for the current status,
roadmap, and decision log.

> **CHANGELOG vs STATUS:** `CHANGELOG.md` is append-only *history* (what changed, in
> order); `../pm/STATUS.md` is a *snapshot* (where we are now) that you overwrite. Keep
> both current.

## How changes are documented

Every code change gets an entry in `CHANGELOG.md` **before or alongside** the change,
containing:

1. **Date** and **branch** the change was made on.
2. **Summary** — one line on what changed.
3. **Motivation** — why the change is needed (link to the review finding if relevant).
4. **Files touched** — with `path:line` references.
5. **Before / after** — the behavioural difference, and whether it is behaviour-
   preserving or behaviour-changing.
6. **Risk & rollback** — how to undo it (e.g. `git revert <sha>` or the inverse edit).
7. **Approval** — whether the owner/collaborator explicitly approved this change.

Behaviour-changing edits (anything a user or the owner could observe at runtime) are
called out explicitly and require approval before being made.
