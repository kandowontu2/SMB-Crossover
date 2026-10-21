# World objects and Lance Bean

This update addresses the reported Contra flagpole/trampoline failures and
missing castle fireballs, and adds Lance as a selectable Bill skin. The
tester supplied no exact ROM build or mapper. The hardware report is evidence
of symptoms; the reproductions below use Mesen 2 and explicit fixtures.

## Lance

On character selection, highlight Bill and press Select to toggle Bill/Lance.
A held press toggles once. Left/Right and Up/Down retain roster navigation;
leaving the slot and returning remembers its variant. The color preview and
highlighted name change together. Gameplay uses Bill's physics, upgrades,
weapons and music, with Lance's own art, LANCE HUD label, lives portraits and
pickup colors.

Art is extracted from the pinned Crossover 2.02 `Bill003` skin, identified as
Lance Bean in `BmdInfo.as`. The source sheet is
`406_com.smbc.graphics.skins.BmdInfo_Bill003.png`, SHA-256
`a75d5df17269f90ad6cd36e6b7324c6b41a88ec07ad7cbc62787c78ff9ed968d`.
The generator reconstructs its separate torso and legs, packs 48 poses into
nine 1 KiB pools, and reserves Bill's bullet tiles in each pool. Three legacy
power states share that skin. Palette 0 is `$1c,$36,$0f`; red pants share the
unchanged world palette. See `docs/reference/lance-assets.json` and
`tools/reference/build_lance_assets.py`.

`lance-select.lua` uses real menu inputs for both toggle directions, a held
button, navigation away/back and game confirmation. It checks the source
preview pointer, actual PPU colors/name and gameplay HUD/movement.
`lance-controls.lua` exercises movement, jumps and all three guns, including
mapped bullet CHR. The lives and power-up tests inspect all three portraits
and both actual native pickup transitions.

## Exit flags

The native 4-1 end could softlock in two ways when all six actor slots were
occupied: the pole flag was skipped, or the castle flag overwrote it. The
player still grabbed the pole, then stayed in engine state 4 at Y=159. A
negative reproduction is retained in
`build/verification/bill-flagpole-full-before-fix.log`.

Both producers now allocate an empty slot or reclaim a noncritical actor,
protecting both exit flags. The pole's score update also restores its actor
index before preparing the flag graphics.

Thirteen `*-flagpole-full.lua` fixtures cover the twelve characters and Lance.
They fill the pool as the real 4-1 pole is parsed, then place the player beside
that pole. Normal Right/jump input completes contact, sliding, the castle and time
conversion, the 4-2 pipe intro, and movement in the real 4-2 underground room.
These are native-room fixtures, not complete controller-only level clears.

## Springs

The guest launch helper changed X while indexing character forces and returned
that changed value to the native spring handler. Rendering and subsequent
native handling could then use the wrong actor slot. It now preserves X.

A separate pit check mistook signed Y page `$ff`, above the viewport, for a
fall below the stage during a high rebound. It now accepts negative pages.
Sophia also applied strong jump-release damping even when A had never been
pressed; release damping now follows an actual release event.

`world-springs.lua` has 52 actual landing/compression/launch fixtures: twelve
characters plus Lance, actor slots 0/5, ordinary and freshly boosted launches.
It checks the native force, per-character velocity, preserved actor index,
airborne movement after launch and a running game loop. `bill-world-objects`
also checks a third spring slot and a simple pole slide. These reproduce
confirmed engine errors; the tester's precise hardware trampoline freeze has
not been independently reproduced on their console.

## Castle firebars

Native firebars wrote OAM during physics, then the guest's final sprite pass
cleared those writes. Their tiles also came from player CHR, replaced by guest
graphics. Parts now retain the native collision/rotation calculation, cache
their positions, and render after clearing using stable native fireball art in
unused misc CHR pairs `$00/$02`. Mushroom art remains at `$3c/$3e`.

`world-firebars.lua` covers short/long bars for every character and Lance. It
checks all six/twelve native parts in final shadow OAM, eight-pixel spacing,
the actual mapped native CHR and unchanged mushroom CHR. The hardware limit
of eight sprites on one scanline still applies. This fix concerns rotating
firebars; native Podoboos and Bowser flames use separate stable actor art.

## Verification

All **345 emulator cases passed** on 2026-10-16, using Mesen 2 on both MMC3
and MMC5. The 19-field Mario replay still matches its baseline for all 521
frames. The final suite log is
`build/verification/world-objects-suite-final.log`.

Run `python tools/verify.py --mmc5` to reproduce the checks. The suite records
individual results and exact ROM SHA-256 hashes in
`build/verification/summary.json`. Screenshots and logs sit beside it.
Physical cartridge validation remains outstanding.

| ROM | SHA-256 |
| --- | --- |
| MMC3 | `bbab762c8b793bf47c47dd1df7c541f60b06dc2de96f8c72ae31f2da40df7c2a` |
| MMC5 | `f330ae8be1069c474d4420f3eaa50b33ad730e5b3dc74483757edc69a45055d9` |
