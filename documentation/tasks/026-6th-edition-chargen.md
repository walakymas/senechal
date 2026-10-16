# Task 026: 6th edition character creation (chargen)

> Source of the rules: *Pendragon Core Rulebook* (6th edition), chapter 3 "Creating Your Player-knight" (pp. 41–57) and chapter 4 "Traits and Passions" (Passion Courts, pp. 74–75). Page numbers are the printed ones.

---

## Metadata
- **ID:** 026
- **Status:** `proposed`
- **Type:** `behaviour-changing`
- **Branch:** `collab/6th-chargen` (backend: this repo; frontend: matching branch in `AngrySenechal2`)
- **Created:** 2026-10-15
- **Reviewed via PR:** <!-- link once opened -->
- **Operational impact:** a new `ruleset` field in the stored character JSON (additive, optional; a missing value means `5th`); new/extended `newchar` data in `senechal.yml` (`/base` response grows). The Angular part must be deployed for the web UI to change. No env vars, no DB migration.

## Context
- **Problem / motivation:** the web character generator (`AngrySenechal2/src/app/chargen`) follows the 5th edition (culture-fixed skill lists, all starting passions at 15, Famous trait, p15/p10/Spec +5 skill choices, "Additional Belongings" roll). The group has agreed that **new characters use the 6th edition passion rules** (four courts, max 40 per court) and will soon switch fully to 6th, so character creation must follow the 6th rules.
- **Decisions already made (2026-10-15, by the user):**
  - Characters are generated **at age 21**, i.e. with the full 7 years of Training & Practice.
  - Cultures come from the **Sir Larkins playtest** (https://www.sirlarkins.com/blog/2025/6/14/pendragon-play-test-other-cultures), **all of them**; earlier-edition material is reused only where the playtest is silent (homeland Hate, religion traits). Today `senechal.yml` → `newchar` has only Cymric, Irish, Aquitainian.
  - The user believes Healing Rate and Move Rate already exist on the sheet under another name. **Checked:** they exist under the *same* names (`utils.py:284-286`, `static/sheet.js:108-109`, `character-detail.component.html:103-104`, `chargen.component.ts:813-814`), but with the **5th edition formulas**: Healing Rate = (STR+CON)/10, Move Rate = (DEX+SIZ)/10 in code (the sheet label even says "(STR+DEX)/10", a label/code mismatch). The 6th formulas are Healing Rate = CON/5 and Movement Rate = (STR+DEX)/2 + 5. The values are computed on display, not stored, so changing the formula would change **existing** characters → see "Ruleset gating".
- **Related review finding:** none
- **Definition of done:** a player can create a complete 6th-edition 21-year-old squire/knight in the web chargen for every supported culture, the result follows the rules listed below (verified by unit tests), is saved with `ruleset: "6th"`, and displays correctly (court totals, derived values) on every sheet. Existing 5th characters are unchanged.

## Rules to implement (6th edition)

### Characteristics (p. 46)
- Constructed: 60 points, each final value 8–15, then the cultural modifier (Cymric +3 CON). Same as today except the 8–15 limits are enforced *before* the modifier.
- Random: SIZ/DEX/STR/APP 2D6+5, CON 2D6+5, then the cultural modifier. Cultural maximum (lifetime): 18, CON 21 for Cymric.
- Derived (p. 48–49): Knockdown = SIZ; Major Wound = CON; Weapon/Brawling Damage = (STR+SIZ)/6; Healing Rate = CON/5; Movement Rate = (STR+DEX)/2 + 5; Total Hit Points = CON+SIZ; Unconscious = HP/4 (round 0.5 up). Distinctive Features count by APP (Table 3.4).

### Traits (p. 50)
- Constructed: all 10; religion's favoured traits 13; Valorous 15; one trait raised to 16; 6 points distributed, none above 15. Pair sums stay 20.
- Random: 2D6+3 for each left-hand trait (Valorous 2D6+8), religious trait +3, opposite of a religious trait −3, then fill the right side (20 − value).
- Religious virtues: Christian: Chaste, Forgiving, Merciful, Modest, Spiritual, Temperate; Pagan: Lustful, Energetic, Generous, Honest, Proud, Spiritual.

### Passions (pp. 50–51, 74–75) — **new, the agreed team rule**
- Courts: **Fidelitas** (Duty, Fealty, Homage, Loyalty), **Fervor** (Hate, Love), **Adoratio** (Adoration, Devotion), **Civilitas** (Chivalry, Hospitality, Station). **Honor** stands outside the courts.
- **The sum of the values in a court must never exceed 40**; a critical-bonus passion counts as 20; no passion above 20 (above 15 at creation).
- Constructed start: Honor 15, Homage (Lord) 15 (mercenary: Fealty), Love (Family) 10, Station 10, Hospitality 10, Devotion (Deity) 5, plus the cultural/homeland Hate (e.g. Hate (Saxons) 5 for Salisbury); **15 free points** over these and any other passions; none above 15.
- Random start: Honor and Homage 2D6+8; Love (Family), Hospitality, Station 2D6+3; Devotion 1D6+2; Hate (Saxons) 1D6+2; up to 4D6+1 extra points distributed; none above 15.
- Optional inherited passions: parent's value − 15 as a bonus, max +5.
- Every court has at least one passion at the start (guaranteed by the mandatory ones); Honor ≥ 5 to keep knighthood.

### Skills (pp. 51–53)
1. Beginning values (Table 3.5): 5 / APP−5 / DEX/2 / STR/2 / 0 (Literacy), see the table for each skill.
2. Cultural Skill Modifiers (Cymric knight: +3 Charge, Horsemanship, Courtesy).
3. Family Characteristic (Table 3.6): +3 to one skill; constructed = free choice (not "Gifted"), random = 1D20 ("Gifted" = roll twice more).
4. Personal Skill Additions: 10 points. Limits: nothing above 15 (bonuses included); skills starting at 0 cannot be raised; APP-based skills cannot exceed APP (except cultural/family bonuses).
5. Later Characteristic changes do not affect the beginning skill values.

### Training & Practice (p. 53) — 7 years, character is 21
For each of the 7 years choose one: (a) 5 skill points with the same limits, (b) +1 Trait (max 19) or +1 Passion (max 20, **court limit 40 applies**), (c) +1 STR/SIZ/DEX/CON/APP (not above the cultural maximum, no effect on skills).

### Knighthood check (pp. 53, 56)
Age ≥ 18 and Sword, Charge, Brawling ≥ 10 plus two non-weapon Knightly Skills ≥ 10 (Awareness, Courtesy, First Aid, Hunting, Recognize, Battle, Horsemanship). If not met at 21 the character starts as an esquire (warn, do not block).

### Equipment and glory (pp. 55, 57)
Table 3.7 squire kit: gambeson and open helm, round shield, spear, dagger, rouncy. Table 3.8 starting horses. Passive Glory (Famous/Exalted trait or passion 15/25, Standard of Living 10, Fair/Elegant Appeal 10/25) and the Glory granted on knighthood (1,000 + 1/100 of the lord's Glory, max 1,000, + 50 for household knights) are noted for the sheet.

## Scope
- **In scope:**
  - A `ruleset` field (`"5th"` default for existing data, `"6th"` for new characters) and ruleset-aware derived values on every display.
  - 6th data in `senechal.yml` (skill start formulas, Table 3.6, cultural characteristic/skill modifiers, starting passions, squire kit) and the API (`getBase`) that serves it.
  - Rewriting the chargen steps for the 6th rules (see Plan), including a Passions step with live court totals and the 40 limit.
  - A pure, unit-tested rules module in `AngrySenechal2/src/app/chargen/` (like `chargen-belongings.ts`).
  - Enforcing the court limit in `passions.py` (helper) and keeping the three copies of the passion rules in sync (`passions.py`, `passion-category.ts`, `static/sheet.js`).
  - Cultures: **all 15 cultures of the Sir Larkins playtest** (see "Other cultures").
- **Out of scope:** converting existing characters, Ideals (Chivalrous/Religious/Romantic) automation, mercenary/Fealty variants beyond a simple choice, non-heir characters, women characters beyond the existing male/female skill split, the Winter Phase, the Discord `!` commands beyond showing the new derived values.

## Plan
- [ ] 1. **Rules module (frontend, pure functions + tests):** characteristic limits, derived values, trait methods, passion start values and court totals/limit, skill start formulas, personal-addition limits, training step validation, knighthood check. Unit tests with the book's examples (average Cymric knight: damage 4D6, HP 27, Unconscious 7, Healing 3, Movement 17, Knockdown 12, Major Wound 15).
- [ ] 2. **Data:** extend `senechal.yml` with a `ruleset: 6th` section per culture (characteristic modifiers, skill modifiers, starting passions, homeland hates, kit). Keep the existing 5th data untouched.
- [ ] 3. **All cultures from the Sir Larkins playtest** (15 cultures, tables above) as 6th data, with the culture step (native / fostered / mixed parents) and the knight/lady skill bonuses; mark them "playtest" in the data file and the UI; document in `documentation/6th-chargen.md`.
- [ ] 4. **Chargen UI:** step order Main → Characteristics → Traits → Passions → Skills (beginning values, cultural, family, 10 personal points) → Training (7 years) → Knighthood check → Equipment → Summary. Passions step shows the four courts with totals and blocks a value that would exceed 40.
- [ ] 5. **Ruleset gating:** save `ruleset: "6th"` with new characters; derived-value formulas (Healing/Movement) switch on it in `utils.py`, `static/sheet.js`, `pdf/sheet.py`, `character-detail`, `team` and chargen; fix the "(STR+DEX)/10" label mismatch for 5th at the same time (flag it as a separate before/after line).
- [ ] 6. **`passions.py`:** add `court_over_limit` helper and use it where the sheet highlights >40; mirror in `passion-category.ts` and `static/sheet.js`; extend `tests/passions_test.py`.
- [ ] 7. **Verify:** run the new spec files, `python -m unittest discover -s tests -p "*_test.py"`, create one character per culture by hand and compare against the book's examples.
- [ ] 8. **Documentation:** CHANGELOG entry, `pm/STATUS.md`, this file's Outcome, and a short `documentation/6th-chargen.md` (rules table and conversion notes).

## Other cultures — source: Sir Larkins' playtest (decided 2026-10-15)
Source: https://www.sirlarkins.com/blog/2025/6/14/pendragon-play-test-other-cultures (a **playtest**, subject to change; it gives only the cultural modifiers, not maxima, religion/trait changes or homeland passions). **All cultures of the page are supported.** Store them as data (`senechal.yml`, 6th section) with the source URL in a comment.

Characteristic modifier by group (+3 to one characteristic, applied after the 60-point distribution):

| Group | Modifier | Cultures |
|---|---|---|
| Celts | +3 CON | Cymri, Irish, Bretons |
| Germans | +3 SIZ | Saxons, Danes, Franks, Goths |
| Scythians | +3 DEX | Picts, Alans |
| Romans | +3 APP | Greeks, Latins, Aquitanians, Spanish |
| Huns | +3 DEX | Huns |
| Zazamancs | +3 APP | Zazamancs |

Cultural Skill Modifiers (+3 each):

| Culture | Knights | Ladies |
|---|---|---|
| Cymri | Charge, Horsemanship, Courtesy¹ | Industry, Stewardship, Courtesy¹ |
| Irish | Spear, Orate, Play Instrument | First Aid, Folklore, Singing |
| Bretons | Spear, Horsemanship, Courtesy | Chirurgery, Stewardship, Courtesy |
| Saxons | Two-handed Hafted, Gaming, Singing² | Industry, Intrigue, Singing² |
| Danes | Sword, Hunting, Seamanship³ | Chirurgery, Folklore, Industry |
| Franks | Horsemanship, Intrigue, Thrown Weapon | Brawling, First Aid, Stewardship |
| Goths | Hafted, Folklore, Orate | First Aid, Religion (type), Stewardship |
| Picts | Spear, Folklore, Hunting⁴ | First Aid, Folklore, Industry⁴ |
| Alans | Bow, Battle, Horsemanship | Bow, Falconry, Horsemanship |
| Greeks | Spear, Literacy, Intrigue | Courtesy, Literacy, Intrigue |
| Latins | Sword, Literacy, Orate | Stewardship, Literacy, Courtesy |
| Aquitanians | Sword, Flirting, Courtesy | Horsemanship, Flirting, Courtesy |
| Spanish | Awareness, Horsemanship, Spear | Horsemanship, Literacy, Industry |
| Huns | Bow, Horsemanship, Falconry | Awareness, Brawling, Horsemanship |
| Zazamancs | Spear, Hunting, First Aid | Chirurgery, Fashion, Recognize |

¹ Cymri from Roman cities may use the Latin bonus instead. ² Saxons from Berroc County may use the Cymri bonus instead. ³ New skill. ⁴ Picts from Jagent County may use the Cymri bonus instead.

Native-culture rules from the same page (chargen should offer them as a "Culture" step): fostered from birth to 7 in another culture → that culture's modifier and skill bonuses; fostered abroad 7–14 → keep the native characteristic modifier, may choose the fostered culture's skill bonuses; parents of two cultures → choose one culture for both modifier and skills (GM may allow the modifier of one parent with the skills of the other).

**Consequences for the plan:**
- The existing `newchar` entries (Cymric `con: 3`, Irish `con: 3`, Aquitainian `con: 1/dex: 1/app: 1`) do **not** match this source (Aquitanians → +3 APP): the 6th data is a separate section; the 5th data stays for `ruleset: 5th`.
- Skill bonuses are the same gender-dependent +3 as the core Cymric rule; the chargen needs a male/female (knight/lady) choice per culture, plus the "or use another culture's bonus" exceptions (¹²⁴) as a selectable option.
- **Skills outside Table 3.5** appear as bonuses (Industry, Chirurgery, Seamanship, Thrown Weapon is in the table; Industry, Chirurgery, Seamanship are not in the core text I read). Their start value and whether a +3 may be applied to a 0-start skill must be checked in chapter 5 / the playtest before coding (see open question 3).
- Homeland passions (e.g. Hate (Saxons)) and religion/trait differences are **not** given by the source: keep the existing `homeland` data (5th) as the proposed Hate, and leave religion choice to the existing trait tables, flagged as "not from the playtest".
- Characteristic maxima for other cultures are not given either: use 18 (CON 21 only for the +3 CON group, by analogy with the Cymric row) and flag it as an assumption.

## Open questions
1. **Homeland/starting Hate and religion traits for non-Cymric cultures** are not in the playtest: keep the 5th-edition homeland data and religion trait tables (recommended) or define new ones?
2. **Characteristic maxima** for non-Celtic groups: analogy with Cymric (modified characteristic max 21, others 18) acceptable?
3. **Skills outside Table 3.5** (Industry, Chirurgery, Seamanship): treat as start value 0 with the +3 allowed, or give them 5th-edition start values? Needs the chapter 5 skill list, which was not read in full yet.
4. **Ruleset gating of derived values.** Recommended: gate by `ruleset` so existing characters keep their numbers. Alternative: switch everyone to the 6th formulas at once when the group moves fully to 6th.

## Respect-the-owner checklist
> This project is owned by **walakymas**; we are collaborators. Confirm each item.
- [ ] Working on a dedicated branch, not `main`.
- [ ] No unrelated reformatting, renaming, or import re-ordering.
- [ ] No deletion of working code without flagging it in *Before / after* below (the 5th chargen steps stay available for `ruleset: 5th`).
- [ ] Behaviour-changing edits are flagged in *Before / after* and *Operational impact*; the PR is the review gate.

## DOCUMENTATION — required (do not set Status to `done` until all checked)
- [ ] Added a `documentation/CHANGELOG.md` entry (date, branch, files, before/after, rollback).
- [ ] Refreshed `pm/STATUS.md` to reflect the new current state (and `pm/ROADMAP.md` if priorities changed).
- [ ] Filled the *Outcome* section of this task file with what actually changed.
- [ ] Listed every file touched in the *Files touched* table with a one-line rationale.
- [ ] Updated any affected README / inline docstrings if usage or behaviour changed.
- [ ] If a new concept/convention was introduced, added or extended a doc under `documentation/` (planned: `documentation/6th-chargen.md`).

## Files touched
| File | Lines | Change | Rationale |
|------|-------|--------|-----------|
|      |       |        | *(filled during implementation)* |

## Before / after
- **Before:** 5th edition chargen; all passions start at 15 with no court limit enforced; Healing/Move computed with 5th formulas.
- **After:** 6th edition chargen for new characters (`ruleset: "6th"`); court limit 40 enforced during creation; Healing/Movement per 6th for `6th` characters; `5th` characters unchanged.
- **Behaviour-changing?** yes — new data in `/base`, a new optional field in stored characters, new derived values for `6th` characters. See Operational impact.

## Verification
- **How tested:** *(fill during implementation)*
- **How the owner can reproduce:** open the chargen for a new character, create one per culture, compare with the book's average-knight example.

## Risk & rollback
- **Risk:** formula changes affecting existing characters if gating is skipped; the three copies of the passion rules drifting apart; fan-conversion values being disputed by the group.
- **Rollback:** `git revert` the backend and frontend commits; stored `ruleset` fields are ignored by older code.

## Outcome  *(fill on completion)*
- **Result:** <what was delivered>
- **CHANGELOG entry:** <date/anchor in CHANGELOG.md>
- **Commit(s):** <sha(s)>
