# Task 029: Heraldic drawings for the coat of arms charges  *(lite)*

- **ID / Status / Type:** 029 · `in-review` · `behaviour-changing` (appearance only, frontend)
- **Branch:** `main` of `AngrySenechal2`, uncommitted (frontend only) · **Created:** 2026-10-20 · **Reviewed via PR:** (not opened)

## What & why
The animals and objects of the Coat of Arms page were emoji silhouettes. They are now authentic heraldic drawings from Wikimedia Commons (Category:English_heraldic_dictionary, Category:SVG_versions_of_images_from_Complete_Guide_to_Heraldry_(book)); 99 charges have one (4 lions by pose, dragon, eagle, stag, wolf, bear, boar, fox, talbot, hound, goat, ram, sheep, bull, dolphin, escallop, serpent, bee, leopard, unicorn, gryphon, wyvern, pegasus, cockatrice, camelopard, phoenix, enfield), plus the heads of boar, bull and ram. Second round: horse, fish, eel, crab, bat, spider, fly, scorpion, ant, sea-horse, wyrm, manticore, ogre, centaur, sea-dog, mermaid, merman, harpy, salamander. Still emoji: hippogriff and yale (Commons has only scenes with a background), giant, satyr, opinicus, and the stag, gryphon and horse heads (black-only drawing / 170 KB).

Third round (objects): sword, bell, lymphad, castle, tower, sun, moon, skull, hand, arm, anchor, rose, thistle, tree, knight and warhorse, cup, helm, crown, warhammer, battle-axe, arrow, mace, flail, hammer, hunting horn, wheel, horseshoe, sickle, shovel, key, book, angel, lance, spear, garb, acorn, thunderbolt, church, walls, maunch, Pascal lamb, and the birds (crow, raven, heron, crane, owl, falcon, swan). The shape-drawn charges (crosses, crescents, mullets, roundels, fleur-de-lis, ...) are already heraldic and stay. Still emoji: gauntlet, spur, morningstar, fetterlock, buckle, scale, harp, saints and gods, Chi-Rho, dove, palm, mountain, fountain, apple, wild man, pavilion, bridge, gate, lighthouse, caduceus, medusa, horned god, shooting star, martlet, cock (422 KB).

## Files touched
- `AngrySenechal2/src/app/arms/images/*.svg` + `README.md` — svgo-optimised sources, with Commons file, author and licence (the four lions are CC BY-SA 3.0, the rest public domain / CC0).
- `AngrySenechal2/scripts/build-arms-images.mjs` → generated `src/app/arms/arms-images.ts` (~1 MB, inlined: the PNG/SVG export is a stand-alone blob and cannot reference files).
- `arms-data.ts` (`image`, `headImage` on `ChargeDef`), `arms-svg.ts` (`drawCharge` draws the image through the same tincture filter as the glyphs).
- `arms-svg.ts` `loadArmsImages()` — `arms-images.ts` is a lazy chunk (dynamic `import()`); `ArmsComponent.ngOnInit` loads it and draws the page again when it arrives. Until then, or if the load fails, the emoji are drawn.
- `AngrySenechal2/README.md` — credit.

## Before / after
Emoji silhouette → heraldic line drawing, coloured by the existing luminance filter (`proper` keeps the drawing's own colours). Quadrupeds are always drawn passant/statant whatever pose the form says (the blazon text still follows the form).

## Verification
`tsc --noEmit`, `arms-generator.spec.ts` (14 specs, one new for the lazy load) pass; `ng build` (development) puts the drawings in their own chunk (~2.7 MB source, ~100 drawings); all 35 images rendered in several tinctures in headless Chrome. Not looked at in the running app.

## Known limits
- The first coat of arms is drawn with emoji for a moment on a cold load, then redrawn with the drawings.
- Many of the drawings (crab, spider, fly, scorpion, bat, sea-horse, fish, horse, merman, the lions) are CC BY-SA; `images/README.md` has the authors.
- Dark tinctures (sable, vert) hide the fine lines of dark-on-dark drawings, as with the old glyphs.
