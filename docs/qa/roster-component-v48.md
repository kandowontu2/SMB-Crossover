# MMC5 settled-Goomba terrain shortcut

The v48 candidate reduces the repeated terrain queries for an ordinary walking
Goomba on a flat floor. It preserves the existing collision routine for every
other case. The broader roster, weapon and final-recording audit remains open.

## Binary scope

MMC5 SHA256: `54d27a36bd04a2c54aeb0219fc6c6317394af7861ba4aa4a2d4b1c1a68d97da7`.
MMC3 remains byte identical to accepted v45 through v47:
`e9c1a98961d26389bc54eefc4c63e725f8ddd91c0e801cf9c553bdf774ece1f1`.

Only two bytes in the old MMC5 JSR operand change, followed by a 193-byte helper
appended to OBJECT. All old labels, other code, CHR and header bytes stay in
place. OBJECT uses 8,186 bytes, with six bytes free. The 403-file source archive
rebuilds both ROMs byte for byte in a fresh directory.

The fast path requires a matching ordinary enemy slot, Goomba ID, state zero,
settled Y alignment, interior X coordinate and direction 1 or 2. It reads the
actual foot and side cells on every call. Only floor `$54` and empty side `$00`
qualify. Pits, changed blocks, bumps, walls, other states, IDs and edges call the
original routine during that same update. No collision sampling frequency,
movement, enemy AI, controller or audio logic is changed.

## Strict behavior checks

The compiled comparison passes 82,272 cases: 82,176 independent inputs and 96
successive terrain changes. It compares A/X/Y, every status flag, SP and all
10,240 physical RAM bytes, including the live self-modifying code and the five
discarded native stack residues. Ordered actor, terrain, sound and other
protected writes also match. Internal scratch/stack instruction writes are
retained and classified; no RAM byte is excluded from the final comparison.

The independent matrix covers all admitted X/Y positions, slots, directions,
page parity, all tile values, state/ID bytes, status flags, boundaries, foreign
slots, world pages and six safe stack depths. It does not promise correctness
for an already overflowing stack.

An ordinary power-on input stream captured 64 real calls from each ROM.
Reexecuting all 128 receipts matches every register, RAM byte and observed
RAM/mapper write on its own version. There were no interrupted captured calls.
The standalone model is not a cycle-accurate NES: all 64 old calls measure 510
cycles in Mesen versus 504 in the host model; new calls measure 283 in both.
That systematic timing difference remains unclassified. Measured performance
claims below come from Mesen, independently of this host cycle estimate.

Two earlier validation negatives remain preserved. V1 incorrectly treated
addresses 0..7 as the scratch registers; compiled R0..R7 are 3..10. V2 corrected
that classifier and passed the whole final-RAM matrix, but its native write
comparison exposed omitted NMOS read-modify-write intermediate writes in py65.
V3 models those writes for the 24 official memory RMW opcodes. Neither repair
changes the ROM, receipt data, final-RAM oracle or protected-write comparison.

## Measured crowd results and limits

All 13,200 paired updates retain the same 204 gameplay observation fields.
The original profiler source is unchanged. Six-Goomba rows with equal redraw
counts save approximately 1,343 foreground CPU cycles per update. One Samus
standing scene with outlines off improves from 30 to 51 redraws in 60 updates;
the corresponding walking scene still draws 30 times.

Repeated six-enemy tests use 1,200 updates per character:

| Character | Physical frames, old to new | Redraws, old to new |
| --- | --- | --- |
| Mega Man | 1,250 to 1,201 | 600 to 600 |
| Samus | 1,201 to 1,200 | 600 to 619 |
| Simon | 1,215 to 1,200 | 600 to 600 |
| Bass | 1,339 to 1,198 | 600 to 600 |
| Ryu | 1,187 to 1,200 | 600 to 600 |

Ryu's physical-frame result is a counterexample to universal improvement.
Individual four-enemy redraw and visibility counters also worsen in some
phases. The independent aggregation retains all 75 rows with at least one
negative metric. Counts of visible enemies also depend on how many physical
frames elapsed, so their raw totals must not be read as a universal visibility
rate. Fallback query paths can cost up to 204 additional host-model cycles.
Dense scenes still skip redraws; the NES eight-sprite scanline limit remains.

## Captured image and sound checks

A new 1,200-frame ordinary-input MMC5 Samus capture was compared to the retained,
accepted v47 native capture. Every one of the 1,199 committed RGB24 frames is
literally equal. The 1,199 input receipts and their physical-frame phases match.
This is a bounded image comparison, not a full route or all-character review.

Literal PCM differs beginning at 10.523104 seconds. Neither stream was aligned,
trimmed or resampled to produce a pass. All 4,463 APU and 15,486 source-queue
writes retain their values, order, physical frames and audio ownership. Frame
state CSVs are equal. There are 539 APU timing changes, normally two or four
cycles. Two writes occur 112 cycles earlier, on opposite sides of the same
97-cycle IRQ compared with the control. The first shifted write is on frame
629, following an NMI whose entry shifts by one cycle. The PCM negative remains
documented; register equality does not establish waveform or perceptual identity.

## Evidence

- `build/checkpoints/roster-audit-v48-provisional-a/`: immutable ROMs, source and candidate metadata.
- `build/verification/goomba47-48-cpu-v3-a.json`: strict full matrix.
- `build/verification/goomba47-48-native-cpu-v3-a.json`: 128 actual receipts.
- `build/verification/goomba47-48-crowd-review-a.json`: all comparisons and counterexamples.
- `build/verification/goomba47-48-ppu-samus-e-a/report.json`: retained native image/PCM capture.
- `build/verification/goomba47-48-apu-samus-e-a/report.json`: actual audio writes and origins.
- `build/verification/goomba47-48-apu-classification/`: independent timing/PCM classification.
- `build/checkpoint-tests/source-v48a-rebuild-smoke/report.json`: fresh-source rebuild.

Acceptance additionally requires one complete unchanged-fixture regression run,
bound to these exact ROM hashes. The accepted checkpoint manifest, when present,
is the authority for that acceptance; this document alone is not a release.
The separate 173-byte stack-residue experiment remains unapplied.
