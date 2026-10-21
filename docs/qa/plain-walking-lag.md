# Plain walking crowd audit

This is an explicit isolated flat-floor arena, not a level-completion replay.
Ordinary neutral/Right controller input drives the player. Each immutable ROM
runs20 scenes: outlines ON/OFF, standing/walking and0/1/2/4/6 real Goombas. After8
warm-up updates, each scene measures60 completed native updates. There are no
attacks, injury, invulnerability, PC/register/ROM patches or omitted native AI
calls. Setup writes only authored RAM fixtures. The player and crowd remain
separate, and each completed update asserts the actual live population.

## Baseline and matched observation

Immutable29: `build/profiling/plain-walking-v29-canonical-a/manifest.json`.
All12 mapper/character runs pass: MM1, Samus2, Bill3, Link4, Simon5 and Ryu10 on
MMC3/MMC5. This yields14,400 completed-update receipts, each with204 player,
AI, collision, freeze, projectile and movement fields. All20 scenes per run
complete and retain the requested population. The Lua source is copied once
and each run executes that frozen copy. Its SHA256 is
`1bf4f10ebfcfc99bb65e5eb3dca94cba0387d0eec1eb42410832be40ed29a992`.

`plain_walking.lua` guards actual foreground opcodes/banks and NMI/IRQ depth.
It counts real hardware frames, skipped NMI receipts, actual draw calls and
native CPU OAM ownership propagated through4014 DMA. Visibility uses actual
hardware sprite RAM, mapped CHR row transparency and the NES8-sprite scanline
limit. Whole-enemy invisible frames and overloaded rows distinguish PPU sprite
contention from skipped sprite draws. Drawn enemy frames mean sprites present
in completed hardware OAM; a repeated stale frame is still present. Draw-call
counts, rather than that population metric, measure render cadence.

Cycle receipts cover NoDecTimers through the final NmiDisable store. Elapsed
loop clocks and hardware counts are exact for those boundaries. The foreground
metric subtracts interrupt instruction bodies;13 entry/RTI cycles per outer
interrupt remain conservatively charged to it. This small limit is unchanged
between the matched ROMs; it is not a cycle-perfect pure foreground measure.

The earlier28 smoke and29 compare-a probes are archived. The28 smoke omitted
clearing unused metasprites, so its low-count cost is not a direct code-change
comparison. Compare-a Ryu's final six-enemy walk accidentally reached a Goomba
after warm-up; the corrected frozen fixture starts Ryu atX0 and all12 runs
pass with no injury. Those failures are fixture errors, not production fixes.

## Measured native work and scoped30 batch

With6 Goombas, Link29/MMC5 spends about14,298 foreground cycles/update in native
actor processing. Nested costs include3,416 background collision,1,950
offscreen bits,1,451 bounding boxes,1,591 native movement,1,341 enemy-pair
collision and1,080 player-body collision. These nested totals must not be
added to their inclusive parent. The old ice/stopwatch admission wrapper costs
about752 cycles for6 actors, including270 in its simple resident-field helper.

The frozen30 source batch keeps every native actor update/contact and all
weapon timers. It removes the mapper round-trip from freeze admission, with
a zero-request direct native path; preserves the old eligibility helper for
nonzero stopwatch/16-bit ice; skips candidate preparation only with empty
pools and no possible attack input; and returns early from MM/Bass-only special
weapon updates for other characters. Each active batch still obtains a fresh
cache after preceding batches may mutate actors. No persistent cache receipt,
physics/AI tick reduction, or new SRAM was introduced. Root30 also contains
its separately measured generated zero-mask outline bypass.

Scoped runtime files: object.s, remaining_weapons.s, samus_weapons.s,
roster_weapons.s, expanded_weapons.s and special_weapons.s. Existing
SpecialClear/RosterClearState/InventoryClearActive lifecycle clears remain.

Before30, `native-freeze-admission.lua` passes4,224 actual-caller cases per
mapper on29: all6 slots, corpse/death states, low/high ice bytes, stopwatch,
ordinary/special eligibility, preserved caller TimerControl and actual native
Goomba movement. Unsupported test IDs are restored to a valid actor only after
the admission decision, before dispatch. This is explicitly a helper/caller
arena. All6 empty-candidate29 controls fail as expected with2 unnecessary
candidate scans per completed update. Evidence:
`build/verification/link-simon-v29-focused-native-freeze-control-a/`.

All12 matched29/30 canonical runs pass. The14,400 completed-update rows,
each with204 gameplay fields, match byte-for-byte, with0 differences.
`build/profiling/plain-walking-v29-v30-comparison.json` binds the per-run
source/CSV hashes and all240 scene comparisons. This covers all six characters,
both mappers, standing/walking, both outline states and every crowd count.

The source controls are consolidated in
`build/verification/scoped-pipeline-v30-evidence.json`. Native freeze admission
passes4,224 cases per mapper before and after; active weapon/source effect
controls pass after the documented fixture corrections. A subsequently
demonstrated real Sophia late-raw-input bug remains explicitly excluded from
30 acceptance: an empty-cache decision could precede a fresh rawB receipt,
creating a cannon with stale tier0.31 moves fresh preparation after actual
shot creation and queries the acquired cannon tier at creation. The identical
late-input negative on30 and positive on31 are preserved separately.

31 also gates the Link/Simon/Ryu source-effect bank calls only when all18
STOP/FLASH/frozen-pose bytes are zero. The post gate follows Link's deferred
thrust, so a newly created effect is still ticked in the same source update.
All662 cleanup/deferred arenas and30 gameplay fields match byte-for-byte
against30. The48 scoped31 test slots pass;16 source-effect controls were rerun
from one frozen corrected completion observer. The earlier observer used the
now-intentionally-skipped zero-effect routine as its completion anchor; its
negative logs remain archived. Acceptance and exclusions are bound in
`build/verification/scoped-pipeline-v31-evidence.json`.

Logic and rendering must be reported separately. With6 Goombas, the matched
MMC5 Link/Simon/Ryu walks still require90 hardware frames for60 updates despite
saving about1,478/1,478/1,624 conservative foreground cycles per update. Samus
with4 Goombas improves from60 updates in90 hardware frames to60 in60, while
DrawAllMetasprites still runs only30 times in those60 updates. That is a logic
improvement with continued skipped renders. Dense6-actor scenes still drop
updates and renders; the measurements do not establish that walking lag or
flicker is solved.

The light DMA supplement uses a separately frozen probe source and counts
actual4014 writes, actual DrawAllMetasprites entries and skipped render calls.
It excludes the heavy gameplay/PPU observation callbacks and subtracts the
outer interrupt's full entry/RTI cycles. Its pure foreground metric is therefore
kept separate from the older full canonical probe. Both immutable29 and30
use exactly the same light source. The final physical counter packet and
latest32 matched-canonical/profile supplement are recorded below.

The29/30 DMA supplement is now complete:12 runs per ROM,240 matched scenes.
The source SHA is `c18c6e7080a94819e59f2ac2abb8f1f5896c2e32a92d1830c6099f4ec1b99894`.
Its exact per-scene packet is
`build/profiling/plain-walking-v29-v30-dma-comparison.json`. For four-Goomba
walking with outlines OFF, the counters below are
`hardware frames / actual DMA writes / draw calls / skipped renders` per60
completed gameplay updates. A DMA can repeat stale OAM and is not a new draw.

| Character | Mapper |29 |30 |
|---|---|---|---|
| Mega Man |MMC3 |82 /52 /30 /30 |64 /34 /30 /30 |
| Mega Man |MMC5 |70 /40 /30 /30 |62 /32 /30 /30 |
| Samus |Both |90 /60 /30 /30 |60 /30 /30 /30 |
| Bill |MMC3 |63 /33 /30 /30 |60 /30 /30 /30 |
| Bill |MMC5 |60 /30 /30 /30 |60 /31 /31 /29 |
| Link |Both |60 /30 /30 /30 |60 /30 /30 /30 |
| Simon |MMC3 |61 /31 /30 /30 |60 /30 /30 /30 |
| Simon |MMC5 |60 /30 /30 /30 |60 /30 /30 /30 |
| Ryu |MMC3 |60 /30 /30 /30 |60 /30 /30 /30 |
| Ryu |MMC5 |60 /30 /30 /30 |60 /32 /32 /28 |

Every six-Goomba walking case remains90 /60 /30 /30 on both ROMs and mappers:
40Hz logic,20Hz newly drawn sprites and some stale OAM transfers. This is a
measured remaining limit, not a claim that dense walking performance is fixed.

## Latest32 canonical and rendering comparison

All12 latest32 runs pass the exact same frozen full probe used for29/30.
Against30, all14,400 completed updates and204 observed gameplay fields remain
byte-identical, with0 differences. The complete240-scene packet is
`build/profiling/plain-walking-v30-v32-comparison.json`.
31 and32 have identical runtime addresses/CHR;32 changes only two menu palette
bytes. Root separately validates that binary difference. Thus32 also exercises
31's effect-gate CPU optimization and ordinary Bill body-layout change.

For four-Goomba walking with outlines OFF, MMC5 Link draw calls improve30→47
per60 updates and Ryu32→50. MMC3 Ryu improves30→31. Simon still draws30 times
on both mappers. Every6-Goomba scene still needs90 hardware frames per60
updates and draws30 times. These results describe the measured scene and phase,
not a universal frame-rate guarantee.

The packet also subtracts measured DrawAllMetasprites cost from the total
foreground metric. This prevents17 additional Link draws from appearing to
be a CPU regression. For Link/Simon/Ryu in the four-Goomba/OFF walk, non-draw
foreground cost falls approximately484/481/486 cycles per update on MMC3 and
421/439/430 on MMC5. Full-probe interrupt-overhead attribution remains the
same conservative convention as29/30. Mega Man and Samus timing/logic match
30 in this comparison. Bill's new body-selection path adds roughly68..73
non-draw cycles; its independently verified reduction in hardware sprite
parts belongs to the separate body-layout acceptance, not an AI speedup.

The latest32 matched light DMA supplement now passes all12 runs and240 scenes
against the same frozen light source as29/30. Packet:
`build/profiling/plain-walking-v30-v32-dma-comparison.json`.
The independent full/light observers agree exactly on physical frames and
draw calls in all240 latest32 scenes:
`build/profiling/plain-walking-v32-observer-crosscheck.json`.
No DMA count is inferred from skipped NMIs or draw calls.

Actual32 DMA confirms the MMC5 four-Goomba/OFF Link improvement30→47 and
Ryu32→50 transfers per60 hardware frames, matching newly completed draw calls.
MMC3 Ryu improves30→31 transfers; other selected four-Goomba counters remain
as30. Every six-Goomba walk still reports90 frames /60 DMA writes /30 new
draws /30 skipped renders per60 updates. The consolidated profile packet is
`build/verification/walking-profile-v32-evidence.json`. Source and tests are
frozen; the potential offscreen fast path remains a read-only proposal.
