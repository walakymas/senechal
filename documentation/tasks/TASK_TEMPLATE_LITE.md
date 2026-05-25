# Task <NNN>: <Short title>  *(lite)*

> **When to use lite:** small, low-risk, **behaviour-preserving** changes — a typo, a
> one-line bug fix, a comment, a dependency pin, a doc tweak.
> **Use the full `TASK_TEMPLATE.md` instead** for anything behaviour-changing,
> multi-file, security-related, or that needs a real plan / verification steps.
> Copy this to `documentation/tasks/<NNN>-<slug>.md`. Documentation is still required.

- **ID / Status / Type:** <NNN> · `proposed` · `behaviour-preserving`
- **Branch:** `collab/<slug>` · **Created:** YYYY-MM-DD · **Reviewed via PR:** <link once opened>

## What & why
<one or two lines: what changes and why; link a finding in `01-code-review.md` if relevant>

## Files touched
- `path:line` — <one-line rationale>

## Before / after
<one line: the difference. If this turns out behaviour-changing, stop and switch to the full template.>

## Respect-the-owner check
- [ ] Dedicated `collab/*` branch · no unrelated reformatting · no deletion of working code.

## Documentation (required)
- [ ] `documentation/CHANGELOG.md` entry added.
- [ ] `pm/STATUS.md` refreshed.

## Verification & rollback
- **Checked:** <how you confirmed it works>
- **Rollback:** `git revert <sha>`
