# DK Jr. private successor: current native mushroom qualification

The private proposal is `e73b66263a8e150d3d21b801e5a55be1817f86d09639fc428ab809b2518842d9`,
composed from exact public `7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`
by `compose_dkjr_helper_retire_1113.proposal_current`. It preserves the Prince
and Karnov updates and all unrelated bytes; its708 DK-owned edits match the
qualified frozen62 proposal. The public Downloads ROM and Latest IPS have
not changed. A full-stage physical pass remains required before delivery.

Root ran `run_dkjr_retire_current_native_1113.py` through the bounded runner
in the existing two-file task, retaining the shared Mesen queue, patch guard,
storage preflight and capture watchdog. No captures or images were produced.

Native first-mushroom Lua SHA256:
`137a7c373e27dcd9288c4cd4f6cf25e0f90b961a049e060610e68f267ae816f5`.
Receipt SHA256:
`62b5f897b6ac046aedd26d7729582b88ab00bf5784ae4fef29450b052d2da1e1`.

- The first helper is the existing native vertical platform actor, in slot5,
  World1-1 initial left336/center352/top192, collision width32. Its constructor
  runs at relativeX287, frame640/epoch145, before the platform is on screen.
  The known native girder artwork spans48 pixels; this does not enlarge the
  qualified32-pixel collision width or change its stated left/center positions.
- The real question-block effect occurs at frame1580/epoch545, player344/144,
  tile193. The original question cell subsequently becomes196 (used block).
- The native allocator selects item slot2 while the helper remains in slot5.
  Original-owner preparation is observed for that exact item slot and kind0.
- Birth: frame1581/epoch545, actor336/136, state1.
- Maturity: frame1718/epoch609, same slot2 at336/119, state128.
- Real collector: frame1781/epoch641, actor368/120, player369/126. Its return
  erases the actor and enters the ordinary powerup animation, engine9/status0.
- At frame1901/epoch671, the powerup animation has completed, status1/size0
  is committed, source ownership remains valid, and30 further active updates
  have resumed with both lives. No controller state or equipment writes occur.

This strengthens the earlier first-pickup result with actual preparation,
birth, maturity, same-slot collection, used-block state and resumed-update
checks. It is not a new all-powerup, full1-1, zero-lag or visual-polish claim.

The full-stage source replay still needs a timer-safe route before root's
physical run. Its existing12 public vertical platforms and horizontal1408
platform remain distinct from the private new336 helper. Source-only terrain
successes and timer-expiry negatives are retained by the owning helper in
`dkjr-retire-resource-request-1113.md`; no private placement is promoted to the public
helper inventory by this first-pickup test.
