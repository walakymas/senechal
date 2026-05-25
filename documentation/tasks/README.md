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
4. If the task is **behaviour-changing**, get owner approval before implementing and
   record it in *Metadata*.
5. Create the branch named in *Metadata* and do the work.
6. Complete the *Documentation* checklist (CHANGELOG entry, Outcome, files table).
7. Set Status to `done`.

## Task lifecycle (Status field)

```
proposed ──approved──▶ approved ──start──▶ in-progress ──finish──▶ done
   │                                            │
   └──────────────── abandoned ◀────────────────┴──▶ blocked
```

- `proposed` — written up, not yet agreed.
- `approved` — agreed to proceed (required before starting behaviour-changing work).
- `in-progress` — branch created, work underway.
- `blocked` — waiting on something (note what, in the task file).
- `done` — merged or ready for review, documentation complete.
- `abandoned` — decided against; keep the file for the record, note why.

## Conventions

- **One task = one branch = one focused change.** Don't bundle unrelated edits.
- **Numbering** is sequential and never reused. Abandoned tasks keep their number.
- **Behaviour-changing** tasks (anything observable at runtime) require approval.
- Every task ends with a `CHANGELOG.md` entry; the task file holds the detail, the
  changelog holds the chronological summary.

## Files

| File | Purpose |
|------|---------|
| `TASK_TEMPLATE.md` | The template to copy for every new task. |
| `001-setup-collaborator-workflow.md` | First task — a worked example (the branch + docs setup). |
| `<NNN>-<slug>.md` | One file per task. |
