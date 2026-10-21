# Pit, Rygar and Sophia through World 2-2

Status: baseline mechanics passed; optimization and full-route acceptance in progress.
Controller route candidates, explicit mechanics fixtures and measured performance
are separate evidence. Fixture setup does not count as a level-clear replay.

## Source audit and changes

- Sophia's source is the pinned 2.02
  `reference/crossover2/extracted/scripts/com/smbc/characters/Sophia.as` and
  `projectiles/SophiaBullet.as`.
- `pressSpcBtn()` requires a live on-screen enemy before launching a homing
  missile. The port previously spent a missile and created an untargeted actor
  when no such enemy existed. The Sophia-only target search now returns without
  spending, rejects defeated and flattened enemies, and includes the real
  Bowser/cannon Bullet Bill while excluding Bowser's duplicate.
- A homing missile now searches again when its enemy disappears, is defeated or
  moves offscreen, and retains its inactive expiry when no replacement exists.
- Sophia's three-cannon limit now counts cannon shots independently of her
  inventory missiles, as `pressAtkBtn()` does in 2.02. Removed the obsolete
  Select+B type-7 missile path that bypassed inventory and ammunition.
- Pit and Rygar are custom additions, absent from Crossover 2.02. Their intended
  behavior is the documented ROM contract plus native NES motion evidence.
  `docs/reference/rygar-motion.json` pins the original Diskarmor sequence.

## Mechanics matrix

| Character | Required coverage | Evidence |
| --- | --- | --- |
| Pit | All three arrow tiers; two-shot limit; fresh presses; crouched, ground, airborne and upward arrows; ground/air hammer; flight activation, fuel, roof collision, landing recharge | `pit-attacks`, `pit-fresh-fire`, `pit-flight`, `pit-systems`, `pit-full-performance` |
| Rygar | All three reaches; crouched and airborne throws; both directions; native 4-pixel retraction; moving hand anchoring; chain OAM and terrain return | `rygar-attacks`, `rygar-native-return`, `rygar-systems`, `rygar-walk`, `rygar-full-performance` |
| Sophia | Normal/Hyper/Crusher cannon; fresh presses and three-shot limit independent of missiles; missile triplets/cost; homing live-target gating, retargeting, four-shot limit and ammo; hover/drain/recharge; wall/ceiling upgrades; water steering | `sophia-inventory-202`, `sophia-homing-targets`, `sophia-independent-weapons`, `sophia-fresh-fire`, `sophia-environment`, `sophia-systems`, `sophia-energy-drops-202`, `sophia-full-performance` |
| All three | Native terrain and protected masonry, question-block pickups, enemy health/damage, power transitions, lives portraits, springs/firebars, exits, water and death/respawn | Existing character-specific suites plus uninterrupted 1-1 → 2-2 replay |

Performance tests use real controller attacks after an explicit arena setup.
They report hardware-frame lag and exclusive CPU cycles for update/draw routines,
subtracting time inside NMI/IRQ. Maximum projectile occupancy is asserted.

## Controller-only routes and recordings

`tools/playthroughs/pit_rygar_sophia_policy.lua` supplies read-only telemetry
discovery. `roster_run.py` snapshots ROM, labels and debug symbols. A candidate
is accepted only after its entire recorded controller stream independently
replays from deterministic power-on, visits 1-1/1-2/1-3/1-4/2-1/2-2, and verifies
control in 2-3. Final native-audio recordings must use the frozen final ROM.

No final controller replay, video or frame review is accepted yet.
Rygar has a controller-only development route through the ordinary 1-2 exit
and into 1-3. A genuine-state branch search independently cold-boot verified
the 1-3 lift branch through x1342, including all 10,240 RAM bytes. The policy
tail reached x2055 before falling; this is partial discovery, not a stage clear.
A later v4 route requires different lift timing and is being rediscovered.

## Development checkpoint results

`build/checkpoints/roster-audit-v1` is immutable. Its MMC3 SHA-256 is
`a9e6547edf0902b203572041efca01a28f11ecee91c4da21040877594cf6b6c3`;
MMC5 is `ec5c350bf1c1f4c023ec7a773ad0ae3dbfb6f90bc749f99c6013e5a17a17f7f9`.

- All 44 selected mechanics tests (22 per mapper) passed. The case ledger is
  `build/verification/pit-rygar-sophia-matrix-v1.json`.
- Pit's five ability profiles and Rygar's three profiles had zero lag frames
  in each 180-frame arena on both mappers. Sophia's cannon/missile profiles
  identified substantial lag and are being optimized; hover had zero lag.
- The pre-optimization Sophia differential oracle pins 2,400 terrain, reward,
  boundary, enemy, pool and load outcomes. Its CSV SHA-256 is
  `3cf3c47688fd010cfcc54d5ac6905906d5226fa271e9e68b7c0fc4f0acaddd21`, recorded
  in `tests/sophia-collision-reference.json` with the original checkpoint.
- The new read-only generic audit and video reviewer were smoke-tested on a
  Sophia candidate that clears 1-1 and dies in 1-2. Every one of its 4,941 video
  frames decoded; 3,365 DMA transactions and 3,273 gameplay split frames were
  observed. No split, lag-CHR, motion, vertical-stage or background-flash
  candidates were found. The final-frame sound had no subsequent frames for
  confirmation. This is infrastructure evidence, not a through-2-2 clear.

`roster_audit.lua` logs committed DMA OAM (including its actual bytes), physical
CHR changes, split timing, per-frame audio writes and source/voice ownership.
`roster_review.py` streams MP4/AVI frames, writes a bounded contact sheet and
reports candidates for inspection. It makes no manual-watch or waveform-parity
claim. The workspace was approximately 6.2 GB at this checkpoint.

## Subsequent checkpoint findings

- On v2, all 2,400 Sophia collision outcomes matched the v1 reference on both
  mappers. The terrain dispatch and enemy-candidate caches reduced normal
  cannon update cost from 7,298 to 4,076 cycles on MMC3.
- On v3, normal cannon had zero lag frames in the 180-frame arena, Hyper 9
  and Crusher 8. Their update averages were 3,765/4,270/4,112 cycles. Standard
  missiles (79 lag frames) and homing (70) remain performance work; the common
  compressed music decoder is being optimized before the next profile.
- Committed OAM/CHR pixel checks exposed two primary cannon art errors:
  left-facing shots always selected right-facing pointers, and upward shots
  retained horizontal art. A Sophia-only regeneration now packs the masked
  source normal/Hyper/Crusher pixels in horizontal and upward orientations.
  Both facings have native pointers. All poses still fit the existing four
  logical CHR banks ($ef–$f2); no extra CHR is used. Pit/Rygar's existing left
  weapon poses are also selected when firing left.
- `sophia-cannon-art.lua` checks all twelve cannon tier/facing/aim combinations
  against `tests/fixtures/sophia-cannon-pixels.lua`, frozen from uncompressed
  SWF pixels before NES packing. Runtime confirmation awaits the v4 snapshot.

## V6 source fixes and independent checks

The immutable v6 ROM hashes are MMC3
`af59d2ee599fabe16ff58efa61d14797d382846574f4eaf396f090d7b57a5c3a`
and MMC5
`d23abf5dd86f56454cb8cae83c819cdbbbe2c8525277fbf4e97f3a14ae83c3fc`.

- Source cannon speed is 450 Flash pixels/s, converted to 3.75 NES pixels per
  update. Muzzle fractions retain half-pixel offsets. Attached firing now uses
  the original wall/ceiling direction and position rules. Existing shots retain
  the tier at spawn when an upgrade is collected.
- Committed OAM/CHR pixels match the independently extracted source cannon,
  missile flame/unlit frames, and all five bullet-impact frames. The impact
  sequence includes its intentional blank second frame. Source frames are
  tested across all five live CHR banks and both horizontal facings, with
  quarter-turn orientations.
- Actual controller shots verify ten-update stationary impacts, no repeated
  collision probes during effects, and source NSF explode/hit/kill requests
  18/19/20. The original 17 remaining-weapon sound streams are preserved.
- Homing terrain tests exposed an actual bug: `Bridge` leaves X=0, but the next
  dispatch read `RgShotType,x` instead of the shot in `AvSlot`. Correcting that
  read removes terrain collisions and repeated probes for homing missiles.
- Homing now projects acceleration onto a normalized target vector, chooses
  target distance independently of enemy-slot ordering, reacquires eligible
  targets, and keeps steering force growing beyond the old 120-update cap.
  A real Select-created missile passed 738 updates at an offscreen world
  position. Thirty-six independent cardinal, diagonal, steep and seam vectors
  passed within native fixed-point precision on both mappers.
- All 2,400 v1 terrain, brick health, coin, pickup, player-position and enemy
  health/state/flag outcomes remain exact. The old full CSV hash is retained.
  Only source-correct projectile state changes differ: retained impact actors,
  active-shot counts, cannon speed and fractional muzzle. The comparison ledger
  is `build/verification/sophia-v6-physics-comparison.json`.

| V6 arena (180 hardware frames) | MMC3 lag | MMC5 lag |
| --- | ---: | ---: |
| Normal / Hyper / Crusher cannon | 0 / 1 / 1 | 0 / 0 / 0 |
| Standard missile triplet | 83 | 19 |
| Four homing missiles | 60 | 59 |

The profiles retain maximum actor occupancy, including short-lived effects;
that is distinct from the four active homing-missile cap. Native routines are
measured excluding NMI/IRQ time. Source-correct normalized steering increases
arithmetic work, so an exact multiplication optimization is queued for v7.
The v6 deep profile CSVs are saved beside the checkpoint.

Literal Flash rendering is not claimed: native missiles use four cardinal
orientations rather than continuous rotation, and normalized steering uses
fixed-point precision. Source enemy-death explosion art is not yet included;
the native SMB defeat visual remains, with the source Sophia kill sound.
Controller routes and final native-audio recordings through 2-2 remain open.

## V9 validation and handoff

V9 immutable ROMs:

- MMC3: `cd6d42a882af548635958385921017e1281f57ea6aa3b208724ce689731e02a5`
- MMC5: `3698f98ad503c2f39dd4fb8ca15da0f54892d98d910edf32c38a341e87f18699`

The quarter-square multiplication helper passes **all 65,536 byte operand
pairs on the native emulated CPU**, on both mappers. The 36 normalized steering
outcomes remain byte-identical to v6, SHA-256
`d45188fcad7c184e7db2b62abcc59fd3b66f272796562a553db5d19494b483ed`.
No persistent RAM was added for this optimization.

A pure-controller boot diagnostic caught a decoder history write into low RAM
on v7 when starting Sophia. The root fix in v8 preserves decoder-owned zero
page across `InitializeMemory`, moves its NMI-owned state outside foreground
roster clearing, and reinitializes its character state. The focused read-only
`sophia-poweron-audio` check verifies valid native dispatch and SRAM-bounded
history writes. The root also checks startup for the other compressed characters.

Standard missiles now use cached corner dispatch for collision ID71. Before
editing, the independent v8 missile fixture recorded 2,400 terrain, enemy,
pool and complete projectile-state outcomes on each mapper. Both v9 outputs
remain byte-for-byte identical to that baseline, SHA-256
`11183d3099895c9c0a9a975d5afa03db50fa3da5ae2178dc4f7d24e3044c6d19`.

| V9 arena (180 hardware frames) | MMC3 lag | MMC5 lag |
| --- | ---: | ---: |
| Normal / Hyper / Crusher cannon | 0 / 0 / 0 | 0 / 0 / 0 |
| Standard missile triplet | 70 | 5 |
| Four active homing missiles | 60 | 58 |

The missile terrain-probe average fell from approximately 1,182 to 521 cycles.
Missile update average fell from 5,156 to 3,726 cycles on MMC3, and 4,994 to
3,664 on MMC5. Normalized homing motion fell from about 2,725 to 2,110 cycles
on MMC5. Four active missiles are still a heavy case; substantial MMC3 frame
skipping remains. The profile now reports active projectiles separately from
all occupied actor slots, because source impact effects can retain extra slots.
Both active caps are asserted (three standard missiles, four homing missiles).
The final ledgers are `build/verification/sophia-v9-summary.json` and the deep
profile/missile differential CSVs saved beside the v9 checkpoint.

Current controller-only discovery prefixes, all on development ROMs:

- Rygar v4: `search/rygar-v4-13-finish/winning-inputs.csv` independently verifies
  all 10,240 RAM bytes through frame10288, x2053/Y176 in 1-3. Its policy tail
  `rygar-v4-13-final-tail-7-v0-mmc3` clears 1-3 and enters 1-4 at11234, then
  dies at12001, x1032/Y112. Investigate the firebar/enemy contact there.
- Pit v6: `search/pit-v6-12-enemies/winning-inputs.csv` independently verifies
  through frame6754, x1909/Y176 in 1-2. Tail `pit-v6-12-tail-6-v0-mmc3` clears
  1-2 and enters 1-3 at8594, then falls at9386, x1040. It has collected a
  mushroom (power1) by this point. The next task is the moving-platform route.
- Sophia's earlier development route reaches 1-2; it needs rediscovery on the
  final frozen ROM after the startup and weapon fixes.

All paths above are under `build/roster-through-2-2/`. Branch discovery may use
unedited binary save states; accepted branch CSVs are independently cold-boot
checked without state loads. Candidate tails may use `--discovery-fast`, which
omits heavy audit capture, while final replay/recording must use the full audit.
The shared search now permits valid guest jumps through top-of-screen Y wrap,
keeps genuine inputs until the exact GameLoop snapshot, and preserves combat
state in its beam. No six-stage clear or final video is accepted for this group.

A concrete follow-up for the missing enemy explosion is to append the six source
`SophiaExplosion` frames8�13 as separate world-window art, keeping all existing
art IDs and family bytes stable. An unused `RgShotType=47` effect can reuse the
existing actor position/age storage, advance for12 updates without movement or
collision, and draw through the existing fair world-family selector. It should
preserve bullet impact separately, remove the native defeated sprite, and defer
the source random drop until the effect ends. A free-slot fallback and Bowser's
native victory sequence need explicit tests. Current CHR usage is246/256 KiB on
MMC3 and238/256 on MMC5; source shared-prefix explosions would exceed its32-pair
limit, so this should use the world window rather than enlarge that prefix.


## V14 Sophia enemy effects (source ready, runtime validation pending)

Six private five-byte actors hold source `SophiaExplosion` frames8..13. Source
frame9 is blank, and the animation advances every two native updates; expiry
runs its independent second item-drop check. The original `Enemy.die()` drop
check stays at defeat. Enemies are removed immediately while native points and
kill sound remain. Native Bowser defeat bypasses the effect and temporarily
suppresses item drops even when SMB changes Bowser's identity inside that call.

The pool consumes30 SRAM bytes plus one Bowser-only transient byte. It handles
all six native enemies at once without consuming any of the ten projectile
slots. Only a genuine seventh concurrent death retires the oldest effect early,
completes that effect's pending drop roll, and reuses the slot. This is the
explicit native saturation adaptation. Existing cannon and missile caps remain.

The generator appends six stable IDs95..100 and one 2 KiB world-window family.
All95 prior IDs, prior metasprite records and bank placement, and every old CHR
byte remain unchanged. Snapshots are under
`build/verification/sophia-enemy-effects-pre-v14/`. No ROM was built by this
agent; final linked budgets and runtime behavior await the parent checkpoint.

New fixtures are `sophia-enemy-explosion-art.lua` (independent uncompressed SWF
pixels across all live body banks, including blank9) and
`sophia-enemy-explosion.lua` (real controller attacks with isolated RAM arenas:
Normal/Hyper/Crusher/standard/homing, both drop rolls separately and together,
six concurrent enemies, all ten projectile slots occupied, true saturation,
and fake/final Bowser). These are mechanics fixtures, not controller route proofs.

The prior cannon and missile full CSVs are archived under `tests/fixtures/` with
their original SHA-256 hashes. The revised full hashes are independently
predicted from those controls before running v14: only217 confirmed defeated
cannon targets and297 confirmed defeated missile targets change enemyFlag from1
to0. Every other field of every row remains exact, including enemyState, HP,
terrain/rewards/player state and all projectile bytes. Already-defeated arena
actors (HP40) retain their original flag. `run_mesen.py` enforces this per-row
condition and normalizes only those flags for the historical unchanged-physics
projection; no captured v14 outcome is used to establish its expected hash.


Source pickup pivots are pinned separately: the16px refill sprites have a bottom
pivot. The shared native enemy hurtbox spansY+8..Y+24, so an immediate Sophia
refill's bottom isY+24; PiranhaGreen instead uses its fully-raised bottom minus
half-height (native UpY+16). A delayed refill is centered on the saved explosion
position, with bottomY+8. Origin assertions run before pickup physics updates.
There is a source quirk here: SophiaExplosion is a SimpleAnimatedObject/LevObj,
whose public hMidX/hMidY fields are never populated by AnimatedObject.setHitPoints.
The original second roll therefore passes an object with unset hit-center fields
to appearFromObject. The native effect deliberately supplies its saved valid
center; this is an explicit positioning adaptation, not a literal claim about
that Flash bug.


## V14 focused runtime validation

Immutable hashes: MMC3
`645d52c7431e4a070b1f02ae4077285383f35d06af41a3b74111f3c128a1096b`;
MMC5 `cbc31ff08f9fa5bfe889e4f490eb83def075ff423b7992f9894e603a02e16219`.
Both new explosion fixtures pass on both mappers, including eleven mechanics
arenas and all six pixel frames across all five live body banks. Fake/final
Bowser collision arenas hold the target at the weapon boundary until actualB
lands because an outdoor arena has no initialized native Bowser AI; its defeat
handler executes unchanged. The full through-stage boss route is still open.

Both2400-row cannon and2400-row standard-missile differential fixtures pass on
both mappers with the conditional per-row source correction. Predicted full CSV
hashes (preserving the archived raw CRLF convention) are cannon
`3ef9a3c2e5de04bd6fea39290838d6abf65fb570861573652635e418fd7e8b9f` and missile
`3766fa133e3117674067a20c9c8e7a4cf2e96ac8fddaf3add1e42842339d507f`.
Historical projections continue to use UTF-8 LF. The prediction was derived from
archived rows, not accepted from a new ROM capture. All source impact/lifetime,
immediate energy collection and independent weapon-pool regressions also pass.

Actual linked SRAM ends at$7FB9, leaving70bytes; EXPANDED remains$1FB9, leaving71.
CHR uses250/256 KiB MMC3 and242/256 KiB MMC5. Deep profiles retain all six active
ability cases. Compared with v9, empty effects add36 exclusive cycles to
RemainingWeapons: normal/Hyper/Crusher still show0lag; triplet72/6lag frames
versus70/5 over180frames; four homing60/58 remains unchanged. Summary:
`build/verification/sophia-v14-profile-summary.json`. No performance claim of
eliminating homing lag is made. An optional cached active-effects byte could
replace the six-byte empty scan without further SRAM allocation.

Fresh v14 discovery has Pit clearing1-1 and the normal1-2 exit (stage entries541,
4476,9526) before a1-3 platform failure atframe10320,x1040. The old Rygar v4 prefix
now falls in1-1 at3260,x2477; it is not a current clear. Fresh Sophia reaches883
in1-1 before an enemy collision. All are diagnostic controller streams with no
memory writes and no accepted final recording; final six-stage proofs remain open.


### v14 dry-route discovery continuation (not final proofs)

Pit now clears1-1, the ordinary1-2 exit, and1-3; castle entry is frame12187.
`search/pit-v14-14-first-lava` and `search/pit-v14-14-firebar` winning streams
independently replay from cold boot with all10240RAM bytes matching. The latter
reaches frame12804,x880,Y112. Its policy tail dies at the next firebar,x1028.

Rygar clears1-1 and ordinary1-2, entering1-3 at8565. The final lift required
releasing jump, walking farther along its real support, then jumping late;
`search/rygar-v14-12-late-lift-jump` reaches7338,x2491,Y98 and independently
cold-boots exactly. Earlier roof and no-jump candidates are failures. Current
tail dies in1-3 at9448,x1259.

Sophia clears1-1 and ordinary1-2, entering1-3 at8079. The moving-platform route
now has verified intermediate controllers at9196,x1417,Y96 and9237,x1475,Y112
(`search/sophia-v14-13-lift-hop` best and `search/sophia-v14-13-next-platform`
winning). Both root states have independent cold-boot and complete-RAM checks.
These are physical waypoints, not full six-stage clears. No final video exists.

Additional v14 physical waypoints independently verify from cold boot:
Pit `search/pit-v14-14-second-firebar` (x1141/Y112),
`search/pit-v14-14-last-lava` (13342,x1539/Y128), and
`search/pit-v14-14-firebar-end` (13418,x1727/Y176). Sophia now enters1-4 at10665;
`search/sophia-v14-14-firebar-timing` reaches11229,x790/Y112. Rygar
`search/rygar-v14-13-high-cap` reaches9529,x1342/Y96,
`search/rygar-v14-13-last-caps` reaches9957,x1901/Y112, and
`search/rygar-v14-13-exit-caps` reaches2111/Y64. Existing generic tails remain
failure diagnostics; no all-stage or video claim is made. Parent requests v14
geometry work until the shared v17 checkpoint is ready.

Rygar enters1-4 at11215 (`rygar-v14-tail-exit-caps-7-v0-mmc3`) without deaths;
its generic controller tail passes the opening lava and first firebar, then dies
atx1032. Pit reachesx1917 before Bowser-fire contact; the corridor landing at
13418,x1727/Y176 is a verified branch, not a castle clear. Sophia's second
firebar is solved at11577,x1120/Y112 (`search/sophia-v14-14-second-firebar`),
with independent cold-boot and10240-byte RAM comparison. All use immutablev14
MMC3 and ordinary inputs, with unedited opaque states only during discovery.

Pit v14 now clears the real1-4 axe sequence and enters2-1 at14771. The controller
branch `search/pit-v14-14-bowser-cross` reaches13852,x2256/Y55 and independently
replays from power-on with all RAM identical. Its policy tail collects a2-1
powerup (power1) and later falls at16481,x1744 in the first gap. The cautious
arrow-only attempt is retained as a failed controller route, not a mechanic
failure assertion. Sophia's verified approach reaches12308,x2080/Y128; its
generic tail collides with Bowser while jumping at12406,x2135/Y65.

Verified next waypoints: `search/pit-v14-21-first-gap` reaches16489,x1834/Y144
with power1 in2-1; `search/sophia-v14-14-bowser-cross` reaches12435,x2255/Y75
on the far side of Bowser's bridge. Both new winning streams match independent
cold-boot execution and all10240RAM bytes. Rygar's64-frame ordinary Down pause
before the central firebar creates a better phase; the retimed controller branch
`search/rygar-v14-14-center-retimed` reaches12354,x1363/Y128 exactly. Its later
policy tail still dies at the last firebar x1565, so the castle remains open.

Pit reaches the2-1 spring atx3025 but the generic policy jumps off to the right,
then repeats normal jumps until timer000 (frame24799). This is active gameplay,
not a hardlock. A dedicated controller search lands on the spring, presses a
fresh A during compression, and finds x3061/Y9 above the tall wall. Independent
verification of that newest segment is pending at this note. No ROM/RAM/register
writes were used. Sophia's2-1 enemy segment verifies to14554,x1461/Y48.

The Pit spring segment now independently verifies (17945,x3061/Y9), and its dry
finish tail is running. This is a source-correct fresh A during real compression,
not a RAM velocity fixture. `pit_rygar_sophia_dry_policy.lua` is a self-contained
ordinary-input copy that returns no buttons in water while the shared v17 build
is pending. Rygar's Bowser crossing independently verifies to13159,x2255/Y65;
Sophia's first2-1 gap/Piranha sequence verifies to1914/Y176. New dry tails use
those exact controller prefixes, and all final capture remains held.

Source boundary audit: `reference/crossover2/extracted/scripts/com/smbc/enemies/Enemy.as`
line407 selects the Sophia explosion when the defeating argument is
`param1 is SophiaBullet`; it does not check the selected character. Block/shell
defeats and stomp therefore retain native defeat visuals. The scoped projectile
hook is intentional and complete for the audited Sophia projectile types; no
global selected-character death hook is required. Bowser still forces the native
victory path.

Pit dry route reaches active2-2 at19188, lives2/deaths0, after clearing all five
land stages. `pit-v14-tail-spring-dry-6-v0-mmc3` ends at19500 with no buttons in
water: result cleared=false, all_six_stages=true, verified_through_2_2=false.
This is a dry-route candidate, not a2-2 completion or final full-audit proof.

Rygar now clears the actual axe sequence and enters2-1 at14066; its current
generic tail dies at15950,x1855 while crossing the first gap/Piranha pipe. Sophia
passes that obstacle with its verified branch and reaches the spring/tall wall
atx3025 with power1. Its dry tail stays active until the20000 frame cap. Both
need their remaining2-1 controller segments before v17 retiming.

### Resume handoff after bounded jobs (v14 MMC3)

All owned emulator jobs have exited. No ROM, source, or art edits are pending.
Root requested this slot for urgent shared weapon/camera fixes; do not launch
new routes until resumed. Final water testing and final capture remain held.
Machine-readable frontier metadata and exact SHA256 values:
`build/roster-through-2-2/pit-rygar-sophia-handoff-v14.json`.

| Character | Saved ordinary-input prefix | Actual frontier | Verification |
| --- | --- | --- | --- |
| Pit | `build/roster-through-2-2/prefixes/pit-v14-dry-through-2-1.csv` | active2-2entry; water idle only | Independent prefix through17945; later dry tail is discovery only |
| Rygar | `build/roster-through-2-2/prefixes/rygar-v14-dry-to-2-1-piranha.csv` | {'frame': 15882, 'poll': 15882, 'x': 1937, 'y': 176, 'state': 0, 'power': 0, 'world': 1, 'level': 0} | Independent cold boot; all10240RAM bytes identical |
| Sophia | `build/roster-through-2-2/prefixes/sophia-v14-dry-to-2-1-spring.csv` | {'frame': 16215, 'poll': 16215, 'x': 3062, 'y': 0, 'state': 1, 'power': 1, 'world': 1, 'level': 0} | Independent cold boot; all10240RAM bytes identical |

Pit clears1-1, normal1-2,1-3,1-4 and2-1, with active2-2 entry19188 and no deaths.
Rygar's final bounded job clears the first2-1 gap/Piranha obstacle; its real1-4
axe sequence and2-1 entry14066 are in the same contiguous controller history.
Sophia's final bounded job clears the2-1 spring/tall wall with power1; its real
1-4 axe sequence and2-1 entry13314 are in the same contiguous controller history.
Neither newer character has a final2-1 flag finish yet. All three need fresh
retiming on the eventual frozen ROM, full frame auditing,2-2 completion, active
2-3 control, and native-audio recording/review.

The currently passing Sophia mechanics/art/oracle batch is already in v14 and
passed both mappers. Native non-projectile defeat visuals remain intentional:
source Enemy.as selects SophiaExplosion only for a SophiaBullet defeating
argument. Do not add a global selected-character death hook. No source change
was made for that resolved audit concern.

### Checkpoint22 retiming restart

Frozen MMC3 SHA256:2ec13bcac6c9c60a37096b0b5e2377c771c345b54325dd26c602c8cfc059debf.
Pit v14 dry input candidate still clears1-1, but active1-2 begins4460 versus4476.
The earliest position/camera difference is1163 (oldx729/Y95/camera617; new
x728/Y96/camera616). The unshifted candidate dies at5518,x730. Removing16
ordinary input frames at the1-2 entry passes that obstacle but later collides
with the triple Goombas at6606,x1544/Y176. These are controller-route failures;
no source regression is asserted. `pit-v22-12-goombas` is a bounded unedited-state
discovery from the actual roof at6520, with independent cold boot required before
reuse. Only one emulator is run at a time for this agent. No runtime/art changes.

Checkpoint22 Pit progress: the new triple-Goomba controller branch independently
verifies to6688,x1670/Y128. Its tail clears the ordinary1-2 exit (1-3 entry8942),
then fails at the first1-3 gap. A new independent branch reaches9741,x1140/Y112.
Retiming the old successful1-3 controls from that cap crosses both moving
platforms; the next collision is the high-cap Koopa at10215,x1694/Y80. Fresh
controllers from10150 now independently verify to10320,x1841/Y176 after clearing
that cap. All proof checks compare10,240RAM bytes, use opaque unedited discovery
states only, and fresh controller-only verification. No source/art changes.

Pit22 exit-cap controls now independently verify to10470,x1991/Y112. A staged
ordinary-input castle candidate, copied into a self-contained policy and keyed
to the new castle entry, clears1-3 and every castle firebar/platform section.
Castle entry is11499. The remaining Bowser collision at13144,x2224 is retimed by
an independent controller branch to13163,x2256/Y70 on the far side. All10,240RAM
bytes match its fresh cold-boot replay. The next candidate uses the previous
2-1 controller history relative to the new2-1 entry; water controls resume only
after actual progression. No v14 binary states are reused on22.

Pit22 clears the real1-4 axe sequence;2-1 entry14083. The old2-1 ordinary-input
section relative to that entry passes the gaps/enemies but misses spring
compression, causing an active-game timer death atx3025. A new branch from
17260,x2994/Y136 independently verifies the spring boost to17349,x3091/Y0.
Its complete controller prefix and all10,240RAM bytes match fresh power-on.
The next candidate uses normal controller water jumps and does not press Down
at Pit's water exit (Down there would crouch; vertical steering is Sophia-only).
No ROM/RAM/register patches or runtime source edits.

Pit22 five land stages now clear: actual2-2 entry18563. The first water
controller tail reachesx905/Y144 at19182 and dies during a Blooper encounter.
This is a route collision, not an asserted engine defect. A fresh bounded branch
starts from actual poll19070 before the encounter; normal jump/shot/wait/left
inputs only. No source/assets changes, no recording yet. Production22 is frozen
and accepted by the parent623-slot verification manifest.

The first22 water branch now independently verifies at19335,x1131/Y96,
state0/power0. Exact fixed-controller polls, target and all10,240RAM bytes agree
from fresh power-on; discovery root states remain opaque and unedited. The
next controller-only tail starts from that standing coral. Route prefix:
`search/pit-v22-water-blooper/winning-inputs.csv` (SHA256
71e97a8f840f709f0f03c3b5df9b63ef0e143e536233301ebaa8a26d4257da42).

The second water controller branch independently verifies through19660,
x1501/Y176, grounded/power0, beyond the hanging coral/fish encounter. All10,240
RAM bytes and fixed controller timing match fresh power-on. The next tail
continues toward the tall2064/2096 coral and bridge. No production edits.

The two-step bridge controller helper passes the lower2064 coral, tall2096
stem and bridge. Next death is21025,x2481/Y105 beside the far coral/fish.
The old discovery policy releases A after34frames, reachingY56 from floor176,
8pixels too low to clear the far coral top80 (player needsY48). The next
controller tail holds the existing water jump longer; no physics edits.

Pit22 controller candidate clears all six stages with zero deaths and real
2-3 movement. Entries:1-1=541,1-2=4460,1-3=8942,1-4=11499,2-1=14083,
2-2=18563,2-3=22752; endpoint22776,x76/Y176 active. The complete22775poll
stream is saved as `prefixes/pit-v22-complete.csv`, SHA256
`da4361c049045566dfaf823563134cf50cfe97a1d8ce81fe7f5cadebab1d3520`.
Full independent fixed replay with per-frame OAM/CHR/split/APU audit is running.
This is still a candidate until that replay passes; no final video yet.

The independent fixed Pit22 full replay PASSES22776frames,22775polls, zero
deaths, all6stages and actual2-3 control. Every physical-frame telemetry audit
has0badHUDsplits,0lagCHRchanges and0unconfirmed22343audioevents. However,
six16pixel castle displacements at12681..12686 invalidate visual acceptance.
Recording is held. Actual controller-only write-PC probe confirms SamusStopAtWall
Left: STA$75 at$EA4A (writecallbacknextPC$EA4C), bank1, R0=2, Local_eb33,
X1567→1663 with no directionalinput. Feet below the thin ceiling areempty;
upperleft sideprobe(+1,+12) hits$62 at(1568,77). Evidence:
`pit-v22-snap-probe/writes.csv`, `contact-summary.json` and4boundedPNGs.
Parent owns shared collision repair; no runtime/assets changes by this agent.
The full22 proof remains diagnostic, not accepted final recording.

Pit uncrouch regression matrix: `tests/pit-crouch-clearance.lua` authors48
explicit blocked/open ground/air arenas, mirrored facings, row/page seams,
stationary/moving releases. Transitions use actual controller inputs. Both22
mappers reproduce the16pixel zip at case1/age4. Both23 candidates pass the12
blocked-air cases, then fail blocked-ground case13: retained short body cannot
leave the tunnel because the existing Direction path zeros all crouch movement.
Right+B for180updates leavesX1263/Y176 unchanged; arrows still work. Parent
owns the follow-up source fix. Full original Pit22 controller stream is also
being replayed on23 as diagnostic; no final recording accepted.

Strict fixture v2 (SHA256 a22b5c4be76f85c5de62cccb04e034a95765adefb213f9a3c4f52c559e647e89)
passes all48 cases on BOTH24 mappers. Both22 controls still reproduce+16 X at
case1/age4. Checks include actual short/full rectangle coordinates, prompt
clear-space stand, release-retained ground/air movement, deliberate Down stop,
primary arrows and normal jumps after clearance. Summary and archived rows:
`build/checkpoint-tests/pit-crouch-clearance-v2-v22-v24/summary.json`.
Parent owns source changes. No production source/art edits from this agent.
Full actual-controller Pit22 stream is now being evaluated on24 with full
read-only audit; no recording until that route is retimed and accepted.

Pit24 retimed controller route passes the underground Goomba group and narrow
pillar using independently cold-boot-verified ordinary inputs. The pillar
target is7053,x1967/Y128, grounded/power0; all10,240RAM bytes agree. Actual
entries are1-2=4460,1-3=8769,1-4=11324. The former castle air-crouch ceiling
passes without the six16pixel displacements; the next old-input failure is a
normal castle hazard at12735,x1841/Y144. Bounded controller discovery resumes
before that raised-platform/firebar encounter. No production source edits.
Final video capture is held globally by the parent until every roster route
has passed its full fixed audit; a successful Pit proof will be preserved first.

The first firebar branch target12830,x1965/Y128 is exact but unsafe: a Bowser
flame defeats Pit on the next update. It remains diagnostic, not a safe route
claim. The replacement branch starts at the earlier first-cap landing and
independently verifies12889,x2050/Y128, beyond the whole platform/flame
encounter. All10,240RAM bytes agree from power-on. Accepted branch evidence:
`search/pit-v24-castle-flame-cap/`. The next ordinary-controller tail resumes
from that later target. No production changes or recordings.

Pit24 ordinary jump/fire masks clear the real Bowser/axe sequence;2-1 entry
is13992. Read-only position scan through14640 has zero active motion jumps
above8pixels X or16pixels Y. A normal Goomba collision atx923 is replaced
by the independently verified `search/pit-v24-21-goomba/` controller branch:
14738,x1090/Y176 grounded/power0, all10,240RAM bytes exact. The next tail
continues toward the spring and water stage. These candidate runs omit heavy
render telemetry for discovery; final complete fixed full audit is still due.

Pit24 controller branches now verify through the2-1 pipe-cap/gap Goomba and
late enemy group. Latest independent target:16442,x2840/Y128, grounded,
power0 (`search/pit-v24-21-last-enemies/`), all10,240RAM bytes exact.
`pit_v24_spring_water_policy.lua` is ordinary controller logic only: align the
spring, release A through native compression frame1, press fresh A at frame2,
then steer right after the boost. Its actual spring/water tail is being tested.
Runtime and assets remain unchanged; final capture is globally held.

Pit24 clears all five land stages with the full native spring boost, waits
before the pole to descend into ordinary contact, and enters2-2 at17939.
Water branch `search/pit-v24-water-coral-blooper/` independently verifies
19836,x2074/Y112, grounded/power0, all10,240RAM bytes exact. The bridge
controller releases A until the actual consumed button clears, then mounts
the tall stem and walks the bridge. A jump fromx2208 clears the Blooper
that defeats a simple walk-off atx2262. The latest candidate reachesx2421
before a fish collision; discovery targets the first far cap atx2510/Y48.

IMPORTANT: Parent source audit now requires ordinary guest body contact to
injure instead of granting Mario stomps (Character.canStomp=false). Final
fixed proof and all recordings are held for that coherent source checkpoint.
The24 route is geometric/controller candidate evidence only. Pit flight, Rygar
Diskarmor animation and Sophia attachment/hover have no extra protected body
move. Square1SoundQueue bit4 cannot identify Pit stomps: his arrow feedback
also uses it, so use guarded EnemyStomped PC evidence if auditing old routes.

Stopped24 water discovery per parent contact-fix freeze. Latest independent
first far-cap proof is20238,x2533/Y48, all10,240RAM bytes exact. Candidate
passes both caps and reaches2703/Y99, then dies to a fish at20425. Exact
ordinary input stream, milestones and pending scopes are preserved in
`build/roster-through-2-2/pit-rygar-sophia-handoff-v24.json`. No recording.

Read-only full audit now emits `stomp-events.csv` and explicit empty-capable
`stomp-summary.json`; final replays reject ordinary native stomps for every
guest. The hook checks resident LDA Enemy_ID,X / CMP Spiny, logical bank0,
active mode/engine, nested IRQ/NMI depth and indexed slot/HP. Component guards
pass both mappers. Actual old24 contact arenas retain12 Mario/Luigi native
controls then flag the first guest stomp on each mapper (13 events,1 illegal,
zero opcode mismatches). Old Pit24 controller replay independently flags a
real illegal stomp at1215,x800/Y171, slot2 Goomba x794/Y184. All1215 trace
rows and1214 input rows are byte-identical to the previous run. This is an
expected old-build negative, not a final level proof. Registry name for parent:
`roster-stomp-audit`; validated summaries under checkpoint-tests/stomp-audit-guards-v24.

Resume38d ordinary-controller audit (component37 is not roster certification).
Runtime is immutable build/checkpoints/roster-audit-v38-provisional-d, MMC3
SHA256 850936f1b58047da23ef2f02243f66efe9eaa8d879ca97f912752aadbe83309a.
Fresh policy pit_38d_policy.lua retains geometric helpers but contains no
old-hash controller movie. A new power-on run reaches1-1 X800/Y171 at1215
and correctly dies to the Goomba body contact that24 wrongly stomped. A
controller branch begins before that pipe/Goomba encounter. No emulated
state mutation, runtime changes, or final capture is authorized for this work.

Pit38d first Goomba/pipe branch independently verifies1358,x1020/Y176,
grounded/power0, all10,240RAM bytes exact. Normal1-2 entry is4430; all
active1-1 frames remain outdoor AreaType1 (no shortcut). The later1-2
Piranha branch verifies7190,x1792/Y176. Fresh controls clear the ordinary
1-2 side exit and enter1-3 at9083. Treetop enemy branch (tag13-koopa-a;
actual screenshot enemy is a Goomba) independently verifies9740,x934/Y128,
grounded/power0, passing that enemy and the first moving platform. Each
branch is independently cold-boot certified against this exact38d ROM and
all10,240RAM bytes; no old24 state is loaded or relabeled. Source unchanged.

Pit38d next certified controller endpoints: vertical takeoff from the question
block reaches the upper cap at9802,x1000/Y48; the later moving-platform
branch reaches10354,x1698/Y80. Generic Right then collides with the adjacent
Koopa, so that endpoint was treated as diagnostic only. A fresh ordinary
retreat/jump/fire branch clears the Koopa and independently verifies10569,
x1953/Y112, grounded/power0. All three cold boots match all10,240RAM bytes
and exact38d inputs/target. No source changes or video captures.

Pit38d fresh continuation clears1-3 and enters1-4 at11586. First generic
castle failure12100,x740/Y112 is a visible ordinary firebar-tip contact.
The independently certified first-bars branch reaches12328,x1000/Y112,
grounded/power0. Continuing Right dies12367,x1050/Y112 to the next rotating
firebar. These are controller-navigation failures, not unexplained zip or
collision defect claims. Failed streams/screenshots remain preserved.

Pit38d middle-bars branch independently verifies12657,x1416/Y128. Normal
controls then reach the Bowser approach; fireball contact at13083,x2014/Y99
is preserved as a failed candidate. A fresh branch independently verifies
13238,x2255/Y51 (air) over Bowser at the axe platform, all10,240RAM bytes
exact. The ordinary victory tail has not yet been tested; no complete proof.

Pit38d actual victory tail enters2-1 at14144; the four World1 stages use
ordinary exits. First2-1 enemy-group landing dies14557,x649/Y169. An
independent read-only contact observer separately repeats the exact castle
prefix and logs the12890 horizontal correction,1756 to1745, at bank10
post-STA PC$A2A2 (R0=1,Local_eb=$23,Y77). The transient bumped block
cell1760/Y80 is under parent geometry review; it is not called a defect.
No route input was changed to hide this correction; no runtime edits.

Pit38d first2-1 group/pipe branch independently verifies14789,x900/Y112,
grounded/power0, with all10,240RAM bytes exact. The endpoint is atop a pipe,
not a claim of future safe passage; the next ordinary continuation is pending.

Castle correction classification completed with parent geometry review:
12888/12890/12892 PNGs and contact-writes.csv in pit-38d-castle-contact-a-6-v0-mmc3
show an arrow activating a hidden coin block ($5F) to transient solid$23 at
12889 while Pit overlaps it. Native table/guards: src/collision.s:282,1270,
1346,2003 intentionally skip hidden blocks before activation. Actual bbox12
is left1/right15; after the wall appears at1760, playerX1745 places X+15
exactly on that boundary. The bank10 PC$A2A2 write1756->1745 at12890 is
valid local separation from a newly appearing solid, not repeated traversal
or a teleport defect. Inputs/oracle were not changed to conceal it; no
runtime patch is warranted by this evidence.

Pit38d later2-1 independently certified endpoints:15863,x2021/Y128;
16676,x2892/Y176;16728,x2970/Y112. The2892 endpoint has another Koopa
close ahead and was extended with a separate ordinary retreat/jump branch,
not assumed safe for genericRight. Every branch matches all10,240RAM bytes
from an independent power-on replay of its exact controller CSV. The2970
endpoint is the brick ledge before the spring; spring/pole tail pending.

Pit38d completed ordinary candidate and independent fixed-input FULL AUDIT:
pit-38d-full-audit-a-6-v0-mmc3 verifies all six stages,22234frames/22233polls,
zero deaths/failure, active2-3 control after entry22210. Entries:1-1=541,
1-2=4430,1-3=9083,1-4=11586,2-1=14144,2-2=18131. Complete CSV preserved
at prefixes/pit-v38d-complete.csv, SHA256
caaa80b66af7e8657f0bd3b0a3eae48f1806383529844ae29a0213fdf4a573e6.
All active1-1/2-1 frames retain outdoor AreaType1, excluding bonus/shortcut
entries. Review finds zero split timing or lag-CHR flags, zero native stomps
(including zero opcode mismatches), and24,295 audio source events all with
voice+physical writes; zero unconfirmed events. The only motion flag is
12890, the separately proved valid born-solid separation above.
This is exact38d controller/telemetry certification only: no video was
recorded, pixels were not decoded, and waveform parity/human frame-by-frame
watching are not claimed. Native-audio final captures remain held. Rygar
and Sophia38d routes remain pending. Bound handoff:pit-rygar-sophia-handoff-v38d.json.

Rygar38d fresh ordinary-controller discovery starts independently of Pit.
Own rygar_38d_policy.lua uses currently collected Diskarmor reach for enemy
braking. Initial cold-a syntax typo is preserved, corrected before cold-b
actual play. Cold-b dies1063,x803/Y169 in the1-1 pipe/Goomba section.
Fresh controller branch independently verifies1224,x1020/Y176; full normal
continuation enters1-2 at3927, then dies4935,x1147/Y169 at the Goomba pair
before the first underground roof/gap. No source/shared-tool changes.

Rygar38d first-roof-a cold-boots but reaches1410/Y0 on the ceiling and is
explicitly REJECTED as a normal-route continuation (route-qualification.json).
The first lower-roof-a retry starts too late in that committed higher jump;
its failed goal remains preserved. Lower-roof-b starts at original4860 and
withholds a second jump: its certified best5028,x1258/Y176 is a legitimate
floor prefix even though the requested higher goal was not achieved. From
that independently bound best root, lower-gap-a verifies5129,x1410/Y80 on
the lower bridge. Own policy walks off that bridge without another ceiling
jump; full prefix trace confirms zero underground grounded frames below48.
Fresh pipe/pillar branch independently verifies5686,x2033/Y176 after a
Goomba landing failure5514,x1821/Y169. All10,240RAM bytes exact per branch.

Rygar38d later underworld route: tail-pillar-a makes an extra jump onto the
ceiling and is rejected; tail-pillar-b suppresses too many jumps and falls
6029,x2485/Y243. A bounded read-only platform observer preserves actual
slots/positions/contacts in rygar-38d-lift-observer-a-7-v0-mmc3/platforms.csv.
It distinguishes the static ledge (playerY96) from native rising lifts
ID$26 atX2476 and descending lifts$27 atX2236. Own policy now permits
the required ledge jump and suppresses the extra high-lift jump only when
PlatformCollisionFlag matches the actual standing native slot.
tail-pillar-c clears the normal1-2 exit and enters1-3 at7305, with zero
underground grounded frames below48; no ceiling bypass. It falls8103,
x1148/Y244 before the small treetop. Fresh ordinary branch independently
verifies8085,x1141/Y112. Its tail misses a moving platform8316,x1455/Y242;
a bounded ordinary brake/landing search is active. No runtime defects claimed.

Rygar38d subsequent ordinary branches independently certify8422,x1612/Y144
after the late moving platforms,8740,x2012/Y112 after the upper enemies,
and10776,x1381/Y128 after the castle firebars. The intervening ordinary
tail enters1-4 at9724. All branch independent cold boots preserve every
10240 RAM byte. Latest tail dies11224,x2037/Y128 to the Bowser bridge
approach fireball; bounded ordinary jump/shoot timing search follows.
No runtime defect or full Rygar proof is claimed. Pit full38d proof remains
unchanged and no final captures are authorized.

Rygar38d bridge-a independently verifies11541,x2261/Y112 on the far
castle platform. Bounded duck/jump/shoot timing uses ordinary buttons,
and all10240 RAM bytes match independent power-on replay. This is a
controller branch endpoint, not yet a complete Rygar route proof.
Continuation tail-bridge-a is running toward2-1.

Rygar38d tail-bridge-a enters normal2-1 at12260 and survives early
enemy groups. It falls13570,x1741/Y244 after its pipe jump starts
too early for the following middle gap; ordinary timing branch
rygar-38d-21-middle-gap-a starts13450. No runtime bug is claimed.

Rygar38d middle-gap-a independently verifies13631,x1810/Y176 past
the middle pipe/gap. All10240RAM bytes and exact frame/controller polls
match. The prior full ordinary tail has zero horizontal frame steps over
8px during same-stage active gameplay. This trace scan is diagnostic,
not a replacement for the eventual exact full-frame replay audit.

Rygar38d later-gap-a independently verifies14274,x2530/Y176,power1
past the raised landing. Controller polls/frame and all10240RAM bytes
match cold boot. Upgrades were naturally collected at10086 (castle,
then lost before the bar endpoint) and13921 (2-1,x2048/Y119).
Fresh ordinary tail continues toward the paratroopas and spring.

Rygar38d tail-late-gap-a survives the paratroopas (losing the upgrade)
and reaches the2-1 spring. Generic inputs make repeated weak bounces
atX3025, then timer death22042. spring-policy-negative.json binds the
observed range. Own policy now applies the already source-native Pit
spring timing to Rygar: A release at compression1, fresh A compression2.
No runtime change, register/RAM patch or edited state is involved.

Rygar38d revised spring controller timing clears the full boost and
normal2-1 pole. Water2-2 entry is16179. tail-spring-b dies17151,
x1249/Y88 to a Blooper while rising onto the middle coral. The genuine
dry prefix to2-2 is preserved as rygar-v38d-dry-to-2-2-candidate.csv;
it is qualified discovery input evidence, not a full strict proof.
A bounded ordinary combat/vertical timing search starts17090.

Rygar38d mid-blooper-a independently verifies17348,x1501/Y176 in
2-2. Exact polls/frame and all10240RAM bytes match cold boot. Candidate
normal-route scan still has onlyAreaType1 in active1-1/2-1 and zero
underground groundedY<48; complete full-audit proof remains pending.

Rygar38d tail-water-mid-a reaches the tall2064/2096 coral route and
lands the upper bridge. It dies18144,x2196/Y32 to a fish while walking
that bridge. A bounded ordinary duck/throw/wait continuation starts
18080; no runtime defect or changed game physics is inferred.

Rygar38d bridge-fish-a independently verifies18277,x2340/Y144 after
the upper bridge and fish encounter, using ordinary controls with no
jump in that local branch. Every10240RAM byte matches cold boot.
A fresh tail continues to the final water caps and ordinary exit.
A further19 completed owned Rygar DBG duplicates were losslessly
gzipped and round-trip/hash verified;217562578bytes saved. All actual
ROM/input/state/RAM evidence remains, with per-folder restore receipts.

Rygar38d tail-water-bridge-a passes both far coral caps and reaches
the last ordinary pipe approach. It dies18987 to a Blooper while
jumping toward the exit ledge; fresh local timing search starts18920.
No game/runtime source changes or final recordings.

Rygar exit-blooper-a local search setup is REJECTED: requiring grounded
active engine8 atX3000+ does not model the ordinary pipe landing, which
immediately becomes engine2. Pit full38d trace21012..21021 independently
showsX3000/Y93 air engine8 thenX3010/Y112 grounded engine2. Current best
3033/Y0 is an exit-wall roof endpoint and is excluded from normal-route
lineage. Only that owned search process was stopped; the runner remains
alive to independently verify and preserve its rejected best. No emulated
memory/register/state mutation. A new original-root airborne approach
goal will be used, followed by mandatory ordinary pipe continuation.

Rygar exit-blooper-b bounded search also fails the corrected pipe-height
air goal; its independently replayed roof best3033/Y0 is excluded.
A new ordinary-controller candidate reuses only the earlier genuine
inputs through18970, before the roof, then brakes besideX2988 until
falling toY88 and movesRight into the mouth. The entire candidate is
replaying from power-on; actual pipe entry and whole audit still required.
The rejected roof endpoint state is never loaded by this candidate.

CORRECTION to the earlier exit-goal diagnosis: actual successful Rygar
trace19084 isX3008/Y112/state0/engine8, followed by normal pipe engine2
at19087/X3010/Y112. Thus the original grounded search goal WAS reachable;
the earlier inference from Pit's faster entry was overbroad. Both roof
best endpoints remain excluded, and all original search evidence stays.
No runtime defect or impossible goal was proved. Successful candidate-d
preserves the Blooper-avoiding wait through18993, then air brakes beside
the mouth. It clears all six stages, active2-3 at20204, final20228 with
zero deaths. Zero underground groundedY<48 and zero water exit-roof
grounded frames. Exact full-frame replay rygar-38d-full-audit-a is now
running; completion/recording is not yet claimed.

RYGAR38d STRICT WHOLE-REPLAY PASS: rygar-38d-full-audit-a-7-v0-mmc3,
20228frames/20227polls, zero deaths, active2-3 at20204 with25 control
frames. InputsSHA0416b40e78f5c0c5978529aa2dc204c607eb80c025bc3419b005bfc8fbb20929.
Frozen38dMMC3SHA850936f1b58047da23ef2f02243f66efe9eaa8d879ca97f912752aadbe83309a.
Exact independent replay, full-frame read-only audit, no states or emulated
writes. Source stomps0/opcode mismatches0, split flags0/CHR flags0.
Both motion flags14875/14937 are unsigned-to-signed16 spring coordinate
wraps (YHigh0<->255), actualdy+/-4, preserved in signed classification.
Own policy temporarily omitsRight during that deep-negative interval;
no runtime input-loss claim. All12372audio events have voice+physical
writes; waveform/listening parity is not certified.1675active lag NMI
frames,966sprite-overload frames remain measured. No video was recorded.
Normal exits:1-1/2-1 onlyAreaType1, underworld groundedY<48 count0,
water exit-roof grounded count0, normal pipe entry19087/X3010/Y112.
Sophia fresh38d ordinary-controller discovery starts next.

Sophia38d fresh cold run clears1-1, enters1-2 at4103, and dies5719
X1667/Y119 at the pipe enemy group; no underground roof frames. A real
shared HUD corruption is independently reproduced by fixed controls,
first active bad4499/X485/Y39 in1-2, well before death. Passive observerC
records actual foreground SetupNums STA8BA4 (physicalPRG62) publishing
20 at old terminator04C0, interrupted before low/length. NMI consumer
WriteBufferToScreen reads202400 and zero count streams256bytes intoHUD.
Producer resumes with intended timer address207A/length3 after NMI.
Firstbad nametable/CHR/palette/RAM/PNG and all guarded producer/consumer
PPU receipts remain in sophia-38d-hud-cause-c-11-v0-mmc3. ObserverB
first-bad trigger was an instrumentation negative (TIME atcol25, not26);
raw snapshots remain, qualification explains it. Root owns runtime fix.
ObserverD now binds busy/skip/draw flags at GameLoop/catchup/NMI/SetupNums
to prove the suspected unprotected catchup path before a shared patch.
No runtime/common-test changes from this agent, no final recordings.


Passive HUD catch-up receipt (2026-10-18):38d flow-D proves GoToNextFrameImmediately and second GameLoop entry with NmiDisable0/NmiSkipped96/drawSkip1. SetupNums publishes high20 at cycle133950325; NMI entry133950332 consumes partial202400 at133950876; producer low7a/count3 resumes133959825/834. Background CHR0..4095 is unchanged against prior4498. Bound packet hud-causal-receipt.json. Accepted41 first exact-input probe E is a qualified negative through4502, with earlier1-2 entry4093 and different motion. F extends the same original controls/passive logging; root owns runtime fix.

Accepted41 F passive replay completed at actual controller death5247: static HUD remained intact, no nativezero-length header consumed. This is a qualified corruption-negative, not a reproduction. Actual ownership positive:18 SetupNums entries withbusy0/drawSkip1; accepted41 catch-up/second GameLoop entries likewise remainunprotected. Full hashed packet: sophia-41-hud-catchup-f-11-v0-mmc3/hud-catchup-receipt.json. Original38d causal receipt remainsseparate. No runtime edits or finalcapture.

HUD41/42a paired diagnostics:original+four1..4neutral titlepadding controls, everycase poweron and sourceguarded;41 had no malformednativeconsume/staticlabelcorruption, but unsafe producerownership.42a allobserved protectedbodies andSetupNums busy255, no malformedcommands/staticlabeldamage. Important responsiveness correction: one inputPolled event/frame means hostdelivery, NOT actual native4016 sampling on skippedNMIs. Prior one-actual-read/frame wording withdrawn; v1receipts preserved, qualified receipts supersede. Native OAM/4016 sampling supplement isrunning41then42a with8-bit completedreads andSavedJoypad history. No routeproof/finalcapture.

Native controller supplement complete41/42a, sameoriginalcontrols andpoweron: bothtraceCSV andinputCSV byteidentical to unsupplementedcases.41:4609 completedguarded native8-bitreads, maximumactivegap2frames, all-mode5 duringtransitions.42a:3934 completedreads, maximumactivegap5frames (1237..1242,1-1X953..961 and4194..4199,1-2X116), all-mode6 duringtransitions. Eachhasmatching4016 high/lowstrobes andexactly8port1reads. This establishes bounded responsivenesscost; no unboundedstarvation claim and no1read/frame claim. Longintervalsin native-long-input-gaps.json; pairboundin sophia-native-controller-41-42a.json. All5candidate commandcases protected23408bodies/3995SetupNums, zerounprotectedwriters/malformedheaders/staticHUDdamage. No activejobs orcapture; rootsolefixowner.


42c/42d bounded diagnostics (2026-10-18): C protected 4,768 bodies and 812 SetupNums; D protected 5,217 bodies and 678 SetupNums. Every observed writer busy255, zero malformed headers/static HUD damage. Both max one immediate catch-up/two protected bodies per group. C native 4,526 reads, D 5,182 reads, all eight bits with matched high/low4016 strobes. Continuous active maximum three frames in both, versus41 maximum two and42a five; all-mode six includes initialization. D old-control timing diverges: normal1-2 entry5480, alive frame5719 cap. These are hardware ownership/sampling diagnostics, not final route or speed proofs. Per-case native-controller-receipt.json binds source guards, native history, group rows and long-gap context.
Sophia38d pipe branch is independently cold-boot certified at5925/X1900/Y176 with all10,240 RAM bytes matching. Full intermediate no-roof qualification is pending next traced tail. Root requested no fresh route after this diagnostic packet; no active emulator/jobs/captures. Updated handoff pit-rygar-sophia-handoff-v38d-20261018.json retains exact Pit/Rygar full38d proofs and this new prefix.


42e stack-preserving bounded case (2026-10-18): original fixed controller sequence only, same passive fields and independently adapted resident guards. 5,217 protected bodies and 678 SetupNums all busy255; zero malformed commands/static HUD damage. 5,181 guarded native reads, each eight bits and paired high/low4016 strobes. Maximum continuous active sample gap three frames; six all-mode includes initialization. 4,748 groups/469 catch-ups, max one immediate catch-up/two bodies. Protected-body stack is250 for both normal and catch-up, compared with D catch-up251. Every recorded trace field matches D except NmiSkipped on56 rows; motion/engine/controls/cycle fields match. Alive frame5719 cap, normal1-2 entry5480; this remains diagnostic only. Native packet SHA6ab93a597b41da6135bdc0b99ba2e059e4f7613a6bebfd565e19d0059e98242c. No active jobs, extra Start variants, fresh routes or recordings. Root owns runtime acceptance.
