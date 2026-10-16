# Feast rules (Book of Feasts v1.2) as implemented

Source: `pdfcoffee.com_book-of-feasts-updated-pdf-free.pdf`. The pure rules live in `feast_rules.py`
(no database, unit-tested in `tests/feast_rules_test.py`); `feast.py` applies them to a feast record.

| Rule | Book | Code |
|------|------|------|
| Seating by the unmodified APP roll | Critical Above, Success Near, Failure Below; Fumble: roll again (fumble = failure) and sit one seat lower, Below -> Floor | `seat_from_app_result`, `seat_after_fumble`, `Feast.seat_by_app` |
| APP modifier | jewelry +1 per GBP 1 and Fashion, max +10; Geniality modifies APP / courtly skills, max +/-10 | `app_bonus`, `clamp_geniality_modifier` (applied by the roller, Phase 3) |
| Geniality per round (end of round) | Above +2, Near +1, Below 0, Floor -1 (-2 after a fumbled APP) | `seat_geniality`, `Feast.end_round` |
| Gossip / Indulge / Flirt / Game | success +1, critical +2, fumble -1 Geniality | `activity_geniality`, `Feast.record_result` |
| Who draws cards | not Above the Salt; Glory **>= 1000** (decision: the boundary is inclusive) | `number_of_cards` |
| Cards per round | 1000+ 1, 2000+ 2, 4000+ 3, 8000+ 4, 16000+ 5, 32000+ 6 | `number_of_cards` |
| One card played per round | the rest is discarded at the end of the round | `Feast.select_card`, `Feast.end_round` |
| Base Geniality of a card | `geniality:` in `feast.yml`, added when the card is played | `Feast.select_card` |
| Keeper cards | stay in hand, `keep.geniality` per round, `keep.draw: no` forbids drawing meanwhile | `keep_card`, `discard_kept`, `keeps_no_draw` |
| Host / Mandatory cards | a Host card must be played, a Mandatory one (trait/passion 16+) before the others | `Feast.card_enabled` (unchanged); `significant` now comes from traits (either side of a pair, 16+ / 4-) and passions 16+ (`significant_traits`) |
| Round 1 restriction | Indulgent 16+: Temperate roll for anything but Indulge; Lustful 16+: Chaste roll for anything but Flirt | `first_round_requirement`; stored as `requires` in the round |
| Leaving | positive Geniality drops to 0 (negative stays), no Geniality while away; Courtesy roll: success check, critical +10 Glory, royal fumble -1 Honor (logged only) | `Feast.leave`, `return_to_feast` |
| End of the feast | highest Geniality: x10 Glory (ties share it); the others their positive Geniality; royal +100; Above the Salt +100 | `final_glory`, `Feast.finish` -> `finalGlory` per guest |

## Not in the first version (decision)

Optional rules: Stewardship roll for the host, ceding your position (Modest roll), Honor loss for being seated below a character with less
Glory. Hosting rules (Hospitality) and the coding of the card effects in `feast.yml` are also left out: a card without a structured `check`
is resolved by the recorded result of the player and the host may override it.

## Data (the `feast.data` JSON)

Existing keys are kept (including the `participiants` spelling). Added with defaults on load: `royal`, `log`, and per guest `geniality`,
`left`, `kept`, `award`, `fumbled`; per round `discarded`, `requires`, `result`; per guest after the end `finalGlory`.

## API (`api/feast_views.py`)

All calls need a valid session `token`. A player acts for the characters he owns (`player.did` = the character's `memberid`), the host
(admin right) for everybody and runs the feast. Mutations are POSTs; the answer is the whole feast (as `GET /feast`) with an `enabled`
list of the playable cards per guest, plus `rolled` with what the call rolled. `fid` selects a feast (default: the latest). Errors are
`{"error": ...}` with 400 (bad parameter), 403 (no session / not allowed), 404, 409 (the rules do not allow it now).

| Route | Who | Does |
|-------|-----|------|
| `GET /feasts`, `GET /feast_get` | anyone | list / one feast (404 when none: reading never creates a feast) |
| `POST /feast_new` | host | `title`, `rounds` (1-10), `royal` |
| `POST /feast_next` | host | init -> round 1 -> ... -> end (Geniality, discards, final Glory) |
| `POST /feast_seat` | host | `cid`, `seat`: seats by hand |
| `POST /feast_app_roll` | player | `cid` (`jewelry`, `fashion`): adds the guest, rolls APP (fumble: second roll), seats; once |
| `POST /feast_activity` | player | `cid`, `activity` (card/gossip/indulge/flirt/game/pass) |
| `POST /feast_requirement` | player | `cid`, `trait`: the Temperate / Chaste roll of round 1 |
| `POST /feast_roll` | player | `cid` (`trait` for Indulge): rolls Intrigue / Temperate or Indulgent / Flirting / Gaming, Geniality modifier on the courtly skills |
| `POST /feast_select_card`, `/feast_discard_kept` | player | `cid`, `card` (a Host card must be played, it disables the other cards; then Mandatory) |
| `POST /feast_leave`, `/feast_return` | player | `cid` (`voluntary=1`: Courtesy roll, not in round 1) |

The legacy `POST /feast` actions stay for the current frontend, but now need a session: the host's right, `roundAction` also the owner of `pid`.
`GET /feast` returns 404 instead of creating a feast (use `feast_new`).
