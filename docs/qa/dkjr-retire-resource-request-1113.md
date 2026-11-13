# Private DK Jr conditional page request, November 13

This is the retained source-backed **resource request**, now conditionally
granted by `docs/qa/allocations/dkjr-retire-page-1113.json`; it is not a
native-ready candidate or nightly update. Reviewed public62 and its tested
Karnov526 successor retain the original13 helpers. Frozen private
f116/fa9/full2057 and its real native full-stage negative remain unchanged.

Request one named conditional lease: **raw WRAM bank2 offsets0900..0CFF,
CPU C900..CCFF, 1024 bytes**, only while the complete DK Jr raw40 cookies in
both bank2/3 headers authenticate. This extends the existing conditional
`dkjr-private-resources-1102-v20.json` owner overlay. It is not an unconditional
reservation against foreign owners. No new native PRG or physical CHR row is
requested.

The prototype is `tools/audit/compose_dkjr_helper_retire_1113.py`:
`parts(parent)` only assembles and authenticates exact owned spans;
`retirement_fixture(parent)` creates an explicitly **UNALLOCATED in-memory CPU
fixture**. It writes no ROM. `controller(raw,full=True)` preserves the frozen
full controls and binds only the moved private constructor-return observer
BD41→BD42. First-pickup controls still observe unchangedD1F0.

Exact reviewed parent is
`62ba7f54117875ec018d6f85fb1c74408aa11f0fe0f6a85b8b4f601034a17639`.
Its DK payload cookie is `a7280130b1118ac41a70e81c2eda030f` at file534485.
The unallocated fixture is
`2172ef3c3713c13bc8f5152771b88b105dfc3b0eadc3eda365e479b76c8b9e20`,
cookie `a728011f8559d5c4972696ec3d9f15c6`. All changes stay in the existing
eleven DK carrier pages and the existing16-byte cookie. No unknown successor
or speculative Prince inverse is accepted.

## Storage, loader and entry ownership

The ninth page is **existing CHR959**. Its complete1024 bytes are copied to
C900..CCFF because the existing PPU transport copies1024-byte pages. The
page is immutable during active DK execution. Code occupies CBE0..CC16
(55 bytes,64-byte storage slot) and CC60..CC79 (26 bytes,32-byte slot).
The rest remains exact art bytes; the entire destination needs the lease.

The96 storage bytes at CHR959 offsets[736,800) and[864,896) were actual
duplicate body pairs: native47/55 equal9,49 equals41. All body consumers now
select identical old pairs. This is qualified by poisoned-art body, effect,
native-pattern and cold-portrait comparisons below, not blank-byte scanning.

Owned compaction funds all other changes: rectangle predicate AEEF62→42
bytes;14-row helper table moves toAF19. Score bridge B940126→103 bytes;
22-byte body tile alias is B9A7..B9BC. Rotated body BC74 gains one byte;
its already-owned8-byte BOX moves BD3C→BD3D, ending at unchangedBD45.
ConstructorD1F0, clockAF2D and all its callers stay pinned. The cold worker
D25E grows102→117 bytes within its existing119-byte cold+old-row-table span.
There is no neighboring fill lease or native OBJECT-tail allocation.

The actual cold chain first retires the authenticated previous owner and
invalidates both headers. The unchanged common worker copies/reads back
D000..D7FF and clears **C000..C8FF only**. The private worker then copies and
verifies8 program pages to raw3 and ninth959 to raw2 C900..CCFF. Neither
private worker publishes a ready header. Current CoCold publishes complete
raw3 thenraw2 ready cookies only after all readback succeeds. The private
worker's R0..R2 remain documented transport scratch; public transport saves
its caller context. A/Y/X and success C/Z/N match the existing success return.

Current exact preimages (SHA256) are checked by the prototype and retained
source reconstruction, without restoring a historical build tree:

| CPU span / owner | Bytes | Current SHA256 |
| --- | ---: | --- |
| AEEF..AF2C original rectangle predicate |62|`53675d3c4fc3d58e7d3ed707fe5a6d5ef5321e7cb930e4359d6bc7d7a636020a`|
| B940..B9BD score bridge |126|`cedede4497ee48e7af9df2222ecf0859f51b275c2b1d663f3fcc6ab61f265fcd`|
| BC74..BD44 rotated body plus BOX |209|`7e2a740aa9daab7759103fb29f61ef8f355908bc1bdb516d6c8032aa5ff7cd3f`|
| D25E..D2D4 cold worker plus old table |119|`588abc682267e3882f40e5f17f20884c7773bc3292ada8888eda3ba3bc7920ea`|
| D180..D18A fruit selector, unchanged |11|`2789c94a8eda008a41cba7758632c2df132c8fe52dcb31adc84d5d2042acb879`|
| B624..B6A4 helper refresh |129|`bb81f0101a001c83b8b29d82becf001eff7ad2724f227cc10914b8517d56d1eb`|
| CHR959[736,800) |64|`0d0e4a141c07bd93bb2bf27dfeee9c2d29d56d97255ad8df6db68fd9b957c4f1`|
| CHR959[864,896) |32|`66687aadf862bd776c8fc18b8e9f8e20089714856ee233b3902a591d0d5f2925`|

Existing page map, in payload order:
817→raw3A000;833→A400;847→A800;856→AC00;867→B000;881→B400;
882→B800;883→BC00;959→proposed raw2C900;960→D000;961→D400.
The worker still verifies the full8192 program bytes; ready headers replace
the reserved final32 bytes only after verification.

## Complete destination lifetime and address census

`check_dkjr_retire_lease_1113.py` authenticates frozen source SHA
`82cca72d6091ca2569093e7fd35aba55f43e0d191de06224d8b2335e316c839d`.
No original operand addresses C900..CCFF. All ordinary translated original
RAM bases are C000..C7FF, so even arbitrary8-bit indexing ends atC8FE.
All19 C8-indexed sites are classified: validated C800/C840/C880 lists end
atC8FF; six geometry pointer stores use X6/4/2/0, ending atC8D7. Geometry
table readers use X0: source selectorC04A has exactlytwo writes, both1,
in genuine constructor/fruit reset. No later metadata/table relies on C9.

All23 translated indirect sites are classified: four fruit reads use the
sole typed C400 producer (bounded28-byte Y);13 pose writers force pointer
high2 before access, so even arbitrary low/Y ends atC3FE; six descriptor
reads use exact relocated immutable original data inside A000..BFE0 or the
validated source-format geometry lists. The current256-byte original data
image is reassembled and matches the parent exactly. New head/score/body
and retirement code have no data write into the proposed page. Retirement
only reads native actor state and calls genuine fixed EraseEnemyObject8D2F.

The new service is reached only from the authenticated private refresh
call while raw3 is in A000 and raw2 is in C000. Its current owner/world/level/
area, native primary flag/ID25/state0/box5, no-passenger and full48-pixel
visual-off-left checks remain explicit. It otherwise tail-calls the original
private bbox wrapperB7CA. There is no standalone public C9 entry or callback.
Inactive/foreign owner callbacks reject the two full cookies before entering
the private image. The existing source reset/retire thaws any hit phase and
clears C8FE constructed state; common owner retirement invalidates both
headers before any successor overwrites its conditional RAM. C9 bytes may
remain as inactive storage after exit; they confer no ownership or ready
state, and every genuine cold rebind recopies and verifies the complete page.

Cold fault suite passed on current62: no-fault path reads every C900..CCFF
byte exactlyonce; persistent read faults C900/CBE0/CC60/CCFF plus original
code/metadata faults reject ready publication. HuMovement cannot enter C9
after failure. Removing the declared fault and retrying restores the entire
page and both cookies. Three bad rendering/interrupt phases reject without
touching C9 or reading PPU; authenticated warm reuse reads zero PPU bytes and
writes no C9 bytes. Cold minimumSP186; total PPU read cost22550, up2050.

## Art consumers and outstanding gameplay qualification

`check_dkjr_retire_alias_1113.py`:11264 public HuDraw cases across22 genuine
donor poses,256 cursors and two rotations compare1,351,680 visible pixels,
source cells, all attributes/positions, cellcounts, publicAXYP/SP and maps.
720 actual body aliases use identical pixels. Injury/death use that same
validated body writer. The entire current411-byte effect renderer plus its
actual11-byte D180 selector are reproduced exactly.6288 paired effect cases
exhaust source tiles, particle/hit/point slots, all flip bits, all256 hanging
kinds×4slots, capacity and rotation: emitted tiles97/99,113..127odd and
129..147odd never read the reclaimed pairs. All254 current native
metasprites (736cells), including six native powerup poses, also exclude
47/49/55. Native powerup tiles are even and select native pattern0.
Cold portrait OAM, CHR latches and palette commands stay exact; current public
portrait is the six-sprite nativeDonkeyKong fallback, not a new DK Jr portrait.

The grant does **not** qualify the new full-stage policy. Correctly bound
ordinary full replay Lua`8d728045113b7fc878ae62f0dcf240b4acae4d179fbd1c36c965f96706a58300`
on2172 admits880 atcamera609/Main3027 and944 at674/Main3347. All four opening
pipes cross; all eight original opening helpers are visible and carried.
It then waits atfourth roofX940/Y112 fromaboutMain4275 to7144, attempts the
retained jump-down controls, and fails actual source injuryX985/Y176/Main7218
(lives2, timer97). This is a **CPU control negative**, not a new native run or
an inferred game defect. Complete1024-byte page remains unchanged with zero
runtime writes across all7218 updates. The earlier unbound diagnostic used
Lua7d469f7c and waited atpipe1 because its obsolete BD41 observer saw no births;
that diagnostic cannot qualify gameplay. Both are separate from frozen
f116/fa9/full2057 and its real native880 missing-helper negative.

Both-header corruption now passes224 public rejections:2headers×16bytes×
7callbacks, with zero private execution, PPU read or WRAM modification.
225 foreign callback pairs retain exact AXYP/native fields/maps/WRAM deltas
for43owners and allthree Quick forms. New stack/IRQ/lag-NMI, foreign exit/
reentry, controller adaptation and the same-policy natural-first/full-stage
positive remain required. No native run or installation is authorized by
these fixtures alone. No space is requested from the old native OBJECT leaves.

All producer commands use the same zero-output root:
`build/dkjr-head-bridge-1113`, reservation1file; no generated files, ROM copies,
captures, expanded trees or archive additions.

## Current526 composition and subsequent diagnostics

The new scoped `proof_parent` accepts only exact62 or known526
`526ef1df172c3172fccbd35aa0471a9ff9a5a256a416acba8f7530d147a5b3f2`.
It explicitly invokes `compose_karnov_ladder_native_1113.inverse_current` for
526 and requires exact62. Frozen prior DK APIs and proof PINs are unchanged.
`proposal_current(526)` produces
`f301981d4e5e1acb2b9d0918940f45e382e5784a7265c19bf009fd93f8e9e5dc`
with exactly the same708 byte edits as2172, preserving every Karnov/other
byte. Its strict source-restoring inverse returns exact526;2172 returns62.

On f301 the unchanged first-pickup policy still passes the real native C1
effect, C4 cell, dynamic slot2 prepare/birth/maturity/collector, source freeze,
status1 and30 resumed updates. Controller
`a91249539ec6f533266e9edb5ebb4807424449ef24d1530f26276773f1deeecd`.
413IRQ+413lag-NMI cuts across the natural first route's changed instructions
match complete Main, all WRAM and mappings; minimumISRSP130, deepest score
SP153. This first cohort covers C9 fallback, **not the taken erase**.
The subsequent suite passes513IRQ+513lag-NMI cuts including100 taken-erase
instruction points, starting at an actual Main service-entrySP178. It also
matches complete Main/WRAM/maps, with minimumISRSP130. The declared actor
coordinates are fixture inputs; they are not an extra natural route claim.

The generic inherited ISR assertion failed immediate map equality at two
FarCallCommon windows,0166/0175: shadow CurrentBank changes immediately before
unbanked STA5115. The strictly guarded exception checks the exact6-byte
`STA CurrentBank; STA $5115` preimage`8d45018d1551` (CurrentBank0145),
A==shadow, prior physical-map phase and
saved stack/NextBank value; all CPU registers/SP, WRAM, scratch and SMC remain
equal. Only the expected physicalA map may advance early when lagNMI restores
the shadow. No map is repaired. A post-ISR clone executes the pending real
STA and stays unbanked before any banked fetch; every interrupted complete
Main still equals its baseline. New C9/source code keeps strict immediate
equality. This is a qualified shared-transport transient, not a game patch.

The ninth-row/done cold cohort passes67 real lag-NMI cuts and67 hardware-masked
IRQ attempts (I is set by the forced-blank cold protocol). Every completed
cold call matches all WRAM, full headers, mapper and PPU state; minimumISRSP165.
No unmasked cold-IRQ entry is claimed.

Actual shared retirement plus wrong-owner public rejection and DK cold/Fresh
reentry passes five declared owners9/37/38/39/41. Foreign C9 contents are
explicitly seeded after both headers invalidate. Each rebind recopies all1024
bytes and reconstructs DK source state. This is a transport/lifecycle fixture,
not a full controller-driven foreign character ingress.

The separate early-ride fourth-roof controller
`e342aa0904adcd5ede5df4a3028f5a8e75bbe5982327497eadb53350f20ef9a9`
has canonical CPU receipt
`94db219ab6e2a0ac9d96ac78d79e8ce26da7956f3ca6db47929ff106ed07cffb`:
negative atMain4307/X945/Y144. It has **no enemy actor** at the injury, only
the880/944 helpers. Exact A8DD (original DA31 via DA22/FallDistance) writes
state5 atMain4306 after sourceY127→159;944top176. That is the original
fall-distance rule. It is not evidence for altering injury or jump physics.
The first observed944 cycle bottoms at114, plateaus, then increases115;
the retained controller's increasing101..114 window misses this cycle. A
separate fresh-jump115..128 window then clears this descent. Controller
`66f416545ae49c17164b8080640bf65e9abd71be9c32c275561ccadcc6baa34e`
stops healthy atMain5039/X1213/Y156 on the retained falling-Goomba safe-distance
guard; canonical receipt
`a5477223ae2bfb772448d760f8020a972a14145b4eaa36ab89d85a2bc42386f0`.
The next controls-only test identifies the falling ledge Goomba earlier,
before an ordinary approach jump locks its original horizontal motion. ROM
bytes remain unchanged. Full-stage/native readiness remains open.

## Known Prince successor and current route scope

`proof_parent` now additionally accepts only exact delivered Prince/Karnov
`7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`.
It verifies `compose_prince_entrance_current_1113.reverse` returns exact526,
then the existing Karnov inverse returns frozen62. No prior DK API/PIN was
relaxed. `proposal_current(7ef)` produces private
`e73b66263a8e150d3d21b801e5a55be1817f86d09639fc428ab809b2518842d9`:
the same708 owned edits/cookie as2172/f301, with every Prince, Karnov and other
byte retained. Strict inverse returns exact7ef; zero generated files.

The earlier ledge-wait controller `ec767badb16070075a85eafbcbb660c3da5acb429c9b181248fbb6002d8cea0e`
fails atMain5012/X1168/Y176: native ground Goomba1181/Y184 contacts DK while
the controller watches a second, higher Goomba1239/Y120. Original damage
entry A2DA writes source state5. Canonical CPU receipt
`fd0e8eda39da5ca0c3e7a18235e6f46f67dd0de56e387ff722d1f5321682821c`.
This is a retained controller negative, not grounds for changing damage.

`check_dkjr_route_branches_1113.py` clones a complete, genuinely played
Main4990 prefix (no RAM/enemy/inventory seeds). Twelve controller-only
branches show a stationary fresh A defeats the approaching ground Goomba;
four neutral-delay choices retain source health/both lives. The optional
`stationary_wait=True` controller uses this defense before the higher ledge
Goomba. On f301 its Lua hash is
`e756d0a391ae9b65ef06423de43e952040b739e5f93fb2bcaddfa29d396e5316`.
It passes all opening pipes and both intervening gaps, then remains healthy
atMain7166/X2126/Y176 on the retained controller assertion
`No height gained on late riser 1`; canonical CPU receipt
`0eb1a00af415197122e17973535a32b6adeddf0ae6dfcb8c31234b3a05e37a7a`.
The C9 runtime page remains immutable. This is **not a full-stage pass**.

The same diagnostic tool's `--riser` clones actual Main7000 atX2127/Y176.
Twelve fresh-A/hold/direction branches show no height gain and no injury.
`--riser --retreat` is the next controller/terrain diagnosis, not a qualified
route. No original jump/body physics, helper positions, retirement predicate
or ROM bytes have changed during these controller investigations. The extra
336 helper remains PRIVATE; the delivered thirteen-helper policy remains
authoritative. Native qualification of the retirement candidate is pending.

The next two actual-prefix cohorts on e73 completed with zero output files:

- `--riser --retreat`: twelve stationary-A branches regain the original15px
  jump (minimum nativeY161), no injury. Subsequent Right input takes effect
  only after landing. The retained `DkjrNativeSourcePhase` explicitly skips
  CE6C input for source states3/4; airborne direction is latched. No midair
  steering change is proposed.
- `--riser --running-jump`: all five branches retreat Left12/16/20/24/28
  updates, neutral4, then Right+A8 and Right80. Every branch lands on the
  genuine first stair atY160/source1, lives2, no injury. Actual takeoffs span
  X2110..2120. The replayed Main7000 body's world rectangleX2127..2144,
  Y191..206 already touches the actual first stair cellX2144/Y192; the
  original takeoffX2127 is too late in this CPU cadence. These are genuine
  controller-only branches of the played prefix, not physical NES proofs.

The optional `early_stairs=True` controller now uses first two takeoffs
2118/2134 and matching second staircase2342/2358. Existing third/fourth
takeoffs2150/2166 and2374/2390 retain the same26px approach to their cells;
all other route policies and ROM bytes remain unchanged. Its continuous
full-stage CPU replay is in progress, not a pass. This option requires the
qualified fourth-window/ledge/stationary-defense controls. Frozen failed
controllers and all strict parent APIs remain available unchanged.

The initial `early_stairs` full replay is retained as a negative: e73 Lua
`b7d2218150c37bdb7df4bcdaccc09eca56e072b35e779de1487c5459f5a7e27c`,
canonical CPU receipt
`49fae665cf526615a24b082075ddf68a2245836136d3491060e4b94ae8f7a019`.
Main7004/X2127/Y176 remains healthy/lives2/timer106, but readiness occurs after
the new takeoff and the controller asserts `Missed late staircase takeoff`.
Eight opening public vertical helpers, including880/944, were carried;
there were no C9 runtime writes. Merely changing an earlier coordinate does
not reproduce the successful actual-prefix retreat.

The optional `riser_retreat=True` now performs exactly Left12/neutral4/
Right+A8/Right32 when a grounded actor has passed the takeoff; then it resumes
the retained driver. On e73 Lua
`bd4bacd76d2584eccc1f745c6abd27c48ab39afe04764d6254438da0f4e11464`,
all three gaps, both late staircases, all six pipes and all six final stairs
pass. Every original public vertical helper is born and carried, including
2576/2640/2832/3040; the original horizontal1408 gap assertions pass too.
The PRIVATE336 helper also spawns. No C9 writes occur. This is still a
**full-stage negative**: genuine timer expiration atMain9564/X3041/Y157,
phase `final-lower`, timer0/expired1 causes the native injury path. Canonical
CPU receipt
`9b71eeb4e32fd68f6c5144bb82ecefe3723783fa71978fe3594144834623043c`.
No flag, castle or 1-2 entry pass is claimed.

The new optional `landing_prep=True` ends the fixed preparation when the
actual grounded actor reaches the intended16px-higher surface after launch.
It retains a four-attempt bound and changes only controller timing. The
continuous full replay with this option is pending. The9564 negative remains
reproducible with `landing_prep=False`. No donor motor, rectangle, helper
position, native timer or ROM byte changed in any of these controller tests.

`landing_prep=True` completed as another timer negative, not an optimization:
Lua `ad07bd6498ea644e1eacf6517d3a5720802aa598722b5d4209e8936c544f4e85`,
canonical `5a2a2f6904f5a27212adfd20ac44fcd80e3e0956c49526056869d853c20b287e`.
It reaches final-capX3038/Y48 atMain9564/timer0/expired1. The final staircase
is96updates later than the fixed preparation policy. Private336 plus all12
public vertical actors are born; all except3040 are carried before timeout.

The optional `settled_stairs=True` adds neutral4 before each fresh Right+A,
retreating Left12 only after an overshoot. This is retained as a negative too:
Lua `87dcbf30e77ca1e0a50162fe5b905f9ff690866fa53c19ad16b489eb501d9c16`,
canonical `f7ceefeff7cfa5fa080e50147f24dc70d22cb77fa5ef1c5aa3176e13c3765849`.
It hits the four-attempt controller bound on riser3, Main7373/X2158/Y144,
healthy/lives2/timer91. No ROM defect or jump change is inferred.

The added bounded wait observer measures logical updates, not physical NES
lag. The largest same-X runs before this failure are511:311,717:280,
439:267,960:265,909:246,589:236; vertical motion is included. The first
`lower` to `depart` phase lasts446updates (Main1008..1454). The private336
actor has no recorded carry in these no-pickup full-route attempts.

An actual first-roof prefix is now selected by observed groundedY144,
not a guessed Main940 (which was still airborne). It occurs atMain956,
X466/Y144, controller prefix
`aa2fb1e2843bdd36f4d5ee3e0b283bd40c2498e42343c53fb1f197d8ecc644dd`.
Six in-memory descent branches wait atX456/462 for the genuine480 actor to
descend through top168/176/184, transfer and use a fresh original jump near
X496. All reach real floorX529/Y176 with both lives, after532 more updates.
This establishes safe controller alternatives, **not a speed gain**. No RAM,
inventory, actor, timer or ability state is seeded; output files remain zero.

The root supplied a separate actual-Mesen e73/bd4 full-route negative:
`8eb7ea9ab60f56e7679aadd080ccb064e1d59fd91c429a43b3a344f84255d350`.
At7250physical frames/Main2835 a real ground Goomba877/Y184 contacts DK
waiting at fourth-boardX891/Y176. All first three pipes pass;880/944 are
both born offscreen and visible, so the old missing880 admission failure is
no longer this run's cause. This is a controller contact failure and **not
a full-stage pass**. It also confirms native pacing differs from this CPU
scheduler; the CPU timer negatives are not physical timer proofs.

`terrain_positive_timer_negative_controller(e73)` now explicitly asserts
the exact e73 and frozen bd4 script pins. The optional separate
`fourth_board_guard_controller(e73)` adds only a stationary fresh A8/rearm47
when waiting at fourth-board, groundedY176, and a real undefeated ground
Goomba is18..24px away. It preserves all ROM/cookie/constructor guards and
the frozen negative factory. Its native qualification is pending; no ROM
or public helper placement has changed.

## Exact e73 current gates and frozen native experiments

The complete current gate command exited0, with zero generated files:
`check_dkjr_retire_lease_1113.py --current --cold --headers --foreign
--lifecycle --cold-interrupts --interrupts`, through the bounded runner.
It directly binds e73, preserving every unrelated Prince/Karnov byte, and
repeats22550-read cold verification, seven declared fault/retry cases,
warm/three wrong-phase checks,224 header rejections,225 foreign callback
pairs, five owner retirement/rebind fixtures,67 maskedIRQ/67 real cold lagNMI,
and513IRQ/513lag runtime cuts including100 taken-erase points. Complete
Main/WRAM/maps match; minimum runtimeISRSP130/deepest scoreSP153.

Its genuinely played first-mushroom CPU route also passes on e73 directly:
controller `137a7c373e27dcd9288c4cd4f6cf25e0f90b961a049e060610e68f267ae816f5`.
Actual selected native item2 is prepared/born at epoch486, mature550,
collected582, erased, and status1 resumes30 further updates with both lives.
Root's separate strengthened physical first-pickup result uses that exact
controller: receipt
`62b5f897b6ac046aedd26d7729582b88ab00bf5784ae4fef29450b052d2da1e1`,
1901physical frames/671updates. Details and scope are root-owned in
`dkjr-retire-current-native-1113.md`. This remains first mushroom only.

The board-guard factory is frozen to Lua
`4302a3494ef9db39764d53d6cb8f1c4af8a4731207d9a7f5c836406b036ab08e`.
Root's actual native result, receipt
`94a127dbb2fca4d50091abec22a2f9cac5b29281805a05f8d92c596dc29954e0`,
proves the fresh hop atMain2816 prevents the fourth-board Goomba injury;
880 carries at2867, ascent2868, crossing3277, roof3309. The run later fails
after waiting until6221 for the old fourth jump-down window: source injury
atMain6295/X985/Y176, timer138. Actual944 carry contacts occur before that
wait, so this is a separate retained controller negative, not a full pass.

`fourth_contact_ride_controller(e73)` derives only from that frozen4302
factory and transitions fourth-roof to the existing lower phase on actual
`carried(d,down)` **and current source-grounded state**. The latter avoids
promoting a transient cached native carry while the donor is still falling;
the earlier CPU early-ride negative remains retained. Existing lower/exit
height and direction checks stay intact. The exact new Lua is
`9f943b1b45c6c829b732b3bc76dc9cf3496e5918fede7816d97d0fd53da93547`.
All three frozen factories assert e73 and their exact output hashes; a
read-only metadata check against root's retained candidate compiled all three
as Lua with zero outputs. Contact-ride native/full-stage qualification is
pending. No source motor, timer, helper placement, ROM or public delivery
changed in these experiments.

## All101 current menu rows and rendered bytes

`check_dkjr_menu_parity_1113.py` passes on exact parent7ef and privatee73.
It authenticates the unchanged `check_menu_facing_1112.py` auditor SHA
`4e886d4259f4ba308c91d9779e052c3756a878bdfdc074551ed82494a576c671`
and requires the strict DK inverse to return exact7ef. The actual resolver,
Select cycles, portrait renderer and NMI run on both images. All101 rows
match identity, owner, facing, sprite count, portrait dimensions/hash and
silhouette hash. Every one of101 portraits and101 silhouettes is also
compared as RGBA bytes:202 images/350404bytes, exactly equal.

The default-separator sorted-JSON row digest remains
`f58ec905102307ca87d9c302248fa7da9c44cd5550df154323e67024da245db7`.
Aggregate receipt:
`8b40e7067344d7735becff2ddb5fc018f08584a8d2e5f14c97a76c53d0810016`.
The owned bounded command exits0 and writes zero files: no sheet, PNG, ROM,
archive restore or emulator launch. This is a current compiled-menu/rendered
byte comparison in the CPU peripheral model, not a new physical raster or
inherent-art orientation claim. The reference auditor's per-slot model setup
and actual Select input procedure are unchanged.

## Frozen causal observer before any carry repair

The actual contact-ride9f943 native run remains negative: root receipt
`07c1ac5f26bad59f4f3e9b2f78248bbdb6e32e78d1e91edc56b8b514e5285ce0`.
One944 carry is observed atMain3345, player939/106/top138/source1. Lower
starts3346, but source injury follows3381 at player945/148, timer260/lives2.
That single contact is not persistent support or a successful descent.

The new scoped `dkjr_contact_observer_1113.controller(e73)` leaves the frozen
9f943 controls intact and appends read-only callbacks. Lua SHA:
`d46b3350c2a23dcc9c2ec5dc4323411c9cc4e114305c995b4e8ec2702067d13b`.
The default Main3338..3385 trace has512 compact rows maximum, retaining the
first128/latest384 if necessary. It records actual native positioning around
PRG71 AC18/AC26/AC29, source carry/step/support/fall/land entries and returns,
native PlatformCollisionFlag0566 and BoundingBoxes0658, source rectangles,
Y/state/previous-state/fall start/limit, query windows and CPU/maps. Current
bytes authenticate AC18's Y store and AC29's finalRTS; AC29 is completed
positioning evidence, not proof that support persists in the next source step.

`check_dkjr_contact_observer_1113.py` exercises the callbacks on a genuinely
constructed32-Main prefix, changing only the telemetry window and test stop.
It exits0, captures195 rows without dropping any, and compares all WRAM,
native RAM, maps, VRAM and CHR exactly to the same unobserved control prefix.
The actual native observer retains its original window and has no test stop.
No game memory writes, repairs, captures or generated outputs occur.

Root narrows only the observation window to3343..3351 for a native run:
Lua `4612b3ae50444b536376bcc4c466629140d82b0b355131b29667be47108d7976`,
receipt `693270bbf2f840a0cc20e77112d1f4497c5c823550364cead53a22a51f69e703`.
The90 trace rows have no drops; trace digest
`1d9077ecf9cc0195e2371d366ea33413bd70c9001f3e6a3b1d8ac64c38a9ad11`.
Native positioning and the source carry endpoint really importY127→121.
AtMain3346 source ground1 persists, support query137..138 appends the current
plane138. At3347 actor top139/flag255 no longer lies in137..138, append count
is0, player bbox bottom remains136, and the actual source store changes1→4.
Fall start121/limit24 then lead to the original injury at3381. This isolates
the descending-support failure. It does not yet establish the correct repair;
native position offsets, source footer and actual actor delta must be
qualified together before any game bytes or donor physics are changed.
