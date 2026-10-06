# Task 021: Performance and logging

## Metadata
- **ID:** 021
- **Status:** `proposed`
- **Type:** `behaviour-preserving`  <!-- same results, fewer queries; the log output changes -->
- **Branch:** `collab/performance`
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** none. Log output moves from `print()` to `logging` (configure the level via env).

## Context
- **Problem / motivation:** N+1 queries (`Character.__init__` queries per instance), `SELECT *` including the JSON blob just to list names, a character cache that is unlocked and never caches misses, PDF rendering that re-parses fonts and leaves temp files, and `print()` of payloads / tokens / message content.
- **Related review finding:** `03-security-audit.md` §8.
- **Definition of done:** the heaviest endpoints (`pcs`, `connectionsByCid`, `pdfs`, `pcresponse`) issue a constant number of queries; the cache is safe; PDF rendering does not leak files; no tokens or message content in logs.

## Scope
- **In scope:**
  - `character.py:547`: do not query in `__init__` (pass the player data in); `Character.pcs` / `npcs` / `team` / `list_by_name` use one batched query (`WHERE dbid = ANY(%s)`).
  - `api/views.py`: `pcs` (dict instead of the O(n×m) scan over `glorys`), `connectionsByCid` (`:447-456`), `pdfs` (`:302-317`), `pcresponse` (cache `MarksTable().year()`, events, config per request); select only needed columns in `list` / `get_character`.
  - `Character.cache` (`character.py:648-700`): lock, consistent keys, cache misses briefly, avoid mutating cached objects (`utils.py:228`).
  - PDF (`pdf/sheet.py:13-15,39`): load fonts once, absolute paths, in-memory zip, `tempfile.TemporaryDirectory`, sanitised filenames (`api/compat.py:261`), rate limit on `pdfs`.
  - Logging: `print` → `logging` in `senechal.py:66,71`, `message_handler.py:48`, `api/views.py`; never log tokens or message content.
- **Out of scope:** schema changes; auth (Task 015); event-loop offloading (Task 017).

## Plan
- [ ] Measure first: count queries per endpoint (enable `log_statement` on the test DB) and record the baseline in this file.
- [ ] Batch `Character` loading.
- [ ] Endpoint fixes one by one, re-measuring each.
- [ ] Cache and PDF changes.
- [ ] Logging.

## Respect-the-owner checklist
- [ ] Dedicated branch, not `main`.
- [ ] No unrelated reformatting.
- [ ] No deletion of working code without flagging.
- [ ] Output identical before and after (compare JSON responses).

## DOCUMENTATION — required
- [ ] `documentation/CHANGELOG.md` entry with before/after query counts.
- [ ] `pm/STATUS.md` refreshed.
- [ ] *Outcome* filled.
- [ ] *Files touched* filled.

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
| `character.py`, `api/views.py`, `pdf/sheet.py`, `api/compat.py` | see Scope | batching, cache, PDF | |
| `senechal.py`, `message_handler.py` | see Scope | logging | |

## Before / after
- **Before:** N+1 queries per request; leaked temp files; tokens in logs.
- **After:** constant query counts; clean temp directory; no sensitive logs.
- **Behaviour-changing?** no (response bodies identical).

## Verification
- **How tested:** save the JSON of each endpoint before the change and `diff` it after; compare query counts; run `pdfs` ten times and check the temp directory.
- **How the owner can reproduce:** same steps.

## Risk & rollback
- **Risk:** cache staleness after writes from another process.
- **Rollback:** `git revert <sha>`.

## Outcome  *(fill on completion)*
- **Result:**
- **CHANGELOG entry:**
- **Commit(s):**
