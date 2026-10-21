# Ordinary-enemy offscreen shortcut

The scoped33 candidate adds `NormalEnemyOffscreenBits` in OBJECT and changes
only the ordinary-enemy call to use it. Baseline builds retain the original
call and do not include the helper. There is no FIXED or persistent RAM growth.
Every rejected case tail-jumps the unchanged resident helper.

The accepted interior predicate and exact ABI are documented in
`docs/qa/enemy-offscreen-cost-analysis.md`. The native algorithm remains the
independent reference; no physics, collision, AI cadence or sprite priority
is changed to reduce work. Original32 ROMs and their acceptance remain frozen.

`tests/offscreen-helper-caller.lua` seeds explicit RAM-only unit arenas at the
actual ordinary-enemy helper boundary. It independently evaluates the native
horizontal/vertical source equations, including conditional R5/R6 stores and
overflow flags. It checks A/X/Y/all status flags/R0..7/SP at the real return,
then restores coherent actor/viewport RAM and lets actual native Goomba AI
continue once. It tests all six slots, rejected edge/page/Y cases and unusual
ObjectOffset values through255 without changing CPU registers/PC/ROM or using
save states. These are ability/ABI fixtures, not level-clear evidence.

Both original32 mappers pass all3,672 real-caller arenas. Evidence:
`build/verification/link-simon-v32-focused-offscreen-caller-baseline-b/summary.json`.
Initial draft assumed descending actor iteration; native order is ascending.
The baseline-a diagnostic is preserved as a fixture error. The final fixture
hash is `cf7976309a5af24b4dff340d719a758788b32b2fed914040acb22160cbf93ccd`.

`tools/profiling/verify_enemy_offscreen.py` independently executes the actual
before/after ROM bytes in a standalone6502 interpreter with RP2A03 binary
ADC/SBC semantics even when D is set. It compares A/X/Y/allP/SP and all native
RAM except discarded stack contents, including every scratch byte. The matrix
includes horizontal/page/wrap boundaries, every Y low byte, hostile Y-high
values, every initial status byte, unusual ObjectOffset, stack wrap, foreign
input slots and fixed-seed arbitrary geometries. It also checks the actual
ordinary-enemy JSR operand on each ROM. This is a numerical unit differential,
separate from real-emulator caller and gameplay/counter observations.

Candidate33 passes all3,672 actual-caller arenas on both mappers with the same
fixture hash. Evidence:
`build/verification/link-simon-v33-focused-offscreen-caller-first-a/summary.json`.
Both standalone actual-ROM differentials pass98,408 cases per mapper,
including14,016 accepted interiors and84,392 rejected cases. They compare
all native RAM except discarded stack contents in addition to the full CPU
ABI. Artifacts: `build/profiling/enemy-offscreen-v32-v33-mmc3-differential.json`
and its `mmc5` counterpart. Accepted interiors take134 cycles, saving165..201
on MMC3; rejected native fallbacks add8..86 guard cycles. Candidate code is98
OBJECT bytes, with no persistent RAM/FIXED growth.

The actual-emulator before/after functional CSVs also match byte-for-byte:
all7,344 rows across both mappers, including geometry, registers, flags, SP
and every scratch value. Bound unit acceptance is
`build/verification/offscreen-v33-unit-evidence.json`.

The first old profiling source exposed an arena boundary defect: endFrame
initialization could shift the first walking input after faster preceding
crowd work, and inactive bounding boxes retained prior-scene values. The
original full result is preserved in
`build/profiling/plain-walking-v32-v33-original-phase-comparison.json` and is
excluded from gameplay-parity acceptance. No runtime fix was made for it.

The corrected profiling-only source waits for stable actual controller
receipts and seeds only at foreground NoDecTimers before the next native
loop. It initializes inactive boxes and retains all204 gameplay fields and
60 measured updates. It directly counts actual4014 DMA in the full probe.
Its SHA is `069d75fe11b71699c8dad071de419f9cce7cd2d7e51ff425456f98824b657ccf`.
The paired Link/MMC5 smoke passes all1,200 canonical rows exactly; four-Goomba
draw/DMA improves46→60 per60 frames, while six-Goomba physics improves90→78
frames per60 updates with30 new draws. These are scoped preliminary scene
results. The complete aligned matrix now passes all12 runs per ROM: all14,400
completed-update rows and204 gameplay fields are byte-identical, with0
differences. Each of480 combined scene audits also verifies exactly60 native
actor-core/body calls per live enemy:37,440 actual actor updates per ROM.
Every scene records actual4014 writes and actual draw entries independently.
No AI update or collision work was omitted to make the code faster.

Final comparison:
`build/profiling/plain-walking-v32-v33-aligned-comparison.json`.
Consolidated unit/crowd packet:
`build/verification/offscreen-v33-crowd-evidence.json`.

For walking with outlines OFF, the following are measured counts per60
completed gameplay updates. Draw calls are newly produced OAM; physical DMA
can additionally repeat old OAM. Full per-scene actual DMA counts are in the
comparison packet.

| Character | Mapper |4 Goombas: frames32→33 |4 Goombas: draws32→33 |6 Goombas: frames32→33 |
|---|---|---|---|---|
| Mega Man |MMC3 |65→63 |30→30 |90→90 |
| Mega Man |MMC5 |65→61 |30→30 |90→90 |
| Samus |MMC3 |61→60 |30→30 |90→90 |
| Samus |MMC5 |60→60 |30→30 |90→90 |
| Bill |MMC3 |60→60 |30→30 |90→90 |
| Bill |MMC5 |60→60 |30→49 |90→89 |
| Link |MMC3 |60→60 |30→49 |90→90 |
| Link |MMC5 |60→60 |46→60 |90→78 |
| Simon |MMC3 |60→61 |30→33 |90→90 |
| Simon |MMC5 |60→61 |30→56 |90→89 |
| Ryu |MMC3 |60→60 |30→42 |90→85 |
| Ryu |MMC5 |60→60 |49→52 |90→70 |

All selected six-Goomba walks still draw30 times per60 logical updates, even
where fewer physical frames improve their real-time draw cadence. The Simon
four-Goomba phase takes one extra hardware frame while producing more draws;
this tradeoff is retained rather than reported as a universal60Hz improvement.
Non-draw foreground cost falls roughly768..805 cycles per four-Goomba update
and1,059..1,065 per six-Goomba update across the selected walking/OFF scenes.
New successful draws are accounted separately from that CPU saving. The
aligned full probe removes full outer interrupt entry/RTI cost; its cycle
metric is kept separate from older full-probe13-cycle attribution.

Source, tests and tools are frozen during the parent full33 suite. Injury
migration and current full-roster routes/recordings remain held/outstanding.
Dense-crowd lag and the NES eight-sprites-per-scanline limit remain material
limitations. This accepts the scoped helper/unit/crowd behavior, not a
source-perfect whole-game implementation or physical cartridge result.
