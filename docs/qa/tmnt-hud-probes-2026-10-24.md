# OE: HUD draw savings and Little Mac's top-of-screen collision repair

Private MMC5 candidate
`c2ee2a9d56e60f470098e71a0fbd429bbcd1ce30a5adcaffbd690a90201200f1`
extends accepted OD
`89d8b2002ad0f471e1d4a782d52b681e5f641cba7843ba5f2eb019841b8cdf72`.
Adoption requires `build/verification/tmnt-probes-oe/proof.json` and its
source-only exact rebuild. This does not complete the full roster/item goal.

Evidence and all lossless captures are retained outside the workspace at
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-host-oe`.
The accepted candidate's tests must name `probe-v6`, not earlier experiments.

## Reproduced defect

A strict review of the first probe candidate's Mac Hard replay failed the
existing eight-pixel maximum world-step bound. Mac moved sideways by9,13and16
pixels around frames2814,2855and2856. Inspection of those actual PNGs showed
the jumps beside the final staircase, with his head near the HUD.

The original Mac side probe temporarily shifts his anchor upward to cover his
tall body. Some samples then fall above terrain row32. The native SMB getter
wraps that row into unrelated memory and can report a false wall. A passive,
byte-identical replay reproduction observed40out-of-domain queries, including
five nonzero false tiles. That failing evidence is retained at
`mac-top-reproduction-v2`; it is not described as a passing route.

Both private Mac side-getter sites now return an empty cell when their actual
sample is outside rows32through239. Valid terrain samples still execute the
original getter with the incoming register and status state restored. The
standing loop and crouched/lower branch both use the guard. Movement constants,
jump height and wall resolution remain the source implementation.

The canonical Mac bank and the local dispatch copy receive identical guards.
This matters because repairing only the copied path would leave another entry
unsafe. Version5 guarded only the standing loop; a CPU edge case exposed the
remaining lower path, so version5 was not adopted.

Fresh v6 Easy/Hard controller-only routes clear1-1in4952/4053frames, with zero
deaths, restored movement in1-2and byte-identical independent input/trace
replays. Strict review records maximum world steps3/2pixels and maximum camera
steps3/2. All8605lossless replay PNGs are retained. Root inspected both24-frame
overview sheets; the human review is sampled.

A separate passive v6 observation uses the fresh Hard controller stream for
3200frames:14out-of-domain samples are rejected, none reaches the native
getter, and no death occurs. An earlier attempt to reuse the pre-fix controller
stream died before reaching that scene; its failed fixture is retained at
`probe-v6/mac-top-fixed-v1` and is not used as fixed-scene evidence.

## Narrow rendering and dispatch changes

Eight original turtle HUD icons extend16pixels upward. The previous common
world helper required a24pixel origin clearance because other effects extend
farther. At their normal origin23the icons needlessly used the general
renderer. A guarded fast path admits only those exact eight original records,
their bank, palette,16through23origin and available OAM capacity. It reads the
existing immutable tile/attribute descriptors and preserves ordered sprite
stores, priority, rotation, clipping fallback and overflow behavior. Valid HUD
calls save183cycles. Ordinary world calls atY24and below retain their original
instructions and timing.

The public head/side bridges avoid a redundant Little Mac bank trip. Turtle
calls enter their existing same-bank handlers. Mac uses a local copy of the
same canonical terrain body; other identities continue to the same next
dispatcher. Turtle probes save71cycles each; other profiles save34or35. Mac
head probes save33through34; a Mac side call can cost70extra cycles when the
new domain guard is needed. Nested savings are not summed.

Only PRG banks87,89,93and127change. CHR, persistent RAM allocation and all
pre-existing runtime addresses are unchanged. The build-only farcall counter
increases by2. Ordinary14-character MMC3/MMC5 rebuilds must retain their exact
published hashes before adoption.

## Verification and remaining limits

- 36,980 actual linked world-helper cases compare registers, meaningful status,
  stack pointer, application RAM, ordered OAM writes and final bank mappings.
  They cover all168world table entries, edge pages, capacity, rotation,
  RAM-descriptor mutation and wrong-bank fallback.
- 7,680 complete public head/side comparisons cover all 20 internal IDs and four
  variants. Only the original Mac private getter outside terrain is modeled
  empty; other baseline code executes unchanged. A further16384actual-wrapper
  cases cover all256shifted Yvalues at both real upper indices and screen
  edges, including13312valid getter calls and3072empty results.
- 4,352 interruptions exercise every instruction boundary of all eight HUD icon
  paths at two Yorigins and two rotations through the actual linked scroll
  IRQ vector/handler. This CPU check is separate from timed native PPU/NMI
  evidence.
- The unchanged 600-update native performance fixture passes its no-added-lag
  gate. Dropped draws per120updates remain0in idle, walking, two-Goomba and
  primary phases. Triple shots improve fromOD32/31to27/25for LeoEasy/DonHard.
  Recorded gameplay fields match; actual input-sampling differences from NMI
  timing are retained. Heavy-shot lag remains open.
- The finalizer requires eight fresh turtle 1-1 discoveries and exact replays,
  strict camera/body-CHR review,32native equipment/primary/boss/ammo components,
  source equipment13708and shared-hook456CPU cases, actual source-pixel/OAM
  checks,37cold entries and existing source-audio regressions on this hash.
  All37entries are not37complete campaigns. Arranged item components do not
  establish natural delivery of every reward.
- Root's overview review is sampled. Complete lossless frames remain available
  for further inspection. Existing scanline overload and sprite dropout are
  measured rather than called solved.

The broad world-descriptor baking experiment passed CPU comparisons but saved
too little and added a native lag frame. It remains rejected outside the live
source. Earlier slower Mac dispatch variants and the versions with real route
or guard failures are also retained. Native TMNT music/effects, other families'
source fidelity, the full37/every-powerup matrix, substantial remaining lag and
the full oversizedMMC3port remain open under the final verification plan.
