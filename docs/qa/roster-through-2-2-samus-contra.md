# Samus, Bill and Lance: through-2-2 audit

This ledger distinguishes controller-only stage traversal from explicit weapon
arenas. A discovered route is not accepted until its complete input stream is
replayed from power-on against the same frozen ROM. Final recordings must use
that verified stream and native NES audio. No stage clear may be fabricated by
changing RAM, ROM or registers. Workspace limit:30GB.

## Source contract

The reference is the pinned Crossover 2.02 source under
`reference/crossover2/extracted/scripts/com/smbc/`.

- Samus mushroom grants Long Beam. Morph Ball, missiles, Ice Beam, Wave Beam,
  Varia and Screw Attack are separately obtained. Ice/Wave replace one another.
- Non-classic Samus first grounded Down crouches; a second Down enters Morph
  Ball when owned. Airborne Down can morph when owned. Up exits crouch/ball;
  A jumps from crouch and exits ball without an additional jump. Releasing Down
  alone does not stand; horizontal movement after releasing Down does.
- Bill's `MUSHROOM_UPGRADES` is empty in 2.02. Machine Gun is a separate gun
  pickup, as are Laser, Flare and Spread. Guns replace one another. Rapid 1 is
  separately acquired and Rapid 2 replaces it. Lance shares the same rules.
- Original Samus High Jump and Missile Expansion are named source resources
  but absent from this pinned build's obtainable arrays; they are not test
  requirements for the2.02 inventory.

## Current work

The normal Samus beam renderer read a pointer array through the wrong A000
bank. Root fixed the runtime pointer source. Targeted MMC3 pointer/family tests
then passed after correcting two independent test defects: ca65 aliases were
missing from the VICE label file, and the Wave Beam fixture never initialized
its spawn center, making it move aroundY0 rather than its intendedY110.

Samus crouching was absent. The new implementation uses the actual2.02 default
skin's crouch and crouch-shoot frames, retains the existing31-pose stride, and
fits all body poses into the existing18CHR banks. The two crouch poses remain
in the C000 graphics bank; pointer arrays move to the Samus A000 code bank to
make room. One SRAM byte records crouch state. The crouch collision rectangle
uses the source25-pixel height, and shots originate19pixels below the player's
top (source27Flash pixels above the feet, rounded). Normal, Ice and missile
shots share this muzzle calculation. Ice upward aiming and its body shoot pose
were also missing and are connected by the change.

The v1 checkpoint passes the Samus controls, combat, six-pickup inventory,
water, beam pointer, family fairness, pipe collision, death/OAM and Ice/Screw
regressions on MMC3. The new crouch/source-pixel, beam-pointer and Ice/Screw
regressions also pass on MMC5. The source-correct standing beam travels above
a Goomba; the Ice freeze test now uses actual crouch input to aim at the short
target. The OAM test removes its earlier Morph upgrade before lethal contact,
so it actually exercises the death burst rather than consuming a mushroom.

Checkpoint ROM hashes:

- MMC3:`a9e6547edf0902b203572041efca01a28f11ecee91c4da21040877594cf6b6c3`
- MMC5:`ec5c350bf1c1f4c023ec7a773ad0ae3dbfb6f90bc749f99c6013e5a17a17f7f9`

No six-level playthrough or final recording is yet claimed here. The real
Samus 1-1 candidate reaches the flagpole but exposes an exit softlock at X3161,
Y136 in engine 5. Its complete controller stream and screenshot are retained
under `build/roster-through-2-2/samus-contra-b-2-v0-mmc3/`. The shared exit
pipeline is being investigated separately. Bill/Lance route discovery remains
in progress. The new HUD fixture still finds 16 early split writes on MMC3 with
Flare during high jumps; root is addressing that timing path.

## Fixed workload profiling

`samus-contra-fixed-performance.lua` ran 2,368 samples on each v1 mapper.
IRQ/NMI entry, handler and return time are subtracted from the measured weapon
function. Samples use explicit equal-workload arenas, 32 positions per scene,
zero/six enemies, all five Bill/Lance guns and all three Rapid states. This
does not count rendering/audio as weapon CPU and does not claim universal lag
percentages. Baseline CSVs/logs are retained in
`build/roster-through-2-2/samus-contra-v1-evidence/`.

| MMC3 weapon workload | No enemies | Six enemies |
| --- | ---: | ---: |
| Samus 3 short beams | 5,214 | 8,061 |
| Samus 3 long beams | 5,193 | 8,040 |
| Samus 3 Wave beams | 2,032 | 4,879 |
| Samus 3 Ice beams | 6,054 | 8,965.5 |
| Samus 3 missiles | 6,093 | 9,006 |
| Samus 3 exploding bombs | 1,560 | 4,577 |
| Samus 3 Waves + 3 bombs | 3,385 | 9,249 |
| Bill 4 normal bullets | 3,540 | 6,058 |
| Bill 6 Machine bullets | 5,066.5 | 8,858.5 |
| Bill 10 Spread pellets | 7,855 | 14,195 |
| Bill 4 Laser segments | 8,205 | 9,765 |
| Bill 6 Flare projectiles | 12,865 | 15,205 |

The source Flare cap was four despite the pinned source allowing six. The
runtime cap is corrected to six, with a focused seven-trigger regression.
An optimization candidate now caches eligible enemy origins plus a conservative
Y envelope for Samus/Bill batches. Mutable defeat/active flags are still checked
before collision. Y seams bypass the ordinary-envelope shortcut. Converted
Laser/Flare terrain probes are being routed through the existing distinct-cell
path, including separate horizontal/vertical radii for the Laser rectangle.
These optimization candidates await a coordinated v2 build and differential
verification before any speedup is accepted.

The v1 converted Laser/Flare collision oracle passes 2,400 boundary/terrain/
reward/enemy cases. Its baseline CSV SHA256 is
`62bb7ca90c5d4c0c7b9c01eabe6a42c6c6b13eea609f18a5b14f298414c21944`.
The optimization must preserve that byte-for-byte, as well as the existing
native-gun oracle.

### Accepted v2 optimization checkpoint

The v2 build passes both 2,400-case native/converted Bill collision oracles
byte-for-byte, the six-Flare cap regression on both mappers, and Samus controls,
combat and Ice/Screw regressions after caching. The repeated 2,368-sample profiles
show these exclusive weapon-CPU reductions with six enemies on MMC3:

| Weapon workload | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| Samus short beams | 8,061 | 5,775 | 28.4% |
| Samus long beams | 8,040 | 5,754 | 28.4% |
| Samus Wave | 4,879 | 2,590 | 46.9% |
| Samus Ice | 8,965.5 | 6,951 | 22.5% |
| Samus missiles | 9,006 | 6,990 | 22.4% |
| Samus bombs | 4,577 | 2,112 | 53.9% |
| Samus Wave+bombs | 9,249 | 3,676 | 60.3% |
| Bill normal | 6,058 | 4,845 | 20.0% |
| Bill Machine | 8,858.5 | 6,699.5 | 24.4% |
| Bill Spread | 14,195 | 10,144 | 28.5% |
| Bill Laser | 9,765 | 6,506.5 | 33.4% |
| Bill Flare | 15,205 | 9,790 | 35.6% |

MMC5 reductions range from 20.2% to 61.2% for the same workloads. Exact mapper,
variant and Rapid-tier results, ROM hashes, retained CSVs and both oracle
fingerprints are in
`build/roster-through-2-2/samus-contra-v2-evidence/comparison.json`.
These are CPU costs for equal weapon workloads, not claims about every game's
total lag. The Samus bomb sample covers the persistent explosion, after its
one-time nine-cell terrain burst. That initial burst needs separate profiling.

## Required coverage

| Character | Weapon and upgrade coverage |
| --- | --- |
| Samus | Short/Long beam, both facing directions, upward/crouched/airborne fire, Morph Ball entry/exit/clearance, three bombs, fuse/explosion/bomb jump, missiles and missile mode, Ice damage/freeze/platform, Wave oscillation/terrain passthrough, Varia firebar protection, Screw contact protection/damage, pickup emergence/recovery/ammo, source music/effects, underwater operation. |
| Bill | Normal gun, Machine held fire/cadence, five-way Spread, four-segment Laser/replacement, Flare orbit, Rapid 1/2 speeds, eight-direction aim/prone/airborne aim, gun replacement, power-up graphics/palette/SFX, HUD jumps/block shots, sprite overflow, underwater operation, all gun lag profiles. |
| Lance | Full Bill mechanics plus native alternate selection, own body/poses/palettes, lives/menu/flag/spring transitions and recordings. |

The dedicated `samus-crouch-202.lua` regression compares actual DMA OAM/CHR alpha
pixels with independent 2.02 source silhouettes, in addition to checking real
controller transitions and a real private-pickup collision. Explicit arena
setup is labeled in the fixture; it is not a controller-only stage clear.


## Additional bomb burst work and route status

The initial simultaneous three-bomb burst costs 33,006 exclusive weapon CPU
cycles with zero enemies and 34,326 with six on v2 MMC3. Each of its nine
terrain cells currently repeats four identical point corners. The proposed
v4 path dispatches type10 directly to one existing tile probe; all other
projectile terrain paths retain their previous dispatch.

A 4,184-case independent arena oracle covers all 16×16 subpixel positions,
brick/ground/question/coin tiles, underground terrain flags, and edge seams.
The complete block, health, coin, reward, player and bomb results are retained
in `build/roster-through-2-2/samus-bomb-v2-baseline/`. The pinned reference hash
is `6beb2d41ad7208e672fab3ffbf31befcd9153cd2ef4b74b11d94da52fc074a04`.
Independent fixture arenas reset VRAM offsets/address control between cases;
otherwise queued writes accumulate across unrelated arena setups. That reset
is fixture-only and does not alter a controller route.

Controller route discovery has genuine power-on 1-1 clears for Samus and Bill
on v2. Bill candidate P passes the underground low ceiling, both gaps and the
descending lift, reaching X2326. It first lands on the final staircase at
X2180–2184/Y112 before crossing to the lift. Samus's third-pipe Piranha attack
is still being refined; current candidates can fire beyond its hitbox after
moving too close. Lance has a fresh v3 candidate through 1-1 into 1-2. These
are partial discovery streams, not verified six-stage clears or final videos.


### Accepted v4 bomb optimization

Both v4 mappers exactly reproduce the frozen v2 MMC3 reference across all
4,184 cases, including actual foreground SFX enqueue events. NMI queue
consumption and read-modify-write rewrites are excluded from the foreground
sound-event oracle. The canonical output SHA256 is
`6beb2d41ad7208e672fab3ffbf31befcd9153cd2ef4b74b11d94da52fc074a04`.

| Maximum three-bomb initial burst | Zero enemies | Six enemies |
| --- | ---: | ---: |
| MMC3 v2 CPU cycles | 33,006 | 34,326 |
| MMC3 v4 CPU cycles | 11,757 | 13,077 |
| MMC3 reduction | 64.4% | 61.9% |
| MMC5 v4 CPU cycles | 11,197 | 12,457 |
| Hard exclusive-CPU ceiling | 12,500 | 14,000 |

Each mapper passes all64 initial-burst samples and the hard ceilings. Samus
combat, beam-pointer/rendering and source-pixel crouch/control regressions also
pass on v4. Retained oracle/profile CSVs, logs, ROM hashes and bounds are in
`build/roster-through-2-2/samus-contra-v4-evidence/comparison.json`.

### Route handoff, partial discovery only

- Lance: v3 candidateT clears1-1 and1-2 normally and enters1-3 at frame12443.
  Same-ROM immutable prefix through frame12400 is
  `samus-contra-t-3-v1-mmc3/prefix-1-3-entry.csv`. CandidateW still dies near
  X625 on the high platform's Goombas; edge landing/firing policy needs work.
- Bill: v2 candidateR traverses1-2 to the normal indoor exit. Its prefix
  `samus-contra-r-3-v0-mmc3/prefix-at-normal-exit.csv` ends at frame11000.
  CandidateU reaches the outdoor exit area but stalls on a Piranha because the
  earlier firing retreat lacked hysteresis. Current policy has hysteresis.
- Samus: v2 candidateQ passes the three pipes and reaches the final stairs,
  but its plant-fire detours exhaust the timer. Fresh v4 candidateX clears1-1 (1-2 entry5468) but stalls at the
  second underground pipe nearX1753 and eventually dies at frame19674. Its
  controller result is separate from v2 prefixes.

Current policies are `tools/playthroughs/roster_samus_contra.lua`,
`roster_samus_contra_nav.lua`, and bounded diagnostic wrapper
`roster_samus_contra_diagnostic.lua`. Every retained run has a manifest with
its ROM hash and exact ordinary-controller inputs. No six-stage clear,
independent complete replay, final recording, or frame-by-frame review of a
complete route is claimed.


Current untested policy tail change: the stationary plant-fire fallback is now
Bill/Lance-only. CandidateX had cleared a Samus plant but then entered that
fallback when the plant moved behind her, causing a left/right stall. The
Samus-specific closer pipe jump remains active. A future discovery must test
this change; no result is inferred from the policy edit.


## Later collision repair and controller evidence

The latest Samus route/collision ledger is
`docs/qa/samus-contra-final34-controller.md`; the machine-readable progress is
`build/verification/scc38d-controller-progress.json`. The34 six-stage proof
remains explicitly qualified by its confirmed ceiling/side displacement bug.
Prototype38d repairs that classification and source ceiling separation;
focused head/wall/debris/reward controls pass both mappers, but its new
controller chain now has an independent full six-stage normal power-on replay
through responsive2-3, zero deaths, on38d only. It has no final capture or
decoded-frame/audible QA; the smaller castle placeholder23 separation remains
qualified in `build/verification/scc38d-samus-route-packet.json`.

Root's accepted39 consolidated run passes all761 component slots with frozen
fixtures; its performance receipt is `docs/qa/crowd-performance-v39.md`.
That acceptance does not relabel the38d controller states or establish a new
six-stage controller proof. Outside Q4.4-coherent wall setup controls pass
38d/39a on both mappers; their proposed fixture-only correction is retained
separately for root's next geometry41 run, with no shared test migration.


2026-10-18 correction to historical v3/v4 six-visible-Flare audit:
Tracing PLAYER_PROJ_DCT registration now proves that each visible source
Flare also registers its hidden center. The source pre-creation predicate
is global length<6, so settled admission is O+2F<6 including old primary
shots; the prior six-visible interpretation and its frozen fixture were
incorrect source oracles. Native phase/handedness and nonbrick terrain
consumption also differ. Independent negative/proposal and natural
controller receipts: build/verification/bill-flare38d-source-runtime-negative.json.
No runtime or shared fixture was edited for this correction.
