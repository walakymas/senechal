# Task 021: Performance and logging

## Metadata
- **ID:** 021
- **Status:** `in-review`  <!-- implemented; 91 tests pass in the Python 3.12 image against PostgreSQL; not run on a live Discord server, not committed -->
- **Type:** `behaviour-preserving` (same answers, fewer queries) — except the items under *Behaviour changes*
- **Branch:** `collab/performance`  <!-- from `collab/infra-and-deps` -->
- **Created:** 2026-10-06
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** none to deploy. Output moves from `print()` to `logging`: `LOG_LEVEL` (default `INFO`; `DEBUG` also shows command arguments). **`requirements.txt` was re-pinned** (see below).

## Context
- **Problem / motivation:** N+1 queries (`Character.__init__` queried per instance), `SELECT *` including the big JSON just to list names, an unlocked character cache that never remembered misses, PDF generation that left temp files and could be triggered repeatedly, and `print()` of payloads, tokens and message content.
- **Related review finding:** `03-security-audit.md` §8.
- **Definition of done:** the heaviest endpoints issue a constant number of queries; the cache is safe; PDF generation leaves no files and cannot pile up; no tokens or message content in the logs. Met.

## Measured (SQL statements, `tests/query_count_test.py`, PostgreSQL, 6 and 24 characters)
| Call | Before (6 / 24 chars) | After (6 / 24 chars) |
|------|-----------------------|----------------------|
| `/players` (`pcs`) | 5 / 14 | **2 / 2** |
| `Character.pcs()` (`!team`, `!check <name>`, …) | 4 / 13 | **1 / 1** |
| `Character.npcs()` | grows with N (one per character) | **1 / 1** |
| `/connections?cid=` (a character connected to everybody) | 17 / 71 | **4 / 4** |
| `/pdfs` (team zip) | 19 / 73 | **5 / 5** |
| `/json?id=` | 5 / 5 | **4 / 4** |
| `/list`, `/json` (names) | 1 / 1 | 1 / 1 (smaller rows) |
| 5 commands by a Discord user without a character | 5 | **1** |

## Scope
- **Done:**
  - **No query per `Character`**: `CharacterTable` records now carry the player's `did` (`JOIN player`, index 9), `Character.__init__` uses it (and falls back to the old query for a record without it). `Character.get_many_by_id` loads several characters with one query.
  - **Endpoints**: `pcs` (glory by dict instead of a nested loop that also printed every pair), `connectionsByCid` (all the other characters in one query, all their marks in one), `pdfs` (below), `list` / names (`CharacterTable.list_summary()`: no `data` JSON), `pcresponse` / `Sheet` read the game year from a cache (`BaseTableHandler.year()`, 30 s; written through `PropertiesTable.set/remove`, so `!db set prop year` takes effect at once).
  - **Cache** (`character.py`): one lock, one key per kind (`('id', n)`, `('member', n)`, `('name', lower)`; `"123"` and `123` are the same entry), per-entry expiry (60 s found, **10 s not found**: an unregistered user is looked up once, and a newly activated player is "unknown" for at most 10 s), `Character.cache` can still be emptied by tests.
  - **PDF**: the sheet finds fonts and images relative to the project (not the working directory) and takes prefetched year / marks / events / glory; `/pdf` and `/pdfs` build in memory (no temp files, no `tempfile._get_candidate_names()`); `/pdfs` builds one team zip at a time and reuses it for 30 s (a second request waits and gets the fresh zip), file names inside the zip are sanitised; `!me pdf` uses `tempfile.mkstemp`; `Content-Disposition` is safe for any name (ASCII `filename` + RFC 5987 `filename*`).
  - **Logging**: `logs.setup_logging()` (called by `server.py` and `senechal.py`; the standalone bot passes `log_handler=None` to discord.py so nothing is configured twice); every `print()` in `senechal.py`, `message_handler.py`, `character.py`, `utils.py`, `config.py`, `api/`, `feast.py`, the database layer and the commands became a `logging` call or was removed. **Not logged any more:** message content, command arguments at `INFO` (they can hold secrets, e.g. `!db set prop hook …`), token records, player records, `modify` values. A test checks the arguments stay out of the `INFO` log.
- **Behaviour changes (small, flagged):**
  - `/pdfs` takes the team from the `player` table (`CharacterTable.get_pcs()`), not from the legacy `characters.memberid` column: with data written since Task 008 the old selection was **empty**. A character with two players appears once.
  - The team zip can be up to 30 s old.
  - `get_by_name` / `get_by_id` order their join so the first player is deterministic.
- **Left open:**
  - Fonts are parsed for every `Sheet` (fpdf2 has no shared font object); with the zip cache this only matters for single sheets.
  - Cached `Character` objects are still mutated in place by a few callers (`get_data()` adds fallback skills; `utils.py` sets `main.Glory`); copying them on the way out is a separate change.
  - The remaining synchronous DB calls on the Discord event loop (Task 017: needs an async data layer).
  - The Angular views (`trackBy` / `OnPush` / lazy routes): after the Angular upgrade, see Task 019.

## Dependency re-pin (found while testing)
`requirements.txt` from Task 020 pinned the versions of the development venv; `fpdf2` 2.8.3 cannot embed the variable font of the sheet (`KeyError: 'fvar'` — **every PDF would have failed**; `tests/query_count_test.py` found it). It is now pinned to the versions the working container ran (`fpdf2` 2.8.9, `fonttools` 4.65.0, `discord.py` 2.7.1, `emoji` 2.16.0, `aiohttp` 3.14.3 and the rest, see the file): `pip check` and `pip-audit` are clean on Python 3.12 and all tests pass there.

## Plan
- [x] Measure first (`tests/query_count_test.py`, numbers above).
- [x] Load characters without a query each; batch the endpoints.
- [x] Cache and PDF changes.
- [x] Logging.
- [ ] Owner: try `!me pdf`, `/pdf?id=`, the team zip and `/connections` on the running stack (rebuild the image first).

## Respect-the-owner checklist
- [x] Dedicated branch, not `main`.
- [x] No unrelated reformatting.
- [x] Output identical before and after except the items under *Behaviour changes* (checked by tests that compare `/list`, `/json`, `/players`, `/connections` and the zip content).
- [x] Operational impact flagged.

## DOCUMENTATION — required
- [x] `documentation/CHANGELOG.md` entry with the before / after query counts.
- [x] `pm/STATUS.md` refreshed.
- [x] *Outcome* filled.
- [x] *Files touched* filled.
- [x] `CLAUDE.md` mentions `LOG_LEVEL` and the new test files.

## Files touched
| File | Change |
|------|--------|
| `database/charactertable.py` | records with the player's `did`; `get_by_ids`, `list_summary` |
| `character.py` | constructor without a query, cache rewrite, `get_many_by_id`, logging |
| `database/base_table_handler.py`, `proptable.py`, `markstable.py`, `eventstable.py` | cached year, `list_for`, `list_by_dbid` |
| `api/views.py`, `api/compat.py` | `pcs`, `list`, `connectionsByCid`, `pdfs`, `pdf`, logging, safe `Content-Disposition` |
| `pdf/sheet.py`, `commands/me.py` | absolute paths, prefetched data, `mkstemp` |
| `logs.py` (new), `server.py`, `senechal.py` | logging setup |
| `senechal.py`, `message_handler.py`, `utils.py`, `config.py`, `feast.py`, `database/*.py`, `commands/*.py` | `print()` → `logging` |
| `requirements.txt` | re-pinned (see above) |
| `tests/query_count_test.py` (new), `tests/performance_test.py` (new) | 13 database tests (query counts, answers), 16 unit tests |

## Before / after
- **Before:** see the table; secrets and chat content in the logs; PDFs left temp files.
- **After:** see the table.
- **Behaviour-changing?** only the three small items above.

## Verification
- **How tested:** `python -m unittest discover -s tests -p "*_test.py"` — 91 tests (66 without a database, plus the 25 database tests). In the Python 3.12 image built from `Dockerfile.senechal` with the new pins, against a PostgreSQL 14 container: **91 tests, all pass, none skipped**. `pip check` / `pip-audit`: clean.
- **How the owner can reproduce:** `TEST_DATABASE_URL=… QUERY_REPORT=1 python -m unittest tests.query_count_test -v` prints the query counts; then rebuild and use the stack: `!me pdf`, the character PDF, the team zip, the connections panel, `!team`, an unregistered Discord user typing a command.

## Risk & rollback
- **Risk:** the query rewrite changes every character lookup (covered by the tests, not by a live Discord session); the 10 s "unknown" cache.
- **Rollback:** `git revert <sha>`.

## Outcome  *(fill on completion)*
- **Result:** implemented as in *Scope — Done*; query counts constant for every measured call.
- **CHANGELOG entry:** 2026-10-06 — Performance and logging (Task 021)
- **Commit(s):** not committed yet
