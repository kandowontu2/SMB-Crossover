# Crossover level-layout audit â€” 2026-10-22

> **Revision 2:** The enemy/object and interactive census below supersedes revision1’s coarse B→S interpretation for2.02 and its XML-only completeness statement. Original revision1 files/hashes are preserved in the evidence history.

**Audit only: no game level data, gameplay code, ROM, or checkpoint was changed by this audit.** Every campaign level and subarea in both pinned XML datasets was enumerated before any proposed map implementation.

The immediate missing feature is real: Crossover authors additional moving platforms and mushroom ledges, selected by character. The current ROM retains all 68 original SMB1Base level/enemy streams byte for byte on both mappers and has no corresponding character-helper dataset. These accommodations must be implemented with their source eligibility, rather than widening every gap for everyone.

## Version and evidence contract

- The hosted six-character reference is the requested site SWF, SHA-256 `46bdcf0b60721bbe0f006cdb083f503e0312feacede6f65f2942f7a5a406b1eb`. Its decompiled `StatManager.NUM_CHARACTERS` is 6. No embedded release-version string was found in its game scripts. It is called **hosted 1.x** here; this is not authentication of an exact 1.0 release.
- The later SWF SHA-256 is `6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af`. `GameSettings.as:68` explicitly declares 2.02. Exact 2.0.0 has not been separately obtained/authenticated.
- The NES comparison baseline is the authored SMB1Base streams at upstream commit `46ff88f7d9e854db80bf8d50e5bf74340fcc64ce`. All 34 level streams plus 34 enemy streams match the baseline MMC3 and both current mapper images exactly. `source-binding.json` gives per-stream hashes and compiled offsets. This proves data identity, not that patched runtime behavior is identical to Nintendo SMB 1.
- The comparison covers 32 campaign levels /61 areas in each version. 2.02 also embeds 9-1a,9-2a,9-8a,9-9a, which are outside the 32-level campaign. `CharacterSelect.FULL_LEVEL_STR` explicitly uses 9-1a. They must not be imported as four new campaign levels.
- Full raw differences, including skin/name changes, are in `xml-inventory.json`. Every nonzero source tile/object from both versions is in `all-source-cells.csv`; every moving platform and transport is in `platforms-and-transports.csv`. Nothing is omitted merely because it is outside 1-1/2-2.

## Exact conditional object rules

| Character | Hosted 1.x horizontal / vertical family |2.02 horizontal / vertical family |
|---|---|---|
| Mario | no / no | no / no |
| Luigi | not present | no / no |
| Bill | yes / yes | yes / yes |
| Link | yes / yes | yes / yes |
| MegaMan | yes / yes | yes / yes |
| Samus | yes / no | yes / no |
| Simon | yes / no | yes / no |
| Ryu | not present | yes / no |
| Sophia | not present | no / yes |
| Bass | not present | no / no |

The protected booleans default to false; only the explicit constructor assignments enable them. Mario/Luigi/Bass therefore have neither family. Pit, Rygar and Scrooge were not official 2.02 characters; their helper policy is undefined by that source. Our Lance alternate is not a separate 2.02 class.

**Hosted 1.x filtering is asymmetric.** `Level.as:1288â€“1295` filters `PICKUPS.charHorz` using the horizontal flag, and `MAP.charVert` using the vertical flag. It does not filter `PICKUPS.charVert`. Consequently the tagged 8-1,8-2 and 8-4c moving platforms appear for all six characters in that reference. 2.02 `Level.as:914â€“934` filters both tags in both layers. Do not apply the later filtering retroactively and claim literal hosted behavior.

## Complete character-specific platform list

Coordinates below are zero-based XML tile origins and NES-normalized platform centers/top Y. Flash coordinates are twice the NES coordinates. Width is measured in 8-NES-pixel units: `width=2` is 16px, `width=4` is 32px and `width=6` is 48px; height is 8px. `shiftRight` adds 8px to the ordinary tile-center anchor. **These are source coordinates, not automatic NES insertion coordinates.** Native level columns sometimes differ; the 1-1 example below demonstrates the necessary landmark alignment.

| Area | XML tile(x,y) | NES center/top(x,y) | Width | Motion | Hosted 1.x eligibility |2.02 eligibility |
|---|---:|---:|---:|---|---|---|
| 1-1a | (192, 4) | (3088, 64) | 16 | waveHorizontal | H | H |
| 1-2d | (17, 4) | (288, 64) | 16 | waveHorizontal | H | H |
| 1-3a | (147, 4) | (2368, 64) | 16 | waveHorizontal | H | H |
| 2-1a | (195, 4) | (3136, 64) | 16 | waveHorizontal | H | H |
| 2-2b | (135, 13) | (2168, 208) | 48 | waveHorizontal | H | H |
| 2-2b | (160, 10) | (2568, 160) | 48 | waveVertical | H | H |
| 2-2c | (17, 4) | (288, 64) | 16 | waveHorizontal | H | H |
| 2-3a | (108, 13) | (1744, 208) | 16 | waveHorizontal | absent | H |
| 2-3a | (220, 4) | (3536, 64) | 16 | waveHorizontal | H | H |
| 3-1a | (196, 4) | (3152, 64) | 16 | waveHorizontal | H | H |
| 3-2a | (204, 4) | (3280, 64) | 16 | waveHorizontal | H | H |
| 3-3a | (146, 4) | (2352, 64) | 16 | waveHorizontal | H | H |
| 4-1a | (221, 4) | (3552, 64) | 16 | waveHorizontal | H | H |
| 4-2e | (17, 4) | (288, 64) | 16 | waveHorizontal | H | H |
| 4-3a | (142, 4) | (2288, 64) | 16 | waveHorizontal | H | H |
| 5-1a | (194, 4) | (3120, 64) | 16 | waveHorizontal | H | H |
| 5-2a | (195, 4) | (3136, 64) | 16 | waveHorizontal | H | H |
| 5-3a | (147, 4) | (2368, 64) | 16 | waveHorizontal | H | H |
| 6-1a | (181, 4) | (2912, 64) | 16 | waveHorizontal | H | H |
| 6-2a | (211, 4) | (3392, 64) | 16 | waveHorizontal | H | H |
| 6-3a | (162, 4) | (2608, 64) | 16 | waveHorizontal | H | H |
| 7-1a | (174, 4) | (2800, 64) | 16 | waveHorizontal | H | H |
| 7-2b | (135, 13) | (2168, 208) | 32 | waveHorizontal | H | H |
| 7-2b | (160, 10) | (2568, 160) | 32 | waveVertical | H | H |
| 7-2c | (17, 4) | (288, 64) | 16 | waveHorizontal | H | H |
| 7-3a | (108, 13) | (1744, 208) | 16 | waveHorizontal | absent | H |
| 7-3a | (221, 4) | (3552, 64) | 16 | waveHorizontal | H | H |
| 8-1a | (223, 13) | (3584, 208) | 16 | waveHorizontal | all six (unfiltered tag) | H |
| 8-1a | (316, 13) | (5064, 208) | 16 | waveHorizontal | absent | H |
| 8-1a | (371, 4) | (5952, 64) | 16 | waveHorizontal | H | H |
| 8-2a | (150, 12) | (2416, 192) | 16 | waveHorizontal | all six (unfiltered tag) | H |
| 8-2a | (211, 4) | (3392, 64) | 16 | waveHorizontal | H | H |
| 8-3a | (209, 4) | (3360, 64) | 16 | waveHorizontal | H | H |
| 8-4c | (23, 13) | (376, 208) | 16 | waveHorizontal | all six (unfiltered tag) | V |

H and V mean the horizontal and vertical character sets in the preceding table. There are 31 campaign moving helpers in hosted 1.x and 34 in 2.02. All are absent from the current port. The four water helpers are not generic replacements for swimming physics: source water-mode behavior and actual moving-platform collision must both match.

Platform trajectories are `x = centerX + sin(angle)*30` NES pixels, angle increasing 1.5rad/s for horizontal motion (period 4.1887902s), and `y = centerY + sin(angle)*75`, angle increasing 1rad/s for vertical motion (period 6.2831853s), initially phase 0. Their maximum speeds are 45 and 75 NES pixels/s respectively. The source platform is a `Ground` object in the `HT_PLATFORM` collision category, uses previous/current platform hit rectangles, and carries supported characters through their platform-ground response. It is not a coin/enemy sprite with a decorative animation. Its 8px-tall rectangular hit shape is confirmed by both SWF shape bounds and the 2.02HRect placement. Native 8-bit phase/table quantization must be documented and tested when ported. Motion updates only while the platform is on screen or requests offscreen updates; both versions default the latter flag to false. Therefore its initial phase is not measured from global power-on time.

Hosted 1.x has no platform-width difficulty shrink. 2.02 nativeFlash difficulty HARD subtracts 2 width units with a minimum 2; VERY_HARD clamps all to 2. The source selector has five positions. **Our Easy/Hard behavior toggle is a different setting** and does not by itself authorize these additional enemy/platform difficulty modifiers.

### 1-1 flagpole example

The source helper is tile(192,4), center(3088,64),16Ã—8px, horizontal sine motion, H characters only. The source flagpole is column 197, but native SMB1Base uses column 198 because the hosted map removes a column after the first pipe. Thus placing a helper blindly at 3088 on the existing NES map would be 16px left of the source-relative position. Preserving current NES geometry requires center 3104,64 to retain the source 64px offset before the flagpole; alternatively the entire source layout must be adopted consistently. This is why positions in the inventory are not direct patch bytes.

## Complete conditional static terrain list

| Area / versions | Source cells | What exists | Eligibility |
|---|---|---|---|
|4-3a / both |(30,7),(31,7),(32,7) | Three 16Ã—16px mushroom-top cells, rectangle 480..528 Ã—112..128 | V |
|4-3a / both |(31,8)..(31,14) | Mushroom stems beneath that support; decorative and non-solid | V |
|3-3a /2.02 only |(34,14),(35,14) | Two 16Ã—16px mushroom-top cells, rectangle 544..576 Ã—224..240 | H |

The 4-3 helper is orange in hosted 1.x and reuses themed green names in 2.02. That name/color conversion is not a new ledge geometry. No other conditional static cells occur anywhere in the 61 campaign areas.

## Complete structural change list between the two pinned Crossover datasets

| Area | Tile(s) | Hosted 1.x â†’2.02 |
|---|---|---|
|1-1a |(128,12) | Remove one Goomba (`enemyGoombaBrown&&shiftRight&&`); all other pickup-layer objects remain unchanged |
|2-3a |(108,13) | Add 16Ã—8 horizontal H helper at center 1744,208 |
|3-3a |(34,14),(35,14) | Add the H mushroom landing above |
|4-4a |(161,10),(225,10) | Remove two solid dungeon cells |
|7-3a |(108,13) | Add the same 16Ã—8 horizontal H helper at center 1744,208 |
|8-1a |(223,13) | Platform tag charVertâ†’charHorz; hosted constructor formerly admitted all six;2.02 admits H |
|8-1a |(316,13) | Add 16Ã—8 horizontal H helper at center 5064,208 (no shiftRight) |
|8-2a |(150,12) | Platform tag charVertâ†’charHorz; hosted constructor formerly admitted all six;2.02 admits H |
|8-4c |(23,13) | Raw object unchanged, but constructor fix changes effective admission from all six to V only |

The first eight rows cover every campaign cell whose collidable class/conditional support or pickup record differs. The final row is a runtime filtering change, so it cannot be detected by XML diff alone. All other pickup/transport/enemy records and campaign map dimensions are identical across the two XML datasets. There are many visual/theme-name changes; the full raw list is retained and must not be mistaken for thousands of new obstacles.

## NES baseline versus Crossover â€” every area

The following table covers every campaign subarea. `NES span` gives the corresponding authored native area and original column start. A span summary is an exact sequence alignment of solid/item/brick/hidden/spring/flag classes, excluding character helpers and scenery. Detailed source cells, raw NES tile IDs and original/replacement coordinate ranges are retained in `static-column-alignments.json`. It exposes authoring shifts and interactive-type changes; it does not infer that each ambiguous floor-column alignment is an intentional design change. Castle maze caveats follow.

| Crossover area | Width | NES span | Literal static differences / representation |
|---|---:|---|---|
| 1-1a | 223 | Ground 6 +0 | delete NES[30,31) â†’ C[30,30); delete NES[205,206) â†’ C[204,204); insert NES[224,224) â†’ C[222,223) |
| 1-1b | 16 | Underground 3 +0 | No static topology/type difference in the compared span |
| 1-2a | 16 | Ground 10 +0 | No static topology/type difference in the compared span |
| 1-2b | 191 | Underground 1 +0 | delete NES[62,63) â†’ C[62,62); replace NES[165,166) â†’ C[164,165) |
| 1-2c | 16 | Underground 3 +32 | No static topology/type difference in the compared span |
| 1-2d | 42 | Ground 6 +176 | delete NES[205,206) â†’ C[29,29); insert NES[218,218) â†’ C[41,42) |
| 1-3a | 176 | Ground 7 +0 | delete NES[158,161) â†’ C[158,158); insert NES[176,176) â†’ C[173,176) |
| 1-4a | 162 | Castle 1 +0 | insert NES[72,72) â†’ C[72,74) |
| 2-1a | 224 | Ground 9 +0 | delete NES[207,208) â†’ C[207,207); insert NES[224,224) â†’ C[223,224) |
| 2-1b | 78 | Ground 12 +0 | delete NES[78,80) â†’ C[78,78) |
| 2-1c | 16 | Underground 3 +0 | No static topology/type difference in the compared span |
| 2-2a | 16 | Ground 10 +0 | No static topology/type difference in the compared span |
| 2-2b | 192 | Water 2 +0 | No static topology/type difference in the compared span |
| 2-2c | 42 | Ground 6 +176 | delete NES[205,206) â†’ C[29,29); insert NES[218,218) â†’ C[41,42) |
| 2-3a | 240 | Ground 8 +0 | delete NES[231,234) â†’ C[231,231); insert NES[240,240) â†’ C[237,240) |
| 2-4a | 160 | Castle 3 +0 | No static topology/type difference in the compared span |
| 3-1a | 225 | Ground 5 +0 | insert NES[111,111) â†’ C[111,112); delete NES[207,208) â†’ C[208,208); insert NES[224,224) â†’ C[224,225) |
| 3-1b | 16 | Underground 3 +64 | No static topology/type difference in the compared span |
| 3-1c | 94 | Ground 21 +0 | delete NES[94,96) â†’ C[94,94) |
| 3-2a | 224 | Ground 22 +0 | delete NES[216,217) â†’ C[216,216); insert NES[224,224) â†’ C[223,224) |
| 3-3a | 176 | Ground 1 +0 | delete NES[157,160) â†’ C[157,157); insert NES[176,176) â†’ C[173,176) |
| 3-4a | 160 | Castle 4 +0 | No static topology/type difference in the compared span |
| 4-1a | 241 | Ground 3 +0 | insert NES[132,132) â†’ C[132,133); delete NES[232,233) â†’ C[233,233); insert NES[240,240) â†’ C[240,241) |
| 4-1b | 16 | Underground 3 +96 | No static topology/type difference in the compared span |
| 4-2a | 16 | Ground 10 +0 | No static topology/type difference in the compared span |
| 4-2b | 224 | Underground 2 +0 | replace NES[128,129) â†’ C[128,129); replace NES[186,187) â†’ C[186,187) |
| 4-2c | 64 | Ground 16 +0 | No static topology/type difference in the compared span |
| 4-2d | 16 | Underground 3 +128 | No static topology/type difference in the compared span |
| 4-2e | 42 | Ground 6 +176 | delete NES[205,206) â†’ C[29,29); insert NES[218,218) â†’ C[41,42) |
| 4-3a | 160 | Ground 13 +0 | delete NES[153,156) â†’ C[153,153); insert NES[160,160) â†’ C[157,160) |
| 4-4a | 320 | Castle 2 +0 | insert NES[82,82) â†’ C[82,147); insert NES[111,111) â†’ C[176,239); delete NES[192,320) â†’ C[320,320); native loop/transport representation differs |
| 5-1a | 224 | Ground 11 +0 | delete NES[206,207) â†’ C[206,206); insert NES[224,224) â†’ C[223,224) |
| 5-1b | 16 | Underground 3 +128 | No static topology/type difference in the compared span |
| 5-2a | 224 | Ground 18 +0 | replace NES[147,150) â†’ C[147,150); delete NES[207,208) â†’ C[207,207); insert NES[224,224) â†’ C[223,224) |
| 5-2b | 65 | Water 1 +0 | insert NES[64,64) â†’ C[64,65) |
| 5-2c | 78 | Ground 12 +0 | delete NES[78,80) â†’ C[78,78) |
| 5-3a | 176 | Ground 7 +0 | delete NES[158,161) â†’ C[158,158); insert NES[176,176) â†’ C[173,176) |
| 5-4a | 160 | Castle 3 +0 | No static topology/type difference in the compared span |
| 6-1a | 207 | Ground 15 +0 | delete NES[195,196) â†’ C[195,195) |
| 6-2a | 240 | Ground 4 +0 | replace NES[113,114) â†’ C[113,114); replace NES[115,116) â†’ C[115,116); replace NES[119,128) â†’ C[119,128); delete NES[223,224) â†’ C[223,223); insert NES[240,240) â†’ C[239,240) |
| 6-2b | 16 | Underground 3 +128 | No static topology/type difference in the compared span |
| 6-2c | 65 | Water 1 +0 | insert NES[64,64) â†’ C[64,65) |
| 6-2d | 94 | Ground 21 +0 | delete NES[94,96) â†’ C[94,94) |
| 6-2e | 16 | Underground 3 +96 | No static topology/type difference in the compared span |
| 6-3a | 192 | Ground 14 +0 | delete NES[173,176) â†’ C[173,173); insert NES[192,192) â†’ C[189,192) |
| 6-4a | 160 | Castle 1 +0 | No static topology/type difference in the compared span |
| 7-1a | 208 | Ground 20 +0 | delete NES[186,187) â†’ C[186,186); insert NES[208,208) â†’ C[207,208) |
| 7-1b | 16 | Underground 3 +0 | No static topology/type difference in the compared span |
| 7-2a | 16 | Ground 10 +0 | No static topology/type difference in the compared span |
| 7-2b | 192 | Water 2 +0 | No static topology/type difference in the compared span |
| 7-2c | 42 | Ground 6 +176 | delete NES[205,206) â†’ C[29,29); insert NES[218,218) â†’ C[41,42) |
| 7-3a | 241 | Ground 8 +0 | insert NES[195,195) â†’ C[195,196); delete NES[231,234) â†’ C[232,232); insert NES[240,240) â†’ C[238,241) |
| 7-4a | 352 | Castle 5 +0 | insert NES[32,32) â†’ C[32,96); insert NES[163,163) â†’ C[227,291); delete NES[224,352) â†’ C[352,352); native loop/transport representation differs |
| 8-1a | 400 | Ground 17 +0 | delete NES[383,384) â†’ C[383,383); insert NES[400,400) â†’ C[399,400) |
| 8-1b | 16 | Underground 3 +32 | No static topology/type difference in the compared span |
| 8-2a | 240 | Ground 19 +0 | delete NES[223,224) â†’ C[223,223); insert NES[240,240) â†’ C[239,240) |
| 8-2b | 16 | Underground 3 +128 | No static topology/type difference in the compared span |
| 8-3a | 240 | Ground 2 +0 | delete NES[223,226) â†’ C[223,223); insert NES[240,240) â†’ C[237,240) |
| 8-4a | 331 | Castle 6 +0 | insert NES[96,96) â†’ C[96,107); insert NES[256,256) â†’ C[267,331); native loop/transport representation differs |
| 8-4b | 73 | Water 3 +0 | insert NES[67,67) â†’ C[67,68); delete NES[72,80) â†’ C[73,73) |
| 8-4c | 64 | Castle 6 +256 | No static topology/type difference in the compared span |

The small one-column changes near many castles are the original breakable-brick tile used in exit artwork versus a noncollidable Crossover castle sprite, not a newly authored giant gap. The 1-1,1-2,1-4,3-1,4-1 and 7-3 alignments also reveal actual inserted/deleted columns and therefore shifted downstream coordinates. 5-2 and 6-2 contain explicit breakable-brickâ†’unbreakable-ground representations (exact cells below). Cloud and water bonus areas sometimes omit or add trailing padding columns. These differences are fully recorded, but padding and exit-art collisions must be distinguished from an obstacle that players can actually encounter.

### Breakable/solid class replacements in unchanged spans

- 1-2b: (164,10) Bâ†’S `groundUnbreakableBrickBlueNight`.
- 4-2b: (186,10) Bâ†’S `groundUnbreakableBrickBlueNight`.
- 5-2a: (147,9) Bâ†’S `groundUnbreakableBrickBrownDay`, (148,9) Bâ†’S `groundUnbreakableBrickBrownDay`, (149,9) Bâ†’S `groundUnbreakableBrickBrownDay`.
- 6-2a: (113,9) Bâ†’S `groundUnbreakableBrickBrownDay`.
- 6-2a: (115,5) Bâ†’S `groundUnbreakableBrickBrownDay`.
- 6-2a: (119,5) Bâ†’S `groundUnbreakableBrickBrownDay`, (120,5) Bâ†’S `groundUnbreakableBrickBrownDay`, (121,5) Bâ†’S `groundUnbreakableBrickBrownDay`, (122,5) Bâ†’S `groundUnbreakableBrickBrownDay`, (123,5) Bâ†’S `groundUnbreakableBrickBrownDay`, (124,5) Bâ†’S `groundUnbreakableBrickBrownDay`, (125,5) Bâ†’S `groundUnbreakableBrickBrownDay`, (126,5) Bâ†’S `groundUnbreakableBrickBrownDay`, (127,5) Bâ†’S `groundUnbreakableBrickBrownDay`.

B means breakable brick; S means solid non-brick terrain. These are authored static classifications, not a promise that every current projectile already respects the distinction.

### Castle loops and shared rooms

Crossover 4-4 and 7-4 use explicit `teleporterCheckPoint`, `teleporterStart`, `teleporterStartOne` and `teleporterEnd` records, with extra repeated geometry laid out in the XML. Original SMB 1 instead rewinds four native pages using `LoopCmdWorldNumber/PageNumber/YPosition` and multi-loop counters. 8-4 splits the native castle/water route into 8-4a/b/c and duplicates a 64-column section in 8-4a. Its source teleporter at column 110,180,317 and pipe-network destinations are recorded verbatim in `platforms-and-transports.csv`. Those are representations of a maze/transport graph, not permission to append all XML columns into one native linear room. A runtime path-by-path maze parity test is required before translating those sections.

Original SMB 1 shares one underground bonus-area stream across many worlds and shares main geometry for 1-3/5-3,2-3/7-3,2-2/7-2,1-4/6-4 and 2-4/5-4. Crossover expands them into per-level XML areas and can assign different pickups/helpers. The source area IDs must therefore remain part of a helper key; a blanket change to a shared native stream would affect unrelated worlds.

## Difficulty, skins, and other global level behavior

- 2.02 has one 32-level campaign XML. Map skins select graphics/music/theme conventions, not independent 1.0/2.0 campaign maps. The developer explicitly announced difficulty-dependent layouts and the SMB Special campaign as **new 3.0 features**: [official 3.0 announcement](https://explodingrabbit.com/super-mario-crossover-3-0-trailer-304/). Lost Levels was described there as a future addition. Do not import 3.x/Special/Lost Levels layouts into this 2.02 audit.
- Native Flash HARD replaces Goombas with Beetles; VERY_HARD uses SpikeTops (`Level.as:1076â€“1088`). Platform width changes are described above. Those settings must remain distinct from our version-behavior selector.
- 2.02 allows leftward camera scrolling by default (`screenScrollsLeft = !Cheats.classicScreenScroll`, default cheat false). Native NES SMB 1 permanently discards the left camera edge. This affects traversal/backtracking but is not a missing platform; adding helpers does not implement it.
- Pipe/vine/warp transport and castle checkpoint records are fully inventoried. Their XML records are identical across both pinned campaign datasets except the six pickup changes already listed; their native engine implementations differ.
- The current cannon/firebar repairs are runtime changes and do not add the authored Crossover helper platforms. Failing to clear a gap with one controller policy is not evidence that the gap should be filled. Bass has a source dash/double-jump route; the root has separately verified his current ordinary route through 2-2.

## Concrete implementation checklist â€” review this list before changes

1. Keep this inventory/report as the pre-change evidence. Bind any implementation to the chosen pinned version per behavior mode; exact 1.0/2.0.0 files remain an explicit provenance gap.
2. Add an area/world-keyed accommodation table containing all 31 hosted or 34 later campaign moving helpers and the conditional 3-3/4-3 static supports. Include hidden/visible admission by actual constructor semantics above. Make no unrequested family assignment for Pit/Rygar/Scrooge.
3. Translate source coordinates using explicit corresponding landmarks/column mapping. Decide consistently whether to adopt the literal source column edits or retain native geometry with source-relative helper anchors; record the choice for every shifted area. 1-1 is already a concrete 16px discrepancy.
4. Implement real 16/32/48Ã—8 platform collision, sine trajectories, phase/timing, sprite rendering, enemy-slot behavior and camera-relative position. A helper must not consume a native enemy slot in a way that silently removes enemies/firebars. Test platform carry, top landing, side/underside contact, offscreen lifetime and pause behavior for both mappers.
5. Apply the confirmed 2.02-only changes deliberately:2-3/7-3 helper additions,3-3 landing,8-1 extra helper and corrected 8-1/8-2 gates,8-4c effective gate,4-4 two removed cells,1-1 Goomba removal. Do not call generic skin renames gameplay changes.
6. Review the complete native/Crossover static alignment inventory, including native shared-room effects, explicit unbreakable bricks in 5-2/6-2 and moved columns in 1-1/1-2/1-4/3-1/4-1/7-3. Resolve maze/transport graph equivalence before changing 4-4/7-4/8-4 or blindly copying expanded XML room lengths.
7. Run ordinary controller routes through every changed accommodation for all eligible and ineligible characters, plus water-mode and native map-sharing counterexamples. Test Easy/Hard independently and retain native screenshots/replays showing platform motion and landings. Include 1-1 flagpole,2-2/7-2 water gaps,2-3/7-3 bridge gap,3-3 low landing,4-3 mushroom climb,8-1 and 8-2 long gaps,8-4 final gap.
8. Recheck the complete 14-identity roster through 2-2 and all remaining-world obstacle/maze transitions; profile dense helper+enemy scenes on MMC3/MMC5. Preserve 30GB workspace cap by archiving captures outside the project.

## What this audit does not certify

This is an exhaustive authored-data inventory of both pinned XML datasets and the current 68 native level/enemy streams. It is not an authenticated exact 1.0-versus 2.0.0 archive comparison, a live Flash playthrough, or a completed runtime equivalence proof for every enemy/maze/transport. Native column decoding uses the actual compiled 6502 parser with authored hidden 1-up blocks enabled; those seeded static calls are map extraction and are never offered as controller clears. The diagrams are source-map schematics, not game screenshots. No level implementation has been silently bundled into this report.

## Revision 2 — enemy, hazard, platform, and interactive-class census

**This section supersedes the earlier claim that the eight XML rows alone form the complete mechanical version-difference list.** Constructor behavior also matters: the 16 unbreakable-looking brick cells are ordinary `Ground` in hosted 1.x, but `Brick` objects with a single-coin payload in 2.02. The earlier B→S table describes the hosted build; it is incomplete for 2.02. The exact original report, inventory and manifest are retained under `build/verification/level-layout-audit-agent/revision1/`, including their original hashes.

The supplementary inventory now includes every native enemy command, every source enemy/hazard/platform/control record, group expansion, per-world hard-only admission, and every mapped interactive cell. The intended source target record set is fully enumerated even where a native/Flash coordinate representation has no unique one-to-one pairing. No game edits were made.

### Original enemy parser and hard-only gating

- All 34 native enemy streams were decoded:502 commands including page/transport controls, with 407 actor/group records.
- 1,628 actual compiled baseline `ProcessEnemyData` calls cover all 407 actor/group records under all four primary/secondary-hard combinations. These are seeded static decoder checks with empty slots, not controller playthroughs. Page-select effects were set to the decoded command state; hard-only rejection, group class/count and 24px spacing were asserted against compiled execution.
- Native secondary-hard admission is off for 1-1 through 5-2 and on from 5-3 through 8-4; primary hard mode, after completing the game, enables secondary hard everywhere and converts Goombas/groups to Beetles. These are separate from our version-behavior toggle and the Flash five-position difficulty selector.
- Group commands 37..3a expand to two/three Goombas (Beetles under primary hard), and 3b..3e to two/three Green Koopas; bit 1 selects native Y=$70 rather than$b 0. The actual group origin is `ScreenRight` when processed. The earliest aligned static origin is commandX−48px; the next members are+24px each. These nominal group positions must not be misrepresented as exact attained coordinates under every camera speed.
- Vertical-pipe Piranhas come from level construction, not the enemy stream. The inventory includes them separately. World 1-1 disables them; empty enemy slots and later warp-zone cleanup can suppress/erase them. IntroPipe graphics are excluded because they do not call `VerticalPipe`.

### All-area actor/hazard/platform count inventory

These counts are authored records/instances, not simultaneously visible enemies. Native small lifts draw two platforms 128px apart from one actor; Crossover stores separate platform instances. Native frenzy commands are generators, not one enemy. Maze-expanded duplicates and source helper platforms therefore legitimately change the number of records.

| Area | Native authored candidates | Crossover explicit records | Native / source firebars | Native / source platforms | Source helpers |
|---|---:|---:|---:|---:|---:|
| 1-1a | 17 | 17 | 0 / 0 | 0 / 1 | 1 |
| 1-1b | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 1-2b | 29 | 25 | 0 / 0 | 4 / 4 | 0 |
| 1-2a | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 1-2c | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 1-2d | 1 | 2 | 0 / 0 | 0 / 1 | 1 |
| 1-3a | 12 | 13 | 0 / 0 | 4 / 5 | 1 |
| 1-4a | 11 | 10 | 7 / 7 | 1 / 1 | 0 |
| 2-1a | 33 | 33 | 0 / 0 | 0 / 1 | 1 |
| 2-1b | 1 | 1 | 0 / 0 | 1 / 1 | 0 |
| 2-1c | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 2-2a | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 2-2b | 7 | 26 | 0 / 0 | 0 / 2 | 2 |
| 2-2c | 1 | 2 | 0 / 0 | 0 / 1 | 1 |
| 2-3a | 1 | 4 | 0 / 0 | 0 / 2 | 2 |
| 2-4a | 14 | 15 | 6 / 6 | 3 / 5 | 0 |
| 3-1a | 33 | 34 | 0 / 0 | 0 / 1 | 1 |
| 3-1b | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 3-1c | 1 | 1 | 0 / 0 | 1 / 1 | 0 |
| 3-2a | 36 | 37 | 0 / 0 | 0 / 1 | 1 |
| 3-3a | 18 | 19 | 0 / 0 | 11 / 12 | 1 |
| 3-4a | 19 | 18 | 9 / 9 | 1 / 1 | 0 |
| 4-1a | 7 | 7 | 0 / 0 | 0 / 1 | 1 |
| 4-1b | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 4-2a | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 4-2b | 31 | 26 | 0 / 0 | 7 / 6 | 0 |
| 4-2e | 1 | 2 | 0 / 0 | 0 / 1 | 1 |
| 4-2c | 3 | 0 | 0 / 0 | 0 / 0 | 0 |
| 4-2d | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 4-3a | 17 | 18 | 0 / 0 | 11 / 12 | 1 |
| 4-4a | 10 | 14 | 5 / 9 | 0 / 0 | 0 |
| 5-1a | 35 | 36 | 0 / 0 | 0 / 1 | 1 |
| 5-1b | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 5-2a | 21 | 21 | 0 / 0 | 0 / 1 | 1 |
| 5-2b | 5 | 10 | 0 / 0 | 2 / 2 | 0 |
| 5-2c | 1 | 1 | 0 / 0 | 1 / 1 | 0 |
| 5-3a | 14 | 15 | 0 / 0 | 4 / 5 | 1 |
| 5-4a | 23 | 24 | 11 / 11 | 3 / 5 | 0 |
| 6-1a | 3 | 4 | 0 / 0 | 0 / 1 | 1 |
| 6-2a | 39 | 36 | 0 / 0 | 0 / 1 | 1 |
| 6-2b | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 6-2c | 5 | 10 | 0 / 0 | 2 / 2 | 0 |
| 6-2d | 1 | 1 | 0 / 0 | 1 / 1 | 0 |
| 6-2e | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 6-3a | 16 | 19 | 0 / 0 | 16 / 17 | 1 |
| 6-4a | 18 | 17 | 11 / 11 | 1 / 1 | 0 |
| 7-1a | 15 | 16 | 0 / 0 | 0 / 1 | 1 |
| 7-1b | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 7-2a | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 7-2b | 14 | 35 | 0 / 0 | 0 / 2 | 2 |
| 7-2c | 1 | 2 | 0 / 0 | 0 / 1 | 1 |
| 7-3a | 8 | 11 | 0 / 0 | 0 / 2 | 2 |
| 7-4a | 8 | 8 | 1 / 2 | 2 / 2 | 0 |
| 8-1a | 62 | 63 | 0 / 0 | 0 / 3 | 3 |
| 8-1b | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 8-2a | 23 | 26 | 0 / 0 | 0 / 2 | 2 |
| 8-2b | 0 | 0 | 0 / 0 | 0 / 0 | 0 |
| 8-3a | 14 | 15 | 0 / 0 | 0 / 1 | 1 |
| 8-4a | 23 | 30 | 0 / 0 | 1 / 1 | 0 |
| 8-4b | 9 | 8 | 5 / 5 | 0 / 0 | 0 |
| 8-4c | 7 | 6 | 0 / 0 | 0 / 1 | 1 |

### Confirmed additional authored differences and representation changes

- **1-1:** the hosted build retains the native second Goomba of the late pair;2.02 removes it at source tile(128,12), as already listed. Source raw positions include the documented column deletion.
- **2-2 and 7-2:** the native authored Blooper at original column 71,row 8 has no corresponding explicit Crossover Blooper. The full source Blooper list is retained; this conclusion is about authored data, not whether the native enemy survives slot admission in a particular run.
- **6-2:** native authored Goombas at original column 68,row 3 and one later grouped Goomba near column 170.5 have no corresponding explicit source Goomba. Raw group coordinates and nominal origin are preserved; do not translate the group position into a camera-independent claim.
- **2-3:** four free coins move down one tile: source columns 72,73,74,75 use rows 6,5,5,6, where native rows are 5,4,4,5. Other map geometry and helper changes are listed in revision 1.
- **4-2:** the native plain brick at column 128,row 2 is absent from the source map.
- **2-4 lifts:** source tile(86,6)/(86,12) contains `type=constantFall` before a duplicate `type=constantRise`; tile(89,6)/(89,12) has the reverse order. Both constructors select the first occurrence. Thus the effective source left/right lift directions are reversed from native Up/Down, and the two source instances in each column are 96px apart rather than the native small-lift drawing offset 128px. **5-4** uses ordinary Rise-left/Fall-right records with 128px-separated source instances. The raw duplicate properties are intentionally retained in the inventory.
- **Firebar speed:** native fast clockwise firebar ID 1c at CastleArea 3 column 103,row 11 is secondary-hard-only, so it appears in 5-4, not first-quest 2-4. Both pinned Flash engines use one 106°/s `ROTATE_SPEED` for ordinary left/right bars. Native 28/38 spin increments correspond to approximately 105.47°/s and 147.66°/s at 60Hz. The fast 5-4 variant therefore becomes the uniform source speed. Short/long direction and every explicit source bar location are listed separately.
- **Water fish:** native water fish are produced by frenzy controls, while the XML authors explicit fish positions. The supplementary list records all 48 explicit fish instances across the relevant water areas; these are a generator-versus-placement change, not 48 independently confirmed native missing enemies.
- **Lakitu, flying Cheeps, Bullet Bills and Bowser flames:** the source uses explicit start/end zone markers; native streams contain spawn/stop-frenzy commands, repeated Lakitu entries and area-frenzy level commands. Every marker/command is retained. Comparing the raw markerX to a native recordX is not a complete spawn-timing proof because native extended screen-right admission precedes that record.
- **Retainers and warp-zone control:** native Retainer/WarpZoneControl records are represented by source scenery/transport/state objects. The absence of a same-class source enemy record is not a removed Toad/Princess or a deleted warp zone.
- **Castle mazes:** all explicit source 4-4/7-4/8-4 firebars, plants, platforms and controls are enumerated, including duplicated geometry. Extra source records in expanded sections must be mapped to loop/transport behavior; they are not automatically additional simultaneous obstacles.

### Complete interactive/payload class census

Every mapped cell was checked for plain brick, powerup brick, vine brick, star brick, multi-coin brick,1-up brick, question-coin/powerup, hidden-coin/1-up, free coin, used block, axe, spring, flagpole, pipe, cannon/stem, bridge and ordinary solid classes. Source-only inserted/unmapped columns are retained separately, not dropped from the comparison.

**All 16 constructor changes:**

| Area | Source tile | Original NES | Hosted 1.x |2.02 |
|---|---|---|---|---|
| 1-2b | (164, 10) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 4-2b | (186, 10) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 5-2a | (147, 9) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 5-2a | (148, 9) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 5-2a | (149, 9) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 6-2a | (113, 9) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 6-2a | (115, 5) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 6-2a | (119, 5) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 6-2a | (120, 5) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 6-2a | (121, 5) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 6-2a | (122, 5) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 6-2a | (123, 5) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 6-2a | (124, 5) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 6-2a | (125, 5) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 6-2a | (126, 5) | Plain breakable brick | Ground / no payload | Brick / single coin |
| 6-2a | (127, 5) | Plain breakable brick | Ground / no payload | Brick / single coin |

Besides those 16 cells, the mapped census finds the four moved 2-3 coins (old/new cells), the absent 4-2 ceiling brick, the already documented 4-4 removal, the 12 conditional helper/stem source cells, and five underwater exit-pipe bottom cells represented by a native generic solid tile rather than a dedicated source pipe graphic/class. The underwater cells are 2-2b(189,8),5-2b(62,8),6-2c(62,8),7-2b(189,8),8-4b(69,8). Their portals are not inferred solely from tile appearance; transport commands remain in the separate graph inventory.

The remainder of powerup/star/vine/1-up/question/hidden/multi-coin classifications agrees in the mapped spans. This is a class/content census, not proof of equal lifecycle timing: both Flash Brick implementations use a 6000ms multi-coin timer and a 14-coin cap, and native hidden 1Ups have their own appearance gate. Actual item emergence, ammo inventories, pickup animation and collection behavior remain separate runtime tests.

### Complete location lists and anchor caveats

- `spawn-revision2/complete-enemy-object-list.csv`: every authored native/source enemy, hazard, platform and control, with original record bytes/offsets, native anchor, geometry-aligned anchor, exact source tile/anchor, class and hard admission.
- `spawn-revision2/all-enemy-object-comparisons.json`: the complete structured records, including group provenance and compiled initialization results.
- `spawn-revision2/complete-interactive-differences.csv` and `all-interactive-comparisons.json`: every interactive class difference, including cells in inserted/unmapped columns.
- `spawn-revision2/original-level-commands.json`: every original level command, including Piranha-producing pipes and frenzy/loop controls; `original-enemy-commands.json` retains all enemy/page/transport/group commands.
- `spawn-revision2/per-world-hard-gating.json`: each area’s native secondary-hard state and gated records.

**Candidate pairings are not silently promoted to proven moves.** Equal anchors are literal after the documented static alignment. Other rows retain their delta or remain unmatched. Moving-platform initial positions versus oscillation centers, flying-enemy launch phases, maze clones, deleted native columns, screen-right generators and source scene-graph objects can prevent a unique one-to-one association. The full source target list is still exact and available for implementation; no coordinate is invented to make a comparison pass. Runtime slot exhaustion, hidden 1Up admission, frenzy timing, scrolling thresholds and maze traversal still require native playthrough evidence.

### Proposed helper masks for our custom characters

These are **port recommendations**, not official 2.02 behavior, and no game changes were made. All three have installed dry horizontal speed 1.5px/update. Do not require a flower or an advanced technique to clear a basic mandatory gap. Use existing authored source helpers rather than inventing new platforms.

| Custom character | Proposed H | Proposed V | Installed capability motivating the proposal |
|---|---|---|---|
| Pit | yes | no | Base jump−4.1667px/update and rising gravity≈0.09723px/update²; flower-only flight cannot be assumed |
| Rygar | yes | no | Adapted higher jump−5.5px/update and gravity≈0.13889px/update²; modest horizontal speed, no intrinsic dash/second jump |
| Scrooge | yes | yes | Ordinary jump deliberately follows the native 58px rise; stronger repeatable pogo requires a separate Down+B action |

Pit/Rygar’s higher ordinary jumps support a Samus/Ryu-like vertical policy; Scrooge’s lower ordinary jump supports the Bill/Link/MegaMan-style V accommodations. These recommendations are derived from installed constants and mechanics, not verified full-world traversal bounds. Confirm at base power in both behavior modes and every affected gap before treating the masks as final.

Revision 2 remains audit-only. Its decoder checks and inventories strengthen the pre-change full list; they do not finish the overarching roster/weapon/recording goal.
