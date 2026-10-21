# Ordinary-enemy bounding-box CPU work

Status: accepted component checkpoint, with known roster defects. The frozen
full regression run passes all755 cases across both mappers, with identical
fixture hashes before/after. This does not certify final roster completion.

`build/checkpoints/roster-audit-v35` contains the byte-identical ROMs tested
under the original immutable name `roster-audit-v35-provisional-a`:

- MMC3 SHA256 `7f6919cf4c6aa1a7e78a7e39f03b5c5025010683d07669114584e39c8ca4ebb5`.
- MMC5 SHA256 `ec8c6edf30ace641064698438640a09cc1c8c06344e8b256d69f4056da276577`.

## Change and independent checks

The ordinary native enemy caller supplies slots0–5. When its computed
offscreen byte is zero, both possible native bounding-box masks produce zero.
The new16-byte OBJECT helper records that zero and uses the existing native
box construction. Every nonzero pattern retains the original helper. Other
bounding-box callers keep their previous targets. No persistent cache, SRAM,
physics simplification or reduced AI update rate is introduced.

The actual-ROM standalone CPU differential checks40,720 states per mapper:
A/X/Y/all status flags/SP and all native RAM except discarded stack contents.
It also checks the real caller's JSR operand. Zero-bit calls save35–42 cycles;
fallback calls cost10 extra cycles. This is a unit test with no interrupts/PPU.

The separate real-emulator authored arenas exercise5,292 actual caller entries
per mapper in both the native control and candidate. Returned registers,
flags, scratch, mask and all four box coordinates match byte-for-byte. The
real terrain/collision/Goomba movement caller continues after each arena.
These tests seed RAM and are explicitly not controller level clears.

Evidence:

- `tools/profiling/verify_enemy_bbox.py` and
  `build/verification/enemy-bbox-v34-v35a-{mmc3,mmc5}.json`.
- `tests/enemy-bbox-caller.lua`, its immutable native control receipt, and
  `build/verification/enemy-bbox-v34-v35a-caller-a/summary.json`.

## Matched crowd results and limits

The unchanged aligned arena covers six characters on both mappers, standing
and walking, outlines on/off, and0/1/2/4/6 Goombas. All14,400 completed updates
match across204 gameplay fields. Native movement/contact remains live.
Baseline v34b differs from final34 only in two Link geometry bytes; the
separate matched final34 Link probe already establishes identical results.

`build/profiling/plain-walking-v34b-v35a-bbox-comparison.json` preserves every
scene, canonical receipt, CPU, physical-frame, DMA and draw count. In walking
scenes with outlines off, foreground CPU excluding drawing falls153–173
cycles/update with four Goombas and233–235 with six. Frame delivery is
nonlinear and not uniformly better:

| Mapper / actor / Goombas | Physical frames per60 updates | Draws per60 updates |
| --- | ---: | ---: |
| MMC3 / Samus /4 |60 →60|30 →30|
| MMC5 / Samus /4 |60 →60|30 →30|
| MMC3 / Mega Man /4 |63 →61|30 →30|
| MMC5 / Mega Man /4 |61 →60|30 →30|
| MMC3 / Bill /4 |60 →59|30 →38|
| MMC3 / Link /4 |60 →60|49 →57|
| MMC3 / Simon /4 |60 →60|35 →43|
| MMC3 / Ryu /4 |60 →60|51 →48|
| MMC5 / Bill /4 |60 →60|51 →50|
| MMC5 / Ryu /4 |60 →60|52 →56|
| MMC5 / Link /6 |82 →70|30 →30|

The complete packet retains the other scenes and regressions. Samus/Mega Man
still have30-draw crowd cases, and six-Goomba scenes can still take90 physical
frames for60 logic updates. This is a small CPU improvement, not a zero-lag
claim. The hardware eight-sprites-per-scanline limit remains separate from
missed redraws; default-off extra black outlines reduce scanline pressure.
The bright gold menu option and default-off setting are inherited from the
already verified v34 build.

## Build and outstanding work

The original baseline remains byte-identical:
`0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146`.
The saved `source-v35.zip` (originally `source-v35a.zip`) rebuilds both ROMs byte-identically from
a fresh extraction with the compiler/Python/Pillow supplied separately.
Archive SHA256:
`0e08ba2561786c001ce5191cb4b068010d3587ee4b7bed1c885ac5b6ad4b664d`.
Evidence: `build/checkpoint-tests/source-v35a-rebuild-smoke/report.json`.

The complete frozen suite and original checkpoint identity are retained in
`build/verification/summary-roster-audit-v35.json` and
`build/verification/roster-audit-v35-full.log`. No fixtures changed during
this755-case run. The subsequent QA/README update does not change runtime
inputs; the source archive retains its recorded README bytes.

v34's documented Simon/Ryu pose-dependent geometry and Simon hurt-ceiling
limitations remain. An ordinary final34 Ryu stair replay has additionally
proved that stale wall attachment cancels a fresh ground jump; a scoped repair
and independent control are being prepared for the next source batch. These
are pre-existing source defects, not claimed as fixed by this CPU change.
All current-hash character routes, attacks/upgrades and final recordings still
require completion. Mario's final34 video and Luigi's final34 strict clear are
retained as34 evidence and are not relabeled with the candidate ROM hashes.
