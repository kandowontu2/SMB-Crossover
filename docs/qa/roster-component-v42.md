# Frame publication and native audio

Accepted component checkpoint42e passed all761 unchanged-fixture emulator slots in one full run.
Mario matches the baseline replay in all19 fields for521 frames. The401-file
source archive rebuilds both ROMs byte identically from fresh extraction. The roster audit and
final recordings remain unfinished. This document records the component's
evidence and limits; it is not a source-perfect or cartridge certification.

## Runtime changes

Every Crossover GameLoop marks NmiDisable negative before updating shared
graphics. Previously, a lag catch-up could enter with NmiDisable zero. A
normal NMI could consume partially written VRAM commands, unfinished OAM or
unpublished CHR state. The new prologue protects catch-ups as well as normal
updates. PauseSkip publishes the completed update by clearing the flag.

IdleLoop permits one immediate catch-up, then waits for normal NMI. Only that
catch-up suppresses its draw; its skip flag does not carry into the next
normal update. An unlimited protected chain delayed native controller reads
and could accumulate too many VRAM commands. The unchanged41-byte injury
bridge moved into previously unused E025..E04D padding. The aligned controller
reader stays byte identical at E000..E024; FIXED still starts at E060. No RAM
was added. Baseline builds retain their previous scheduler.

MMC5 native audio has three narrow reductions: MM2 writes use their existing
outer flag protection instead of nesting another protected writer; two MM3
writer tails jump directly to the unchanged helper; Bass clears its sixteen
dirty bytes with descending absolute stores. MMC3 retains the old audio
paths. Song data, effects, buffer contents and ordered hardware writes retain
their tested contracts.

Outlines remain OFF on reset with the gold option row introduced in32.
Samus's ordinary jump still cannot stomp under the pinned2.02 source;
Screw Attack supplies aerial contact damage. Neither rule changed in42.

## Independent findings and retained prototypes

The ordinary Sophia38d replay supplies the actual corruption negative:
SetupNums published command-high20, then NMI read header20/24/00 before low
7A and length3 were written. Zero length underflowed into a256-byte HUD
stream. The background CHR bytes stayed identical. Receipt:
`sophia-38d-hud-flow-d-11-v0-mmc3/hud-causal-receipt.json`.

The accepted41 replay and four ordinary Start-timing variants expose the same
unprotected ownership, but did not reproduce malformed consumption. Their
motion and interrupt phases diverge from38d; they are qualified negatives.
They must not be represented as actual41 corruption reproductions.

42a/42b protected all writers, but the unbounded catch-up chain increased
actual active-play controller sampling gaps from two to five frames.42b's
unchanged full suite passed754 slots and failed seven: Sophia's missile pool
on both mappers, both brothers' water initialization on both mappers, and
MMC5 Knuckle VRAM overflow85. All761 raw logs are frozen under42b/validation.
The first generator full-label assertion failure is preserved separately.

42c bounded catch-up and passed the four focused MMC5 failures. It still
carried a second draw skip into the next regular update, reducing dense
six-Goomba redraws. Its source archive, crowd results and diagnostic receipts
are retained. No complete42c suite or acceptance is claimed.

42d restored redraw frequency, but its full run passed759 slots and failed
the immutable native bbox caller on both mappers. All5,292 geometry rows
matched except SP was one higher in2,646 catch-up rows. The new direct call
omitted the original NmiSkipped stack byte.42e restores LDA/PHA/PLA around
the catch-up; both unchanged5,292-row caller CSVs now match the native golden.
D raw CSVs and all761 logs are retained. No fixture comparison was relaxed.

The42e ordinary-controller observer records5,217 protected bodies and678
SetupNums entries, all busy255, with zero malformed commands or damaged
static HUD labels. It observes4,748 groups with at most one catch-up/two
bodies. All5,181 actual native reads have eight bits and matching strobes.
Continuous active-play read gaps peak at three frames, compared with41's two;
six-frame gaps occur in initialization. This remaining responsiveness cost
is explicit. Host inputPolled events do not prove native reads. The fixed
controls reach1-2 at5480 and remain alive at5719; this diagnostic is not a
route-completion or comparative playthrough-speed proof.

## Audio and crowd evidence

`mm-bass-audio-v42-proof/receipt-e.json` binds20,326 compiled CPU cases:
16,000 full MM audio updates, eight initializations,3,294 full Bass updates
and1,024 direct clears covering all256 incoming flag values. A/X/Y/allP/SP,
RAM including live SMC except discarded upper stack, and ordered APU writes
match. Exact cycle arithmetic includes independently matched5,652,681 branch
decisions and six explained page-crossing changes. The original unadjusted
cycle-estimate failure remains. Measured model savings average90.55 cycles/MM
update and112.60/Bass update across these streams; the clear itself saves95.
These units omit PPU, interrupt scheduling and sampled waveforms.

`mmc5-multiplier-ownership-v42e/report.json` separately binds actual Mesen
hardware ports:63 exact products,4,502 NMI and4,445 IRQ entries, including ten
lag NMIs. All20,181 ordered APU writes across eleven guest drivers match the
unchanged pre-optimization golden.

Matched full arenas retain all204 fields and60 updates in each of20 scenes.
MM/Bass and Samus supply3,600 paired updates with no gameplay mismatch.
Default-outlines-off walking results, draws/physical frames:

|Character|Goombas|41|42e|
|---|---:|---:|---:|
|Samus|4|60/60|60/60|
|Samus|6|30/63|30/63|
|Mega Man|4|35/60|34/60|
|Mega Man|6|30/89|30/90|
|Bass|4|44/60|51/60|
|Bass|6|30/82|30/81|

A separate twenty-repeat, four-Goomba outlines-off supplement adds2,400
matching updates. MM totals1,104→1,119 draws over1,200 physical frames;
Bass904→925 draws over1,197→1,198 frames. Individual counterexamples remain;
the supplement does not erase the table above. No universal speedup or
zero-flicker claim follows. The42b five-other-character comparison used the
wrong setup source and was rejected by the unchanged comparison guard; its
standalone runs are not counted as paired evidence.

## Remaining work

Dense crowds still lag and exceed NES sprite scanline limits. The native
three-frame input gap is a known cost of safe publication. Simon/Ryu geometry
and input-phase work, Ryu wall/vine action gates, Bill Flare source differences,
every weapon/upgrade, final-hash fourteen-character routes, recordings and
visual/audio review remain incomplete. Older34/38d/40 routes do not certify42.
