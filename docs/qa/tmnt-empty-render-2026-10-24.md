# TMNT drawing optimization: private NZ

Candidate `10853b91f87379aa53ab52f69479c1f97f9cf434313f48404c0946eb7710b85c`
is based on NY `45a2cad0cdb60e2d5ea79b108c8b4dff226e05f037839b9a1d97deeebd0ed2ba`.
All CHR, physics, collision, animation, inventory and audio data remain unchanged.

The single game-source change is `tmnt_equipment_draw.s`. It performs the same
ordered five CHR-publication stores locally instead of taking a banked call.
When selection, all three projectiles, all four drops and all six private pickup
stamps are empty, it skips actor scans and retains the original ammo HUD path.
The final scratch slot, registers, flags, OAM and meaningful application memory
match the old renderer in 960 assembled-code cases, including capacity edges,
rotation, four turtles, equipment, shots, drops and physical scrolls.

The CORE size change moves two existing owned targets. Only three immediate
operand bytes change outside TMNT banks 87/89: palette target low/high in bank78
and graphics target low in bank93. The staging tool verifies those exact symbol
relocations. No resident segment grows and no extra RAM or sprites are added.

## Matched native measurements

Evidence:
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-performance-nz`.
`performance-baseline-v5` and `performance-candidate-v5` use the same fixture,
profiler and ordinary controller inputs after actual menus. Each representative
turtle (Leonardo Easy, Donatello Hard) executes exactly 600 native game updates,
120 each in idle/walk/live-enemy/primary/triple-shot components. Inventory and
target arrangements are explicit. All 120 enemy-phase samples retain live
native actors. Their complete per-update gameplay CSVs are byte-identical.

| Component | Whole drawing CPU saved |
| --- | ---: |
| Idle | 6.04% |
| Walking | 5.98% |
| Two live Goombas | 5.85–5.86% |
| Primary attacks | 5.41–5.50% |
| Triple shots | 0.41% |

The empty equipment routine drops from 484 to 178 cycles; with two live
Goombas, from 534 to 178. Active equipment examples save 32–34 cycles.
Primary-phase lag NMIs decrease from 1/2 to zero in these 120-update samples.
Idle/walk/enemy phases already had zero lag. Triple-shot stress retains 52 lag
NMIs per 120 game updates and only 68 constructed draws in both versions.
This is useful headroom, not completion of heavy-shot lag or a 60 Hz claim.
Routine spans exclude interrupt entry/body/exit and nest; they are not summed.

Retained fixture failures establish the accepted setup: an unexported constant
needed its source-owned alias; Goombas require logical Y184 (sprite Y192) to
stand at floor208; and immediate catch-up loops require stopping at the final
GameLoop return rather than waiting for endFrame. The live-actor assertion was
retained. Initial hotspot profiling timed out at frame3212 of the unchanged
8000-frame bound; a 120-second host rerun completed the original 4756-frame
replay with exact input/trace bytes. It is diagnostic, not the accepted delta.

## Exact-candidate regressions

All four turtles pass cold Easy/Hard1-1 discoveries and independent input
replays with zero deaths, into movable underground1-2. Input and telemetry
bytes match per replay:

| Turtle | Easy frames | Hard frames |
| --- | ---: | ---: |
| Leonardo | 4,748 | 4,716 |
| Raphael | 5,210 | 5,251 |
| Michelangelo | 4,646 | 4,896 |
| Donatello | 4,796 | 4,894 |

37,557 lossless route PNGs are retained. All 26,237 measured body CHR frames
match, and 101,840 recorded visible scroll writes retain the native bank126
scanline31 split. Root inspected all eight 24-frame overviews; visual review
is sampled, supplemented by automated CHR/scroll checks.

All 32 native equipment/primary/boss/ammo components pass, along with 13,708
source/linked CPU cases, 456 non-TMNT shared-hook cases and all37cold entries.
Actual equipment DMA/source checks pass across 30,358 parts and 8,948 draws.
Both ordinary mapper outputs remain byte-identical to their existing builds.
The saved source ZIP must rebuild the private candidate exactly.

World sprite overload, source palette adaptation/audio, heavy projectile lag,
other roster/castle/terrain work, natural delivery of every reward, the final
every-character/every-item matrix and the full37-identity MMC3 port remain
open. Public ROMs are preserved. This local optimization does not complete the
active user goal.
