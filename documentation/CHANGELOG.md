# Changelog

A detailed, chronological log of every change made by collaborators. Newest entries
at the top. See `README.md` for the entry format and the "respect the owner's code"
principles.

Each entry states whether it is **behaviour-preserving** (no observable runtime
difference) or **behaviour-changing** (requires owner/collaborator approval).

---

## 2026-05-25 — Add project README; preserve original template README (Task 003)

- **Branch:** `collab/readme` (stacked on `collab/code-review-and-docs`)
- **Type:** behaviour-preserving (documentation only)
- **Approved by:** collaborator
- **Summary:** Replaced the upstream-template README with a project-specific one, and
  **preserved the original README verbatim** so nothing is lost.
- **Where the old README went:** moved verbatim to
  `documentation/original-template-readme.md` (with a header noting its origin and that
  it still documents the command/event plugin pattern and the `utils` helpers). The new
  `README.md` links to it.
- **Motivation:** The old README documented the generic template (`settings.py`,
  `BOT_TOKEN`, `client.send_message`) rather than how senechal actually works.
- **Files added:**
  - `documentation/original-template-readme.md` — the original README, preserved verbatim.
  - `documentation/tasks/003-project-readme.md` — the task record.
- **Files changed:**
  - `README.md` — rewritten to describe the real project (purpose, architecture, config,
    how to run), crediting the agubelu template origin and keeping the GPL-3.0 reference.
- **Source code touched:** none.
- **Risk & rollback:** none to application behaviour. `git revert <sha>`, or copy
  `documentation/original-template-readme.md` back to `README.md`.

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
