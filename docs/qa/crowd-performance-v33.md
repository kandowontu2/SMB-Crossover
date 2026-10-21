# Ordinary-enemy CPU shortcut, v33

Accepted component checkpoint: `build/checkpoints/roster-audit-v33`.

- MMC3 SHA256: `3511b1a325800a5dc2992d0ad4367b3a162dc81b71e686be7ba959884a571321`.
- MMC5 SHA256: `a2332ba0d73c3073bb5a9dc9c702000ffaf9cf33acaa5d69ea625cab9e2bba7b`.

The new OBJECT-bank helper replaces the ordinary enemy's visibility calculation
only when both actual camera edges and vertical bounds prove the native result
is zero. Every rejected case uses the unchanged native routine. The helper
preserves caller-visible registers, flags, stack pointer and scratch values;
it adds no persistent cache, SRAM, FIXED-bank space or CHR. Enemy AI, movement
and collisions still run normally.

## Direct differential evidence

`build/verification/offscreen-v33-unit-evidence.json` binds the ROMs and tests.
The standalone interpreters compare actual linked 6502 code across 98,408
cases per mapper. The accepted interior path costs 134 cycles, saving 165–201
cycles per call on MMC3. Rejected calls add 8–86 cycles, so a crowd measurement
is also required before accepting the optimization.

Actual emulator caller tests cover 3,672 arenas on each mapper, with the same
frozen test run on both immutable v32 and v33. The 7,344 before/after CSV rows
are byte-identical, including boundary geometry, all native enemy slots,
unusual ObjectOffset values, registers/flags/SP and scratch. Native enemy AI
continues after each explicit unit setup. These are isolated arenas rather
than ordinary-controller route proof.

## Benchmark setup correction

The original crowd probe initialized the next arena at endFrame and inherited
inactive bounding boxes. Faster execution changed the setup/input-latch phase;
the negative comparison is preserved at
`build/profiling/plain-walking-v32-v33-original-phase-comparison.json`.
It is excluded from gameplay-parity acceptance.

The corrected probe seeds arenas at the foreground NoDecTimers boundary after
two real stable controller receipts, clears inactive boxes and records actual
$4014 DMA writes. Both ROMs use exactly the same probe, SHA256
`069d75fe11b71699c8dad071de419f9cce7cd2d7e51ff425456f98824b657ccf`.
It retains all 204 gameplay fields and 60 completed updates per scene.

The completed corrected matrix matches all 14,400 paired update rows across
204 gameplay fields: six characters, two mappers, 20 scenes per run. Standing
and walking scenes use zero/one/two/four/six live Goombas and both outline
settings. The source is unchanged throughout both complete matrix runs.
Evidence: `build/profiling/plain-walking-v32-v33-aligned-comparison.json`.

Selected walking results with outlines OFF, per 60 completed logic updates:

| Mapper / character | Goombas | Physical frames before → after | Redraws before → after |
| --- | ---: | ---: | ---: |
| MMC3 / Link | 4 | 60 → 60 | 30 → 49 |
| MMC3 / Ryu | 4 | 60 → 60 | 30 → 42 |
| MMC5 / Bill | 4 | 60 → 60 | 30 → 49 |
| MMC5 / Link | 4 | 60 → 60 | 46 → 60 |
| MMC5 / Simon | 4 | 60 → 61 | 30 → 56 |
| MMC5 / Mega Man | 4 | 65 → 61 | 30 → 30 |
| MMC5 / Samus | 4 | 60 → 60 | 30 → 30 |
| MMC5 / Ryu | 6 | 90 → 70 | 30 → 30 |

Four-enemy scenes save approximately 757–805 non-draw foreground cycles per
update; six-enemy scenes save about 1,058–1,066. Redrawing more often can spend
those savings on rendering. Simon's four-enemy scene takes one extra physical
frame on each mapper while drawing more frequently; this tradeoff is retained
in the evidence. Samus and Mega Man's six-enemy scenes still need 90 physical
frames and only 30 redraws. Actual DMA counts are recorded separately because
a DMA can repeat an earlier image. These results do not establish universal
60Hz game logic or rendering.

## Native baseline and outstanding work

A cached baseline binary predated the v32 source. Rebuilding it changed its
binary hash. Reconstructing the exact v32 source without the v33 additions
produces a baseline byte-identical to the fresh v33-source baseline. The legacy
and fresh baselines and custom v33 also produce the same 521-frame/19-field
Mario trace. `baseline-source-control.json` in the checkpoint retains the
qualification and exact hashes.

The full v33 regression run passes all 731 cases on both mappers in one run,
with unchanged fixtures and tools. The original summary and launch report are
`build/verification/summary-roster-audit-v33.json` and
`build/verification/roster-audit-v33-full.json`. The checkpoint also preserves
a verified source archive. Its runtime sources match the build manifest;
the subsequent caller-test registration and benchmark comparison updates are
recorded separately as validation-tool changes.

Default OFF outlines, the bright-gold
option row and the pixel-preserving Bass/Bill sprite layouts are inherited
from v32; their evidence is in `crowd-performance-v32.md`.

Dense crowds can still exceed CPU time and the NES eight-sprites-per-scanline
limit. Full current-ROM routes through 2-2, final recordings and source injury
migrations remain separate outstanding work. No hardware or complete-source
parity claim is made.
