# MMC5 native audio scan optimization

Accepted component checkpoint with known roster defects. Both immutable39a
ROMs pass **one full761-slot emulator run**, with identical fixtures before
and after and no failures. This is not final roster or hardware certification.

- MMC3 SHA256 `ae73ef228800b917694c40d5de9bdbbb9467087f9a047ecb0fb6e216984853e8`.
- MMC5 SHA256 `86826923fbf0d6b2624a44b2dad5eb52a030d404b1e2c31952f6bf03d269dd71`.
- Frozen run: `build/verification/summary-roster-audit-v39-provisional-a.json`.

## Changes and CPU proofs

This includes the Samus ceiling separation, firebar initialization and MMC5
copy/mixer work described in [the38 candidate record](crowd-performance-v38.md).
The38 full-run observer failure and its original fixtures/logs remain preserved.
The actual-bank/depth injury correction was in place before the39 frozen run.

Two additional changes affect only MMC5. The pinned native Metroid flag scanner
shifts A while retaining the original private flag byte, and takes a short path
when no bits are set. Its replacement has the same62-byte extent, routine
addresses, default RTS at$B4EE and song data.64,000 compiled CPU cases cover
every flag byte and all ten valid dispatch tables in all five imported banks,
including all incoming status-register values on the empty path. A/X/Y/allP/SP
and complete RAM except discarded stack match. Empty checks save147 cycles;
active checks save7..63.

SoundEngine also bypasses its eight effect scans when all eight init/continue
flags are zero. Music, repeat and music-init scans still run. Any effect uses
the three original scan roots. An initial prototype failed because even an
empty native Multi scan clears overflow through Add8; the final empty branch
explicitly reproduces that flag. The negative remains at
`build/profiling/metroid-lifecycle-v39-empty-sfx-negative.json`.

Eight coherent2,000-update compiled lifecycle streams cover music, native
effects, pause, mute and restart. All16,000 updates retain full registers,
flags, private RAM and ordered$4000..$4015/$4017/$5000..$5015 writes. The sampled
paths save0..2,663 cycles. These are CPU units, not interrupt or waveform tests.
No music/effect update is dropped or played at a lower cadence.

- Scanner: `build/profiling/metroid-flags-v38e-v39a-mmc5.json`.
- Lifecycle: `build/profiling/metroid-lifecycle-v38e-v39a-mmc5.json`.
- Native flush/audio copies:1,928 cases against37.
- Expansion mixer:4,096 cases against37.
- Firebar initializers:3,072 cases per mapper against37.

The new fixed helper moves aligned MMC5 DPCM data from$F100 to$F140. All3,713
sample bytes remain identical and end at$FFC0, before the vectors at$FFFA.
The source-SFX emulator checks pass in the frozen run. See
`build/verification/native-audio-v39a-sample-and-baseline.json`.

The older Samus wall matrix also has four outside controls with source-coherent
Q4.4 native speed mirrors and truly subpixel Q8.16 velocities. Both38d and39a,
both mappers, pass every original head/wall/debris/pickup oracle. Those controls
do not modify the shared frozen fixture or count as controller routes:
`build/verification/samus-zero-wall-q44-controls.json`.

## All240 matched crowd scenes

Both comparisons retain14,400 completed updates with zero differences across
204 observed gameplay fields. The arena source is identical and all twenty
scenes per character/mapper remain:0/1/2/4/6 Goombas, standing/walking, outlines
on/off. Explicit arena initialization is separate from ordinary-input routes.

Compared with38e, eight Samus MMC5 scenes improve. No scene loses redraws or
takes more physical frames. Seven foreground averages rise; the savings occur
in the excluded NMI, and additional drawing adds foreground work. See
`build/profiling/plain-walking-v38e-v39a-comparison.json`.

Compared with accepted37, outlines-off walking gives:

| Character | MMC3 four-Goomba redraws/60 updates | MMC5 four-Goomba redraws/60 updates | MMC5 six-Goomba physical frames/60 updates |
| --- | ---: | ---: | ---: |
| Mega Man |30 →30|30 →30|90 →90|
| Samus |30 →30|30 →60|90 →63|
| Bill |55 →55|54 →53|72 →66|
| Link |60 →60|60 →60|61 →60|
| Simon |55 →55|57 →59|71 →68|
| Ryu |51 →51|55 →60|63 →62|

All listed four-Goomba scenes use60 physical frames for60 updates. All listed
six-Goomba scenes still have30 redraws. Four regressions inherited from38 remain
visible against37: MMC3 Simon outlines-on walking/four draws56 →55; MMC5 Bill
outlines-on walking/four uses60 →61 physical frames while draws improve51 →58,
and outlines-off draws54 →53; MMC5 Ryu outlines-on standing/six uses62 →63
physical frames. See `build/profiling/plain-walking-v37c-v39a-comparison.json`.
There is no universal speedup or zero-lag claim.

## Full interrupt budget

A separate read-only observer retains identical Samus canonical gameplay and
includes the preceding regular NMI. For MMC5 outlines-off four-Goomba walking,
all sixty sampled updates fit the frame budget. The maximum NMI-start to update
end is29,187 cycles; the regular NMI averages4,967. AudioUpdate averages3,812
cycles excluding nested IRQ, with native Samus update averaging2,531. Nested
routine totals overlap and must not be summed. See
`build/profiling/samus-nmi-followup-v39/report.json`.

Mega Man still misses the deadline in all thirty updates following a regular
NMI in that crowd scene. His MMC5 native audio wrapper averages5,599 cycles,
and the NMI averages8,208. The C000 wrapper observer tracks actual C-bank writes
as well as A-bank writes; all1,200 canonical updates per mapper match the main
benchmark. This identifies further audio/foreground work, not a finished fix:
`build/profiling/megaman-nmi-followup-v39/report.json`.

## Rebuild and remaining work

The401-file build-input source archive plus index rebuilds both ROMs identically
from a fresh extraction, with compiler/Python/Pillow supplied separately. A fresh
vanilla baseline also matches SHA256
`0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146`.
Archive SHA256 is
`30c310243e62609a1526345dc10a30c8bde920b998bbba35e68a38d44f822679`.

Outlines default off and the option row remains gold. Pinned2.02 Samus has no
ordinary enemy stomp; Screw Attack supplies eligible aerial contact attacks.
Normal Simon/Ryu geometry and Simon's hurt-ceiling transition still need work.
The observed Pit castle correction is a local separation when an arrow reveals
a formerly non-solid hidden coin block inside his body; the native$5F guards,
new$23 tile, bbox and screenshots support that classification.

Earlier34/34b/38d controller routes retain their exact hashes and qualifications.
Final-hash roster routes, every attack/upgrade and final recordings remain
incomplete. Dense scenes still lag and the PPU permits eight sprites per
scanline. No source-perfect port or physical-cartridge claim is made.
