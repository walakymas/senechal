# Task <NNN>: <Short title>

> **How to use this template**
> 1. Copy this file to `documentation/tasks/<NNN>-<kebab-slug>.md` (next free number).
> 2. Fill in every section. Leave a field blank only if it is genuinely N/A.
> 3. One task = one branch = one reviewable change.
> 4. A task is **not done** until the *Documentation* section is fully checked off.

---

## Metadata
- **ID:** <NNN>
- **Status:** `proposed`  <!-- proposed | approved | in-progress | blocked | done | abandoned -->
- **Type:** `behaviour-preserving`  <!-- behaviour-preserving | behaviour-changing -->
- **Branch:** `collab/<slug>`
- **Created:** YYYY-MM-DD
- **Owner approval required?:** <!-- yes for any behaviour-changing edit; no for docs/internal -->
- **Approved by / date:** <!-- fill once approved -->

## Context
- **Problem / motivation:** <why this task exists>
- **Related review finding:** <e.g. 01-code-review.md §3.2 — broken cleanupTokens SQL, or "none">
- **Definition of done:** <the observable condition that means this task is complete>

## Scope
- **In scope:** <what this task will change>
- **Out of scope:** <what it deliberately will NOT touch — guards against scope creep>

## Plan
- [ ] <step 1>
- [ ] <step 2>

## Respect-the-owner checklist
> This project is owned by **walakymas**; we are collaborators. Confirm each item.
- [ ] Working on a dedicated branch, not `main`.
- [ ] No unrelated reformatting, renaming, or import re-ordering.
- [ ] No deletion of working code without flagging it in *Before / after* below.
- [ ] Any behaviour-changing edit was approved (see Metadata) before implementing.

## DOCUMENTATION — required (do not set Status to `done` until all checked)
> Every task must produce documentation, not just code. This is the core rule of the
> task system: writing the docs is part of the task, not an afterthought.
> Mind the split: the **CHANGELOG** is append-only *history*; **`pm/STATUS.md`** is a
> *snapshot of now* that you overwrite. A finished task updates **both**.
- [ ] Added a `documentation/CHANGELOG.md` entry (date, branch, files, before/after, rollback).
- [ ] Refreshed `pm/STATUS.md` to reflect the new current state (and `pm/ROADMAP.md` if priorities changed).
- [ ] Filled the *Outcome* section of this task file with what actually changed.
- [ ] Listed every file touched in the *Files touched* table with a one-line rationale.
- [ ] Updated any affected README / inline docstrings if usage or behaviour changed.
- [ ] If a new concept/convention was introduced, added or extended a doc under `documentation/`.

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
|      |       |        |           |

## Before / after
- **Before:** <current behaviour or state>
- **After:** <new behaviour or state>
- **Behaviour-changing?** <yes/no — if yes, restate the approval>

## Verification
- **How tested:** <commands run, manual steps, expected vs actual>
- **How the owner can reproduce:** <steps>

## Risk & rollback
- **Risk:** <what could break>
- **Rollback:** `git revert <sha>` or <the inverse edit>

## Outcome  *(fill on completion)*
- **Result:** <what was delivered>
- **CHANGELOG entry:** <date/anchor in CHANGELOG.md>
- **Commit(s):** <sha(s)>
