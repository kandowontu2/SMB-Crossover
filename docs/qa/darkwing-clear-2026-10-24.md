# Darkwing native 1-1 route: OL

Current private MMC5 ROM:
`88906bd9b21a65c2a09128730599a4683ff6123a655386c1b55d3e0ec1ef3b8a`
(OJ collision routing). No game code or physics changes were made for these
routes. Existing native recovery and Arrow abilities were used through ordinary
controller input, without equipment, health, invincibility, position or terrain
writes.

Both modes now clear1-1 with zero deaths into movable1-2. Easy takes5724video
frames and Hard6070. Independent fixed-input replays reproduce every input and
trace byte. All11394lossless replay PNGs are retained; body CHR, visible
scanline31, adjacent world<=8 and camera<=4 checks pass. The maximum observed
world step is2and camera step3. Significant route lag remains:1436/1535lag NMIs
in the admitted gameplay video rows. These counts do not establish60Hz.

The failed controllers exposed several test-policy problems:

- The generic first-upgrade approach reveals the actual Arrow stamp$26at full
  health but does not collect the stationary item above the block. A passive
  cold-menu1400frame prefix confirms the real stamp and item bounds. It is not
  an equipment grant or an all-block accessibility proof.
- Repeated early jumps prevented the source's grounded, stationary push into a
  tall pipe from requesting its existing recovery cache. The corrected route
  allows that native condition, walks back to the visible actor, and collects
  it. The inventory then changes to Arrow with real ammunition.
- Grounded shooting invokes the native stand-and-fire pose; firing constantly
  on empty ground caused repeated stops. The route now fires deliberately at
  ordinary enemies on either side and uses the free gun rather than spending
  Arrow gas on them.
- One-poll jump edges could be lost between game updates during lag. A short
  held edge allows the native input/update path to observe A. Gap approaches
  wait nearer the edge; both tall staircase tops are actually landed on before
  releasing and pressing A again. No jump height or contact rule is changed.

Versions1–4and the earlier generic attempts remain as failed evidence. Version5
collects the real cache in both modes, uses Select, shoots an attached Arrow,
grips it and supplies a fresh A to climb the actual pipes. Root viewed both
24-frame overviews and six exact cache-contact frames. These are sampled visual
checks, not exhaustive human pixel review. The original item above the first
block remains uncollected on these routes. Three gas adaptors, every reward,
source audio and complete natural delivery are still separate open obligations.

The route audit records the powerup sound queue at each cache pickup; that alone
is not an acoustic or source-audio fidelity proof. No missing-SFX repair is
claimed by this controller work.

Evidence:
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-controls-ok/darkwing-recovery-routes-v5`.
Local receipt: `build/verification/native-controls-ol/proof.json`.
The full roster/every-item/final-mapper goal remains active and incomplete.
