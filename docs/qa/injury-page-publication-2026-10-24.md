# Injury pages must follow the image actually drawn

The broad roster sweep reproduced two bad video frames after recovery in both
Proto Man Hard and Mega Man Hard. Proto's last drawn hurt image needed physical
page 267; the old recovery routine wrote logical page 64 while his explicit
upper bits remained active, selecting page 320. Mega Man's retained hurt image
needed page 244; the same early restore selected his normal page 53. Both were
real native CHR ownership failures, not controller deaths.

The repair keeps the committed injury page through a skipped draw. Legacy
Mega Man and Bass restore their buster page inside an actual drawing transaction;
their next visible body still chooses its own pose bank. Proto Man retains his
existing explicit body publisher. The helper rejects other identities, Roll,
Proto's alternate mode and unrelated direct pages. It allocates no new RAM and
changes no CHR artwork, movement or injury duration.

Private candidate:
`f8571591a8d829210ec9dd352ac36bbfcf44f8700aabbaa88deca6e2be9e0008`.
Only the acceptance receipt at `build/verification/proto-hurt-of/proof.json`
and its source-only rebuild establish adoption. Evidence lives at
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-proto-hurt-of/fix-v8`.

The original 52-byte recovery span contains its banked call and a small draw
gate. The original public return marker remains executed, and all prior linked
addresses stay fixed. The draw gate preserves incoming status and the original
zero return value, including across an interrupt between its saved status and
conditional branch. The roomy new segment follows the existing menu in bank 66,
preserving every menu address. Only banks 10 and 66 change; the build-only
farcall counter increases by two.

Verification covers:

- 6,400 linked CPU comparisons: 3,200 injury-end cases and 3,200 zero-timer draw
  cases. All 20 internal IDs, variants, logical/direct pages, wrapping reload
  counters, registers and flags are covered. The only intentional differences
  are deferred MM-family bank writes and the admitted legacy restore during
  drawing. Reserved application bytes in the stack page remain compared;
  only the actually unused upper stack slice is excluded.
- 6,436 actual scroll-IRQ interruptions across 208 paths, including the saved
  status branch, farcalls, physical/direct rejection and original return marker.
  Registers, meaningful flags, live stack, final banks and completed state match
  the declared original behavior.
- Native Mega Man and Bass source injury components: 14 arenas each, with dry,
  water, ground, air, seams and both facings. The original movement, 26 locked
  updates, 75 immunity decrements, unrelated world motion and caller checks pass.
- Four fresh cold-menu 1-1 discoveries and independent exact input/trace replays
  reach movable 1-2 without death: Proto Easy/Hard 5,015/5,012 frames; Mega Man
  Easy/Hard 5,053/4,996. All expected replay image files are retained, and the
  per-frame body CHR/scroll checks pass. Maximum world steps are 2/3 and 2/4 pixels respectively; all
  visible scroll writes remain on scanline 31. All 19,276 lossless PNGs remain
  retained externally.
- Root viewed all four 24-frame overview sheets and the prior-error scene frames
  1301/1302 (Proto Hard) and 1312/1313 (Mega Man Hard). No new displaced or green
  background tiles were seen in those samples. Partial-body visibility in other
  injury/overload samples still needs source/scanline review; it is not certified
  by this bank repair.
- All 37 cold entries and the seven existing source-audio regression fixtures
  pass on this hash. The matched turtle performance fixture is byte-identical
  to OE, with unchanged CPU measurements and lag. Heavy gameplay lag remains.

The old Bass injury fixture failed on the unchanged OE build too: at video
frame 130 it had completed all 26 recoil updates but only 70 of the required 75
immunity decrements. The bound fixture now waits for the remaining native
decrements within its existing 160-video-frame limit. No movement, count,
input, world-motion or caller assertion was removed. Both baseline and repaired
build pass that scheduling adaptation; the original failed logs are retained.
This is not a claim that the existing physical-time slowdown has been fixed.

Rejected preparations remain outside the live source: the resident-space
overflow, an invalid constant reservation, a layout that moved menu addresses,
and the earlier Proto-only versions. Version 4's functional route evidence is
not final-version acceptance. Version 8 also repairs the independently found
Mega Man case and preserves the original return instrumentation.

The full roster/every-item matrix, remaining route failures, major lag and
sprite dropout, native audio/effects fidelity and full oversized MMC3 port
remain open. Published ROMs are preserved. Source ZIP rebuilds and ordinary
mapper hash checks precede adoption; workspace usage stays below 30 GB.
