# Core, empty weapon and audio-budget follow-up

Accepted component checkpoint with known roster defects. Its759 component
slots are covered by the frozen758-pass/one-failure run plus two corrected
observer invocations on the same ROMs. This is not one entirely green frozen
run or a completed roster certification.

`build/checkpoints/roster-audit-v37` copies37-provisional-c byte-identically:

- MMC3 SHA256 `44290b93abf3344b60b071dadcd5db37a93f5537ca816eba8a1c554fb6415078`.
- MMC5 SHA256 `cd096f7ddb181e929013586f116df676b88c7163b06c8b69e1c3b79c7325d3c6`.

## Changes and independent checks

The primary player's top-score comparison now walks the digits once and copies
only a larger score. The secondary-player helper stays unchanged. The actual
linked function passes2,034 initialized CPU cases per mapper against an
independent three-score maximum, including arbitrary byte values. All registers,
flags and RAM except discarded stack agree with36.

The metasprite loop retains its header across validation instead of stacking and
reloading it. Its1,640 CPU cases per mapper cover all256 headers, signed positions,
OAM exhaustion and rotation; all public registers/flags/RAM agree. Existing
header128 behavior is deliberately retained by this performance-only change.

Samus and the remaining draw caller publish CHR locally instead of entering
another bank for the same logic.672 whole-caller units per mapper cover idle
world/HUD/death states and publication/rotation edges. The initial416
RemainingDraw cases used the wrong entry bank and are explicitly excluded;
the corrected reports derive bank61 from the linked debug segment. Samus's
entry is bank10. The incorrect-bank diagnostic remains on disk.

Empty Samus pools skip redundant draw/weapon slot loops, preserving exhausted
scratch values. Freeze, stopwatch and Screw Attack state/audio still advance.
Any fresh Select or nonzero pool type takes the original active path.2,352
whole RemainingWeapons CPU cases per mapper cover live timers, all characters,
unsupported pool types and state/input/power variations.1,872 whole outer
weapon-caller cases check the supported-character bank admission. Active
weapons, real contacts and interrupts use the separate emulator checks.

Evidence: `build/verification/core-render-v36-v37c-*.json`,
`idle-draw-v37a-v37b-*-corrected-bank.json`, `idle-draw-v37b-v37c-*.json`,
`remaining-empty-v37b-v37c-*.json`, `weapon-admission-v37b-v37c-*.json`.

## Preserved negative and fixture correction

The frozen run fails MMC3 `link-beam-impact` at age0, with758 passing slots
and byte-identical fixtures before/after. A passive reproduction shows its
LinkBeamFragments address also runs in bank0, and its render address runs in
bank8. The observer incorrectly treats those unrelated foreground instructions
as a fragment start/render. The failed callback is not actual fragment code.

An outside control restricts both observers to physical bank4 and foreground
context. Both36 and37c on both mappers pass every original fragment quadrant,
diagonal position,84-piece/21-update lifetime, expiration and impact assertion.
Only after the frozen run closed, the fixture gained actual mapper-write and
interrupt-depth qualification. Both mapper slots pass again on unchanged37c
ROMs. No damage, geometry or lifetime oracle was removed.

- Original: `build/verification/summary-roster-audit-v37-provisional-c.json`.
- Passive negative: `build/verification/link-beam-v37-passive-a`.
- Outside controls: `build/verification/link-beam-v37-qualified-b`.
- Migration/original fixture/log/hashes: `build/verification/link-beam-v37-fixture-migration`.
- Consolidated: `build/verification/summary-roster-audit-v37-consolidated.json`.

## All240 matched crowd scenes

All14,400 completed updates match36d across204 observed gameplay fields.
Both mapper sets, six characters, standing/walking, outlines on/off, and
0/1/2/4/6 Goombas are retained in
`build/profiling/plain-walking-v36d-v37c-comparison.json`.

With outlines off, six-Goomba walking uses the following physical frames
per60 logic updates. Every listed scene still has30 draws:

| Character | MMC3 | MMC5 |
| --- | ---: | ---: |
| Mega Man |90 →90|90 →90|
| Samus |90 →90|90 →90|
| Bill |88 →77|77 →72|
| Link |71 →63|62 →61|
| Simon |85 →77|76 →71|
| Ryu |72 →68|65 →63|

Four-Goomba Samus walking remains60 physical frames/30 draws. Mean foreground
cost falls533 cycles on MMC3 and514 on MMC5, without crossing the redraw
threshold. Thirteen scene foreground averages increase, partly because more
drawing costs CPU. Three scenes draw less often: MMC3 Ryu outlines-on four
Goombas58 →55, outlines-off53 →51, and MMC5 Bill outlines-on57 →51.
No compared scene uses more physical frames. These are measurements, not a
uniform frame-rate or zero-lag claim.

## Remaining NMI budget

The unchanged Samus observer also measures the preceding NMI. Every one of
its30 four-Goomba drawn updates misses the physical-frame deadline on both
mappers. MMC5's full GameLoop elapsed maximum is29,664 cycles, but that alone
omits the preceding regular NMI, averaging7,717 cycles. Comparing GameLoop alone
to29,781 therefore cannot establish that the frame fits. The37 report qualifies
the earlier36 outer-only interpretation.

MMC5's AudioUpdate averages6,307 cycles excluding its nested IRQ, with Samus's
native update using4,771 of those and the extra-channel flush376. Routine costs
overlap their parents and cannot be summed. Diagnostic-a wrongly gated banked
audio by foreground CurrentBank; diagnostic-b tracks hardware PRG writes and
retains identical canonical gameplay. See
`build/profiling/samus-nmi-followup-v37/report.json`.

The400-file source archive plus generated index rebuilds both ROMs identically
from a fresh extraction, with separately supplied compiler/Python/Pillow:
`build/checkpoint-tests/source-v37c-rebuild-smoke/report.json`.
The vanilla baseline hash remains unchanged.

Default-off outlines and the gold option row remain. Samus has no ordinary
stomp in the pinned2.02 source; Screw Attack handles eligible spin contacts.
Normal Simon/Ryu geometry, firebar initialization lifecycle, final-hash roster
routes, every upgrade/attack and final recordings remain unfinished. Hardware
still permits only eight sprites per scanline. No physical-cartridge claim.
