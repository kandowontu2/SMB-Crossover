# Link, Simon and Ryu through 2-2 audit

Current status (immutable36 accepted): the Link/Simon2.02 movement, source
contact/effect and LSR injury migrations are implemented and covered by the
accepted component suites. The documented normal Simon/Ryu HRect follow-up
remains open; this is not a claim of complete source geometry identity.

Current Link proof: `lsr-v34-link-fixed-full-audit-a-4-v0-mmc3` passes an
independent fixed-CSV power-on replay of1-1 through2-2 with the complete
read-only frame audit, zero deaths, playable2-3 at21968 and final control21992.
ROM SHA256 is5f62764c0e531fecd5e1f6e146fc5d50f6ad9cbc237365a44838c50896b36707;
fixed-input SHA256 is7b40825f7efcec732222573df79f622bbfb226059628fe4806a8be6a3942ff38.
No final recording or current36/37 controller proof is claimed; this stays
bound to34. The source/normal-geometry follow-up and newer-runtime retime remain
open. Simon34 discovery is next. Ryu34's grounded-wall defect is source-fixed
and tested in36, but its latest-source full route still needs fresh discovery.

Historical handoff (v22; superseded): the guarded Windmill source equations pass both mappers;
the corrected full-pool native flag fixture passes all28 profile/mapper cases.
Root accepted the frozen22 runtime in
`build/verification/accepted-roster-audit-v22.json` (623 case slots covered).
The earlier v19 castle-pixel14 and Ryu-origin40 fixtures pass both mappers.
The new Link2.02 movement edit is pending root's next build, as detailed below.
Ryu's newest independently cold-boot verified
prefix is `search/ryu-v22-water2299-b/winning-inputs.csv`, poll18332,
x2440/Y70 in2-2. It compares all10,240 RAM bytes and includes all2-1.
`lsr-v22-h/inputs.csv` clears through2-2 with2-3 control at20065 and zero deaths;
strict fixed replay `ryu-v22-control-full-audit-10-v0-mmc3` independently passes
all six stages with the complete read-only audit. Provisional24's fixed replay
also passes; final recording remains outstanding pending24 acceptance.
The older v15 Ryu x2980/Y176 root in late2-1 is geometry evidence only; Link and
Simon still have v12 partial castle roots; their current routes are incomplete.

Pinned source: `reference/crossover2/extracted/scripts/com/smbc/characters/`
`Link.as`, `Simon.as`, `Ryu.as`, and `data/DamageValue.as`. Route policy:
`tools/playthroughs/link_simon_ryu_policy.lua`. Only ordinary inputs are permitted
in the cold-boot routes; ability arenas are explicitly separate fixtures.

## Source findings and changes

- Link's sword must deal 50/75/100 damage for no mushroom, mushroom, and red
  ring. Simon's whip must deal 70/75/100 for leather, morning star and flame.
  Their collision bridge still used `PlayerStatus`, so separately collecting
  the final upgrade changed the art without increasing melee damage. Both
  terrain and enemy probes now derive the damage ID from actual inventory.
- Simon's leather and morning-star hit rectangles both measure 57x14 Flash
  pixels; flame measures 87x14. The old reach calculation double-counted the
  mushroom. Corrected centers/radii retain the near edge and extend flame
  outward. Integer NES radii round the half-scale source outward.
- Ryu's sword extension changes reach, not damage: both deal 75. A restored
  accumulator value of 32 incorrectly made the old branch always choose the
  extension collision ID. The collision ID now tests the returned upgrade
  before loading it. Normal/extended standing and crouched centers follow the
  source rectangles around the generated foot anchor. Widths 48 and 75/79
  Flash pixels become 24 and approximately 38 NES pixels; crouch preserves the
  wider tip with a one-pixel center adjustment. Heights round to 8/16 NES pixels.
- Link throwing a short boomerang before obtaining a mushroom is intentional:
  `pressSpcBtn` explicitly permits it when the mushroom is absent. The previous
  user-facing breakdown described this incorrectly as partial behavior.

## Prepared ability checks

`link-melee-upgrades-202.lua`, `simon-melee-upgrades-202.lua` and
`ryu-melee-upgrades-202.lua` use explicit arena/enemy fixtures, real mature
pickup collision and one controller B press. They check mirrored damage tiers,
standing/crouched whips and swords, and a far target reached only after Ryu's
extension. Existing inventory tests cover every independent pickup, attack
type, ammunition cost, source sound and refill. These fixtures do not prove
any full-stage clears.

## Required final evidence

For each of Link, Simon and Ryu: uninterrupted power-on 1-1, 1-2, 1-3, 1-4,
2-1, 2-2 clears; independent fixed-input replay on the frozen build; native
video/audio recording; source-derived isolated coverage of all specials and
passives; lag profiles and completed-frame OAM/CHR inspection.

## Checkpoint results

`roster-audit-v1` hashes:

- MMC3: `a9e6547edf0902b203572041efca01a28f11ecee91c4da21040877594cf6b6c3`
- MMC5: `ec5c350bf1c1f4c023ec7a773ad0ae3dbfb6f90bc749f99c6013e5a17a17f7f9`

All 82 scoped existing regression invocations passed after resolving three
fixture assumptions. Simon's morning star now uses the same two-block scene
as leather, with the longer flame whip retaining the three-block transaction
stress. Ryu's windmill return is observed at physical frame 640 rather than
610, with its catch check still at 650; the independent source-equation
trajectory test passed throughout. Three new melee tests exercise 42 arenas
per mapper. Link's red-ring fixture observes 100 melee damage before its later,
separate 50-damage sword beam. Logs and rerun resolutions are in
`build/verification/link-simon-ryu-v1/summary.json`.

All six new weapon-profile invocations passed. Their explicit full-inventory
arenas exercise primary attacks and every selectable special in empty and
six-enemy scenes. The CSVs report inclusive routine CPU costs, including any
interrupt that occurs within the measured interval. They are not claims about
ordinary playthrough frame rates. Skipped physical NMIs across these synthetic
scenes were Link 434/1500, Simon 615/1800, Ryu 633/1800 on MMC3, and 342, 491,
364 respectively on MMC5. Simon's occupied holy-fire/cross updates averaged
roughly 6,300/6,400 cycles in `RemainingWeapons`; Ryu's occupied single-projectile
paths averaged roughly 5,600. The Samus agent owns the resulting shared enemy
cache/rejection optimization, so it is not duplicated here.

## Additional common injury bug found through a real route

Samus's controller-only `samus-contra-b-2` route reproduced a pole lock on v1.
After real mushroom collection and enemy injury, native `PlayerInjuryBlink`
falls through at timer `$f0` into Mario's shrink initializer. Guest graphics
never call the native cleanup, leaving `PlayerChangeSizeFlag=1`. Custom movement
continues during normal gameplay, but native scripted movement stops. The flag
slides down independently, then Samus stays at `(3161,136)` in engine state 5.
The read-only diagnostic first observes the stale flag at frame 3146 and timer
240, and confirms no subsequent pole movement.

The five-byte guest guard in `src/player.s` retains Mario's original fallthrough
and skips the shrink initializer for guests. On `roster-audit-v2`, the explicit
`guest-injury-scripted-state.lua` fixture passes both mappers: actual Spiny
contact, native injury through `$f0`, retained Mario shrinking, no guest size
flag, injury completion and resumed controller movement for every character
including Lance. Its negative control on v1 fails immediately for Mega Man.
The old real-controller stream needs rediscovery after the timing changes; the
prepared `samus-injury-flagpole-controller.lua` remains a draft and is excluded
from accepted verification. It must not be presented as a completed clear.

## Outstanding routes and resumption details

- Link: `link-simon-ryu-v3-4-v0-mmc3` clears 1-1 and reaches 1-2, then falls in
  the first underground gap at x1309. Its first-level prefix is a candidate
  only; it has not had a successful independent replay or final recording.
- Simon: `link-simon-ryu-v4-5-v0-mmc3` collects the first mushroom but later loses
  it and dies at x1217 on the 1-1 brick platforms. Combat timing against elevated
  enemies needs retuning.
- Ryu: `link-simon-ryu-v4-10-v0-mmc3` collects the mushroom, clears 1-1 and reaches
  1-2, then waits against the first pipe near x1633 until timeout. The next
  navigation revision should hold jump presses across several physical polls:
  one-poll A/B/Select pulses can be missed while the main loop is busy. The
  profile fixtures already use four-poll attack holds for this reason. Ryu's
  crouched sword is needed against short ground enemies.

The current candidate policy is `tools/playthroughs/link_simon_ryu_policy.lua`.
The shared runner now accepts `--rom` to copy an immutable checkpoint and its
matching symbols. No route uses memory/register/ROM writes. No final video has
been recorded. Root retains ownership of staging final builds and resuming
these three route searches after the shared performance/injury checks.


## Frozen v10 continuation (2026-10-17)

The rare v9 Link inventory menu failure was not reproduced in twelve fresh ROM
stems: nine v10 and three v9 runs passed all five pickup cases. The failed v9
log CRC matches its actual checkpoint. `remaining-inventory.lua` now prints
actual character, mode, task and engine on a startup failure. This is retained
as unreproduced evidence, not attributed to the earlier fixed audio race.

A proposed Ryu projectile-facing change was rejected by the source audit.
`RyuProjectile.setDirection` changes position/velocity and `thrownRight`, never
`scaleX`; its Projectile/AnimatedObject/LevObj ancestry does not auto-mirror by
velocity. Small and windmill stars therefore retain the same chiral spin in
both launch directions. `ryu-projectile-source-pixels.lua` independently
compares every exact source phase against completed DMA OAM/CHR pixels after
actual Select launches, both directions and both projectiles. Both v10 mappers
pass. Its frozen silhouettes are extracted directly from the pinned 2.02 sheet
by `freeze_ryu_projectile_pixels.py`, without reading NES CHR/metasprite tables.
The source comment documents the deliberate common pointer; no emitted bytes
or data changed for this finding.

Controller-only progress on v10 remains discovery, not accepted final proof:

- Link `lsr-v10-c-4-v0-mmc3` clears 1-1 and 1-2, enters 1-3 at frame 9260,
  then falls at the elevated treetop near x706. Its pipe branch
  `search/link-v10-pipes1648-a` passed an independent power-on comparison of
  exact input polls, frame/target state and all 10240 RAM bytes.
- Ryu `lsr-v10-c-10-v0-mmc3` clears 1-1 and reaches the 1-2 pipe at x1860,
  where he contacts a Piranha Plant. The low obstruction at x849 was a brick
  wall under a low ceiling, solved with crouching sword attacks. Both that
  branch and `search/ryu-v10-gap1280-a` passed the independent power-on check.
- Simon still needs the paired Goomba section around x1900 in 1-1. The first
  bounded search did not win; its best branch was independently replayed, and
  a wider search with crouch/attack and double-jump inputs is in progress.

All these prefixes belong to v10. They must be checked again on the next
checkpoint before a final replay or recording. No final video is claimed.


## v11 route progress

Ryu's exact-phase pixel fixture passes both frozen v11 mappers as well.
The first pickup helper now aligns its head probe and drops off the top of the
brick row before bumping underneath. Fresh ordinary-controller runs collect
the first mushroom: Link frame 1222, Simon1242, Ryu1126. The older claim that
Simon's v10 route collected it was incorrect: that trace stayed at power0.
This was a route-policy setup mistake, not a gameplay pickup failure.

New verified v11 local branches, each independently cold-boot compared through
all 10,240 RAM bytes:

- `search/link-v11-stair2440-a`: powered Link crosses the1-1 stair gap.
- `search/link-v11-treetop1120-a`: Link reaches the narrow1-3 platform.
- `search/ryu-v11-gap1280-powered-a`: powered Ryu crosses1-2's first gap.
- `search/ryu-v11-lift2480-a`: Ryu reaches1-2's final bank at x=2590.

The ordinary fixed-prefix continuation `lsr-v11-h-10-v0-mmc3` reaches1-3 at
frame 8981, then falls near x=1555. `lsr-v11-f-4-v0-mmc3` reaches1-3's moving lifts,
then falls at x=1436. Powered Simon's `lsr-v11-e-5-v0-mmc3` reaches1-2's exit region
but sits on the roof; repeated generic double jumps are the cause. The next
policy follows the shared descending-lift walk and a single jump to the rising
lift, preserving close-enemy combat. Its route is still being tuned.
No three-character route through 2-2 or final recording is accepted.


## Ryu flame orientation regression found after v11

The facing audit also covers Fire Wheel and Fire Dragon Ball: `setDirection`
never changes `scaleX` for those projectile types either. Independently unpacked
SWF frames 9-16 are chiral. `RemainingDraw` incorrectly passed their motion
`RgShotDir` into the generic mirrored art selector. The scoped correction
forces source art direction1 for Ryu in the remaining-shot branch, preserving
his actual shot direction, motion, damage and collision.

`ryu-fire-source-pixels.lua` creates both flames using actual Select and checks
all eight frozen source silhouettes, both launch directions. It captures actual
MetaspriteRenderLoop calls and completed DMA OAM/CHR, excluding frames where
CHR-family arbitration omits the shot. `ryu-dragon-source-pixels.lua` starts
with the dragon cases for an independent negative. Both tests pass every
rightward phase on v11 and fail the first leftward case on both mappers.
The four negative logs and hashes are preserved in
`build/verification/ryu-fire-art-v11-negative/`. Post-correction positive checks
pass the parent's immutable v12 checkpoint, as detailed below; no agent build ran.

## Additional controller progress on v11

A live-platform width check improves the policy: native 0x24..0x2c objects are
absent from the metatile buffer, so treating that empty map as a gap caused an
immediate jump on their near edge. A genuine Ryu root at x=1434/Y75 contains
Enemy 0x28 at1353/Y128 and1462/Y144, with the next static bank beginning1568/Y176.
The policy now matches footY to native objectY and uses native box widths
(48/32/24 pixels) before deciding where to launch. It is control logic only.

Powered-start Ryu `lsr-v11-l-10-v0-mmc3` now clears all of 1-3 and enters1-4 at
frame 11306; a firebar kills him at x=1029/frame 11985. Link's old-start stream
`lsr-v11-m-4-v0-mmc3` now enters1-4 atframe11721, then contacts a firebar at
x744/frame 12222. Link's source explicitly disallows a ground jump during a
sword/throw attack; waiting on the support for that animation avoids consuming
A before walking off. Powered Simon still needs the last1-2 lift/enemy scene.
No final through 2-2 clear, final replay or final recording is accepted.


The same flame audit found a second source omission: generic remaining-shot
muzzles were used instead of Ryu's shared setDirection pads. The existing star
origin prefix is now factored into RyuProjectileOrigin and called by all four
projectile types. Their velocity initialization remains separate. A v11 native
negative reproduces a standing fire-wheel birth at(40,194), while the source
requires(55,187) for a player at(32,176); its log/hash is preserved with the art
negatives. The fire pixel fixture now checks source launch velocity and muzzle
as well. A separate 40-case source-origin model uses actual Select launches and
explicit creation-pose fixtures for all four weapons, both directions, and
standing/crouched/air/wall/backward-wall poses. This is isolated ability-unit
evidence, not controller traversal proof.

## v12 Ryu correction validation

Parent checkpoint `roster-audit-v12` includes the flame-art direction and shared
projectile-origin corrections. MMC3 SHA-256 is
`77153d86883962ce37ad8f02595a162812b8385cb4d4615fb90d5dec500c5adc`;
MMC5 is `30175d7d5132d553330a76ba382af76ef168700368f03daea75e5c11ff082959`.
Both mappers pass `ryu-fire-source-pixels.lua`: all eight source flame phases,
both launch directions, exact initial velocity and standing muzzle. Both also
pass all 40 cases in `ryu-projectile-origins.lua` (four projectiles, two
directions, five creation poses). The original v11 negative evidence remains
preserved; no runtime test patches are used to claim traversal.

The following eleven prior Ryu tests pass on both mappers: independent
small/windmill source pixels, source weapons/motion, weapons, inventory,
melee upgrades, controls, systems, energy drops, big drops, world SFX and
weapon profile. Their logs, copied ROMs/symbols and per-test log hashes are in
`build/verification/lsr-v12-ryu-audit/{mmc3,mmc5}/summary.json`.

The latest v11 route candidates remain partial. Link reaches castle x=1879
before a castle hazard beside the next gap. The endpoint is still above the floor, so this is not evidence of a fall. Ryu reaches castle x=1565 before the
approaching Bowser flame; an earlier-tail avoidance candidate reentered the
prior firebar, so it is rejected. Simon's `simon-v11-platform1460-a` branch
reaches x=1620/Y144 in 1-3 and passes independent cold-boot verification of
all 10,240 RAM bytes. Route continuation is now running on v12; these v11
inputs are useful proposals, not accepted v12 clears. No owned character has
an accepted full 2-2 clear or final recording yet.

The focused Link/Simon suite also passes all 32 invocations on v12: inventory,
melee upgrades, controls, combat, energy drops, world SFX, underwater behavior
and block rendering, each character on both mappers. Evidence and log hashes
are in `build/verification/lsr-v12-link-simon-audit/{mmc3,mmc5}/summary.json`.

Simon continuation `lsr-v12-a-5-v0-mmc3` reaches 1-4 at frame 11634 and dies
at the first major firebar (x778/frame12225). Link local branch
`link-v12-castle1870-a` crosses the castle gap to2050/Y128 and Ryu branch
`ryu-v12-castle1560-a` passes the first Bowser flame to1750. Both v12 branches
pass independent cold-boot checks of the complete 10,240-byte RAM state. Link
continuation `lsr-v12-b-4-v0-mmc3` reaches Bowser at2232 before dying; these
remain partial candidates, not six-stage clears.

## Castle roof defect, v13 validation and next-build handoff

Link's controller branch `link-v12-bowser-a` independently reproduces a roof
crossing: frame13389, x2244/Y0, standing above the white castle roof. This is
a real defect, not an accepted clear. Link's head adder is18, but native
`HeadChk` disabled the probe below canonicalY32. His head only enters the
first terrain row after that cutoff. Other guest adders also had mismatched
windows. `PlayerHeadWithinTerrain` now compares the actual guest head point
against HUD boundary32. Mario/Luigi use their original32/16 native cutoffs.
The original R4 canonical-Y low-nibble test is unchanged.

V13 passes `guest-head-upper-extent.lua` on both mappers:32 exact adder poses
at three heights (96 collision arenas). The fixture sets its table pose at
`MegaManCollisionAdder` entry after native default-fall initialization; it is
explicit collision-unit evidence. The roof is actual castle white wall$61.
`link-roof-jump.lua` additionally uses actual A input in an explicit movement
arena. Both v12 mappers fail after canonicalY12/head30 crosses the roof;
both v13 mappers stop at minY27 and land on the original support. Unique-stem
negative logs/hashes are in `build/verification/lsr-v12-head-negative-audit/`.

All24 focused v13 invocations pass (12 tests on each mapper), including the
two new roof tests, scripted injury, Samus controls/pipes, Mega Man physics,
Link controls/block rendering, Simon/Ryu controls, Ryu40 origins and Ryu flame
pixels. Copied ROMs, logs and summary hashes are in
`build/verification/lsr-v13-head-audit/{mmc3,mmc5}/summary.json`.

The first helper version cost about20 extra cycles on every collision. The
old Link stream on v13 first diverges at frame6988 (x1521, skippedNMI100->101)
and subsequently dies in1-2. It is not a controller roof-positive or a v13
clear. The same MMC3 CSV dies earlier on MMC5 and was never claimed valid
for that mapper. The short actual-A fixture supplies the discriminating
movement positive on both mappers.

The source now has a parent-approved common-path optimization awaiting the
next checkpoint: canonicalY>=32 goes directly to the normal head probe.
All native cutoffs are at most32 and guest adders are nonnegative. Only the
top band calls the resident helper, which still honors native16/32 cutoffs.
The two-byte cutoff table moved to FIXED to keep COLLISION within PRGLow.
No RAM was added. Re-run both roof tests and the focused suite on the next
immutable build; no agent assembled a ROM.

Best genuine partial route roots to resume (all MMC3 v12; all independent
cold-boot winners compare exact inputs/frame/target and all10,240 RAM bytes):

| Character | Proof directory under build/roster-through-2-2/search | Endpoint | Next action |
|---|---|---|---|
| Link | link-v12-castle1870-a | frame/poll13252, x2050/Y128, castle | Retest new build; solve Bowser below roof. The later bowser-a roof branch is rejected. bowser-b reaches2244/Y64 but its entire path still needs a roof-crossing audit. |
| Simon | simon-v12-castle1248-a | frame/poll12851, x1450/Y128, castle | Retest new build; pass Bowser flames and final bridge. |
| Ryu | ryu-v12-bridge-a | frame/poll13028, x2244/Y103 airborne, castle | Retest new build, walk to axe and verify actual transition to2-1. |

Use each directory's `winning-inputs.csv` as a proposal for a cold-boot prefix
on the next checkpoint. Never reuse opaque save states across changed ROMs.
The shared branch tool now supports optional `--goal-y-min` (default0); both
the trial and deferred goal checks enforce it. MM/Bass independently smoke
tested inclusion/exclusion. It constrains the endpoint, not earlier movement.
The new optional `--root-proof` workflow belongs to MM/Bass and can reuse
verified states only on matching ROMs. No owned full2-2 replay or final
recording is accepted. All launched processes for this handoff have completed.

## v15 resume: fresh route and retiming diagnosis

New controller work uses immutable v15 MMC3
`8a5e41a721170addd94ff7e35997dad869721097b522524f83871717eeb07f16`.
The untouched old v12 Ryu prefix diverges and dies in1-2; it is not new proof.
Fresh policy run `lsr-v15-b-10-v0-mmc3` collects the first mushroom, clears1-1
and enters1-2 at frame4574. Its first-pit jump hits the underside of the low
ledge. Genuine branch `search/ryu-v15-gap1280-a` starts at poll5550, climbs the
ledge and reaches x1430/Y80/power1 at frame5726. Independent cold-boot replay
matches all10,240 RAM bytes. Its winning-inputs.csv is the current v15 Ryu
prefix; continuation is `lsr-v15-c-10-v0-mmc3`.

The shared observer also independently replays the old near-axe v12 Ryu
proof, preserving its entire endpoint RAM. Its12901 logical tick observations
are in `tick-observations/ryu-v12-bridge-ticks`. First retimed v15 candidate
`ryu-v15-retimed-a-10-v0-mmc3` fails at frame5517 in1-2. The diagnostics show
source-held Right lost during native injury engine10 and one active tick5462
requiring A+Right but receiving Right only. There are no multiple-update poll
gaps. This is a host harness limitation: it normally calls its policy only in
engine8. MLS owns a coordinated optional policyAllModes fix for the retimer;
no gameplay RAM/ROM/register writes are involved. Do not accept this failed
candidate or silently ignore the active input mismatch. Every eventual winner
still requires a fixed-CSV independent replay on the final build.

Fresh continuation `lsr-v15-c-10-v0-mmc3` clears 1-2 and 1-3, entering the
castle at frame 10535. New v15 branches `ryu-v15-castle736-a` (frame 11192,
x980/Y112) and `ryu-v15-castle1024-a` (frame 11583, x1450/Y128) each pass
independent cold-boot verification of all 10,240 RAM bytes. Their verified
opaque roots are reused only with the same v15 hash, never across ROM builds.
The next search is `ryu-v15-castle-flames-a`, targeting x2050 before Bowser.

The full retime-A diagnostic also has earlier active input differences at
tick 2064 (expected Right, actual Down), before injury. MLS confirms the early
INC observation can precede another NMI changing the input before its actual
consumption. Its policyAllModes opt-in repairs injury gating but is not a
guarantee of cross-build phase invariance. These are discovery tools; the
fresh routes above remain the accepted partial proofs.

The owned controller policy now tests actual flame/body vertical overlap
before jumping. Native Bowser flames use bbox Y+4..8; Link's body begins at
Y+18, Simon and Ryu at Y+1, and all end at Y+32. The old |dy|<32 test could
jump directly into an otherwise harmless overhead flame. Remaining vertical
travel toward the native target rows (144,128,112,144) is included. This is
controller navigation only, with no runtime ROM change.

The subsequent v15 flame branch `search/ryu-v15-castle-flames-a` reaches
x2050/Y128 at frame/poll11985, and `search/ryu-v15-bowser-a` reaches
x2244/Y80 at frame/poll12164. Both pass independent power-on replay and the
complete10,240-byte RAM comparison. Their opaque roots remain same-ROM only.
Continuation `lsr-v15-e-10-v0-mmc3` stalls at the right wall because the test
controller keeps holding Up, repeatedly wall-climbing instead of falling
onto the axe. This is a policy failure, not evidence of a game softlock.

The next controller-only continuation, `lsr-v15-f-10-v0-mmc3`, releases that
wall input and settles at x2248..2251. It genuinely activates the axe and
enters2-1 at frame13072, preserving the full unbroken power-on input stream.
It then stalls at x369/Y112 beneath the first staircase's brick ceiling and
eventually times out in-game. No2-1/2-2 clear is claimed. The first-mushroom
routine is already limited to world0/level0 and did not cause this stall.
Local staircase search `search/ryu-v15-21-stairs-a` starts at poll13280.
It wins at frame/poll13519, x681/Y176, and its independent fresh power-on
replay agrees in all10,240 RAM bytes. Continuation is `lsr-v15-g-10-v0-mmc3`.

There is also a new native graphics concern in the Bowser encounter. The
actual `lsr-v15-d` screenshot shows background-like tiles in Bowser's body.
Static analysis of the independently verified Ryu endpoint's OAM and mapper
shadow (`build/checkpoint-tests/bowser-chr-probe.json`) finds bank1 logical14,
physical2, with SsChrActive=0 and ReloadCHRBank=0. Its predicted PPU$0c00
native Bowser pairs differ from the MMC5 sprite source. This is a diagnostic
finding pending a direct PPU read and an independently confirmed pixel
oracle, not an implemented asset correction or a completed regression.

The graphics finding is now directly confirmed: a read-only diagnostic loads
the already verified opaque same-ROM Ryu endpoint and reads mapped PPU bytes
at$0c00 on the next foreground update (player x2245). All eleven Bowser pair
differences remain. `build/checkpoint-tests/bowser-direct-ppu.json` and its
1KiB `bowser-actual-ppu.bin` preserve this graphics inspection; it supplies
no new traversal proof. The native MMC5 sheet and the existing MMC3 castle
sheet contain all correct pixels, so no asset converter is needed.

The parent-approved source correction changes only MMC3 definitions in
`src/metasprite.s`: Bowser uses SPRITE_BANK_3 with local index+8; Toad and
Peach use their existing exact pairs in SPRITE_BANK_2. MMC5 definitions are
unchanged. No runtime instructions, RAM or CHR are added. The independent
`native-castle-source-pixels.lua` fixture compares completed DMA OAM/actual
mapped PPU pixels against the local authoritative native sheet for the four
Bowser fragments, Toad and Peach in both facings, including their palettes.
On immutable v17, MMC3 fails the first exact Bowser pixel and the unchanged
MMC5 control passes all12 cases. Copied ROMs and unique logs are preserved
under `build/checkpoint-tests/native-castle-v17-{negative,control}`. Positive
checks await the parent's next assembled checkpoint.

Parent-built v18 passes those12 native actor pixel cases on both mappers.
MMC3 SHA256: `9c62290a9c1218bddeb789c3a83c02db56ad1f04e70c5697e9f73fe8cf15dfd4`;
MMC5: `f9deeae365066795722be8628554ec143b95c28bcf9a1b9a52aee509a5bee8d4`.
The fixture is now extended with Bowser's native24x16 flame. Its old three
MMC3 indices also address body pixels; the existing castle source has the
correct flame pairs at file offsets$74/$76/$78. This related correction is
pending the same explicit v18 negative/control check and parent integration.
The eventual complete fixture has14 cases, with the flame's intentionally
fixed left-facing artwork checked under either object-facing flag.

This extended v18 negative is preserved in
`build/verification/native-castle-v18-flame-audit/summary.json`: MMC3 passes
the first12 actor cases and fails only at BOWSER_FLAME facing1 pixel1; MMC5
passes all14 cases. The three flame data bytes now use the same native
Bowser bank/shift constants. Source is ready for the parent's next build;
the positive remains pending. No additional graphics/code/RAM bytes appear.

Ryu's next genuine route `search/ryu-v15-21-pipegap-a` starts at poll14390
and lands x1847/Y144 at frame/poll14596. Independent fresh power-on replay
matches all10,240 RAM bytes. It solves the pipe-edge jump that the generic
controller launched too early; no runtime traversal defect was demonstrated.
`lsr-v15-h-10-v0-mmc3` continues from its winning ordinary input CSV. The
full six-stage clear and frozen latest-build replay remain outstanding.

Continuation H reaches x2772 in2-1, then its generic crouch attack loses to
a hopping Koopa. Local `search/ryu-v15-21-turtle-a` instead reaches x2980/Y176
at frame/poll15598. Independent power-on replay again compares all10,240 RAM
bytes successfully. Ryu's best genuine v15 prefix is now this winner.
`lsr-v15-i-10-v0-mmc3` continues it with a controller-only spring routine:
align at x3008, release landing A, press fresh A during native compression
states2..4, then cross the tall wall. This geometry came from MLS's actual
native2-1 route. The controller also keeps Ryu's standing sword for airborne
targets above him, rather than always selecting the lower crouch sword.
Neither change alters ROM state or code. No full2-1/2-2 clear is accepted yet.

The native actor correction keeps ROM instructions and table sizes unchanged,
but encounter timing can still improve: MMC3's renderer now takes the odd-tile
branch rather than checking table0 sprites against the HUD. Old controller
streams must therefore be replayed on the final checkpoint, as with every
other source change. No cross-build state equivalence is claimed.

I/J do not clear the spring. I hangs on its side at x2993/Y163; J adds Up
and reaches a repeated deep foot/side contact at Y149. This uses old v15
collision code; the parent has since changed GuestFootContactSide, so no
duplicate runtime fix is proposed. `search/ryu-v15-21-spring-a` was stopped
for the higher-priority origins investigation. Its grounded goal at x3100,
Y<=32 was beyond the tall wall and unsuitable. It has no accepted winner or
independent best verification. Do not use it as traversal evidence.

The full v17 suite exposed `ryu-projectile-origins` failure. Unique-stem
reproduction B fails before any Select, case1/age1, with RgShotType0 and
CurrentBank61. The test attached only a CPU address, which aliases unrelated
PRG banks. Actual RyuProjectileOrigin/Done live in ROSTER bank22, confirmed
by both debug segment offsets180240. The fixture now guards both callbacks
against that bank. All opposite-input, muzzle, direction, kind and exact
one-launch assertions remain intact. Both immutable v17 mappers pass all40
actual Select cases; no runtime origin code changed. Evidence is in
`build/checkpoint-tests/ryu-origin-v17-investigation/guarded-summary.json`
and the unique `smb-crossover-{mmc3,mmc5}-ryu-origin-v17-guarded` logs.

The native-castle fixture's object-authoring callback likewise now requires
the actual renderer bank4. Its v18 MMC3 flame-only negative and MMC5 fourteen-
case control are unchanged with that scope; unique copies are in
`build/checkpoint-tests/native-castle-v18-guarded`.

Latest-build port candidate `lsr-v18-a-10-v0-mmc3` uses ordinary input only.
It matches the old v15 full movement/power/engine trace through frame6520,
clearing1-1 and most of1-2. First difference at6521 is x2181->2182 and an
NmiSkipped4->5 transition at the final stairs/lifts. The old fixed tail then
dies at6683. It is not an accepted v18 route. New same-ROM search
`search/ryu-v18-12-tail-a` starts from that actual v18 run at poll6500 and
targets the ordinary sidepipe approach x2616, grounded Y128..176. No opaque
state or decoded bytes are transferred from v15.

The new v18 tail independently wins at frame/poll6828, x2617/Y128, with all
10,240 RAM bytes identical from power-on. Continuation `lsr-v18-b-10-v0-mmc3`
clears1-2 and1-3 (entries7999 and10439), then dies at the first castle firebar,
x741/frame10894. `search/ryu-v18-castle736-a` resumes its actual v18 input
stream from poll10790. The old v15 late2-1 root remains useful geometry but
is never loaded into this build.

Both callback fixture corrections now also exclude nested NMI and IRQ via
actual interrupt-entry/RTI scopes. Ryu origins still pass all40 launches on
both v17 mappers; native v18 still passes all12 corrected actor cases before
the known pending MMC3 flame failure, while MMC5 passes all14. Exact ROM/test
hashes are in `build/checkpoint-tests/lsr-foreground-guards/summary.json`.

The v18 first-firebar branch independently wins at x980/Y112 (its target
and full power-on/all-RAM proof are in `search/ryu-v18-castle736-a`). This
prefix is still v18 evidence. New candidate `lsr-v19-a-10-v0-mmc3` proposes
its ordinary input stream to immutable v19 from power-on, without state loads.

Both v19 mappers now pass the complete14-case native castle pixel fixture,
including the corrected flame, and all40 Ryu origin cases with foreground
bank plus nested NMI/IRQ exclusion. Unique copied ROMs, logs and exact hashes
are in `build/verification/lsr-v19-focused/summary.json`. MMC3 ROM SHA256 is
`1f36f4c2d7d1c82d73b737623c953735cf45455480933a822f4e90946c3bd71b`;
MMC5 is `228adb0a0b65af9a9df42a9dd0ea039ddc43ab33167a72eaa834725f71d596e5`.
All owned runtime source corrections are integrated and positively checked.
Full controller clears/latest final replays and recordings remain unfinished.

The v19 candidate preserves all first-three-stage entries (1-2 at4574,
1-3 at7999, 1-4 at10439) and reaches x980/Y112 at11106 using that proposed
ordinary stream. Generic continuation then dies at x1028/frame11138. New
same-ROM `search/ryu-v19-castle1024-a` starts at poll11106 and targets the
next bank x1450/Y48..160. No final clear or video is claimed.

That branch independently wins at poll11505, x1450/Y128, grounded, on v19;
all10,240 RAM bytes match a fresh full power-on replay. New same-ROM
`search/ryu-v19-castle-flames-a` extends this verified endpoint toward x2050.

The flame-section extension independently wins at poll11927, x2082/Y128,
grounded. Its screenshot also displays the corrected actual native flame and
Bowser artwork during ordinary traversal. `search/ryu-v19-bowser-a` continues
from this exact same-ROM root toward x2244/Y48..144, allowing an airborne goal.

The v19 Bowser branch independently wins at poll12032, x2244/Y78, with exact
all-RAM cold-boot comparison. Actual continuation `lsr-v19-b-10-v0-mmc3`
releases wall-climb input and reaches2-1 at12920, then stalls at the first stair
bank x369/Y112 until death. This is a controller-policy limitation, also seen
on v15; no new gameplay defect is inferred. `search/ryu-v19-21-stairs-a` starts
from its actual v19 stream at13128 (x354/Y119), before the stall, targeting
x681 grounded. Builds20/21 are deliberately excluded from route work because
root/MLS confirmed a separate temporary guest-physics dispatch regression.

The first2-1 stair branch independently wins at poll13386, x709/Y176, grounded;
its power-on replay matches all10,240 RAM bytes. Candidate `lsr-v19-c` continues
with a controller-only fix: when the Ryu wall controller requests Up and a
fresh A/release, `finish` no longer replaces that release with the remaining
ground-jump A hold. Gameplay source is unchanged; this tail is not yet proof.

That candidate reaches x1736 before falling at14289: it lands on the narrow
pipe at x1659/Y112 while still holding A, then steps off before a new edge.
A broad release-on-every-landing experiment (`lsr-v19-d`) instead launches too
early from the previous cap and falls at x1503; it was reverted. The retained
policy change only respects Ryu's wall-controller release. New same-ROM
`search/ryu-v19-21-pipegap-a` starts from the real `lsr-v19-c` stream at14235,
just before the x1659 landing, and seeks x1847 grounded. No ROM bug is claimed.

The v19 pipe-gap branch independently wins at x1847/Y144, grounded, with exact
power-on/all10,240 RAM comparison. Route work then yielded to root's full22
Windmill failure investigation. The unique-stem negative trace proves that an
unguarded $B126 exec callback fires in physical bank61 (MMC3 register7=61,
opcode$D0) as well as real ROSTER bank22 (register7=22, opcode$AE). At frame565
the false foreground entry advances the host oracle between real ages3/4,
causing exactly the reported6.027786/6.347222 discrepancy. Interrupt depth is0
in that occurrence. `tests/ryu-source-weapons.lua` now excludes unrelated banks
and nested NMI/IRQ execution; all source equations/tolerances, actual muzzle,
45ms launch, total updates and catch assertions remain, with extra exact-one
launch/nonzero motion checks for each direction. Both immutable22 mappers pass.
Evidence: `build/verification/ryu-windmill-v22-investigation/guarded/summary.json`
and the `mmc3-unscoped-c/callback-trace.csv` negative. No runtime edit was made.

## v22 shared flagpole fixture investigation

The old full-pool4-1 fixture teleported the actor to poleX-25 while preserving
the far-left native camera, starting at screenX247. Physical-bank/interrupt
traces prove its parser hooks were genuine. At the22 pole contact Ryu is
worldX3593, camera3366; engine5 clamps him at worldX3605/screenX239 on the
flag baseY160. ScrollLock prevents camera movement until he steps off, so this
incoherent setup reaches the watchdog. The same17 fixture falsely passes by
wrapping worldX3593 to the left edge3351, then walking back across the room.
Both negative/false-pass traces are preserved under
`build/verification/flagpole-v{17,22}-investigation/ryu-mmc3-unscoped`.

The corrected shared `tests/flagpole-common.lua` retains native camera, edges,
scroll mirrors and parsed terrain. It starts the visible approach at poleX-160,
Y48, checks the full body is clear of native metatiles, and approaches using
ordinary controller inputs. Existing full-pool allocation, contact, castle/time
conversion, next-room control and2200-frame watchdog requirements remain.
Added foreground interrupt guards and opcode checks,16px maximum displacement
per completed gameplay update, and a poleX-16 lower bound through slide/walk
prevent the prior left-edge false pass. A Bass diagnostic also demonstrates a
low contactY162 setting engine4 then advancing5 within one update; the contact
latch now observes the actual guarded resident FlagpoleCollision entry rather
than depending on its physical-frame duration. That trace is preserved under
`flagpole-v22-investigation/bass-mmc3-approach-b`.

The coherent-b run passes13 MMC3 profiles; Scrooge's one-poll A only makes a
four-pixel hop, so ordinary A is now held through his ascent. The final
all14-profile/both-mapper run passes all28 cases with the strict completed-
update bounds and contact/watchdog assertions. Unique copied ROMs, logs and
consistent fixture/ROM hashes are under
`build/verification/flagpole-v22-coherent-c/summary.json`. No runtime camera or
physics change was made for this fixture.
The shared fixture SHA256 is
`b3421f1a8fa677636ba28cafb592237af87c599bda2e5046be03d7c4d8e0498f`.
Immutable22 MMC3 is
`2ec13bcac6c9c60a37096b0b5e2377c771c345b54325dd26c602c8cfc059debf`;
MMC5 is `3bdf2fabe064b47c4c53660ec525afd12c693e28aa521b55fe5c03981f3e5cb4`.
The17 left-edge jump was242 pixels (3593 to3351), now caught by the16px bound.
The guarded Windmill fixture SHA256 is
`f5c52644ebb8df90fc929f783fc1e78a4689f41266646bd4a7c109bbdb8061c2`;
its original source equations, tolerance and actual weapon lifecycle assertions
remain intact. Root retains the original full22 failures alongside these
corrected-fixture reruns for acceptance.
Root approved subsequent Ryu route discovery on immutable22 by proposing the
archived19 ordinary input CSV from fresh power-on; opaque states stay with19.

Actual22 candidate `lsr-v22-a-10-v0-mmc3` reproduces all14,765 gameplay
position/state/engine/power frames of19's `lsr-v19-e` exactly, with a different
NmiSkipped counter. It reaches2-1 at12920 and the same hopping Koopa death at
2348/frame14765. New same-ROM `search/ryu-v22-21-koopa-a` starts from its own
actual input stream at14705/x2304 before that encounter, targeting x2640.
No final22 clear or video for these three owned characters is accepted yet.

That Koopa branch independently wins at poll14940, x2641/Y176, grounded, with
exact power-on/all10,240 RAM comparison. `lsr-v22-b-10-v0-mmc3` continues from
this22-only proof toward the spring and2-2. The archived19 roots are retained.

The generic continuation dies at x2650/frame14957 to the next hopping Koopa.
`search/ryu-v22-21-lastkoopas-a` uses the exact verified22 root at14940 and
targets x2980/Y144..176 grounded before the spring. Root accepted22 after its
full suite plus the independently preserved fixture-only corrections; no new
production edit or cross-ROM opaque-state reuse is involved.

That last-Koopa branch independently wins at poll15193, x2980/Y176, grounded,
with exact power-on/all10,240 RAM comparison. `lsr-v22-c-10-v0-mmc3` continues
from that frozen22 proof to the actual native spring and last tall wall.

For the pending Ryu water navigation, pinned `Ryu.as:942` only starts a normal
jump from onGround (or a valid wall jump); base `Character.pressJmpBtn` only
sets the button and spring boost. Water sets jump power400 and gravity500 in
the original Flash units. Repeated A in free water does not grant a Mario
swimming stroke, so the controller uses floor jumps and legitimate wall moves.

`lsr-v22-c` genuinely lands on the spring at3009/Y146, receives the native
boost, then clings at the tall wall3025/Y39 because the helper's cross phase
only held Right. The controller-only cross phase now uses Up and a clear
source wall-top fresh-A edge. `lsr-v22-d` clears2-1, enters2-2 at16536 and
reaches1184 before an enemy hit at17354. New same-ROM search
`ryu-v22-water1180-a` starts at17280 (~1070/Y50), targeting1550/Y32..176 with an
airborne endpoint allowed. No full2-2 clear or final recording is claimed.

The water branch independently wins at poll17661, x1551/Y127, state1/power0;
its fresh power-on replay matches all10,240 RAM bytes. This proves the entire
spring/wall/2-1 exit and water entrance sequence. Candidate `lsr-v22-e` resumes
from this22-only prefix. After a full candidate clear, root requires a fixed
zero-death full-audit replay, then coordination for exclusive native capture;
the checkpoint itself is already accepted and needs no new approval.

`lsr-v22-e` dies to an enemy at1617/Y121, frame17712, while crossing the next
water obstruction. New same-ROM `search/ryu-v22-water1617-a` starts at the
verified17661/x1551 root and targets x2000/Y32..176 (air allowed). No source
defect is inferred from a failed controller continuation.

Root's separate Pit route established useful later2-2 terrain landmarks:
lower coral2064/Y112 then stem2096/Y0; far coral cap around2516/Y48 followed
by the2612 cap. Those are terrain hints only. Ryu must use his own legitimate
wall/top jumps and independently verified input sequence, never another ROM
or character's opaque state.

That second water branch independently wins at poll17986, x2000/Y142,
state1/power0, with exact fresh-power-on inputs and all10,240 RAM bytes.
Ordinary candidate `lsr-v22-f` resumes from this22-only proof. Root has held
future final captures while a separately observed Pit corner snap is diagnosed;
read-only route discovery and proof continue on the accepted22 checkpoint.

`lsr-v22-f` crosses the2064/2096 coral platforms using Ryu's legitimate wall
moves, then dies to an enemy at2299/Y98, frame18232. Its rendered endpoint
shows the underwater enemy contact. Search `ryu-v22-water2299-a` reuses the
verified17986 root on22 only and targets2460/Y32..176, with attack and timing
alternatives. This remains partial controller discovery, not a complete clear.

The broad2299-a search did not win (4914trials/depth36); its independent best
replay only verifies a2095/Y160 alternative and is not forward progress.
Scoped2299-b instead takes the already controller-attained18192 approach in
`lsr-v22-f/inputs.csv` from fresh power-on, targeting2440 with8-poll attack
timing. The practical final pipe landmark from Pit is3008/Y112: approach the
wall from the floor around2935, jump, drop to its side entrance, then hold
Right with A/Down released. That is a terrain hint, not a transplanted state.

Scoped2299-b independently wins at18332, x2440/Y70, state1/power0, comparing
all10,240 RAM bytes from fresh power-on. Candidate `lsr-v22-g` continues from
that prefix. Its controller policy now handles the final pipe's Ryu-specific
grab: launch from the real floor near2935, use source Down climb while grabbed
above Y112, then Right into the native Y112 opening. Unlike Pit, Ryu's source
wall attachment sets vy0 while Right is held, so merely releasing Up cannot
make him fall. This is controller logic only; runtime source is unchanged.

`lsr-v22-g` reaches the pipe2993 without injury after both final coral caps,
but the initial helper stopped Down atY80; Ryu remained correctly attached
there until the candidate watchdog. The helper now continues real Down to
Y112. `lsr-v22-h` retests that ordinary controller correction. Root's new23
candidate adds a separately confirmed Pit-only crouch-clearance correction;
after a full22 clear the entire ordinary CSV can be proposed to23 from fresh
power-on, never by transplanting an opaque state.

`lsr-v22-h` clears all six stages and reaches controllable2-3 at20065, zero
deaths. It is a discovery candidate, not yet a strict accepted replay.
The full fixed CSV proposed from fresh power-on to provisional23 diverges
first at6683 on1-2's moving lifts:22x2393/Y66 versus23x2392/Y63. It eventually
falls in1-3 at10925. Its full read-only telemetry review has zero HUD split,
lag-CHR or unconfirmed audio-owner/write candidates, but it has no recorded
video. `ryu-v22-control-full-audit` checks the exact same CSV on its original22
build to separate cross-build timing from any export/replay fault.

A read-only motion scan of the full22 candidate finds twelve isolated -9px
right-wall corner corrections (frames1232,1378,3169,3274,3331,4893,5984,6239,
6532,9179,9601,13135), without any +16px zip. At1232, x442→433/Y148→149 with
Right+A under the1-1 brick edge; the full-side clamp aligns to tile448.
These are reported for visual/source review, not yet classified as defects.

The strict22 control PASSES at20065/poll20064, zero deaths, with
`verified_through_2_2=true`. Full telemetry review finds0 HUD-split candidates,
0 lag-CHR changes and0 unconfirmed audio events (3760 source events have voice
and physical writes). It records1751 gameplay lag hardware frames and881
sprite-overload frames; those counters are evidence, not a claim of lag-free
play. Twelve -9px collision corrections remain visually/source classified.
No native video/audio has been recorded yet. Provisional23 was subsequently
rejected by root's separate Pit ground-tunnel regression, so no23 retuning is
being pursued. Root prepares24 while preserving the ordinary non-Pit path.

Bounded read-only power-on observation
`build/verification/ryu-wall-corner-v22-observation/` captures eight actual
PPU frames1229..1236 and foreground wall-entry/X-write PCs, excluding NMI/IRQ.
It identifies the first -9 correction as the1-1 pipe top corner, not a brick:
pre-endFrame1231 fixed-bank PC$EA28 writes x443→433/Y149. Smaller436→433
clamps recur while Right+A hugs pipe448; the frames show one left correction
followed by normal wall poses. `Character.groundOnSide()` explicitly snaps
nx to wall minus half width. No false direction, solid pass-through, +16 zip
or exact source mismatch is demonstrated, so no production fix is proposed.
The original trace's final eight scratch columns sample raw addresses00..07;
derived `corner-addresses.csv` only corrects those labels tozp00..zp07 and
`column-labels.json` binds original/derived hashes. Original rows are preserved.

Root released immutable provisional24, MMC3
`36dad7ac1bcdd9f87e80345fb767e99d46d042115c229366bca668d598337214`.
Fresh fixed `ryu-v24-full-audit` matches22 position/state/camera through18751,
including all five dry stages. Its first difference18752 is near the water
exit:22x2898/Y93 versus24x2897/Y96. The old timed pipe/outdoor tail then arrives
at different moments, stalls on the outdoor stairs, and exhausts its complete
fixed stream at20065 without a death. That is not a latest-build clear.
`lsr-v24-a` keeps the ordinary prefix through18720 (masks unchanged, hashes in
`prefixes/ryu-v24-exit18720.json`) and resumes state-aware real controls for
only the final pipe/outdoor tail. No opaque state crosses ROMs.

`lsr-v24-a` clears all six stages, zero deaths, and reaches2-3 control at20065
again. It changes only the ordinary final pipe/outdoor controller tail after
18720. Fresh strict fixed `ryu-v24-final-proof` replays its complete24 input
CSV with the full read-only audit. The build is still provisional and capture
remains held pending root's Pit regression and broad-suite acceptance.

Fresh strict `ryu-v24-final-proof-10-v0-mmc3` PASSES all six stages, zero
deaths,20064 exact controller polls and2-3 control at20065. Its telemetry has
0 HUD-split,0 lag-CHR and0 unconfirmed source-audio ownership/write candidates
(3750 physical events),1749 gameplay lag hardware frames and881 overloaded
sprite frames. It preserves the same12 corner corrections already examined.
Final native capture remains held pending24 acceptance. The exact24 input
is `lsr-v24-a-10-v0-mmc3/inputs.csv`;90 masks differ from22, only18721..19260.

Link24 discovery: archived12 castle CSV is obsolete by1-1, dying to an enemy
at1972/frame3032. Fresh ordinary policy `link-v24-b` collects the real mushroom
and reaches2444, then falls in the ordinary1-1 gap at3100. The shared stair
helper brakes too late for Link's old24 ROM inertia: x2434→2449 while Left is
held during landing. New `search/link-v24-11-stairgap-a` branches from the
actual fresh24 input3030/x2399 approach, targeting2640. This is controller
retuning; no source physics edit or cross-ROM state is used.

The temporary predicted-stop controller works around24's inertia and clears
1-1, entering1-2 at4708. `link-v24-c` then misses the native descending lift and
falls at2312/frame7396. Its real7290 stair input root independently wins
`search/link-v24-12-lifts-a` at7482, x2450/Y117, with all10,240 RAM bytes equal
from fresh power-on. These remain archived24 geometry/baseline proofs only.

### Link2.02 horizontal movement migration pending next build

Reading pinned `reference/crossover2/extracted/scripts/com/smbc/characters/Link.as`
615..672 disproves the earlier source-inertia description. `movePlayer()`
immediately assigns vx±175 for valid directional input, zero for neutral/both,
and zero during a grounded attack; airborne attacks retain normal direction
control. `Character.as`1159 calls checkBtns then movePlayer, followed by its
underwater-ground-only90 cap at1214. No later horizontal acceleration stage
applies. The earlier78-rule contract intentionally used hosted1.0 Link, whose
coasting rules differ; those observations must retain their original version.

Root authorized the migration to2.02. Only LinkMove/LinkWalk in `roster.s`
now assign signed Q16 round((175/120)*65536)=$017555, stop instantly, and apply
the shared90/120=$00c000 underwater-ground cap. Bill/Simon ImmediateInput,
common MegaManMovement and shared vertical/jump/hurt dispatch stay unchanged;
no RAM or asset allocation is added. The temporary controller momentum
workaround was removed for future corrected builds. Link's old accelerated
water expectation is changed only for character4, using the2.02 direct cap.

`tests/link-source-movement.lua` independently checks84 combinations of power,
dry/wet, ground/air, start/reversal/release/both and sword state, including
signed source equations, integrated positions and allowed facing changes.
Four explicit hurt-dispatch retention arenas verify that normal input cannot
overwrite an existing hurt velocity; they do not certify full knockback
trajectories. Actual enemy injury/recovery remains covered by the separate
real-enemy fixture. Foreground callbacks exclude NMI/IRQ and validate actual
opcodes; each assertion samples a completed logical update.

Canonical immutable24 negatives are
`build/verification/link-source-movement-v24-negative-c/summary.json`:
both mappers fail the first actual start at0.083328247070312 instead of
175/120=1.4583333333333. Fixture SHA
`97033f0e1f2f1e618c5ad69cf6d8d3ed29790a7f8972878aa9426cbb52ed6266`.
The initial syntax-only attempt is retained separately and excluded; b is an
earlier correct velocity negative before facing assertions. Root is the sole
builder; no post-fix positive or next-build route is claimed yet. All final
captures stay held until the roster's full-audit routes are checked.

Root then chose coherent default2.02 movement for Simon as well, retaining
the explicit native Mario/Luigi and native-game Pit/Rygar/Scrooge references.
Further pinned Link.as288..304 stats differ from hosted1.0: dry jump600,
gravity1300, fall800; water-room jump500/fall500 and submerged gravity500;
springs450/950 and bounce325. `Character.update()` still applies submerged
250 before gravity, and the water-room500 fall cap also applies above the
surface. The source-ready code now changes these Link-only values in
`roster.s`, `megaman_physics.s`, `megaman_environment.s` and the real downward
thrust enemy bounce in `roster_weapons.s`. No RAM or assets are allocated.

Simon.as557 defaults to nonclassic controls because Cheats.as51 initializes
_classicSimon=false and setter350 assigns Simon.classicMode. He sets vx±150
in the air and stops on neutral/both, but movePlayer preserves launch facing
while airborne; fresh/double jump can set facing separately. Existing550
jump,1500/750 gravity,500/1000 springs and uncapped character fall are retained.
Only the scoped Simon horizontal dispatch now follows that default.

`simon-source-movement.lua` shares the independent88-case equation/facing
matrix with Link. `link-source-kinematics.lua` adds27 source-equation cases
across all powers: dry/wet/surface launch, upward release, gravity, fall caps,
integrated positions and rejection of an airborne re-jump. `water-common`
updates only Link's changed jump/dry-gravity/direct-ground rule; `world-springs`
updates only his450/950 expectation and excludes NMI/IRQ from its callbacks.
Canonical complete immutable24 negatives are now
`build/verification/link-simon-v24-negative-d/summary.json`: all eight expected
failures across Link movement, Simon air control, Link vertical profile and
Link springs on both mappers. Shared fixture SHA
`945a7104e019e83e836d5cb6b0e5a39b9a2e1b0c8fe2a092853c091ef1fe31e0`.
No post-migration build or positive is claimed yet; root is sole builder.

Confirmed remaining Link contact gaps are reported to root, without editing
shared collision:2.02 hitEnemy1040..1058 damages unprotected body contact
unless bottom+dThrust or top+uThrust, preserving star/shell exceptions.
Native collision currently routes any descending guest through EnemyStomped
without Link/RgThrust eligibility; surviving thrust hits have no native-stomp
suppression. Actual order is player movement→RosterWeapons→enemy body checks,
so current-frame thrust is available at contact. Source thrustStart856 delays
activation until the next checkState update, while the port activates at once.
Source downward attacks bounce on attackable ground too; upward contacts stop
upward motion; the port only bounces enemy Down hits and imposes18 reset
updates. Stale RgMeleeHits receipts may also affect repeated thrust contacts.
These contact/timing changes await root's shared collision plan. Source Link
takeDamageStart1288 also assigns±500 with32NES travel; the isolated retention
fixture does not claim that native engine10 already implements this trajectory.

### Coherent profile and Link contact batch (unbuilt)

Canonical profile negatives are now
`build/verification/link-simon-v24-negative-e/summary.json`: all ten expected
failures across both mappers. This adds Simon.as819..899's successful ground
and double-jump cancellation of pending whip/throw to the earlier eight.
`tests/simon-source-jump-states.lua` checks24 separate power/water/jump states;
a rejected third jump must retain its pending attack. The old negative fixture
snapshot has SHA`da7a5d274b7e61ba575e56e0af08e92e2147d5219f469f965d02b6d94d47a2a6`.
The new contact preparation changes the movement-entry opcode, so future
source fixtures validate the new actual SelectedCharacter load; the preserved
old snapshots remain the authoritative negative equations.

`build/verification/link-body-v24-negative-a/summary.json` independently
observes an actual unprotected falling Link/native Goomba overlap on each
mapper. Both incorrectly remain in engine8 and turn the enemy into state4,
confirming the native stomp path bypasses source body eligibility and HP.
`build/verification/link-phase-v24-negative-a/summary.json` observes a real
held Down input: both old ROMs activate immediately (`RgThrustReset=0`,
`RgThrust=1`) instead of the source START phase. These are isolated mechanics
arenas, never controller-only traversal evidence.

The scoped contact implementation reserves exactly38 independent SRAM bytes
(28 previous native hurtbox edges, six slot identities, valid mask, previous/
current thrust overlap masks, and same-update receipt). It does not alias
expanded-character movement or NMI audio storage. LinkBodyContact preserves
X/Y and returns carry only for the matching active vertical source side;
root owns the shared native injury/stomp wrapper. Source side precedence is
HitTester.as237..475: previous separation above wins upper corners; separation
below resolves lower corners by current penetration, vertical winning ties;
previous horizontal separation permits a bottom contact only airborne within
STOMP_PADDING15 Flash pixels. Integer NES native edges use <=7 pixels after
half-scale quantization. Wrapped/offscreen cache entries and reused identities
cannot establish a protected side. Native corpse/inert-shell handling and
hostile projectile contacts remain separate. Bowser's actual contacted half
supplies side geometry while its canonical primary owns HP/contact receipts.

Thrust START/END uses a one-update held-direction phase with Up precedence,
release/landing reset, and no invented18-update rebound cooldown. Real Down
contacts use325/120 bounce and clamp penetrated feet; upward contacts cancel
negative VY. Attackable block receipts use four previous/current exact map-cell
keys in16 bytes of the mutually exclusive ordinary sword map; nonattackable
terrain does not produce a sword bounce. New source fixtures cover36 actual
controller phases,104 directional helper-contact arenas, and36 block arenas,
including separation/recontact and native real-brick shatter sound. No new
positive ROM or final route is claimed until root assembles and tests it.

The source dictionary audit found an important ordering nuance: body collision
is synchronous and precedes the separate sword rectangle. Link.hitEnemy clears
C_HIT/L_HIT; Character.hitIsAllowed tests L_HIT only, so a second same-update
sword call is allowed when the rectangle still overlaps. Link's FLASH/STOP/
KNOCKBACK properties do not grant target invulnerability. A one-hit-per-update
virtual/body receipt would therefore be an engine adaptation, not exact2.02
damage. Root has been asked to integrate a deferred thrust-enemy rectangle
after the native body loop so the port can preserve source body→sword order.
Root selected the exact ordering and owns the post-enemy-loop game wrapper.
`LinkDeferredThrust` now rebuilds only the enemy rectangle after all native
body contacts; it does not repeat the earlier block pass. A canonical body
receipt joins Bowser's two native halves without imposing a damage limit on
the separate sword rectangle. `link-source-thrust-order.lua` independently
checks six power/direction arenas in which both source attacks are valid.
Ordinary forward sword contacts also preserve Character C/L across a thrust
transition, in addition to their separate ATK_DCT swing lifetime. The coherent
source/test batch is frozen and declared source-ready for root's build; no
post-fix positives are claimed yet.


### Effect batch and walking-lag steering

V27 all34 prior source profile/contact slots pass;6 full effect trajectories,
long boomerang180 trajectory,18 Link/10 Simon/7 Ryu property cases pass both
mappers. Evidence is in focused-effects-first-c, effects-properties-a/d and
focused-regression-a. Composite Bowser DMA negative both27 mappers is preserved
in effects-properties-b; renderer fix/optimization is frozen in29, positive
pending. Detailed source/art limitations: docs/reference/lsr-enemy-effects-202.md.

Injury source audit/matrices saved as docs/reference/lsr-injury-202.md/json.
Actual28 Spiny negatives all6 slots are in focused-injury-negative-a. Helpers
and5-byte Link endpoint remain unauthored after user walking-lag steering.
Root owns shared injury and outline-cache/menu changes. Current priority is
plain walking/standing0/1/2/4/6 Goombas, both outline settings/mappers, actual
CPU/NMI/render/OAM visibility metrics. First28 Link/MMC5 smoke is complete in
build/profiling/plain-walking-v28-smoke-a; expanded29 comparison is next.
Ryu24 complete route remains historical; latest Link/Simon full routes remain
incomplete. No final captures and no injury parity claim.

### Walking/source-effect checkpoint32 follow-up

The29 renderer positives now pass all16 source-effect wrappers, including
actual Bowser front/rear DMA flash phases. Scoped30 native freeze/empty-pool
optimization passes the14,400-update204-field crowd canonical comparison
against29, with0 differences.31 fixes a demonstrated late-rawB Sophia cache
admission defect and adds the exact zero-effect gate; all48 scoped control
slots pass. Its662 cleanup/deferred arenas retain30 fields byte-for-byte.
Bound packets: `build/verification/scoped-pipeline-v30-evidence.json`,
`build/verification/scoped-pipeline-v31-evidence.json` and
`build/profiling/plain-walking-v29-v30-comparison.json`.

Matched29/30 light probes additionally count physical4014 DMA, actual
DrawAllMetasprites entries and skipped renders across240 scenes. The complete
packet and limitations are in `docs/qa/plain-walking-lag.md`. Six-Goomba
walking remains40Hz logic/20Hz newly drawn sprites; dense lag is not solved.
Latest32 full gameplay/render comparison is complete. Simon's sequential
adjacent-block fixture failure was diagnosed as two state leaks; its corrected
candidate passed both32 mappers and all original fullsuite negatives remain.
No production or frozen-test edits were made during the broad suite. After
root closed that run, the validated Simon fixture was promoted with SHA256
`01c7cb5b7a0bd493a6659b8445ae8c7948b35784fa16a71d3bb1fb3c05dd02f1`.
Root's affected-slot confirmations pass both mappers, retaining all original
negative diagnostics. The consolidated32 component acceptance now covers
all729 unique slots in `build/verification/roster-audit-v32-consolidated.json`.
The latest32 full crowd comparison is complete:14,400 rows and204 gameplay
fields are byte-identical to30, with0 differences. The latest32 light DMA
supplement also passes12 runs/240 scenes. Its physical frame/draw counts
match the independent full observer in every scene.
`build/verification/walking-profile-v32-evidence.json` binds all final profile
packets. Runtime/tests are frozen; no new offscreen implementation is authorized.

An independent read-only analysis of the resident offscreen helper documents
its exact interior return/scratch ABI and7,776 actual-ROM6502 interpreter
positives per mapper: `docs/qa/enemy-offscreen-cost-analysis.md`. No candidate
runtime replacement has been implemented. Injury helpers and current full
Link/Simon/controller recordings remain pending under the performance priority.

### Authorized33 offscreen batch

Root subsequently authorized the OBJECT-only ordinary-enemy helper.98 code
bytes, no FIXED/SRAM growth, baseline unchanged. Both actual-ROM6502 comparisons
pass98,408 cases per mapper; all3,672 actual-emulator caller arenas per mapper
pass and all7,344 functional CSV rows are byte-identical. Source/tests/tools
are frozen. Registered `offscreen-helper-caller`; verify hash is
`1bf8584781eab083df10fd8efa935579eca251ed1d053f62536fbe66905f7a3e`.

The original endFrame-initialized profile exposed controller/setup-phase and
inactive-box leakage after the CPU speedup; its full negative is preserved.
The corrected profiling-only source seeds at actual NoDecTimers after stable
controller receipts, clears inactive boxes and retains every204 gameplay
field. Both complete12-run matrices pass:14,400 rows byte-identical,0
differences, plus37,440 native actor updates per ROM with exact call counts.
Actual DMA and draw counters show gains and remaining dense-crowd limits.
Final packets: `build/verification/offscreen-v33-unit-evidence.json` and
`build/verification/offscreen-v33-crowd-evidence.json`; detailed measured table:
`docs/qa/enemy-offscreen-v33.md`. Parent full33 suite remains separate/pending.
LSR injury migration stays held; current full routes/recordings remain open.

### Provisional34 source injury migration

Full33 subsequently passed731/731 and was accepted; its source archive and
performance evidence remain frozen. The authorized injury migration adds
source LSR live-world recoil/75-update protection, actual wall and ceiling
responses, primary body art, and four source injury/landing cues. The28-arena
motion matrices per character,64 endpoint arenas,16 actual-DMA primary-body
composites, DMC lifecycle, and prior24 source streams pass both provisional34-b
mappers. Fresh33 source-entry negatives and the actual34-a missing wall-bit
negative remain preserved.

The independent body/head query exposed the old one-pixel Link table error:
playable source frames1..38 have top-15, requiring native top17 rather than18.
Root applied that two-byte correction. The source17 fixture remains negative
on b, and final34 passes44 profile queries plus Link motion/roof/head tests on
both mappers. Simon actual landing/head-query lifecycle
passes and needs no artificial grounded-hurt workaround. The legacy native
injury fixture now covers six retained profiles and passes both b mappers.
All source fixtures remain distinct from contiguous controller stage proofs.
Current full Link/Simon/Ryu final-build recordings remain open.

Fixtures/tools are now frozen for root's final34 broad regression. Eleven new
registrations are the ten LSR injury wrappers plus native-wall-corner. Freeze
manifest: `build/verification/lsr-injury-v34-fixture-freeze.json`; focused
packet: `build/verification/lsr-injury-v34-focused-evidence.json`. Every earlier
negative remains preserved. Runtime has no new edits pending in this scope.

The full34 run subsequently closed with749/753 positives and exactly two old
Link fixture failures on each mapper; its fixtures/tools stayed unchanged.
The ordinary body test still expected native engine10. The directional-contact
fixture inherited new LSR recoil/protection across its explicit arenas: a
read-only observer saw helper87 enter with Kind4/Ticks67, then no later contact.
After root closed the broad run, only those two independently validated fixture
migrations were promoted. Direct actual tests pass all four final34 slots,
retaining all104 directional assertions and the1600 watchdog. Evidence and
originals/diffs: `build/verification/link-contact-v34-triage-a`; final rerun:
`build/verification/link-contact-v34-migrated-tests-b/summary.json`.

Read-only follow-up identified source limits beyond the accepted component
scope: normal Simon/Ryu state-dependent HRects still use legacy31/13 tables,
and Simon's actual hurt-ceiling callback selects stand30 rather than retaining
hurt25. Raw matrices, exact state/attack/wall mapping and update-order notes
are in `build/verification/lsr-normal-hrect-readonly-v34.json`; explicit scope
correction: `build/verification/lsr-injury-v34-known-source-gaps.json`. No frozen
runtime/test change was made for these follow-up gaps.

Controller-only final34 progress: Ryu clears1-1 and1-2 and enters1-3 at8232.
`search/ryu-v34-13-first-bridge-a/winning-inputs.csv` independently reproduces
frame/poll9482, X1450/Y112 on an actual moving support, with all10,240RAM bytes
identical. It includes real sword kills for both1-2 Koopas and the1-3 high-cap
Goomba, and ordinary controller traversal of the final lifts. Current tail is
`build/roster-through-2-2/policies/ryu-v34-tail-l.lua`; its candidate output is
`lsr-v34-ryu-tail-l-10-v0-mmc3`. No full six-stage proof or recording yet.

The subsequent ordinary Ryu M/N tails exposed a real final34 defect at the
last1-3 staircase, X2225/Y112. A read-only SRAM observer proves freshA128
reaches normal launch (VY−540/120), then same-update WallAttached clears VY
before integration and native feet restore grounded. Six-poll A holds and
one-poll edges both reproduce it; the native grid above the head is clear.
Pinned Ryu.as groundOnSide requires !onGround && !lastOnGround, which the
current launch/old-side-contact ordering omits. No workaround clear is claimed.
Exact ordinary prefix, observer/grid, physical ROM/PC evidence, zero-SRAM
six-byte patch proposal and outside-suite actual-input arenas are preserved in
`build/verification/ryu-ground-wall-launch-v34-a`. Both mappers reproduce eight
ground/water/stale/ceiling negatives; genuine mirrored wall-away/top launches
retain source300/430 speeds and12/15 locks. Runtime/tests/tools remain frozen
for root's35a broad suite; positive production proof awaits a later root build.

Link's fresh final34 candidate `lsr-v34-link-a-4-v0-mmc3` clears1-1 and enters
1-2 at4839, then dies at the paired-pipe/narrow-pillar gap nearX1945. This is
an incomplete controller route, not a completed six-stage proof. A fresh
ordinary-control branch is investigating that gap; no game-state writes are
used for stage traversal.

Root36a tested the proposed wall-lock1 workaround, but independent review
found that Horizontal also treats that byte as forced facing-directed motion.
The original12-case positive is diagnostic only: an extended20-case fixture
correctly catches all eight neutral/away VX errors on both36a mappers. Root36b
instead skips Crouch/Wall only immediately after a genuine Ryu launch, keeps
the original jumped tracking and adds three code bytes. All20 source controls
pass on both36b mappers. The fixture and before/after case CSVs are in
`build/verification/ryu-ground-wall-launch-v36-extended-a`; no shared test has
yet been promoted for the next broad suite.

The unchanged final34 ordinary prefix on36a diverges at its first neutral
mushroom jump (frame745), reproducing the VX error. On36b the body/camera trace
remains equal through5243, then diverges during a1-2 wall-climb sampling
sequence and later dies before the final stair. Accepted35, without the Ryu
fix, has the exact same first physical-frame divergence and matches36b body
rows through5270. Read-only raw-latch, logical-loop/completion and motion
observers are collecting first-cause evidence; no controller retune has been
used to conceal a possible regression.

Link final34 has further independent ordinary prefixes through the1-2 final
lifts (X2591/Y128, poll7576), the first1-3 high cap (X721/Y32, poll9221, surviving
an actual source injury), and the middle low-cap section (X1107/Y112,
poll9485). Each winning branch replays from cold boot with all10,240RAM bytes
identical. These remain partial routes, and do not claim every enemy was killed
or a six-stage final recording. Policies/proofs stay under uniquely named
`build/roster-through-2-2` outputs.

The passive clock investigation establishes the36b prefix drift at equal
logical tick5212. At input poll5243(mask9),34 is still inside5211 and NMI sees
NmiDisable255, taking the lag path and retaining raw1. The faster build has
completed5211 before that NMI, which sees0 and refreshes raw9. Geometry/contact
at5212 entry match; raw1/9 then produce fresh0/8 and wall VY0/−1. This is an
observed input-sampling difference, not an inferred difference from NMI counts.
Hashes, actual INC/completion receipts, interrupt depth and pre/post motion:
`build/verification/ryu-ground-wall-launch-v36-extended-a/equal-logical-tick-cause.json`.

Link continuation E clears1-3 and enters1-4 at11273 using the actual moving
supports. It then dies at the first firebar corridor nearX744. Continuation F
is attempting the castle's actual question-block powerup with ordinary input
before approaching that corridor. No full2-2 proof or recording is claimed.

Link continuation J collects the real castle mushroom at X497, releases the
powerup/attack input before the bank-edge jump, and survives one real firebar
injury. The next independently verified ordinary branch,
`search/link-v34-castle-second-firebar-a/winning-inputs.csv`, reaches X1171/Y128
at poll12282 with all10,240RAM bytes equal on a fresh power-on replay.
Continuation K then clears1-4 and enters2-1 at13941. It dies at14459,
X648/Y167, descending toward the first paired Goombas. This remains a partial
route; no six-stage controller proof, all-enemy clear or final capture is claimed.
The Samus route's passive existing observer independently locates those enemies
at X636/660, Y184, with the first Piranha at X744/Y120; these are route hints,
not transferred state or claims of identical character physics.

Two additional Link final34 ordinary branches now pass independent cold-boot
position/poll/state and all10,240RAM-byte comparison: early2-1 paired enemies
and pipe to X827/Y176 at14583 (`search/link-v34-21-early-platforms-a`), then the
second pipe/brick bank to X1341/Y48 at15316
(`search/link-v34-21-second-bank-a`). The second Piranha remains active at
X1192 after crossing; no kill is claimed from the point popup alone. Tail M
continues from this prefix toward the native spring. A narrow read-only scan
of tail L found no adjacent active/same-room physical-frame X displacement
above8px; it is not a full logical-update/visual/audio audit.

Root accepted byte-identical36d as immutable36 after its frozen broad run:
758 of759 original slots passed; the remaining Ryu weapon fixture's
single-hardware-frame Select pulse was demonstrably missed on the faster
MMC3 input-sampling phase. After the run closed, the shared fixture changed
to a four-frame single press and all four Bass/Ryu mapper slots passed.
The original negative remains preserved. Runtime36 includes the corrected
Ryu launch skip; no final36 six-stage LSR route or capture is claimed.

Link M reaches the third2-1 pipe near X1960, where a diagonal jump into the
Piranha dies at15952. A passive P policy records RgAttack0/RgThrust2 before
its later15962 contact, so simply holding Up does not make the approach
invulnerable. Source LinkBodyContact protects only a thrust-matching contact
side; the horizontal approach is not a claim of a missing global immunity.
These ordinary failures and controller/latch logs remain preserved, and a
normal wait/jump search is solving the pipe without runtime changes.

The next ordinary branch resolves the third pipe at X2030/Y48, poll16027
(`search/link-v34-21-third-pipe-a`). A subsequent generic high-bank drop dies
on the green Koopa near2151; the separate existing Samus RAM observer confirms
that actor/position as a route hint. `search/link-v34-21-middle-span-a` then
independently reaches X2320/Y176 at16226 with all10,240RAM bytes exact. Both
are genuine same-ROM controller histories; reused opaque roots are only
discovery accelerators, and each winning stream still replays from power-on.
TailR is approaching the late pit and spring, not yet a six-stage proof.

Link now has a full real2-1 clear in its current34 controller history. TailT
aligns to spring center3008, releases A during compression1, presses from
compression2 and holds A through the actual boosted tall-wall crossing.
Playable2-2 begins18133, with no deaths. Its old generic attack-spam/short
jump policy stalls at the first tall coral; tailU waits for RgAttack0 and holds
a real source water jump100polls. It reaches the observed water apexY53 from
floor176, then its always-Right path overshoots the narrow first cap and dies
at1122. `search/link-v34-water-first-coral-a` solves the landing/next-jump
sequence and independently reaches1270/Y128 at19221, comparing all10,240RAM
bytes from power-on. TailV continues; the final water exit is still pending.

A passive observer piggybacked on the ordinary LinkS prefix confirms functional
FirebarPartCount reads for slots0..2 one frame before their first producer.
The exact PC/bank/opcode, flags/ID, producer order, archived34 sources and raw
CSV are retained in `build/verification/firebar-first-producer-v34-a`.
Counts are0 in this deterministic power-on, so no garbage sprite is claimed.
Slot3's first bus read is instead an indexed-STA dummy read, explicitly
classified separately. No runtime change was made; a three-byte common
InitShortFirebar initialization proposal is saved unapplied for root review.

The second water branch independently reaches1644/Y176 at19490, including
ordinary sword/thrust controls around the Blooper/coral encounter. Bridge
helper failures were controller-policy errors: X never initiated its floor
jump, while Y borrowed Samus's Y<=0 target that Link's source waterline/dry
gravity transition does not reach from112. Link's held jump peaks nearY4..5.
Z starts Right atY<=32, then native feet collision grounds Y4->0 at
X2092->2094 and later Y32 on the long upper row. That near-corner landing is
explicitly retained for review, not a claim of exact source terrain collision.
Z proceeds to the late coral2481 and dies on an enemy at21050; the new
`search/link-v34-water-late-corals-a` is solving the lower-cap landing and
next jumps with ordinary input. No runtime/test/tool edits were made.

LinkAA completes the water pipe with only Right held: engine2 begins3010/Y112
at20753. Its complete ordinary candidate reaches playable2-3 at21968/control
21992. Separate fixed replay
`lsr-v34-link-fixed-full-audit-a-4-v0-mmc3` returns exit0 and
verified_through_2_2=true with full_frame_audit=true, zero deaths and identical
fixed CSV. The complete OAM, render, CHR, audio-event, scroll and movement
telemetry is retained; the resident stomp audit reports zero illegal guest
contacts and zero opcode mismatches. This proves the34 route only. It does not
claim every enemy/powerup was collected, final visual/audio recording review,
or replay equivalence on a later CPU build.

The full fixed Link trace was additionally scanned read-only for adjacent ordinary
engine8 same-room displacement: all21,992 rows contain0 horizontal steps over8px
and0 vertical steps over16px (room/engine transitions excluded). The bounded
report is `build/verification/link-v34-full-trace-movement-review.json`; it
does not replace manual frame-by-frame video review. The4px bridge landing
remains documented. Simon34 now starts fresh ordinary-controller discovery.

Fresh Simon34 ordinary discoveryA repeatedly jumps before lining up below the
first question block and eventually times out; this is a controller-policy
sequence, preserved as negative. Owned policyB begins first-power alignment
at280 instead of320, collects the real mushroom (power1 at1093), survives
source injury nearX2000 and reaches the late1-1 Goomba pair before death at
X2738/frame3328. Branch `search/simon-v34-11-late-enemies-a` begins from the
genuine B controller prefix atpoll3100; no runtime changes were made.

Simon branch `search/simon-v34-11-late-enemies-a` reaches2908/Y144 at3421
with ordinary controls. Its winner independently replays exact polls, frame,
endpoint and all10,240RAM bytes from power-on. CandidateC continues that
fixed prefix with the owned B policy; no complete six-stage proof yet.

SimonC clears1-1 and enters1-2 at4751, then its repeated generic double jumps
remain against the first underground vertical brick face at977 until the
clock expires (death14382). Ordinary branch search from5745 has already
moved past that face; the failed trace is preserved. A confirmed runtime
brick-damage defect has not been demonstrated by this policy stall.

Simon first-wall winner reaches1200/Y176 at6013 and independently matches all
10,240RAM bytes. D continues through the last underground stair at2179/Y112
but leaves the descending lift and meets a floor Goomba near2424 at7398.
The separate `simon-v34-12-final-lifts-a` search uses the real7088 stair
endpoint and targets the upper exit. A read-only C trace scan finds no
ordinary same-room engine8/task3 horizontal step over8px; report
`build/verification/simon-v34-c-large-x-review.json`.

Simon final-lifts branch reaches2590/Y128 at7421; its independent cold boot
again matches all10,240RAM bytes and exact polls/endpoint. CandidateE applies
the normal no-A side-pipe approach from that stream. This remains a partial
34 proof; no final recording or later-runtime replay is claimed.

SimonE clears the normal1-2 sidepipe and reaches1-3 at8660. The generic late
jump at630/Y96 contacts the high cap underside, so it falls beneath that
cap and dies737/Y245 at9218. The new high-cap branch starts from grounded
596/Y96 at9105 to test earlier ordinary double-jump positioning. This is
a preserved failed controller approach; no new runtime defect inferred.

Simon high-cap winner independently reaches723/Y32 at9222. F then makes an
unnecessary above-viewport second jump and overshoots the lower cap, falling
to869/Y249 at9339. Owned G supplies only Right between720 and840 to test
the natural drop, then resumes the ordinary policy. This changes controller
planning only. Five inactive SimonA..E duplicateDBG files were losslessly
gzipped with decompression verification; all ROMs/CSVs/failure receipts and
certified search roots remain, saving57,088,950 bytes.

SimonG naturally lands the lower cap near796/Y176 and crosses the next gap.
It later walks to1110/Y176 then jumps too late under the low cap1136..1184,
falling1201/Y241 at9604. The new middle-low-cap branch starts from genuine
poll9495 before that approach, targeting a real grounded1165/Y112 landing.
No latest-runtime six-stage Simon replay is claimed.

The middle-low-cap endpoint1165/Y112 at9575 is exact but its ordinary H
continuation dies at9586/X1178/Y123. Offline verified-RAM decoding identifies
a RedParatroopa (ID0F) at1184/Y141; the Goomba is farther1250/Y72. Thus the
earlier casual Goomba identification was incorrect. The safe continuation
search now returns to G9495 and targets1450, requiring survival beyond that
contact. The short proof is retained without calling it a safe route.

The farther Simon bridge branch independently reaches1450/Y112 at9804,
matching all10,240RAM bytes. It survives the earlier flying-enemy encounter.
Owned I observes native48px platforms, centers on actual support and waits
for a conservative24px gap before an ordinary jump toward bank1568.
No controller state, actor state, RAM or ROM is patched for traversal.

SimonI crosses the actual moving bridge after waiting on its support, landing
on static bank1576/Y144 at9950. A later raised-cap enemy encounter ends at
1694/Y80/frame10051. New second-bridge search starts from grounded I9949
and targets1900 with stationary B/AB timing choices included. I remains a
candidate; the last independent prefix is the9804 bridge proof.

The second-bridge branch independently reaches1900/Y112 at10209, all10,240
RAM bytes exact from power-on. J continues this genuine controller prefix
toward the final stair and pole. The earlier I failure remains retained.

SimonJ clears1-3 and enters1-4 at11541, then dies at the first firebar. The
new firebar branch independently reaches1170/Y128 at12506 with all10,240
RAM bytes exact, surviving both bars. K continues toward Bowser. The full J
trace scan has0 horizontal steps over8px during ordinary same-room engine8
/task3 adjacency; bounded report `simon-v34-j-large-x-review.json` is not a
final visual/audio clean bill. Shared runtime/tests/tools remain untouched.

SimonK reaches the later lower/upper firebar pair, where an ordinary jump
contacts a pellet at1368/Y108/frame12690. New late-firebar search starts
from the same-ROM independently certified12506 root, targets1750 and adds
real Down+A input options. Discovery may load that opaque genuine root;
every winner still requires independent fresh power-on replay/allRAM match.
Root39a broad suite is frozen; no shared source/test/tool edits here.

The later firebar branch independently reaches1854/Y128 at13106, matching
all10,240RAM bytes. L reaches Bowser before the axe and dies2206/Y115 at
13406 after jumping beneath his airborne body. Bowser search starts from
the real L13239/X1999/Y128 approach. These are ordinary controller histories;
no enemy/player state or collision rule was changed for traversal.

Bowser winner reaches2257/Y48 at13626 with all10,240RAM exact. M drops
left onto the axe, enters real2-1 at14535, then lands into the early Goomba
pair. N walks off the first high brick bank without an unnecessary double
jump and survives those enemies, reaching the third pipe before contact at
1952/Y108/frame16495. The third-pipe branch independently reaches2030/Y48
at16487, allRAM exact; O continues toward the late pit/spring.

A passive N observer also binds the axe-wall corner: integration moves
X2257->2259/Y47->48, native LandPlyr writes Y48/state0 and SamusStopAtWall
clampsX2259->2257. The next update restores falling; M/N drop without
using a new jump from the transient ground. The same wall column is solid
above the foot sample. Source parity remains unclassified; no repeated zip
or clean finalQA claim is made. Packet `simon-v34-axe-corner-readonly.json`
records actual opcodes, balanced interrupt depth and source/ROM/CSV hashes.

SimonO passes the third pipe but an early enemy-triggered jump begins near
2333 and its second jump expires before the real narrow pillar near2474.
It falls2443/Y246 at16879. The late-pillar branch starts from genuine
O16719/X2321/Y176 and targets2700 through that gap. Root accepted39 after
761/761 component slots with unchanged fixtures; runtime/test ownership
remains root and this traversal history remains specifically34.

Simon late-pillar winner independently reaches2700/Y48 at17027, all10,240
RAM bytes exact. P continues toward the native spring using compression
state2+ fresh A and a held boost, without changing force/terrain/position.
Source-profile geometry and the recorded small axe-wall corner remain
open follow-ups, so no clean final visualQA or current39 replay is claimed.

SimonP clears real2-1 through the native spring boost and reaches playable
2-2 at18615. Its generic water jump lands into the first Blooper, ending
294/Y158 at18830. all_six_stages=true only means all six were entered;
cleared=false is preserved. Early-water branch starts from genuineP18672
before the first floor jump, targeting650 with ordinary jump/whip timing.

Simon34 water continuation: `simon-v34-water-early-bloopers-a` independently replays through X663/Y80 at19124; generic Q walks off that coral into the gap (death19289), retained as a policy negative. `simon-v34-water-first-gap-a` then independently cold-boots to X1051/Y96 at19447, matching controller polls, target/frame and all10,240 RAM bytes. Candidate R continues from this certified input stream. No completed water/strict six-stage proof is claimed yet.

Simon34 R reaches1359/Y88 and meets a Blooper at19742; no new defect inferred. Search `simon-v34-water-second-coral-a` revises genuine controls from19680, independently cold-boots to X1814/Y176 at20143 with all10,240 RAM bytes identical. S continues with a controller-only lower-coral alignment / vertical double-jump helper and suppresses new jump input at the exit pipe. No water clear claimed until completion and separate full-audit replay.

Simon34 S continuation from1814/Y176 meets an enemy at1825/Y125 on20157; the short branch endpoint was valid but committed to contact. `simon-v34-water-bridge-approach-a` instead revises the real input history from the earlier1626/Y48 coral at19981. Its winner independently cold-boots to upper bridge X2091/Y0 at20396, exact target/polls/frame and all10,240 RAM bytes. T continues toward the far coral and exit; no full clear or strict six-stage claim yet.

Simon34 actual walk-off source negative: ordinary cold-boot probe B at20580 enters RosterMovement with X2259/Y47, state1, raw/parsedA128, previousA0, RgDoubleJump0, and whip10. The next completed update remains falling (positiveVY1.87509) and whip9. Pinned Simon.checkState rearms canDoubleJump on ground, so that fresh A after walking off should launch/cancel the whip. Evidence/proposed7-byte rearm is bound in `build/verification/simon-walkoff-source-gap-v34/summary.json`; no runtime change. Probe A had an observer key typo before the input and is excluded. Root has scheduled this with geometry for batch41 after40c closure.

`build/verification/lsr-geometry-functional-batch41-proposal.json` is a read-only implementation proposal, not a fix: exact Twips normalization, retained attack/current and cached profiles, old-world water receipt, hurt/ceiling/landing refresh order, input phase split, field/space budget, insertion points, and independent fixture requirements. It explicitly retains native collision-adaptation and axe-corner limitations.

Simon34 far-coral proof `simon-v34-water-far-coral-a` starts from genuine grounded upper-bridge20520 and independently cold-boots through X2612/Y48 at20872, with all10,240 RAM bytes identical. Candidate U continues to the exit. This is legitimate alternate controller routing, authorized by root, and does not certify the separately demonstrated source gap clean. No full water/strict six-stage claim yet.

Simon34 U reached the final pipe roof because the generic helper repeatedly jumped near the wall; V stayed below it but stopped on the authoredY128 lower stair because the final-jump gate incorrectly requiredY>=144. W corrects the controller threshold toY>=128 and leaves the actualY112 mouth unjumped. W completes all six stages and real2-3 control at22,471 frames/22,470 polls, zero deaths. This remains discovery-only until the separate strict fixed replay `lsr-v34-simon-fixed-full-audit-a-5-v0-mmc3` finishes. No clean source-geometry claim is made.

Actual40 walk-off component: `build/verification/simon-walkoff-v40-component-b/negative-summary.json`. Both mappers complete12 seeded cases/16 actual fresh-A receipts. Four walk-off source cases fail velocity (six assertions including missing whip cancellation); eight armed/unarmed, exhaustion, and real-landing controls pass. The native authored1-1 question block256/Y144 and empty neighbor remain untouched. Player/camera/actors/physics are explicitly seeded; water is an environment-flag override on that authored geometry. This is not a route/clear proof. A retained predecessor had stale heldA consume armed controls before the intended input; B requires real raw/parsed/previous neutral before each seed. B fixture is frozen and root may now apply the scoped source rearm. No shared tests/runtime/tools were edited.

Workspace maintenance: nine inactive copied Simon N/P/S..W/probe DBG duplicates were losslessly gzip-compressed, each byte-identical after decompression; saved102,760,317 bytes. Manifest `build/verification/lsr-simon-n-w-disposable-dbg-compaction-2026-10-18.json`. Checkpoints, certified roots, active strict proof, component B, all ROMs/inputs/receipts remain unchanged.

Simon34 strict proof now passes: `lsr-v34-simon-fixed-full-audit-a-5-v0-mmc3` independently cold-boots and consumes only the fixed ordinary CSV, with full frame audit enabled. All six stages clear in22,471frames/22,470polls, zero deaths; actual2-3 entry22,447 and control through22,471. Input SHA `b5901642b0131ebcd02a0cf9d0a8321b9656bb7b73b5d44766ace08a229f53ef`, manifest SHA `e67a50baa823c32d9b9e3a930c03129e36d473916811cf2a98eb0a64a3bb73ea`, ROM exact final34 `5f62764c0e531fecd5e1f6e146fc5d50f6ad9cbc237365a44838c50896b36707`. Stomp audit has0events/illegal contacts/opcode mismatches and interrupt guards. No latest40/41 proof, final recording, all-enemy/pickup completion, manual video/audio clean bill or source-geometry parity is claimed. Root41a independently passes the unchanged twelve-case walk-off component on both mappers but remains provisional pending geometry.

Bounded Simon34 full-trace review is `build/verification/simon-v34-full-trace-movement-review.json`: 22471rows, 0 same-room engine8 horizontal steps over8px, 0 vertical steps over16px; 274 screen-disabled samples, 0 during playable task3. This telemetry does not substitute for manual audiovisual review or resolve the documented axe corner/source geometry gaps.

Ryu discovery resumes on accepted40 MMC3, ROM `ae73ef228800b917694c40d5de9bdbbb9467087f9a047ecb0fb6e216984853e8`, which includes the independently verified36 ground-launch correction. Candidate `lsr-v40-ryu-discovery-a-10-v0-mmc3` uses only ordinary power-on controller input, collects the first powerup, later loses it, and dies at1-1 X2002/Y166 onframe2431. No runtime regression is inferred from this combat route failure. A new branch revises actual input frompoll2320 before that encounter; earlier34/22 states are not transferred. Eight policy dependency hashes are bound separately because the discovery policy composes earlier read-only helpers.

Fresh Ryu40 branch `ryu-v40-11-late-enemies-a` independently cold-boots through1-1 X2503/Y128 atpoll/frame2734, with exact input/target and all10,240 RAM bytes. Ordinary input timing survives the earlier combat and staircase; input SHA `3fec090544f308d7ac208636e4f4f2298d27df2b163cbccd2ede62ed60d55f31`. B continues this same-ROM certified history. No full stage clear or current final proof is claimed.

Ryu40 B clears1-1 and enters1-2 at4537; the first underground enemy contact ends192/Y167 at4657. New `ryu-v40-12-first-enemies-a` revises ordinary inputs from4580 and independently reaches441/Y128 at4808, exact controller/target and all10,240 RAM bytes. C continues this certified same-ROM history. No engine change or speculative hitbox repair was made by this agent.

Ryu40 C approaches the first pit below the raised masonry and falls1314/Y246 at5726. Branch `ryu-v40-12-first-gap-a` revises controls from5560 and independently cold-boots through X1420/Y176 at5783 with all10,240 RAM bytes exact. D continues toward the later gaps/lifts, still on accepted40 and without any emulated gameplay writes.

Ryu40 D reaches the paired pipes but descends onto an enemy at1812/Y170 on6117. New `ryu-v40-12-middle-pipes-a` revises ordinary controls from6028 and independently reaches2031/Y176 at6276, exact all10,240 RAM bytes. Owned outside-shared policy E stops on real floor support before nearby ordinary enemies, waits through a full sword sequence and releases B before requesting another; this is controller behavior only. E continues toward the exit lifts.

Ryu40 E reaches the last1-2 lift encounter and dies at2424/Y176 on6731. An already-running branch independently cold-boots through2590+ /Y128 (`ryu-v40-12-final-lifts-a`, exact target and10,240 RAM); it is retained as genuine input history but is not promoted as clean QA. A bounded scan identified persisted +11/+16/+16 X steps at5299/5301/5302, allY144. Further route continuation is held while root prepares the functional correction.

First-cause packet `build/verification/ryu-v40-wall-snap-readonly-a/summary.json` binds an exact fresh replay with actual bank/opcode/interrupt-depth guards. Ordinary Right+B starts sword14 while actually wall climbing atX849/Y152. The illegal sword opens the upper wall brick; a fresh top jump then gets native head speed cancellation without Y separation, native feet groundY144, and a stationary left clamp walks three cells. RgCrouch stays0; this is not an assumed crouch expansion. The packet retains all virtual weapon save/restore writes separately from persisted clamps.

Independent negative components remain outside shared tests: frozenB confirms two ordinary-wall-B failures and eight ground/air/valid-wall-throw controls per mapper; F confirms six real sword hit-rectangle entries after an admitted air swing attaches to a wall, with timerage9 retained (two source failures/map); G obtains actual native0x26 vine contact from state2 atX169/183 before real B/Select/Up+B, then exposes six source input rejections missing per mapper. Source pressAtkBtn rejects climb/vine, pressSpcBtn rejects vine but permits wall throws, and checkState clears sword rectangles during climb. Original C/E vine setups did not actually retain vine contact and are excluded; D/F initial opcode metadata mistakes and the initial G wrapper missing inherited metadata are retained and excluded. New native-meta F receipts derive exact addresses/bytes separately per mapper. No runtime/shared-test/tool edits occurred.

Frozen outside-source validation index `build/verification/ryu-source-input-negative-v40-index.json` covers B/F/G/I:44 actual-input component cases across accepted40 MMC3/MMC5,24 source mismatches and20 passing controls. F/I block_writes fields count real compiled sword rectangle entries, not terrain writes. I first admits air B/Select in state2, then actual native vine contact entersstate3; sword geometry wrongly continues, while the two pending-air-throw controls correctly release no projectile on the vine. H same-update-attachment predecessor is excluded as an existing-air-attack proof. All timer, ground/air primary and allowed wall-special controls are retained. No source/shared-test/shared-tool edits or owned emulators remain active. Root owns the next runtime correction after the frozen41 suite.
