# Pose caching, caller admission and Ryu launch correction

Status: accepted component checkpoint with known roster defects. All759
component slots are covered by an initial frozen run and four corrected
fixture invocations. This is not one entirely green frozen run, a final
roster certification, or a source-perfect port.

`build/checkpoints/roster-audit-v36` contains byte-identical copies of the ROMs
tested as `roster-audit-v36-provisional-d`:

- MMC3 SHA256 `e4c878ce7e26b2f355530ed391b33d9faf610e6dcf75b0f456dd15a60b7a2825`.
- MMC5 SHA256 `eaf266ac5247945433586f39cf6e1578b7053f8493ddf6c357ee15f59af2f7c0`.

## Runtime changes

Four small, immutable outline-filter results share the existing129-byte
buffer. Cache keys include the source address and physical source bank. A
large result restarts through the original full-buffer filter and invalidates
the small entries. Mutable RAM poses invalidate the cache and use the original
filter. No source art or retained colored pixels change. The15 added work
bytes leave52 bytes of SRAM free in this candidate.

The guest body-contact dictionary advances inline at its existing caller.
Only Mega Man/Bass enter their banked special-weapon batch, matching that
batch's existing character eligibility. The other weapon batches, timers and
native AI remain active. Drawing skips the firebar bank only when no native
actor ID can represent a firebar; every possible ID retains the original live
flag/part checks. The original exhausted firebar scratch value is preserved.

Ryu now bypasses stale wall/crouch detection during a fresh ground-jump update.
This does not create a wall-jump lock or force horizontal velocity. His real
wall jump retains its original direction and lock behavior. The rejected36a
prototype did force neutral/away jump velocity; it remains a negative
diagnostic and is not the candidate described here.

## Independent checks

- The actual36d compiled outline helper passes909 independent CPU/RAM cases
  per mapper: every legal length, all/no/mixed masks, bank keys, four/five-pose
  cycles, large output, mutable aliases, invalid headers and bounded writes.
  Returned bytes/bounds and all out-of-contract native/SRAM bytes are checked;
  R2–R7 survive. These are initialized standalone units, without interrupts/PPU.
- The actual whole weapon caller passes1,872 before/after CPU cases per mapper.
  All13 character IDs, three power forms, timers, four engine states and six
  body dictionaries preserve A/X/Y/all flags/SP and native/SRAM bytes except
  discarded stack and self-modifying call-target scratch. These idle cases
  save71–205 cycles; active weapons/swimming need their separate emulator tests.
- The real-render firebar admission fixture covers432 initialized arenas per
  mapper, including all six slots, ID boundaries, inactive/duplicate flags and
  part-count boundaries. These arenas are not controller traversal.
- Ryu's20 terrain controls per mapper include neutral/away ground launches,
  water, stale contact, ceiling contact, and real wall-away/top positives.
  Outside controls retain the rejected prototype's eight velocity failures.
- The cache's real-caller fixture still compares independent filtered bytes,
  bank changes and mutable poses. Its old fixed-base-pointer assumption was
  explicitly migrated before the frozen run, retaining byte/bounds checks.

Evidence is under `build/verification/outline-cache-v36d-*-unit.json`,
`weapon-admission-v36b-v36d-*.json`, the frozen regression log, and
`ryu-ground-wall-launch-v36-extended-a`.

## Frozen run and explicit input fixture correction

The initial frozen run passes758 of759 slots. Its fixtures are byte-identical
before/after. The sole negative is MMC3 `ryu-weapons`: a one-hardware-frame
Select request falls on a skipped controller-read frame, and no Windmill is
created. Passive35/36d receipts first differ at frame561 only in the raw
controller latch and fresh Select bit. All observed geometry/weapon/enemy
state agrees through560. MMC5's passive receipts agree byte-for-byte.

An outside control changes only that one press from1 to4 hardware frames.
Both35 and36d, on both mappers, pass every original damage/return assertion;
each creates exactly one Windmill. The original failing probe and fixture
bytes remain in `ryu-weapons-v36d-negative-probe-b`. The conclusion is limited:
the lag schedule really can miss a one-frame request; runtime input polling
has not been changed to eliminate this.

Only after the frozen run closed, `tests/expanded-weapons.lua` was migrated
to the four-frame press. All original damage, hit suppression, return/catch
and watchdog assertions remain. Both Ryu and Bass use this shared fixture,
so all four character/mapper slots were invoked again and pass on the exact
same ROMs. The consolidated report replaces those four slots and retains
the original failed summary/log and every fixture hash. Evidence:

- `build/verification/summary-roster-audit-v36-provisional-d.json`.
- `build/verification/roster-audit-v36d-full.log`.
- `build/verification/ryu-weapons-v36d-input-timing-report.json`.
- `build/verification/weapon-input-v36-fixture-migration/summary.json`.
- `build/verification/summary-roster-audit-v36-consolidated.json`.

## Matched crowd results

The unchanged aligned arena covers six characters on both mappers, standing
and walking, outlines on/off, with0/1/2/4/6 Goombas. All14,400 completed updates
match v35 across204 observed gameplay fields. The complete comparison retains
CPU, physical-frame, DMA, visibility and draw results for all240 scenes:
`build/profiling/plain-walking-v35-v36d-comparison.json`.

Four-Goomba walking with outlines off:

| Mapper / character | Physical frames per60 updates | Draws per60 updates |
| --- | ---: | ---: |
| MMC3 / Samus |60 →60|30 →30|
| MMC5 / Samus |60 →60|30 →30|
| MMC3 / Mega Man |61 →61|30 →30|
| MMC5 / Mega Man |60 →60|30 →30|
| MMC3 / Bill |59 →60|38 →48|
| MMC3 / Link |60 →60|57 →60|
| MMC3 / Simon |60 →60|43 →55|
| MMC3 / Ryu |60 →60|48 →53|
| MMC5 / Simon |60 →61|53 →56|
| MMC5 / Ryu |60 →60|56 →53|

Six-Goomba Link walking falls90 →71 physical frames on MMC3 and70 →62 on
MMC5. Several other dense scenes improve; Samus/Mega Man retain90 physical
frames and30 redraws. Across all240 scenes, nine average foreground totals
increase and two draw counts decrease. Increased draw delivery itself costs
CPU, so parent frame totals are not an isolated helper benchmark. Neither
uniform frame improvement nor zero lag is claimed.

Samus's four-Goomba walking foreground average falls493 cycles/update on
MMC3 and431 on MMC5, but that saving does not cross the redraw threshold.
The read-only outer follow-up measures work omitted by the original anchor:
about1,212/1,172 foreground cycles before the core per update. Including that
work and observed interrupts,30 of60 updates exceed29,781 cycles; maximum
elapsed work is30,989 on MMC3 and30,567 on MMC5. The unchanged engine's
catch-up path therefore still skips redraws.

`build/profiling/samus-outer-followup-v36/report.json` preserves these results,
all canonical hashes, and the two earlier observer setup mistakes. No frame
pacing or AI-clock change follows from these measurements. The NES hardware
eight-sprites-per-scanline limit remains a separate source of flicker.

## Build and remaining work

The source archive `source-v36.zip` (originally `source-v36d.zip`) has SHA256
`1525e14ec43035c87a38c30cca2dccdd0e097dd7d78571f572d9fd006e949f98`.
A fresh extraction with separate compiler/Python/Pillow rebuilds both ROMs
byte-identically: `build/checkpoint-tests/source-v36d-rebuild-smoke/report.json`.
The archive retains its recorded README bytes. The original baseline remains
`0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146`.

Default-off extra black outlines and the gold menu option are inherited from
the preceding accepted builds. Samus's ordinary no-stomp rule remains the
pinned2.02 behavior; Screw Attack handles eligible spinning body attacks.
Normal Simon/Ryu pose-dependent geometry and Simon's hurt-ceiling transition
still require correction. All final-hash roster routes, full attack/upgrade
verification and final recordings remain incomplete. Historical32/34 route
and video evidence is never relabeled with these ROM hashes.
