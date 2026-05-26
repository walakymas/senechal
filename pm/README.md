# Project management (pm/)

Living project-management artifacts for collaborator work on **senechal**. These
complement the per-change records in `documentation/`.

The key idea: **different files answer different questions.** Keep them in their lanes.

| File | Answers | Update style |
|------|---------|--------------|
| `STATUS.md` | Where are we **right now**? | Snapshot — **overwrite** to keep current. |
| `ROADMAP.md` | What's next, and why? | Forward-looking — now / next / later. |
| `DECISIONS.md` | **Why** did we choose this approach? | Append-only (lightweight ADRs). |

Related (in `documentation/`):

| File | Answers |
|------|---------|
| `documentation/CHANGELOG.md` | What changed, in order? (append-only **history**) |
| `documentation/tasks/` | The detailed plan/record for one unit of work. |

## STATUS vs CHANGELOG — the important distinction

- **CHANGELOG** is the *history*: a permanent, dated list of what changed. You never
  rewrite old entries.
- **STATUS** is a *snapshot*: it sums up the current state and is **overwritten** every
  time the picture changes, so it always reflects "now."

When you finish a task you do **both**: append a CHANGELOG entry *and* refresh
`STATUS.md`. The task template's documentation checklist enforces this.

## Ownership reminder

Repo owned by **walakymas**; collaborators work on `collab/*` branches. Roadmap items
and proposed tasks are suggestions pending owner approval unless noted otherwise.
