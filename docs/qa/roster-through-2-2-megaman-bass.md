# Mega Man and Bass through 2-2 audit

Status: in progress. No final 1-1 through 2-2 recording is accepted yet.

Genuine v3 controller discovery reaches Mega Man's final 2-1 spring wall
(independently verified x3071/Y16/poll18919) and Bass's 2-2 water room. Bass's
latest ordinary suffix dies at x1454. Remaining route and final-build replay
are still required. The user selected Mega Man 2.02 movement; its source batch
and independent motion/BG fixtures are prepared for checkpoint v14 below.

The route policy is `tools/playthroughs/megaman_bass_policy.lua`, run by the
shared `tools/playthroughs/roster_run.py` cold-boot controller harness. Discovery
may inspect RAM but supplies only controller input. A final route must replay its
complete input log independently on the frozen ROM and record native audio/video.

Ability fixtures remain separate from that controller-only progression evidence.

## Source inventory audit

The pinned Crossover 2.02 `MegaMan.as` and `Bass.as` agree on these obtainable
weapons and energy costs: Super Arm 8; Metal Blade 4; Hard Knuckle 8; Pharaoh Shot
4 (charged balloon release 8); Charge Kick 4; Flame Blast 4; Water Shield 16.

Each weapon has 112 energy. Mega Man additionally obtains Rush Coil (12 energy
at spring contact), and the mushroom adds Charge Shot. Bass has no mushroom
inventory item; his powered buster increases its simultaneous-shot allowance.

Both can replace an already acquired weapon in the upgrade pool with Energy
Balancer. Magma Bazooka appears in generic base-class data but is absent from
both 2.02 obtainable lists, so it is not a missing obtainable weapon here.

Implementation locations: `src/special_weapons.s`, `src/megaman_weapons.s`,
`src/megaman_physics.s`, `src/expanded.s`, `src/inventory.s`,
`tools/reference/build_inventory.py`.

## Source findings and verified fixes

- Mega Man's Hard Knuckle armor handling was gated to Bass in
  `MegaManWeapons::DamageEnemy`. The common 2.02 projectile gives both characters
  pierce strength 10, exceeding Beetle/Bullet Bill armor strength 5.

- Shared special projectiles only received the source armor-deflection behavior
  as Bass. Mega Man's Metal Blade and Pharaoh shots were consumed instead.

- `SpecialWeapons::EnemyCandidates` counted only IDs below `$15`, excluding
  native Bowser and cannon Bullet Bills. Its zero-enemy shortcut skipped all
  special-weapon collision when either is the only live target, even though
  the native general collision loop supports those enemy IDs.

- Water Shield empty-arena baseline spends 10,902 exclusive CPU cycles in
  physics and 5,508 in drawing per full-orbit update on the retained Bass profile.

  Collision and drawing are optimized through v6, as detailed below. The exact
  two-part direct drawing code in `src/water_draw_proposal.inc` is included and
  passes the independent OAM oracle on both mappers.

`tests/megaman-special-armor-202.lua` passed both mappers on immutable v2.

`tests/megaman-bass-lone-boss.lua` passed v2 MMC3: controller-created Metal and
Knuckle shots damage a lone Bowser for both characters, and Knuckle defeats a
lone cannon Bullet Bill. The fourteen selected ability suites in
`build/verification/mm-bass-v2-ability-summary.json` all passed (seven per mapper).

## Water Shield optimization evidence

Immutable v3 uses one conservative orbit-envelope terrain scan, direct signed
orbit lookup integration, a specialized Water update, and direct drawing of the
exact two source sprite pieces. Root also optimized the shared OAM clear and
Mega Man native-audio zero-page transfer. Both mappers pass 20,480 original
right-facing motion checks and 1,760 source OAM-piece checks. The 2,016 native
corner outcomes are byte-identical between v2 and v3 on both mappers; their SHA
is `7015bab9af1725ecf2e5b9e0e264d50842ce18bc5e6cfd9f1dfebe4b5942dfbf`.

Measured v3 completed sprite DMA during a 100-hardware-frame orbit window:

| Character | MMC3 DMA / lag | MMC5 DMA / lag |
| --- | --- | --- |
| Mega Man | 100 / 0 | 100 / 0 |
| Bass | 87 / 13 | 98 / 2 |
The new profiler also measures the entire live eight-ball expansion window.

V3 expansion still rendered only 35/66 frames for Mega Man MMC3, 34/65 for Bass
MMC3 and 36/62 for Bass MMC5. This remaining lag is explicitly tracked.

V4 corrects left-facing shields to start pi earlier, rotate negatively, and reveal
balls at the source's negative-pi threshold. The real-controller left-facing
summon test passes both mappers through 100 updates. Both mappers also pass
40,960 orbit-ball checks, 21,504 expansion-ball integer products (radii through
255, both directions, mismatched phase keys), 1,760 source OAM-piece checks and
the unchanged 2,016-case native corner fingerprint. The quarter-square tables
are safely reduced from 512 to 384 entries: maximum sum index is 382.

V4's per-axis scalar cache saves too little: expansion physics still averages
6,734 cycles for Mega Man MMC3, with 31 skipped render frames in a 63-frame
expansion window on MMC5. V4 Bass orbit improves to 99 completed DMA frames per
100 hardware frames on both mappers through shared decoder changes; Mega Man
MMC3 has one skipped frame and fails the strict zero-lag regression bound.

V5 replaces the per-axis wrapper with eight precomputed signed
low/high vector offsets built from four nonnegative products per phase. Each
ball checks its low-five-angle-bit key once and directly indexes cosine/sine
offsets. Nonuniform phase fixtures conservatively rebuild the vectors. Both mappers pass 40,960 exact orbit checks, 21,504 expansion checks and the real left-facing summon test. Expansion physics falls to about 5,405 cycles. MMC5 completes 53/62 expansion DMA frames (9 skipped, previously 31); Bass MMC3 completes 38/62 (24 skipped, previously 29). Mega Man MMC3 orbit still misses one frame and fails the strict zero-lag bound. These remaining failures are not suppressed.

## Progression status

Controller-only discoveries are still candidates. `mm-bass-discovery-b` cleared
1-1 as Mega Man and reached 1-2; `mm-bass-discovery-c` cleared 1-1 as Bass and
reached 1-2 x1643. Both later died. No complete six-stage route, fixed replay or
final recording has been accepted yet.

## Planned independent checks

- Default busters, powered busters, Mega Man charge and Bass seven-direction aim.

- Ground/air movement, slide/dash, dash jump and double jump.

- Separate native pickups and Select cycling for every obtainable weapon.

- Super Arm lift/throw, block impact, question rewards and debris.

- Metal aiming, Knuckle startup/steering/armor, Pharaoh charge and release.

- Charge Kick activation/cost, Flame surface orientations and repeat damage.

- Eight-ball Water Shield appearance, orbit, expansion, damage and exact drawing.

- Rush summon, landing, spring contact/energy and departure.

- Damage/recovery, death cleanup, small/large energy drops and Energy Balancer.

- Six contiguous stage clears, underwater movement, castle boss/axe and exit state.

## Canonical Water edge correction for v6

The earlier Water optimization used a radius-3 candidate prefilter, whereas the
retained generic projectile table specifies radius 4. V2/v3 equivalence proved
only preservation of that existing optimization error. The corrected filter
uses four-pixel corners and a conservative 26-pixel orbit-center envelope.

The independent control redirects only the two Water candidate calls to the
retained generic CollisionCandidate and bypasses the empty-envelope shortcut.

It runs isolated arenas, never a playthrough. Both mapper controls yield SHA
`75f5c8118d2e3c7b2bd4eaad7bc75028aec9fcdb8340c7c2db2d7b880d82d17a`
for 2,016 targeted cell/page-seam cases. Frozen v5's radius-3 implementation
differs in 464 cases, proving this test detects the corrected bug.

The control manifests, patch list and negative-control outcomes are retained in
`build/verification/water-generic-control/` and
`build/verification/water-corner-radius4-correction-evidence.json`.

The shipping v6 result must match this independent control before acceptance.

## Controller branch discovery evidence

The generic bounded search stores only opaque controller-reached binary states
for discovery. Each accepted branch is independently replayed from power-on
without state loads, with exact input poll/frame and all 10,240 RAM bytes
compared at the endpoint. It never edits emulated memory, registers or states.

`search/mm-12-columns-e` verifies Mega Man through 1-2 x1810, Y176, frame7442.

This is partial progression evidence, not a complete 1-2 or six-stage clear.

## V6 accepted Water results

Both immutable v6 mapper ROMs pass all fourteen Water checks. Numerical evidence
covers 40,960 orbit balls, 21,504 expansion balls, 1,760 exact OAM pieces,
2,016 canonical radius-4 corner arenas and the real left-facing summon. The
shipping corner output matches the independent retained generic collision
control exactly. No physics, drawing or display thresholds were weakened.

| Character | Mapper | Orbit DMA /100 (lag) | Expansion DMA /62 (lag) |
| --- | --- | --- | --- |
| Mega Man | MMC3 | 100 (0) | 44 (18) |
| Bass | MMC3 | 99 (1) | 43 (19) |
| Mega Man | MMC5 | 100 (0) | 59 (3) |
| Bass | MMC5 | 100 (0) | 60 (2) |
Orbit physics averages about 4,000 cycles versus the earlier 10,902-cycle Bass
baseline; drawing averages 3,038–3,206 versus 5,508. V6 expansion physics averages
5,459–5,485 cycles with canonical four-pixel collisions. Root's native-audio
fast flush removes Mega Man MMC3's last orbit skip and further improves actual
expansion sprite DMA. Remaining expansion lag is explicitly measured above.

Evidence: `build/verification/mm-bass-water-v6-summary.json`, versioned v6 logs
and `v6-smb-crossover-*-water-performance-*.csv`.

Further genuine controller progress: Mega Man clears normal 1-2, enters 1-3 at
frame9446 and independently verifies the high-cap branch through x806 at frame10073.

Bass clears normal 1-2, enters 1-3 at frame9394 and independently verifies the lift
branch through x1461/Y112 at frame11032. All are partial six-stage routes on immutable
v3. Final six-stage controller replay and recording remain outstanding.

## Deterministic interrupt coverage after rendering speedups

V6's original Bass weapon fixture checked 1,140 valid NMI bank restores but
accidentally observed only native graphics bank 34 at NMI entry. Faster drawing
removed incidental interruption inside the short special-art mapping window.

The ability assertions all passed. The fixture now runs an explicit isolated
post-ability idle-bank phase: map each of the three graphics banks observed
during real body/weapon drawing, allow a real NMI, then verify CurrentBankC and
every byte of the actual 8 KB C window on return. It does not manufacture a
playthrough. V6 and V7, both mappers, pass 1,144 preserved native NMIs and all
unchanged weapon cases. Evidence is
`build/verification/bass-deterministic-nmi-coverage-summary.json`.

## Later controller discoveries, still partial

On immutable v3 MMC3, Mega Man's `search/mm-13-second-bridge-b` reaches 1-3
x1900/Y112 at frame 11,078. The earlier x1700 branch lands beside a Goomba and
dies two frames later; it is superseded. The broader search preserves projectile
and enemy-health differences during beam deduplication, so a fired shot cannot
be discarded merely because the player has the same X/Y as a no-shot branch.

Bass clears 1-3 and enters 1-4 at frame 12,507. His
`search/bass-14-first-bars-a` reaches x1101/Y112 at frame 13,456. Both endpoints
have independent power-on, fixed-input verification against all 10,240 RAM
bytes, with no state loads or emulated writes in that verification.

These are discovery routes rather than accepted six-stage recordings. A v3
Bass prefix was also replayed on v7 as a migration smoke test; it diverged at
the first 1-1 jump and died. V7 subsequently proved to have startup audio-history
corruption and is explicitly rejected as a final recording build. Continue
geometric discovery on v3 and retime/reverify on the accepted final checkpoint.

Further v3 ordinary-input proofs: Mega Man reaches x1100/Y112 at frame 13,282
and x1550/Y128 at frame 13,692. Both have independent exact-RAM cold-boot
verification. The latter endpoint still has an active slide, so a successful
next move must account for slide cancellation and a fresh A edge; Player_State
zero alone does not mean the character can immediately jump.

Bass reaches x1820/Y176 at frame 14,094 and x2241/Y112 at frame 14,333, both
independently verified. `bass-tail-k` then clears the castle and enters 2-1 at
frame 15,235. It dies at x646/frame 15,743 while landing near an enemy. This is
genuine controller-only fifth-stage entry, still not a six-stage clear. A combat
branch preserves active-shot and B-held alternatives as separate spatial
classes so damage setup is not pruned as a duplicate of walking.

The generic search now snapshots its Lua search and verification sources into
each new result directory and hashes both in the manifest. This prevents a
later shared helper edit from changing the meaning of a saved wrapper.

Mega Man's castle entrance branch `search/mm-14-entry-gap-a` independently
verifies x351/Y128 at frame 12,502. The low ceiling requires takeoff near x193;
the original generic takeoff near x178 falls short. The next island's question
block at x480 also interrupts an early jump. Waiting until approximately x500
before leaving the island reaches the far bank. `mm-tail-t` then reaches the
first firebar corridor at x778, where a further branch is in progress.

Bass's `search/bass-14-second-bars-b` independently verifies x1551/Y128 at
frame 13,891. A plain Right suffix is hit by an incoming Bowser fireball eight
frames later, so this endpoint is not a completed hazard clear. Further ordinary
controller branching is in progress. The earlier search pruned every alternative
into fatal airborne poses near x1393. Eight-frame chunks and an optional limit
of two alternatives per 24-pixel position/movement region retain useful waits
and pass that earlier firebar. All previously default search actions remain
unchanged unless a specific subset is requested.

## Movement source versions

Before the user's October 17 movement choice, Mega Man retained the originally hosted model documented in
`docs/reference/parity.md`: 150 walk speed, 580 jump power and 1100 gravity in
Flash units. The later 2.02 shared MegaManBase instead uses immediate 165-speed
walking, 1500 gravity and 650/560 dry/water jump power for Mega Man; Bass uses
565/500 and already follows that later source. The movement-version choice is
resolved in favor of 2.02 by the user. The exact special-weapon
and Water Shield tests do not claim the older movement model is 2.02 movement.

Candidate tails may use `--discovery-fast` to omit the expensive physical-frame
audit. It cannot be combined with fixed final replay or recording. Final proof
still requires full graphics/audio telemetry and actual native audio/video.
Both route runners reject a nonempty output tag, and recording preflight
reserves the complete bounded raw frame budget plus 512 MiB below the 30 GB cap.

## Native recording verification

Two bounded 650-frame real native-capture smoke runs, one per mapper, produce
649 images at 256x240 and 60.098811 frames/second. Mesen commits the prior image
after Lua's endFrame callback, so the recorded count is exactly one below the
harness frame counter. Both captures contain 48,000 Hz stereo audio: video
duration 10.798883 s, audio 10.786 s, peak -12.7 dBFS (MMC3) / -11.3 dBFS (MMC5).

The runner now verifies frame count, dimensions, nonempty/non-silent audio and
audio/video duration agreement before accepting or deleting the native AVI.
A missing capture, failed encoding or failed metadata check returns failure.
`recording_verified` additionally requires the successful fixed-input six-stage
replay, so these short calibration clips correctly remain false. Independent
negative controls with the wrong frame count, no audio and silent audio are all
rejected. Evidence is
`build/verification/mm-bass-native-capture-metadata-summary.json`.


Further controller discovery now clears the castle for both characters. Mega
Man's `search/mm-14-bowser-crossing-b` independently verifies x2260/Y112 at
frame 14,433; the ordinary suffix `mm-tail-x` enters 2-1 at frame 15,150.
Bass's `search/bass-21-enemies-a` verifies x936/Y176 at frame 15,992, and
`search/bass-21-mid-gap-a` verifies x1772/Y176 at frame 16,624. All of these
are exact cold-boot, fixed-controller verifications against all 10,240 RAM
bytes. They are discovery on v3, with final build retiming still required.

The final tall 2-1 wall requires the actual spring. `bass-tail-m` reaches its
approach normally but fails to time the boosted bounce and eventually expires
the timer. `search/bass-21-spring-wall-b` starts from its genuine poll 17,752,
uses fresh A edges during native spring compression, and independently verifies
x3070/Y16 at poll/frame 17,872. The search's deduplication key now includes
the spring animation, timer and force so a boosted compression cannot alias a
normal jump. No spring or movement RAM is written.

Terrain terminology correction: a grounded player near x1450/Y112 in 1-3
can be on a moving platform; it is not evidence of a static bank. Native
platform ID/position and width must be inspected. The shared read-only route
policy now matches the feet against real active platform objects and walks
toward the platform's far edge before launching. Final MM/Bass replay will
verify its own timing; Ryu's separate controller proof established this helper.


Bass's `bass-tail-n` enters 2-2 at frame 19,136 with all six required stages
visited, then dies against a Blooper at x945/frame 19,867. This is not a clear.
The first water discovery branch reaches x1201/Y116 at frame 20,033; independent
cold-boot verification is pending at the time of this note. Mega Man's first
2-1 combat branch independently verifies x752/Y112 at frame 15,714; its suffix
reaches the middle gap, where another branch is needed.

The parent task also identified an entrance-only audio-pointer overwrite in
older builds: a guest palette routine leaves X=12 before SetupBubble, causing
Bubble_Y_Position+12 to alias XgAudioPtr+1. V12 will restore the native bubble
slot and initialize the song counter. V3 route discovery remains geometric
evidence only; its audio is not final-build acceptance evidence.


Water route-policy correction: at the verified x1201 endpoint, the nearest
actor is a fish twelve pixels behind Bass; another fish is forty pixels ahead.
The old generic nearest-actor helper hides that approaching threat and suppresses
forward fire, so its next suffix dies at x1233. The owned water policy now checks
native actors ahead before choosing aim. This changes only ordinary input
selection, not game mechanics. Independent final fixed input remains required.

Trace interpretation: native AreaPointer can change while the loaded map does
not. ParseRow0e updates it to the next optional pipe entrance destination. Its
2-1 changes near x818 and x1586 therefore do not by themselves show a warp or
corruption. Stage progression is established by world/level, active engine and
actual control in the following stage.


The mechanics-guided Mega Man middle-gap crossing succeeds: the independent
`mm-21-gap-approach-c` proof walks to x1460/Y176 at frame 16,723 without
sliding, then `mm-21-gap-jump-d` holds Right+A across the 64-pixel floor gap
to x1560/Y176 at frame 16,805. The latter independent verifier is running.
No Rush Coil, artificial upgrade or runtime change is needed. The owned route
helper uses a 16-pixel ground-gap probe for Mega Man because Mario's 32-pixel
run-speed lead launches Mega Man's slower walk too early.

Bass's second water branch `bass-22-fish-b` independently verifies x1400/Y19
at frame 20,253, including the intervening real coral and fish hazards. Its
ordinary suffix is still in progress.


## Verified discovery-root reuse

`tools/playthroughs/roster_branch_root.py PROOF_DIR` performs one fresh
independent fixed-controller replay of an older verified endpoint. Only after
all target and 10,240 RAM checks pass does it export an opaque reusable state.
New successful branch verifiers export this root automatically. The state is
never decoded or edited. Use `--basename best` for a separately verified best
endpoint.

`roster_branch_search.py` optionally accepts `--root-proof PROOF_DIR` and
`--root-proof-basename best`. The prefix must be exactly that endpoint's input
CSV and root-poll must equal its target. The tool binds the ROM, input bytes,
target, RAM, state and verifier-source hashes, plus the completed independent
proof flags. It checks all RAM again after loading the discovery root. Every
new winner still requires its own complete independent power-on replay. The
final roster replay/recording tool has no state-loading option.

The ordinary MM gap control and `root-reuse-mm-gap-smoke` produce byte-identical
inputs and all 10,240 RAM bytes at x1560/Y176/frame 16,805. Reuse reduces discovery
emulation from 16,805 to 90 frames; the new winner also passes a fresh independent
replay. Six negative controls reject wrong ROM, poll, input bytes, unverified
metadata, substitution of a different unchanged opaque state and changed
verifier source. No binary state is modified for these controls.

Link's optional `--goal-y-min` is also tested together with reuse: a real Y162
airborne endpoint is allowed by minimum 160, while minimum 176 excludes that
short crossing. Evidence: `build/verification/root-reuse-validation-summary.json`.

Mega Man's complete middle-gap jump now passes independent exact-RAM replay.
Its suffix reaches the final 2-1 spring wall, where boosted-bounce discovery is
in progress. Bass's low water candidate traverses the early coral but stalls
when it keeps firing at fish between the seven available aim rays. The route
policy now fires only when a source cannon ray can meet the target, so ground
firing lock does not prevent it from repositioning. This changes controller
selection only.

## Mega Man movement target: Crossover 2.02

The user selected 2.02 movement for consistency on October 17. This supersedes
the earlier hosted-1.2 movement target for Mega Man. Bass keeps its existing
2.02 movement path. The primary source is the pinned SWF recorded in
`reference/crossover2/source.json` (SHA256
`6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af`).

`MegaManBase.as` overrides `movePlayer`: horizontal velocity immediately takes
WALK_SPEED=165 Flash px/s, with no acceleration or coast. A fresh grounded
direction first changes position by STEP_MOVE_AMT=4 Flash pixels (2 NES), then
STEP_TMR=100ms pauses ground velocity for six updates. Underwater ground speed
is Character's 90; air steering still uses 165. The source has no double-jump
skill for Mega Man, selecting jumps 650 dry / 560 water, gravity 1500 / 500,
spring powers 475 / 1000 and fall caps 700 / 250. Underwater fall capping
precedes gravity; dry fall capping follows it. Released upward jumps multiply
velocity by `(1e-6)^(1/60)` each update.

Slide speed is 300 / 225, with strict source distance tests beyond 125 / 100
Flash pixels. Down+A during a slide does not restart it. A fresh A without Down
jumps out only when there is no ceiling. Carrying a Super Arm brick prevents
starting a slide; an uncovered reversal ends it, while a covered reversal
keeps the short profile until the ceiling clears. Walking off an edge ends
slide state; Level's exactly-one-static-tile gap support runs after background
collision. The short-form ceiling probe excludes coordinates outside terrain.
The startup timer also advances on a vine.

The existing skin's step artwork is appended after the original 64 body poses,
preserving existing sixteen-pose skin strides. Head/helmet/power palettes and
original existing pose content remain sourced from the established art. Carry
poses use their existing source step frame during the new timer.

`tests/megaman-motion-202.lua`, invoked by mandatory `megaman-physics`, models
the above in floating-point source units independently of runtime Q16 constants
and tables. It checks 31 input/state sequences plus one-tile gap support and
eight negative controls. `megaman-step-collision-202` tests the actual native
background collision after startup at bricks, pipes and unsupported ledges in
both directions, including page seams. These are explicitly isolated arenas,
not stage clears. Historic environment/water expectations now use the selected
2.02 target.

Checkpoint v14 passes both mappers: 616 numeric motion/state updates, nine
slide-gap cases, 216 actual wall/pipe updates, 18 unsupported-edge updates and
72 startup artwork checks spanning all three power forms. The wall fixtures
also require native contacted-side bits after the exact clamp. The environment
fixture verifies that a nonzero startup timer expires while on a vine, plus
native stomps and both source spring strengths. The unchanged v13 ROM fails
the new oracle on its first grounded direction update, demonstrating that the
checks distinguish the selected source behavior from the older movement.

All 34 focused mapper fixtures pass, including controls, real 2-2 water room,
camera/HUD trace, crowded buster OAM, Rush, special armor, lone Bowser/Bullet
Bill handling, exact Water Shield OAM/corners, native audio timing, Bass's full
source movement/aim reference and four-pipe traversal. No runtime repair was
required after v14; fixture setup fixes normalized MMC5's bank bit and rounded
fixed-point arena positions coherently. Archived evidence and final fixture
hashes are in `build/verification/megaman-motion-202-v14/summary.json`.

The strict MM steady-orbit performance bound stays zero lag: 100/100 completed
OAM DMA frames on both mappers. Full expansion is 44/62 on MMC3 and 59/62 on
MMC5. Bass steady orbit is 99/100 and 100/100 respectively; expansion is 44/62
and 60/62. Residual expansion lag is still recorded, with no reduced ball count
or weakened collision/art assertions. v14 leaves 29 PLAYER bytes, 1 COLLISION
byte, 50 FIXED bytes before DPCM alignment and 70 SRAM bytes free.

## Latest geometric controller handoff before movement retiming

On immutable v3 MMC3, `search/mm-21-spring-wall-a` now independently replays
from power-on through the final 2-1 spring to x3071/Y16 at poll 18,919. Complete
ordinary inputs and a hash-bound reusable discovery root are retained. Earlier
MM and Bass route prefixes reached all first five stages; Bass also enters
2-2 at poll 19,136. Its latest ordinary low-water suffix dies at x1454. Neither
character has an accepted full through-2-2 replay or final recording yet.
These older geometric paths require retiming on the final checkpoint; the new
MM movement deliberately changes its route timings.

## Flame Blast palette and green-column investigation, v22

The video report at74.8s (native1-2, Mega Man, FLAME048) is not yet reproduced
as the exact green pipe-like column. This investigation does not attribute that
column to a CHR/OAM fault by appearance. Explicit native1-2 multi-seed traces
retain completed hardware DMA OAM, the actually mapped pattern bytes, full
nametables and palette bytes. The oldv18 normal probes observed226/246 DMA
frames and594/661 Flame parts on MMC3/MMC5, with zero CHR/OAM contract errors.
The finalv22 probes observed225/248 DMA frames and585/668 parts, also zero
errors. Bounded binary samples and per-DMA CSVs are under
`build/verification/flame-v18-baseline` and `build/verification/flame-v22`.
The MMC3 star variant is explicitly named `flame-star-*`; it is distinct from
the freshly rerun `flame-normal-*` baseline.

A separate actual color defect was demonstrated against the pinned2.02 SWF.
The old art borrowed player palette0 and encoded red/orange in Bass's order;
Mega Man's Flame suit reverses those entries. On both oldv18 mappers the new
independent source oracle fails at seed22: expected orange$27, actual red$16.
A separate old-ROM pillar sample comparison finds1882 wrong pixel colors in21
samples on each mapper. Old Bass source pixels pass, consistent with its
matching original palette; this is an unchanged control, not a Bass failure.

The raw source Flame regions for all16 frames24..39 are outside all four suit
recolor rectangles in `GraphicsManager.as:229`. Source masks and bitmaps produce
identical Flame pixels for Mega Man and Bass. `tools/audit/build_flame_source_reference.py`
checks the archived SWF SHA, derives those regions and exclusions, and emits
61 unrotated/rotated source color frames without reading generated CHR,
metasprite records, or packed tiles. The source hashes and raw source regions
are in `tests/fixtures/flame-source-pixels.json`.

The narrow asset fix changes only Flame records/pixels: fixed sprite palette2
provides red$16 and orange$27; palette3 color1 provides the seed's black$0F.
Both palettes were verified from actual completed-DMA PPU pixels in every
native area theme. The generator preserves all54 non-Flame records, their134
referenced8x16 pairs, Water family4 and poses38/39, and Remaining weapon overlay
pairs28..31 byte-for-byte. One additional2KiB family is allocated. Special
families append directly to the physical pool via `SsPhysicalBanks`; family16
maps physical200/201 and does not overwrite logical$80 reserved for Samus.
Packing is252/256KiB MMC3 and244/256KiB MMC5. There is no runtime/SRAM change.

Finalv22 ROM hashes:

- MMC3: `2ec13bcac6c9c60a37096b0b5e2377c771c345b54325dd26c602c8cfc059debf`.
- MMC5: `3bdf2fabe064b47c4c53660ec525afd12c693e28aa521b55fe5c03981f3e5cb4`.

All16 source-pixel cases pass: both characters, native water/ground/underground/
castle themes, three power forms, four contact orientations, every61 source
frames, star activation and live post-star recovery. These compare10122 exact
source DMA images and21305 hardware parts, including3646 star images and3456
recovery images. Power0 cannot launch special weapons; those cases retain an
ordinary-B-created live projectile while the isolated fixture reduces power.
Ceiling-contact fixtures explicitly give that live seed an upward velocity.
These are ability/pixel arenas and do not claim ordinary-controller progression.
Eight named wrappers are registered in `tools/verify.py`.

All24 supplemental checks pass on unique v22 ROM aliases/output stems: Water
motion, expansion, source-left path, exact OAM, exact corners, lone Bowser,
both Water performance profiles, pickup art, Flame contact/lifetime, Samus beam
rendering, and the native1-2 DMA coherence diagnostic. Existing performance
bounds are unchanged:

| Mapper | Character | Orbit DMA | Orbit lag | Expansion DMA | Expansion lag |
| --- | --- | --- | --- | --- | --- |
| MMC3 | Mega Man |100/100|0/100|44/62|18/62|
| MMC3 | Bass |99/100|1/100|44/62|18/62|
| MMC5 | Mega Man |100/100|0/100|58/62|4/62|
| MMC5 | Bass |100/100|0/100|60/62|2/62|

The accepted2.02 movement also required stale legacy assertions to be updated.
`crossover.lua` now checks MM's exact immediate1.375px/update Q16 steady speed
and immediate stop on release. `world-springs.lua` uses source475/120 and
1000/120 launch forces. Both tests pass bothv18 mappers; all other character
expectations are unchanged. This update does not bless builds20/21, whose
unrelated shared character-ID dispatch regression was repaired forv22.

Final machine-readable summary, ROM/source/fixture hashes, matrix logs,
performance CSVs and invariants: `build/verification/flame-v22/summary.json`.
Exact green-column video attribution remains open. No new playthrough clear or
final recording is claimed by this focused investigation.

## Controller route diagnostics on accepted component checkpoint 32

These are ordinary-input route candidates, not final recordings or exhaustive
enemy/pickup clears. Every exported winning search below was independently
replayed from power-on with no savestate loads, memory/register writes, or ROM
patches; target polls/frames and all 10,240 compared RAM bytes match. Discovery
alone uses genuine, unchanged same-ROM binary states. No cross-ROM state is used.

Checkpoint 32 MMC3 SHA is
`df61b1e120307c6033a0cffa97e98f63414a509d15f935760f76295df0f1920b`.
Mega Man clears 1-1, normal 1-2, 1-3, 1-4 and 2-1 and reaches 2-2 X2364/Y144
at poll 25606. The contiguous verified inputs are
`build/roster-through-2-2/search/mm32-22-coral-c/winning-inputs.csv`;
its manifest binds the exact ROM, source, input, target, RAM and opaque root hashes.
Bass clears the same first four stages and reaches 2-1 X2950/Y176 at poll 17794.
Its verified inputs are
`build/roster-through-2-2/search/bass32-21-stairs-c/winning-inputs.csv`.
The remaining water section for Mega Man and spring/2-2 for Bass are unfinished.

A real camera problem was found while pressing Right against the 80px pipe in 2-1:
Mega Man's world X stays 2065 while the camera advances 1957 to 1986. An independent
authored arena compares pre-scroll/pre-BG/post-BG and actual wall-helper paths,
and reproduces the missing native camera hold across all guest profiles on
both 32 and 33. Native Mario installs SideCollisionTimer 16; custom Page contacts
leave 0. The 78-case roster/direction/walk/jump/moving-away matrix and hashes are
in `build/verification/mm-bass-camera-probe/report-roster-32-33-a.json`.
These explicitly written terrain/initial-state arenas are isolated correctness
evidence and never count as playthrough progress. The prospective Page-timer
assertion correctly fails 33; the root agent owns the pending runtime correction.

The coherent 34-provisional-b fix passes that same 78-case matrix on both mappers:
3677 actual Page contacts per mapper return with timer 16; 83 moving-away-only
returns preserve position, camera, velocity and timer exactly. All 22 blocked
walking guest scenes stop accumulating camera motion (0px, except Sophia 1px).
Mario and restored-native Luigi retain their native 2px initial pan. Post-BG
position/Y/collision/velocity observations remain exact 33-to-34 for every ID
except the explicitly restored-native Luigi. Hash-bound packets are
`build/verification/mm-bass-camera-probe/accepted-v34-mmc3-provisional-b.json`
and the corresponding `mmc5` packet. No runtime code was changed by this probe.

Mega Man's checkpoint 32 route subsequently passed a complete independent,
full-audit coldboot replay: `mm32-proof-1-v0-mmc3` reaches active 2-3 at frame
27367 and ends at 27391 with zero deaths. The exact input CSV SHA is
`73feef880d581abadd9858a52b54aa711a11e8661ae07819e3f836ac07bcccb6`;
it matches the original candidate byte-for-byte. The trace audit records zero
illegal guest stomps and zero resident opcode mismatches. Audio-event, CHR,
completed OAM, rendering and scroll-write traces are retained. This proves the
six-stage traversal on 32; final captures and exhaustive combat/pickup coverage
remain pending. Bass's verified path now reaches 2-2 X1500/Y176 at poll 21226.
The compact bound evidence packet is
`build/roster-through-2-2/mm-bass-v32-progress-20261017.json`.

Replaying the same ordinary MM CSV on 34-provisional-b fails in 1-1 at X872,
frame 1496. The first world-motion difference is a jump at 1356, where the old
CSV contains timing-sensitive one-poll A releases at polls 1351 and 1353.
That failure is preserved as a route migration, rather than attributed to
changed movement constants. New controller-only 34b discovery has independently
replayed to X1011/Y176 at poll 1526. No checkpoint 32 opaque state was loaded on
34b; a new adaptive continuation gives button releases at least five polls.


Bass subsequently passes its full-audit coldboot replay on checkpoint32:
`bass32-proof-9-v0-mmc3` reaches active2-3 at frame23830 and ends23854,
with zero deaths, zero illegal guest stomps, and zero resident opcode
mismatches. Input SHA `50ece1f6a4472d327ad984d616a6804dc12d04a634dee2f2a1ce6b1940624a4c`
exactly matches candidate `bass32-s-9-v0-mmc3`. Both MM/Bass complete proofs,
source hashes and compact evidence are bound in
`build/roster-through-2-2/mm-bass-v32-complete-20261017.json`.
Final recordings and exhaustive every-enemy/every-item coverage remain pending.

Controller retiming on34-provisional-b now clears the first four stages for
Mega Man and reaches2-1 X1815. The policy stalls while aiming at an obstructed
foe; ordinary controller branching is underway. Bass clears1-1 with a new
solid-pipe jump policy, then needs a different landing in early1-2 (deathX458).
These failures are preserved as controller-route diagnostics. No new runtime
defect, source edit, final capture or34 complete clear is claimed.


Further34b controller discovery clears2-1 for Mega Man (active2-2 entry19809).
An independent coldboot branch reaches2-2 X1552/Y176 at poll21560, after
the first fish encounter. Bass takes the normal1-2 exit and enters1-3 at10019.
Its verified final underground lift target is X2601/Y128 at poll8838.
The obstruction at undergroundX1153 was resolved by adding Bass's available
Up+B actions to the search; no runtime fix was needed. Current route/root
metadata is bound in `mm-bass-v34b-progress-20261017-a.json`.
Full34b clears, final34 migrations and final captures remain pending.


Water route limitation discovered during34b retiming: the strict32 MM/Bass
traces include supported ceiling-top positions and above-screen jumps in2-2.
For Mega Man, the first observed supported column top is nearX2093/Y0,
then the ceiling roof atY32. This appears reachable over the exposed left
edge of the ceiling column; solid-tile penetration has not been established.
The recorded ordinary-input, six-stage, zero-write traversals remain valid,
but they do not establish a below-ceiling water route or exact source roof
boundary parity. Counts and trace hashes are preserved separately in
`mm-bass-v32-water-roof-annotation-20261017.json`.

The failed34b `mm34b-l` corridor controller incorrectly attempted repeated
airborne paddle edges. Accepted2.02 Mega Man only initiates a jump while
grounded; the source and ROM both enforce that rule. This is a controller
planning error, not evidence of a physics defect. Its negative is preserved.

Two bounded controller micro-searches on34b independently reproduce the
column-top landing atX2090/Y0 in2-2. Search`mm34b-column-controller-micro-a`
lands atpoll22125; its original setup-rejection note is retained alongside
a clarification because the intended trial setup included an already queued
A press. The actual winning input stream still passes the independent
coldboot verifier, matching all10240 RAM bytes. Search
`mm34b-column-controller-micro-b` repeats the landing atpoll22122 from a
full genuine input tail and an explicitly A-released grounded root. Its
ordinary input SHA is
`da7078ce51b44c616074c61f38461abcf8960efdf659695aa1e55b5f10eaef6a`.
Both remain qualified ceiling-route diagnostics; this does not establish a
below-ceiling route or hosted-source boundary parity.

Bass34b now clears1-3 and independently replays the final castle firebar
corridor toX2200/Y128 atpoll16738. Search`bass34b-14-final-bars-c` input SHA
is`2ced9a3644b0e0543507e50c8e145bfa3c636112c16438cc3bfc76b6965db3e3`;
the independent coldboot verifier again matches all10240 RAM bytes.
No source changes or recordings accompany these controller discoveries.

Mega Man now passes a strict full-frame power-on replay on34b in
`mm34b-proof-1-v0-mmc3`: all six stages, active2-3 at28114, end28138,
zero deaths, zero illegal guest stomps, and zero resident opcode mismatches.
The complete ordinary input file is byte-identical to candidate`mm34b-u`
and has SHA
`3e3fbc75c2aba7d0dab7393c83c83c8b2f5ab77c0bb259e69b04668b8d20ce63`.
No emulated memory/register writes or savestate loads were used for this
strict replay. Artifact hashes and the ceiling-route qualification are bound
in`megaman-v34b-complete-20261017.json`. Final recording, migration to the
newest accepted build, and exhaustive enemy/item coverage remain pending.

Bass's old X2200 castle target was too late for the next contact: every
immediate branch died within four frames. The preserved negative is
`bass34b-14-axe-a`. Starting earlier at poll16695 yields the independently
verified `bass34b-14-axe-b`, X2360/Y176 at16975, with input SHA
`520145103832675d32824043f726bb1e115d08ac333a4d8e18dc23ca169fb46b`.
The ordinary continuation enters2-1 at17612. A further independent branch,
`bass34b-21-first-stairs-a`, reaches X751/Y112 at18139. The current remaining
route work starts at the later pipe gap; these are controller diagnostics,
with no accompanying runtime change.

Bass now also passes a strict full-frame power-on replay on34b:
`bass34b-proof-9-v0-mmc3` clears all six stages with zero deaths, enters
active2-3 at27272, and ends at27296. Input SHA
`7282fba44d6d9848201d82b953d05165999053cb981998b7e289bd2162a0613a`
is byte-identical to candidate`bass34b-r`. Illegal guest stomps and resident
opcode mismatches are both zero. The proof uses ordinary inputs, with no
emulated memory/register writes or savestate loads.

The combined `mm-bass-v34b-complete-20261017.json` binds both complete
proofs and their raw audit artifacts. The water-route limitation remains:
Mega Man has220 supported ceiling samples and61 above-screen samples;
Bass has285 and116 respectively. Hosted-source ceiling-boundary equivalence
is unclassified, and solid-tile penetration has not been demonstrated.
Neither exhaustive enemy/item coverage nor a final recording is claimed.
Migration to the newest accepted checkpoint remains held by root instruction.

An optional cleanup of redundant owned candidate ROM/LBL/DBG copies was
rejected by tool policy before execution. No files were deleted in that
attempt and no alternate mechanism was tried. The rejection is recorded in
`mm-bass-v34b-cleanup-policy-rejection-20261017.json`; all evidence remains
available and the workspace is below30 GB.
