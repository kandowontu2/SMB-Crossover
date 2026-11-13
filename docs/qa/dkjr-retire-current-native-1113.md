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

## Exploratory full route on actual native timing

Root subsequently runs the exact frozen terrain-positive/CPU-timer-negative
controller `bd4bacd76d2584eccc1f745c6abd27c48ab39afe04764d6254438da0f4e11464`
using `--full-frozen`. No source controls, game bytes or results are changed.
This is useful because the real native catch-up caller is not reproduced by
the CPU model's one-call-per-frame schedule; its result is not inferred from
the earlier source timer failure.

Actual native result is **negative**, receipt
`8eb7ea9ab60f56e7679aadd080ccb064e1d59fd91c429a43b3a344f84255d350`.
The first three pipes pass with both lives. Opening platforms336/416/480/560/
624/688/752/880/944 all construct before entering the viewport. The fourth
ascent880 platform is visible at relative255/frame5927; its descent944 is
visible at relative255/frame6534. Thus this is not the old missing-platform
capacity failure.

At frame7152/Main2788, DK Jr. begins fourth-pipe boarding at X891/Y176.
While waiting on the ground, a Goomba approaches. At frame7249/Main2835,
the real injury path sees player891/176 and Goomba877/184 in slot4; the next
frame records original source injury state5. Timer282 and both lives remain.
The replay correctly stops on injury. This is a controller encounter failure,
not a new proved runtime or helper-retirement defect, and no public delivery
is made. A narrowly scoped fresh-A defense during that boarding wait is the
next controller experiment. Earlier CPU terrain and timer results retain
their separate recorded scope.

The separate boarding-hop controller4302a349 then advances past that Goomba:
fresh stationary A atMain2816, actual880-platform carry at2867, rise2868,
cross3277 and fourth roof3309. Its native result is still **negative**:
receipt `94a127dbb2fca4d50091abec22a2f9cac5b29281805a05f8d92c596dc29954e0`,
frame14243/Main6295, original fall injury at X985/Y176 after jumping from
the fourth roof. Both lives/timer138 remain. It waits untilMain6221 to
jump, despite150 actual944 support observations fromMain3345 to5931. The
next experiment uses the existing grounded source-supported contact with944
to enter the ordinary descent phase. No ROM or platform position changes.

That contact-ride experiment9f943b1b is also **negative**: receipt
`07c1ac5f26bad59f4f3e9b2f78248bbdb6e32e78d1e91edc56b8b514e5285ce0`,
frame8410/Main3381, X945/Y148/source injury5, both lives/timer260. The
first944 support observation at3345 is real, but it does not persist.

The separate read-only observer keeps9f943's controller decisions unchanged.
Root narrows its window to3343..3351 to retain the actual contact and first
lost-support updates without truncating the middle. Lua4612b3ae yields native
receipt `693270bbf2f840a0cc20e77112d1f4497c5c823550364cead53a22a51f69e703`,
90 rows/dropped0, full trace SHA256
`1d9077ecf9cc0195e2371d366ea33413bd70c9001f3e6a3b1d8ac64c38a9ad11`.

- At3345 the real native position routine changes playerY112 to106 for the
  platform at138. Its completed source carry import changes sourceY127 to121.
- The resulting source/player rectangle has bottom136; native player box is
  `[90,121,107,136]`, control1. Helper box is `[96,138,128,151]`.
- At3346 the compatibility bridge appends a support plane137..138. Original
  source support still retains grounded state1.
- At3347 the live helper has moved to139, native support flag is255, and the
  player bottom is still136. Cached carry top138 remains. Original source
  support then changes state1 to4; falling later exceeds its existing limit.

Thus the native position and source import actually occur; the immediate
support loss is not explained by the replay merely failing to request the
descent phase. The native/source footer alignment and moving support cache
need a causal compatibility audit. No position correction, jump/gravity
change or game patch is justified solely by this trace.

Direct currente73 source qualification now also passes all retained cold,
fault/header/foreign/lifecycle and IRQ/lag-NMI gates (including513+513 runtime
cuts and100 taken-retirement cuts). An independent menu audit compares all101
rows and202 portrait/silhouette RGBA images against7ef:350404 bytes exact,
digestf58ec905, receipt
`8b40e7067344d7735becff2ddb5fc018f08584a8d2e5f14c97a76c53d0810016`.
Those positives retain their scope; the private full-stage failure remains.
