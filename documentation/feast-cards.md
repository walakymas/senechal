# Feast cards: `check` / `keep` / `mandatory` data in `feast.yml`

> Companion to Task 025. What was filled in, the conventions used, and — most
> importantly — the cards whose data is **doubtful or incomplete** (each carries a
> `# TODO(feast-check): …` comment right above its `check:` block).

## 1. What was done

- All 154 cards of `feast.yml` were read against their `full` text.
- Cards **1–9, 11** were already filled in (11 by hand); cards **10, 12, 13** were completed in this series; card 10 was added now.
- Cards **14–154** got a declarative `check:` block (plus `keep:` / `mandatory:` where the card text states them) and a short `text:` (the first line of `full`) where it was missing.
- Existing fields (`name`, `geniality`, `tags`, `text`, `full`) were **not changed** — verified by loading the file before/after with PyYAML.
- Card 12 now uses `choose: [love, amor]` (same as card 11) instead of a `skill:` list.
- No `.py` file was touched.

## 2. Conventions (as already used by cards 1–13)

| Key | Meaning |
|---|---|
| `check.skill: x` | a skill roll; outcomes in `success / critical / failure / fumble / partial` |
| `check.choose: [a, b]` | the player may pick one of the skills |
| `check.passion: x` + `win` / `oppose: y` + `lose` | trait/passion contest, "X wins" vs "Y wins" |
| `check.opposed` (+ `versus.unknown: 2d6+8`) | opposed roll; `unknown` is the rival's value when not known; `win / lose / tie` |
| effects | `geniality`, `glory`, `check: <name>` (mark on the trait/skill = "gain"), `damage`, `money`, `loyalty`, `honor`, `bonus`, `intoxication`, `feast: leave\|miss\|duel`, `winter: Childbirth` |
| `keep:` | read by the engine: `geniality` (per round) and `draw: no` |
| `mandatory: x` | read by the engine: card is forced when passion/trait `x` is significant (≥ 16) |

`check:` blocks are **declarative only** — `feast.py` / `feast_rules.py` do not read them yet (only `geniality`, `tags`, `keep`, `mandatory`). Keys such as `bonus`, `pass_card`, `per_rival` are therefore a proposal, not an implemented schema.

## 3. Runtime impact (behaviour-changing)

The engine **does** read these keys, so adding them changes a running feast:

- `keep: {geniality, draw}` added to cards **37, 44, 56, 58, 66, 67, 68, 118** → the kept card now gives per-round Geniality / blocks drawing.
- `mandatory: indulgent` added to cards **92–107** (More Drink / More Food) → forced when Indulgent is significant.
- `text:` added to every card that lacked it (shown wherever the UI/API renders `text`).

Everything else is inert data. Please review these three groups before merging; reverting them is a matter of removing those keys.

## 4. Doubtful or incomplete cards (reminders)

Almost all of them boil down to: **the card does not name the rolled skill** (the engine/UI will need a choice or a decision), or the effect needs an engine feature that does not exist (passing cards, counters, bonuses, preconditions).

| Card | Name | Reminder |
|---|---|---|
| 14 | A love Poem | A roll's skill is not named on the card; Compose assumed (he asks you to help with the poem). |
| 15 | A Man for All Seasons | Counter mechanic is not modelled in the engine (keep.counter / depart bonus are only declarative). |
| 16 | A New Teacher | Which Skill is rolled/gained is chosen by the player/GM ('appropriate Skill') - needs a skill picker. / Failure: leaving is optional (player decision), gain the Skill only if they leave. |
| 17 | A Roaring Fire | Rolled skill/stat is not stated on the card (Dexterity? Awareness?) - fill in. |
| 18 | A Serving Girl Flirts | Critical: it is unclear whether the success effects (+1 Geniality, Flirting) also apply. |
| 19 | A Serving Girl Flirts | Critical: it is unclear whether the success effects (+1 Geniality, Flirting) also apply. |
| 20 | A Serving Girl Flirts | Critical: it is unclear whether the success effects (+1 Geniality, Flirting) also apply. |
| 21 | A Serving Girl Flirts | Critical: it is unclear whether the success effects (+1 Geniality, Flirting) also apply. |
| 22 | A Serving Girl Flirts | Critical: it is unclear whether the success effects (+1 Geniality, Flirting) also apply. |
| 23 | A Test of Strength | Reroll counting and passing the card to another player are not supported by the engine. |
| 24 | A Test of Strength | Reroll counting and passing the card to another player are not supported by the engine. |
| 26 | About Things Real | Opposing trait 'Worldly' - confirm that the contest is Spiritual vs Worldly. |
| 27 | All You Can Eat | Size-increase rule (Winter Phase) is only text. Tie handling is not described. |
| 28 | Alms | The roll is not named (likely a Generous/Religion roll) - fill in. / Pagan exception only modelled as text/flag. |
| 29 | An Ideal Wife | Random Marriage table (+5) and passing the card are not implemented. |
| 30 | An Ideal Wife | Random Marriage table (+5) and passing the card are not implemented. |
| 31 | Be Valorous | Opposed trait 'Reckless' is the contrasting trait on the card - verify the exact contest (Valorous vs Reckless). |
| 32 | Biggest Mistake | Rolled skill not stated on the card (Orate? Intrigue?). |
| 33 | Boasting Knights | Number of knights is not specified (GM/player decides). |
| 34 | Cristian Virtue | Per-success Geniality / bonus / discard conditions are declarative only (engine has no hook). |
| 35 | Pagan Promise | Same as card 34 (pagan version). |
| 36 | Center Stage | The list of usable skills (story/music/song) is a guess - confirm. |
| 37 | Chance Encounter | The roll is not named; 'appropriate Trait, Passion or Skill' needs a picker. |
| 38 | Chivalrous Life | Rolled skill not stated (Orate? Chivalry?). |
| 41 | Awkward Conversation | Roll/skill not named; needs a skill picker. |
| 42 | Damaged Goods | Rolled skill not stated (Dexterity? Awareness?). / 'Discard and draw again if no jewelry' needs a precondition hook. |
| 43 | Dangerous Game | Rolled skill/stat not stated (Dagger? Dexterity?). |
| 44 | Difficult Question | 'Lose all Geniality gained from this card' on fumble is not supported. |
| 45 | Angry Dogs | Rolled skill not stated (Hunting? Animal Handling?). |
| 46 | Raucous Contest | Number of rival knights is not specified. |
| 49 | Emergency | Rolled skill not stated (First Aid? Dexterity?). |
| 51 | Faerie Tales | Skill assumed to be Faerie Lore (not named on the card). |
| 52 | Faerie Tales | Skill assumed to be Faerie Lore (not named on the card). |
| 53 | Fashion Disaster | Skill assumed to be Fashion (not named). / Per-round penalty until clothes change is not supported. |
| 55 | Generous Knight | Precondition (maintenance grade) is not checked by the engine. |
| 57 | Glory Hound | Player-to-player card theft and discard rules are not implemented. |
| 59 | Gossip | Rolled skill not stated (Intrigue? Awareness?). |
| 60 | Gossip | Rolled skill not stated (Intrigue? Awareness?). |
| 61 | Gossip | Rolled skill not stated (Intrigue? Awareness?). |
| 62 | Great Deeds | Unclear whether the FUMBLE applies only to Proud's Orate roll or also to the Modest side (modelled under Proud). |
| 63 | Great Deeds | Unclear whether the FUMBLE applies only to Proud's Orate roll or also to the Modest side (modelled under Proud). |
| 64 | Great Deeds | Unclear whether the FUMBLE applies only to Proud's Orate roll or also to the Modest side (modelled under Proud). |
| 65 | Gwyddbwyll | 'Gain Gaming trait' - Gaming is a skill; interpreted as a check mark on Gaming. |
| 67 | Holy Blessing | Automatic success on any later roll is not implemented. |
| 68 | Holy Blessing | Automatic success on any later roll is not implemented. |
| 69 | How's the Wine | Rolled skill not stated. |
| 71 | Insult to a Lady | Rolled skill not stated (Orate? Courtesy?). |
| 73 | Introductions | Rolled skill not stated (Courtesy? Intrigue?). |
| 76 | King of the Beam | The 'must draw / cannot play other keepers' restriction is not enforced. |
| 78 | Lady in Distress | Rolled skill not stated (Courtesy? Orate?). |
| 82 | Lost Love | Tag 'duel' does not match the card text (no duel) - check tags. |
| 83 | Malicious Slander | Tag 'leave' does not match the card text - check tags. |
| 84 | Tipsy | Rolled trait not stated; Temperate assumed. |
| 85 | Manners! | Rolled skill not stated (Courtesy?). |
| 87 | Regale the Host | Skill assumed to be Orate (story). |
| 88 | Meet the Host | Rolled skill not stated ('your expertise'). |
| 89 | Mercy, Milord | Opposing passion is 'Hate (foe)' - confirm. |
| 90 | Minstrels Sing | Usable skills (Singing/Play) are a guess. |
| 92 | More Drink | Effects come from Table 2.2 of The Book of Feasts - not transcribed. |
| 93 | More Drink | Effects come from Table 2.2 of The Book of Feasts - not transcribed. |
| 94 | More Drink | Effects come from Table 2.2 of The Book of Feasts - not transcribed. |
| 95 | More Drink | Effects come from Table 2.2 of The Book of Feasts - not transcribed. |
| 96 | More Drink | Effects come from Table 2.2 of The Book of Feasts - not transcribed. |
| 97 | More Drink | Effects come from Table 2.2 of The Book of Feasts - not transcribed. |
| 98 | More Drink | Effects come from Table 2.2 of The Book of Feasts - not transcribed. |
| 99 | More Drink | Effects come from Table 2.2 of The Book of Feasts - not transcribed. |
| 109 | Old Friends | Rolled skill not stated. / 'Love (Family) and Hospitality +2 Geniality' wording is unclear. |
| 110 | Oops! | Rolled skill not stated (Dexterity?). |
| 111 | Overindulgence | Rolled skill not stated (Temperate? Constitution?). |
| 114 | Passing Praise | Rolled skill not stated. |
| 115 | Passion | Rolled passion/skill and which Passion is gained are not specified. |
| 116 | People Skills | Rolled skill/trait not stated. |
| 118 | Popular | Tag is 'duel' but the card is a keeper - the 'keep' tag is missing; tag not changed. |
| 123 | Safekeeping | Passion pair (Trusting vs Suspicious) is as written; confirm names exist in the character data. |
| 124 | Sage Advice | Rolled skill not stated (Intrigue? Orate?). |
| 125 | Secret Dish | Card text says 'TEMPERATE SUCCESS' / 'INDULGENT SUCCESS' (not 'WINS') - confirm the roll type. |
| 130 | Stewardship | 'STEWARDSHIP WINS / ORATE WINS' = comparison of the player's own two skills - confirm. |
| 131 | Story Request | Rolled skill not stated (Orate?). |
| 133 | The Best Weapon | Rolled skill not stated; which weapon skill is gained is open. |
| 134 | Host Calls for a Dance | Card name says 'Dance' but the text is about a hunt/falconry (duplicate of 135) - likely a data error. |
| 136 | Host Calls for a Song | Rolled skill not stated (Singing?). 'Partial success' is not defined elsewhere. |
| 137 | Host Calls for a Toast | Rolled skill not stated (Courtesy? Orate?). 'Partial success' is not defined elsewhere. |
| 138 | Host Calls for a Toast | Rolled skill not stated (Courtesy? Orate?). 'Partial success' is not defined elsewhere. |
| 139 | Host Calls for a Toast | Rolled skill not stated (Courtesy? Orate?). 'Partial success' is not defined elsewhere. |
| 140 | Host Passes By | Rolled skill not stated (Orate? Courtesy?). |
| 141 | Host Passes By | Rolled skill not stated (Orate? Courtesy?). |
| 143 | Host Needs Advice | Rolled skill not stated (Intrigue? Courtesy?). |
| 145 | Those Bandits | Rolled skill not stated (Hunting? Tactics?). |
| 146 | Time to Share | Giving away a drawn card is not supported by the engine. |
| 148 | Wallflower | Rolled skill not stated (Flirting? Courtesy?). |
| 150 | Well-Dressed | Skill assumed to be Fashion (not named). |
| 151 | Who Are You? | Rolled skill not stated (Intrigue? Awareness?). |
| 153 | Wifely Woes | Precondition (married only) is not enforced by the engine. |
| 154 | Young Braggarts | Rolled skill not stated (Orate?). |

## 5. Other observations

- **Card 134** is named *Host Calls for a Dance* but its text is the hunt/falconry text of 135 — probably a data error.
- **Card 118 (Popular)** is a keeper but is tagged `duel` instead of `keep`; tags were left untouched.
- **Cards 82, 83**: tags (`duel`, `leave`) do not match the card text.
- **Cards 140 / 141** have the same `full` text but different `text`.
- "Partial success" (cards 136–139) is not defined elsewhere in the data.
- Engine features the cards need but that do not exist: passing/stealing cards (23, 24, 29, 30, 57, 146), counters (15), skill bonuses and "automatic success" (14, 34, 35, 58, 59–61, 67, 68, 108), preconditions (42, 55, 153), per-round penalties (53, 110).
- Cards 7, 8 and 9 were left as they were; 7 still uses an unexplained `action: check`.
