# Task 003: Project-specific README (preserve the original)

---

## Metadata
- **ID:** 003
- **Status:** `in-progress`  <!-- implemented locally; → in-review when pushed/PR opened -->
- **Type:** `behaviour-preserving`  <!-- documentation only -->
- **Branch:** `collab/readme` *(stacked on `collab/code-review-and-docs`)*
- **Created:** 2026-05-25
- **Reviewed via PR:** <link once opened — the PR is the review/approval gate>
- **Operational impact:** none (documentation only).

## Context
- **Problem / motivation:** The repository README was the upstream template's generic
  docs (agubelu/discord-bot-template). It described `settings.py` / `BOT_TOKEN` /
  `client.send_message`, none of which match how senechal actually works — misleading
  for anyone landing on the repo.
- **Related review finding:** `01-code-review.md §5` (docs); general maintainability.
- **Definition of done:** The README describes the real project (purpose, architecture,
  config, how to run), credits the template origin, keeps the GPL-3.0 reference, and the
  original README content is preserved (not lost).

## Scope
- **In scope:** Replace `README.md` with a project-specific one; preserve the original
  verbatim elsewhere.
- **Out of scope:** Any source-code change; rewriting the preserved command/event guide.

## Plan
- [x] Preserve the original `README.md` verbatim at
      `documentation/original-template-readme.md` with a header explaining its origin.
- [x] Write a new project-specific `README.md` that links to the preserved guide.
- [x] Record the preservation + its location in the CHANGELOG (the PR log).

## Respect-the-owner checklist
- [x] Working on a dedicated branch (`collab/readme`), not `main`.
- [x] No unrelated reformatting / renames.
- [x] **No content lost** — the original README is preserved verbatim, not deleted.
- [x] Behaviour-preserving (documentation only); reviewed via PR.

## DOCUMENTATION — required
- [x] `documentation/CHANGELOG.md` entry added (notes the preserved file's location).
- [x] `pm/STATUS.md` refreshed.
- [x] *Files touched* table filled below.
- [x] The new README links to the preserved original so the command/event guide stays discoverable.

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| `README.md` | rewritten | replace | Describe the actual senechal project. |
| `documentation/original-template-readme.md` | new | add | Preserve the original README verbatim (with origin header). |
| `documentation/CHANGELOG.md` | new entry | add | Log the change + where the old README went. |
| `pm/STATUS.md` | snapshot | edit | Reflect Task 003. |

## Before / after
- **Before:** `README.md` = upstream template's generic, partly-inaccurate docs.
- **After:** `README.md` = project-specific; original preserved at
  `documentation/original-template-readme.md` and linked from the new README.
- **Behaviour-changing?** No — documentation only.

## Verification
- **How tested:** Confirmed the original was copied verbatim before overwrite
  (252 → 266 lines, +14 header). Checked the new README's internal links resolve
  (`LICENSE`, `Procfile`, `runtime.txt`, `documentation/`, `pm/`, preserved README).
- **How the owner can reproduce:** open `README.md` and the preserved file; compare the
  preserved body against `git show HEAD~1:README.md` from before the change.

## Risk & rollback
- **Risk:** None to application behaviour (docs only).
- **Rollback:** `git revert <sha>` (restores the old README and removes the new files),
  or copy `documentation/original-template-readme.md` back to `README.md`.

## Outcome
- **Result:** Project README written; original README preserved verbatim and linked.
- **CHANGELOG entry:** 2026-05-25 — "Add project README; preserve original template README".
- **Commit(s):** <this branch's commit>
