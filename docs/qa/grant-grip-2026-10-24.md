# Grant floating-block grip repair

Grant could grab the side of a short floating block and immediately lose it
without moving. His admission probe touched the block beside his body; the
retention probe checked only below that contact, at his feet. Ordinary held
Right/Up alternated grab/loss forever. Exact failed native prefixes and
201completed stationary updates preserve the failure.

The repair keeps the existing foot check first and also retains the same body
contact that admitted the grip. Jump/climb speeds, collision masks, artwork,
levels and RAM layout are unchanged. A17-byte helper is appended in PRGbank82;
two operand bytes retarget the old retention call. Every other ROM byte,
header, CHR byte and previous instruction address is preserved. Ordinary solid
foot contacts cost19additional CPU cycles; the first helper probe adds two
stack bytes. This is a collision repair, not a lag improvement.

Candidate SHA256:
`f0fd9264601e13e7f079eeb0e6dd025d1f0c857704ebbdd7509efa00abee5064`.
Live adoption is established only by the exact source-rebuild receipt at
`build/verification/grant-grip-pm/proof.json` and its checkpoint manifest.

## Verification

- Actual original USA CV3 wall-state instructions are authenticated against
  original ROM SHA`085ec6395681c7ebfda19c2986069c21a3d27738cc61ada76249de70a07ed7d3`.
 248instruction bytes cover the relevant state. Thirty mirrored body-contact
 cases compare original retention/vertical intent with the linked port:
 parent30mismatches, candidate0. Original room queries are a declared solid-map
 adapter; original movement/animation leaves are observed, not a full scene.
- The linked port retains11,592contact cases and repairs696body-only contacts,
 covering all256metatile classes, both facings, four geometries, three input
 directions and page-boundary/interior origins. Another240delay/attack/fresh
 leap/admission/ceiling cases retain old outputs.2,204actual MMC5 IRQ injections
 across16paths preserve the interrupted state and live stack.
- The same old controller that times out on both parent modes clears the
 candidate: Easy5,316frames, Hard5,310. Independent strict direct replays reach
 movable1-2with zero deaths;10,226actual PPU frames and lossless raw captures
 are retained. Original logical world/camera and visible split bounds remain.
- Separate exact-input native observers record5,308/5,302NMIs and5,194/5,157IRQs.
 Both retain minimumSP190with no immutable SMC poisoning or invalid execution.
- A source-qualified read-only hook observes nine real foot-probe fallthroughs,
 including three body-contact recoveries. Root inspected all40consecutive
 actual PPU frames2220..2259at the first floating-block recovery, plus48sampled
 whole-route frames. This is complete local window review; whole-route human
 inspection remains sampled. NES sprite-overload flicker remains a separate
 audit concern.

Evidence lives under
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-grant-grip-pj/candidate-v1`.
Cold roster entry, firebar regressions, source-only rebuild and ordinary
flag-off hashes are separate adoption gates controlled by the final receipt.

The parent PC audit finished63strict pairs out of74required. Those are a
different ROM hash and are not added to this candidate's two. Every-powerup
delivery/use/effects/SFX, the remaining roster cases, source fidelity, lag and
the final full MMC5/oversizedMMC3release remain unfinished.
