# Samus ceiling contact and MMC5 audio copies

The immutable candidate `roster-audit-v38-provisional-e` is **not an accepted
release**. Its frozen full run has760 passing component slots and one failing
observer. No fixture changed during that run. The original negative and full
summary remain preserved. A later candidate will run the complete suite again.

- MMC3 SHA256 `ae73ef228800b917694c40d5de9bdbbb9467087f9a047ecb0fb6e216984853e8`.
- MMC5 SHA256 `68c9273fa77eb8be09b177d08b265f0e32f2038b733d9226540f663191af5739`.

## Runtime changes and independent checks

An ordinary-input Samus1-2 route exposed repeated16px horizontal movement
after an actual head-brick contact. The temporary brick tile$23 caused the
native ceiling nibble guard to omit separation. The port now resolves the
actual solid ceiling before side checks, retains the real impact origin and
applies the pinned2.02 positive ceiling VY only when the source jump flag is
set. Morph contact keeps its appropriate cue. New state lives at the end of
SRAM, preserving every earlier RAM address. Non-Samus side behavior is retained.

The new matrix covers150 head contacts,240 wall contacts,75 debris origins and
19 real question-block pickups including complete rise. The earlier38b ROM
fails the real ceiling assertion. The existing432-case head fixture needed its
authored jump state and parser clock isolated; both original negatives and
outside controls remain in
`build/verification/samus-ceiling38d-focused-receipt.json`. No original contact,
position, origin or bounded-progress oracle was removed.

Firebar initialization now clears the owner's part count before any renderer
can consume stale SRAM.3,072 actual-initializer CPU cases per mapper retain
all other registers/flags/RAM, except discarded stack. They cover native short
IDs$1B..$1E and long$1F, six slots, all256 stale counts and free/full pools.

MMC5 uses direct private-ZP audio copies and an unrolled expansion-register
flush.1,928 CPU cases compare native flush and coherent Samus audio lifecycles;
4,096 cases cover every expansion ownership mask, dirty/image combinations
and sweep edges. Full registers, flags, RAM and ordered hardware writes match.
Native flush saves30 cycles. Expansion flush saves226 cycles when silent and
232..250 when active. Samus lifecycle changes range from189 saved to two added
cycles, depending on the path and placement. MMC3 retains the original audio
loops. These units establish no interrupt, waveform or traversal result.

## All240 matched crowd scenes

All14,400 completed updates match37 across204 observed gameplay fields. Both
mappers, six characters, standing/walking, outlines on/off and0/1/2/4/6 Goombas
remain in `build/profiling/plain-walking-v37c-v38e-comparison.json`.

With outlines off and four Goombas, Samus walks for60 physical frames on both
mappers: MMC3 remains30 redraws, MMC5 improves30 to33. For six-Goomba walking,
all listed scenes still have30 redraws:

| Character | MMC3 physical frames per60 updates | MMC5 physical frames per60 updates |
| --- | ---: | ---: |
| Mega Man |90 →90|90 →90|
| Samus |90 →90|90 →90|
| Bill |77 →77|72 →66|
| Link |63 →63|61 →60|
| Simon |77 →77|71 →68|
| Ryu |68 →68|63 →62|

Four scene regressions are retained: MMC3 Simon outlines-on four-Goomba walking
draws56 →55; MMC5 Bill outlines-on uses60 →61 physical frames while drawing
51 →58, and outlines-off draws54 →53; MMC5 Ryu outlines-on six-Goomba standing
uses62 →63 physical frames.238 foreground averages increase. Foreground timing
excludes the NMI where these audio savings occur; functional contact guards and
additional drawing also add foreground work. This is no universal speedup.

The preliminary38b run without `--source plain_walking_aligned.lua` used a
different arena source. Its30 →46 claim was withdrawn and qualified on disk.
The aligned38b diagnostic reaches36 draws; the later ceiling fix changes the
budget. The final38e comparison above,33 draws, is the relevant measurement.

## Preserved injury observer failure

The frozen run fails MMC3 `samus-injury-202` at arena22. A passive observer
shows audio bank15 executing$BA6B in NMI while foreground `CurrentBank` remains
10. Its opcode$85 is unrelated to the actual Samus bank10 entry's$A9. The
original observer interprets that audio instruction as a second injury.

Outside controls qualify actual physical bank10 and interrupt depth0. Both37
and38e on both mappers pass all32 arenas,448 numeric recoil updates,250ms lock,
1250ms protection, flicker timing, cue and live-world assertions. After the full
run closed, the shared fixture gained those two qualifications and retained
every original oracle. Both corrected38e mapper invocations pass. This is a
targeted correction, not an entirely green frozen full run.

- Original: `build/verification/summary-roster-audit-v38-provisional-e.json`.
- Passive: `build/verification/samus-injury-v38-passive-a`.
- Outside controls: `build/verification/samus-injury-v38-qualified-c`.
- Migration, original fixture/full log and both corrected runs:
  `build/verification/samus-injury-v38-fixture-migration`.

The401-source-file archive plus index rebuilds both ROMs identically from a
fresh extraction (`build/checkpoint-tests/source-v38e-rebuild-smoke/report.json`).
Baseline SHA256 remains
`0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146`.

Default-off outlines and the gold option row remain. Samus has no ordinary
enemy stomp in pinned2.02; Screw Attack supplies eligible aerial contacts.
Normal Simon/Ryu pose geometry, final-hash roster routes, all upgrades/attacks
and final recordings remain unfinished. Dense scenes still lag; hardware
allows eight sprites per scanline. No physical-cartridge or source-perfect
port claim is made.
