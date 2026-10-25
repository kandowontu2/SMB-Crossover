# Roll mobile integration: private MMC5 checkpoint

Roll is Bass's Select alternate in the private 37-identity MMC5 build. The
published 33-identity MMC3/MMC5 ROMs remain at `mmc3-menu-nk`. This is tested
character integration with explicit unfinished fidelity/performance work,
not admission through the final full-roster verification gate.

Candidate: `build/verification/roll-roster-nn/smb-crossover-mmc5-roll-v18.nes`.
SHA256: `e805bbec953fc5305fc3b3391961566f8b50bc925604916c4bea2229d93d6bdf`.

## Implemented behavior

| Input or item | Behavior |
| --- | --- |
| Select on Bass in character selection | Toggle Bass/Roll; show Roll's own supplied portrait and name. |
| Left/Right, A | Walk and jump using the installed Mega Man movement profile, with the same profile's terrain probes and hurtbox. Easy/Hard use that profile's respective movement rules. |
| B | Up to three ordinary buster shots, including left-facing artwork. |
| Hold B | Automatically fire a charge after 60 native updates, spending 4 of 28 energy. A full projectile pool waits without spending energy. |
| Mushroom or flower | Physically emerge and collect through the native actor path; restore both 28 HP and 28 energy. A mushroom permits the next native flower. They do not grant Bass's equipment. |
| Enemy capsules | Separate small/large health and energy restorations: 2 or 10 units. Existing enemy drop frequency/size rules are reused; the health/energy choice is shared evenly. |
| Star / 1-up | Retain native SMB invincibility/expiry and actual extra-life behavior. |
| Damage | Ordinary contact removes 4 HP; Bowser removes 8. Recoil, protection, defeat, particle burst and life-loss respawn use the native paths. |
| Easy/Hard contact | Shared Easy stomp policy; Hard contact requires attacks/avoidance. |
| HUD | Compact HP/EN numbers; retain WORLD/TIME labels and native score, coins and timer. |

Roll has no Bass dash, double jump, seven-way gun or Bass inventory. Gameplay
Select does not change her identity or equip Bass weapons. The unused mobile
carrying sheet is not interpreted as evidence for a broom or carrying move.

The 60-update charge, 4-energy cost, shared movement, damage amounts, capsule
policy and instant restoration are documented SMB adaptations. Exact mobile
timing, health scaling and audio have not been established from an executable
mobile-game reference. This checkpoint does not claim that fidelity.

## Artwork, memory and rendering

The supplied [Sprites Inc mobile sheet](https://sprites-inc.com/sprite.php?local=Classic/Roll/Mobile/)
is pinned locally as `reference/new-roster-art/rollsheet_mobile1.png`, SHA256
`80a6f15a6741cd237098a9accb20e7a7d0f4e2736a8de4b11948e18634dc14a0`.
Seventeen body poses retain their opaque source pixels and mirrors. Extra ink
records obey the existing outline option. The source pellet and two actual
beam flash frames replace the early incorrect crops, which included fragments
of other source poses. Left-facing shots have mirrored records.

The beam's two flash frames quantize to magenta/white, retaining their exact
opaque shapes. Four sprites per beam replace the eight-sprite layered version
that could hide the player's torso. Small/large health orbs reuse supplied
mobile circle graphics as an explicit pickup adaptation; energy capsules reuse
the game's existing source-derived Crossover capsule art.

The private palette is green/gold/magenta. Fixed world palettes supply the
white/red and face/ink shades. Roll does not depend on palette1, which changes
underground; her bow no longer becomes cyan, and native enemy colors are
preserved. Native window4/5 actor graphics remain owned by the original engine.

Four body pools and the repeated private projectile page occupy the first
16 KiB of the reserved 24 KiB Roll asset. Physical source pages are documented
in `reference/roll-mobile/art.json`; the allocation uses audited unused tails
at 364–379, 304–307 and 336–339. The latter two spans are currently zero-filled.
Code/art occupy A119, A120 and C121. Existing 8 KiB cartridge WRAM is now full:
the last byte, $7FFF, is exclusively Roll's legacy-outline bypass flag.
Do not allocate further persistent WRAM without redesigning ownership.

## Repaired integration defects

- The legacy outline cache shared its buffer with weapon drawing. A shot could
  replace the player's body record. Roll now uses her own prepared ink records
  and an explicitly initialized bypass byte, checked against native writes.
- Graphics selection published a new pool even when catch-up skipped OAM
  drawing. Publication now happens with actual sprite construction; direct
  menu/lives portraits retain their explicit publication path.
- Her camera cache was absent, then a native side-contact hold caused drift.
  Her movement publishes the pre-step position and clears that inappropriate
  hold while native collision still separates real walls.
- Bass's standing terrain probes were still used with the Mega Man movement
  profile. They admitted a late ceiling contact and a 16-pixel side clamp near
  the mushroom block. Roll now selects the matching airborne/standing probes
  and hurtbox. A real head bump between adjacent bricks preserves her X/page
  and both neighboring bricks.
- Area palette reloads overwrote the private shot palette. The palette hook now
  restores it, with the green bow independent of the native changing palette.
- A reset wrote the current life count before detecting life loss, retaining
  zero HP after respawn. Life-loss detection now precedes volatile reset.

## Exact-candidate evidence

Evidence is under `build/verification/roll-roster-nn`:

- `art-proof.json`: 68 body pose/facing/outline source-pixel cases and 10
  projectile/orb facing cases. Charge frames must fit four sprites each.
- `final-components-easy-v18-r2` / `final-components-hard-v18-r2`: real menu
  selection, three-shot cap, automatic charged fire/payment, left-facing fire,
  real question-block activation/reward, physical restorations, no inherited
  Bass actions, native Goomba damage, defeat and playable full-health respawn,
  then a real head bump between adjacent bricks. Hard also turns outlines on
  through Options. Arena layouts and positioned actors are explicitly seeded.
- `final-rewards-easy-v18` / `final-rewards-hard-v18`: four native block rewards
  actually emerge and are collected; four enemy capsule cases require a real
  controller-driven defeat, native drop allocation and physical collection.
  Only random choices are fixed. Native star expiry, two ordinary brick hits,
  one charged full-health brick hit and protected adjacent ground are checked.
- `final-replay-roll-easy-v18` / `final-replay-roll-hard-v18`: independent saved
  controller streams clear 1-1 without death and restore movement in 1-2,
  at 4,724 / 4,762 video frames. No gameplay memory writes. Every committed body
  image in these runs is compared using actual OAM, hardware sprite CHR pages
  and palettes: 3,264 / 2,900 frames, including the underground transition.
  Screenshots are sampled every 12 frames, not a claim of manual review of
  every video frame. Earlier input streams that failed after timing changes
  remain retained and are excluded from the passing result.
- `camera-proof-v18.json`: 3,240 / 3,017 ordinary 1-1 gameplay video frames.
  Camera steps are 0–2 pixels, never backwards, and player screen X stays at
  or left of 112 in both modes.
- `final-entry-v18-r2`: all 37 cold controller selections, alternates,
  lives/level entry, bounded ordinary movement and interrupt-bank assertions.
  The old single-pulse entry fixture had an intermittent startup timeout;
  the current fixture pulses Start until the actual selection menu opens.
- `final-parodius-components-v18`, `final-parodius-bells-v18` and
  `final-parodius-pickups-v18`: the three Parodius variants retain their native
  component/Bell paths and actual source-pixel pickup checks after shared hooks.

Some earlier authored fixtures were invalid: reused enemies retained the
previous actor's collision bit, and a positioned player was put inside the
floor while approaching a capsule. Native-state traces identify these errors;
the real contact and collection assertions remain in the repaired fixtures.
The frame observer also now follows the last constructed image's visibility,
not a newer pose computed by a skipped catch-up update.

## Remaining work

Performance is still open. The two surface routes contain 1,244 / 1,122 video
frames with a lag NMI. These counts do not establish game updates per video
frame or CPU cost; those require a dedicated profile. Scanline-eligibility
analysis still finds extensive partial body dropout, though no completely
hidden body frame in these runs. The four-sprite beam repair does not solve
the complete scene's eight-sprite limit. Optimize body/projectile packing and
measure the result before publication. Preserve source geometry/colors when
possible; do not call a decoded-OAM pixel pass a full screen-visibility pass.

Roll's dedicated music/source audio, exact mobile reference timing, refill
presentation and production oversized-MMC3 integration remain unfinished.
Check other new profiles' CHR publication during skipped drawings; their old
narrow component passes do not prove that transition safe. The final every-
character 1-1 and every-powerup matrix is still required on the completed
candidate. Do not publish this checkpoint as a finished roster build.

## Private performance follow-up NO

The next private candidate is
`build/verification/roll-performance-no/roll-empty-v4.nes`, SHA256
`14b0955db88871be563216fb4ccbff735393ad81cb5f715af54fc45c0a1080ae`.
The published MMC3/MMC5 files and checkpoint NN remain unchanged.

The interior renderer uses the existing source records, preserves rotated OAM
order and retains the general renderer at screen edges and capacity rejection.
It occupies Roll's own code bank. Its admission replaces the unreferenced
Darkwing draw guard and unused legacy padding; the first prototype incorrectly
treated that occupied tail as free and failed to link. The linked renderer
comparison covers 5,904 cases across all 82 body/projectile records, interior
and edge origins, OAM capacity and rotation. Ordered OAM writes, A/X/Y, carry,
stack and bank restoration match. The standard farcall epilogue's identified
N/Z change is reported separately; those flags are overwritten before use in
the real callers. No unexplained status differences are accepted.

The sprite packer chooses a separate horizontal grid per palette and vertical
grid per column. All 68 pose/facing/outline results preserve every visible
pixel from NN, including the exact outlines-off omissions. No colors or poses
are replaced. Examples: standing uses10 sprites with a five-sprite peak instead
of13 with seven; the first walking pose uses8 with a five-sprite peak instead
of12 with nine. Some airborne poses still exceed eight sprites on a scanline.
Four body pools and all existing physical CHR reservations are retained.

Read-only terrain/enemy broad phases avoid repeating the complete collision
dispatcher in clear air. Possible solid cells retain the original native
probe order. Possible enemy contacts retain the original collision/damage
routine, and invalidate the cached envelope before the next shot can reuse it.
Existing exclusive volatile bytes hold the render length/envelope flag; no
additional cartridge WRAM is allocated. The separate compiled broad-phase
comparison is retained under `empty-space-v4-exhaustive.json`:98,304 terrain
cases include every Y byte, and14,400 enemy cases compare skipped contacts
against the actual native collision core. The earlier5,376-case terrain sample
is retained separately; its initial "every terrain row" scope wording was too
broad for the sampled Y positions. The expanded check covers the stated rows.

`performance-proof.json` compares the same Easy controller arena, with the same
test/menu/observer/profiler dependencies, against NN. In its normal-shot phase,
weapon CPU cost drops47.7% (mean3,112.1 to1,626.6 foreground cycles), lag NMIs
drop18 to0, and sprite constructions rise73 to91 across91 video frames with90
movement updates in both runs. CPU spans subtract ISR duration but remain
inclusive of nested foreground routines; they must not be added together.
The charged-shot phase also improves. The block phase still has one lag NMI.
This is bounded evidence, not a60Hz/full-campaign claim.

The current candidate passes Easy/Hard component and physical-reward arenas,
all37 cold entries and all three Parodius component/Bell/pickup regressions.
Both standard14-identity builds retain their exact prior hashes. Independent
Roll replays clear1-1 without death and restore movement in1-2 at4,496 Easy /
4,375 Hard video frames. Their input files exactly match the discovery streams.
One Easy profiled run hit its60-second host limit at frame4,396; that failure is
retained. The identical bounded replay passes with a90-second host allowance.

`camera-route-proof.json` retains a player screen-X maximum112 and no backwards
camera movement. Easy's observed steps are0–2. Hard has one3-pixel step at
frame2,625: the native2.02 fresh-direction2-pixel step and jump/movement occur
together. The player moves the same3 pixels and retains its screen position.
The earlier universal two-pixel camera assertion was too narrow for this
requested source behavior; no movement rule was changed to satisfy it.

The full surface profiles still measure830 /766 lag NMIs across3,016 /2,794
ordinary gameplay video frames. They contain2,700 /2,476 movement updates and
2,186 /2,028 sprite constructions. Partial body scanline eligibility improves
but remains extensive:2,213 /2,010 of3,001 /2,730 observed body frames; none is
fully hidden, and the worst observed eligible fraction is21.4%. These are
actual OAM/CHR/palette checks and first-eight scanline eligibility, not a
complete PPU/background-occlusion oracle. Screenshots are sampled, not manually
reviewed frame by frame. Dedicated audio, remaining lag/dropout, the production
MMC3 integration and the final every-character/every-powerup matrix remain open.
