# Ryu side contacts

Both main builds now include Ryu's source climb bypass and the prepared normal
airborne overlap check. A native side probe no longer pushes him horizontally
when he is climbing, or when his current and previous normal hit rectangles are
already inside the queried solid cell. Ordinary side contacts, landings,
unsupported poses and other characters retain their native handling. This is a
bounded correction, not a complete port of the source's stuck-state lifecycle,
later recovery, or all body profiles.

The pinned 2.02 `Ryu.as` groundOnSide method returns immediately in ST_CLIMB.
`HitTester.as` assigns stuckInWall for prior interior Ground overlap, and
`Character.as` rejects groundOnSide in that state. The admitted predicate uses
the original normal 13.5 by 25 source rectangle and cached fractional previous
position. Its eligibility and strict prior/interior boundaries are the frozen
F implementation, including all exclusions for unsupported body states.

The previous private patch cannot be copied directly onto the current build:
the current cold initializer has six additional bytes for Cheats. The adapted
implementation keeps the original 15-byte SAMUS entry and the unchanged
42-byte stomp policy. A 40-byte dispatch in bank24 handles the source's existing
resolved-side, ground and climb guards before calling the unchanged 725-byte
overlap predicate. The predicate's assembled bytes match frozen F literally.
The gate's sole predecessor supplies Y=R0 and consumes carry; incoming A is not
an input to either the predicate or native fallback. The native fallback returns
through the existing nested farcall mechanism. No old public address, RAM byte
allocation, CHR byte or header changes. Both baseline ROMs remain identical.
The new code occupies B700..B9FC, below the reserved score tail and above Water.

Evidence:

- HD and optimized HL each build both mappers and both literal baselines. Only
  bank10's Ryu-only entry and previously unused bank24 space change. Every old
  public label remains fixed. Source overlay materialization preserves the
  current menu, cheats, HUD, terrain, score, firebars, Water, audio and Sophia
  changes; it does not replace older files wholesale.
- The final HL candidate passes 62 native whole-PlayerBGCollision cases per
  mapper, covering both behavior modes, both sides, source interior/climb,
  native fallbacks, excluded profiles, water, platforms, coins, landings,
  foreign characters and two captured ordinary source contexts. All 124 native
  source/anchor/fallback assertions pass.
- `ryu-native-hm` independently reexecutes 119 complete captured calls with
  exact registers, all 10,240 RAM bytes, live stack, ordered writes, mapper
  state and native CPU cycles. Five actual in-call interrupt cases remain
  explicit standalone CPU-model gaps. Their native assertions pass; they are
  not silently included as independently reexecuted cases.
- The first HF counterfactual verifier compared against current GO while
  retaining the older B parent's expectation that climb state was already
  fixed. Its failure is retained. HG and HM allow only the individually listed
  native side-response fields for the independently source-backed climb and
  interior changes. All other register/RAM checks remain intact.
- Sixteen unchanged Ryu control, wall launch, water/environment, injury,
  powerup, systems, source weapon and flagpole checks pass on final HL. Twenty
  four additional focused checks passed on HD, before the guard optimization.
- `ryu-dispatch-cost-ho` compares 119 matched whole BG calls between HD and HL.
  The tested climb cases save 234 cycles and landings save 313. Detailed rare
  predicates cost 18 more; coin, empty and foreign cases remain unchanged.
  Live RAM and registers agree. The actual next compiled caller instruction
  is LDA SmCeilingHit, which replaces the differing unused A/N/Z values. Popped
  stack cells and exact mutable-call operands are individually traced. This is
  a local guard comparison, not a global lag reduction claim relative to GO.

Main builds reproduce HL ROM bytes exactly. Checkpoint:
`build/checkpoints/ryu-overlap-hr/manifest.json`. The first source-guided Ryu
route attempt on HD dies in 1-1 at frame2309; it is retained as a controller
discovery failure and is not a current full-route proof. Full Ryu routes,
remaining source geometry, all weapons and final recordings remain required.
