# MMC5 Mega Man audio work

Accepted component checkpoint with known roster defects. Both immutable40c
ROMs pass one full761-case regression run with identical fixtures before and
after and zero failures. This is not final roster, recording or cartridge proof.
Frozen summary: `summary-roster-audit-v40-provisional-c.json`.

- MMC3 SHA256 `ae73ef228800b917694c40d5de9bdbbb9467087f9a047ecb0fb6e216984853e8`, byte identical to accepted39.
- MMC5 SHA256 `0b1a841730fcbc018857912bcbab41aa293fb1103a21bc895ef50f1e49acc98d`.

## Runtime change

The native MM3 unsigned8x8 fraction routine uses the MMC5 multiplier in the
audio NMI. Its original entry, following routine addresses and song data stay
fixed. The appended implementation preserves the native partial-product A/V
result, X, Y, all flags, stack balance and private RAM, as well as the product.
No current foreground or IRQ code consumes the multiplier ports.

Mega Man's MMC5 audio wrapper swaps only MM3's owned C0..DC state. MM2's
E0..F5 state is still loaded, saved and restored separately when its music
engine runs. The original full54-byte foreground scratch save remains exact.
Unused MM3 private bytes remain unchanged and foreground DD..DF is untouched.
Both changes are disabled on MMC3.

## Independent checks

`mm3-multiply-v39-v40a-mmc5.json` covers131,072 actual compiled CPU cases:
every factor pair, both incoming overflow states, varied remaining flags,
registers, stack and C3. Product results are checked against independent
unsigned multiplication. The entire physical MM3 bank11 in40c is identical
to that tested40a bank. Zero inputs save134 cycles; nonzero inputs save up
to207 and one corner adds1 cycle before wrapper savings.

`mm-audio-outer-v39-v40c-mmc5.json` covers eight coherent2000-update streams
through actual AudioUpdate, both native music engines and shared mixers.
All A/X/Y/P/SP, private RAM, live far-call image and ordered APU writes match;
only discarded upper stack storage is excluded. Actual special requests,
charge, landing, effect queues, pause, title and restart are included. There
are6440 hardware products. Sampled full-update savings are0..1120 cycles.
This CPU model does not supply PPU, interrupt, DMC playback or waveform proof.

`mmc5-multiplier-ownership-v40c/report.json` observes63 actual Mesen products
with4502 NMI entries,4445 IRQ entries and10 lag NMIs. Every access belongs to
the native audio NMI and every low/high result matches its factors. All20,181
ordered hardware APU writes across11 guest drivers match the immutable
pre-optimization oracle, including effects, transitions and pause.

## Walking controls and results

The original aligned benchmark reports98 differences only in scene6:
60 X-fraction and38 integer-X fields. Its read-only initial-phase observer
shows the setup retained different source movement state:39 starts timer0,
previous-direction0;40c starts timer6, previous-direction1. Staging two real
Right polls can execute another foreground update before the arena seed.
The setup reset position and velocity but omitted those two variables.

The original negative comparison and both diagnostic CSVs remain preserved.
The separate `plain_walking_aligned_v40.lua` setup explicitly initializes
timer0 and the already-held direction. Both39 and40c are rerun with this
same setup. No canonical field is excluded, tolerance added or runtime/input
policy changed. All2400 measured updates across40 scenes and204 gameplay
fields match exactly. These are authored RAM arenas, not controller routes.

`plain-walking-v39-v40c-step-aligned-comparison.json` shows no scene loses
redraws or needs more physical frames. Mega Man improves in four scenes:

| Scene | Redraws per60 updates,39 to40c |
| --- | ---: |
| Standing, four Goombas, outlines on |30 to44|
| Walking, four Goombas, outlines on |30 to35|
| Standing, four Goombas, outlines off |30 to44|
| Walking, two Goombas, outlines off |59 to60|

Outlines-off four-Goomba walking still redraws30 times per60 updates.
Six-Goomba walking still needs90 physical frames and redraws30 times.
The Bass idle-crowd results remain unchanged: four-Goomba walking redraws37
times per60 physical frames; six-Goomba walking takes85 frames with30 draws.
Foreground averages can rise when the engine performs additional drawing.
These changes do not remove every source of lag or scanline sprite overload.

The additional five-character MMC5 comparison retains the original frozen
aligned arena and39 controls: Samus, Bill, Link, Simon and Ryu. All6000 updates
and204 fields match, with identical physical-frame and draw counts in all100
scenes. See `plain-walking-v39-v40c-other-comparison.json`. This explicitly
checks the other graphics consumers after the C000 code layout changed.

A separate actual-bank NMI observer has identical canonical gameplay to the
original40c arena. In Mega Man's outlines-off four-Goomba walking scene,
native audio averages4856 cycles versus5599 in39. The NMI averages7463 versus
8208. All30 updates following regular NMI still miss the physical-frame
deadline. Nested routine totals overlap and cannot be summed. See
`megaman-nmi-followup-v40c/report.json`.

## Rebuild, retained negatives and remaining work

The401-file source archive rebuilds both ROMs byte identically from fresh
extraction with compiler/Python/Pillow supplied separately. Archive SHA256:
`d45b13536f22407cac94de1e837a06eed74bf729b02282ad9159a50bb28c1f3d`.
The fresh extracted baseline also matches the original0511c684...1cdc5146
hash; its separate receipt is `native-audio-v40c-baseline.json`.

Prototype40b was rejected before runtime testing: an unparenthesized assembler
logical guard altered the wrong copy range, and the unchanged-MMC3 binary
assertion caught it. Its exact candidate bytes and rejection reason remain.

Outlines remain off by default with a gold option row. Samus ordinary contact
remains faithful to2.02: no ordinary stomp; Screw Attack supplies aerial damage.
Known39 geometry gaps, dense-scene lag, final-hash roster routes, every weapon
and upgrade, and all final recordings remain incomplete. Older34/34b/38d route
proofs retain their exact ROM hashes and are not40c certifications.
An additional Simon walk-off jump mismatch is confirmed on the34 route:
grounded source state grants an unused air jump, but the current movement
code arms it only after a ground jump. Its actual fresh-A negative and source
proposal remain at `simon-walkoff-source-gap-v34/summary.json`; a40 reproduction
and next functional batch are still required.
