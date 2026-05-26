# Decisions

> Append-only log of notable decisions (lightweight ADRs). Newest at the bottom.
> Records **why** a choice was made, so it isn't re-litigated or lost. Distinct from the
> CHANGELOG (what changed) and STATUS (current state).

Format: `D<NN> — date — decision — why — status`.

---

### D01 — 2026-05-25 — Work only on `collab/*` branches, never `main`
- **Why:** Repo owned by **walakymas**; collaborators must keep `main` clean and let the
  owner review before merge.
- **Status:** active.

### D02 — 2026-05-25 — Track work via a documentation + task system under `documentation/`
- **Why:** The collaborator wants every change isolated and documented in detail. The
  task template bakes documentation into each unit of work.
- **Status:** active.

### D03 — 2026-05-25 — Enforce the workflow via `CLAUDE.md` guidance only (no repo slash command)
- **Why:** Wanted agents to follow the process without adding tooling to the owner's
  repo root beyond a single guidance file.
- **Status:** active. (Considered: a committed `/task` slash command — declined to keep
  repo footprint small.)

### D04 — 2026-05-25 — The `/task` scaffolding command is **personal**, not committed
- **Why:** Keeps the convenience tool on the collaborator's machine
  (`~/.claude/commands/task.md`) without changing the shared repo.
- **Status:** active.

### D05 — 2026-05-25 — Add a top-level `pm/` folder (STATUS, ROADMAP, DECISIONS)
- **Why:** Needed a *current-state snapshot* (STATUS) and *direction* (ROADMAP) that the
  chronological CHANGELOG doesn't provide; DECISIONS captures rationale.
- **Status:** active. (Alternative considered: nest under `documentation/pm/` — chose
  root for visibility; can be moved if the owner prefers fewer top-level folders.)

### D06 — 2026-05-25 — The PR is the approval gate; no pre-implementation approval for `collab/*` work
- **Why:** Work on a `collab/*` branch never reaches `main` without the owner reviewing
  and merging the PR, so gating implementation on prior approval was redundant overhead.
  Implement on a branch and let the PR carry the change and its review.
- **Implication:** Behaviour-changing tasks must loudly flag the runtime change and any
  **operational impact** (new env vars, possible client breakage, migrations) in the task
  file and PR description. **Supersedes** the earlier "behaviour-changing requires owner
  approval before implementing" rule (D02-era wording).
- **Status:** active.
