# Task system

A lightweight, in-repo system for tracking collaborator work. Each unit of work is a
**task**: one branch, one reviewable change, with documentation built into the
definition of done.

The point of the system is simple: **documentation is part of the task, not an
afterthought.** The task template (`TASK_TEMPLATE.md`) carries explicit instructions
to write documentation, so no change can be marked complete without it.

## How to create a task

1. Pick the next free number (`NNN`), e.g. `002`.
2. Copy `TASK_TEMPLATE.md` to `documentation/tasks/<NNN>-<kebab-slug>.md`.
3. Fill in *Context*, *Scope*, and *Plan*; set Status to `proposed`.
4. If the task is **behaviour-changing**, make sure the task file (and later the PR)
   clearly flag the runtime change and any **operational impact** — new env vars,
   possible client breakage, migrations. No pre-implementation approval is required.
5. Create the branch named in *Metadata* and do the work.
6. Complete the *Documentation* checklist (CHANGELOG entry, STATUS refresh, Outcome, files table).
7. Open a PR (Status `in-review`); the owner approves by merging (Status `done`).

## Task lifecycle (Status field)

```
proposed ──start──▶ in-progress ──open PR──▶ in-review ──merge──▶ done
   │                     │
   └──── abandoned ◀─────┴──▶ blocked
```

- `proposed` — written up, not started.
- `in-progress` — branch created, work underway.
- `in-review` — PR opened; the owner reviews here. **This is the approval gate** — the
  owner approves by merging. No pre-implementation approval is required.
- `blocked` — waiting on something (note what, in the task file).
- `done` — merged, documentation complete.
- `abandoned` — decided against; keep the file for the record, note why.

## Conventions

- **One task = one branch = one focused change.** Don't bundle unrelated edits.
- **Numbering** is sequential and never reused. Abandoned tasks keep their number.
- **Behaviour-changing** tasks (anything observable at runtime) must be flagged in the
  task file and PR; the owner approves them by reviewing/merging the PR (no pre-approval).
- Every task ends with a `CHANGELOG.md` entry; the task file holds the detail, the
  changelog holds the chronological summary.

## Files

| File | Purpose |
|------|---------|
| `TASK_TEMPLATE.md` | The template to copy for every new task. |
| `001-setup-collaborator-workflow.md` | First task — a worked example (the branch + docs setup). |
| `<NNN>-<slug>.md` | One file per task. |
