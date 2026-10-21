# Samus, Bill and Lance: immutable final34 controller progress

This ledger covers ordinary controller history; root is the sole builder.
Arena tests are separate from these route claims. Samus has a complete,
independently cold-booted six-stage controller clear on final34, with a confirmed
ceiling-collision defect described below. Bill and Lance do not yet have such
clears. No final video or clean final graphics/audio QA pass is claimed.

ROM: `build/checkpoints/roster-audit-v34/smb-crossover-mmc3.nes`  
SHA256: `5f62764c0e531fecd5e1f6e146fc5d50f6ad9cbc237365a44838c50896b36707`

The complete fixed-input Samus proof is
`build/roster-through-2-2/scc34-samus-proof-a-2-v0-mmc3`: 24,242 hardware
frames, 24,241 controller polls, zero deaths, all six ordinary stages and an
actual responsive entry into2-3. Its input SHA256 is
`ac6fe4163f5db0981f9ee1a80d1fa6045229c2207221a445f0c4da10bb150310`.
No emulated RAM, ROM or register writes occur in that proof. Entries are1-1
at541,1-2 at5656,1-3 at10089,1-4 at13141,2-1 at16144,2-2 at20120 and2-3
at24218. Normal1-2 and2-2 exit pipes are used; the1-1 shortcut is not used.

The physical-frame audit has zero HUD split flags and zero lag-CHR flags.
Its11 motion candidates include three confirmed stationary ascending-ceiling
snaps: X1235→1247→1263→1279 in1-1 (frames2185..2187),
X241→255→271→287 in2-1 (16313..16315), and
X1311→1327→1343→1359→1375 in2-1 (17294..17297). Native VX is zero and
the camera stays fixed at these events. A separate read-only, same-ROM
controller replay traced the first event to0x51→0x23 at an origin nibble3:
native ceiling separation was skipped, then a side probe clamped successive
16-pixel cells. The clear is reproducible but is qualified by this actual
runtime defect. Root authorized a source-based ceiling/side classification
repair and a separate focused arena fixture; that repair requires a new-ROM
proof before final acceptance.

The audit records900 overloaded-sprite hardware frames and4,504 lag frames.
Audio includes2,902 source events and55,407 physical APU writes;2,400 events
are unconfirmed by the generic source-ownership classifier, which does not
establish missing audible sound. Native audio/visual recording review remains
pending. There is no video file and no decoded-video-frame review in this
packet. The previous110 group component passes are separate evidence, not a
claim that every weapon was collected during this mostly base-suit clear.

The parent-provided `root-samus-v34-k-2-v0-mmc3` stream clears all four World1
stages normally and enters2-1 at frame16144. It dies at the first Goomba/stair
when the old floor-fire policy stops too close to the enemy. All new branches
retain that genuine prefix; no state or input is transplanted from another ROM.

| Packet | Target | Exact ordinary input SHA256 | Independent cold boot |
| --- | --- | --- | --- |
| `scc34-21-first-a` | `return {frame=16465,poll=16465,x=451,y=176,state=0,power=0,world=1,level=0}` | `396aba4ecdd041823f12ce86b9c730857316613b423090c0b026eb40c54e2548` | True; all10,240 RAM bytes |
| `scc34-21-koopas-b` | `return {frame=16658,poll=16658,x=621,y=176,state=0,power=0,world=1,level=0}` | `f99e7aa1714eba6f3df9e08c136f7ca27668e9e9d85a2b1db2e8dbfbc9d72084` | True; all10,240 RAM bytes |
| `scc34-21-pipe-a` | `return {frame=16930,poll=16930,x=901,y=112,state=0,power=0,world=1,level=0}` | `5ee248c1f781e16df7fcbf951e07968ca4ca973bfdd4721a69db633a91cf3047` | True; all10,240 RAM bytes |
| `scc34-21-row-a` | `return {frame=17322,poll=17322,x=1400,y=112,state=0,power=0,world=1,level=0}` | `8b7274d0043fc587fe5b4e2962700ee9575fc5041c29ad0dd9032227f7ce50aa` | True; all10,240 RAM bytes |
| `scc34-21-midpipes-a` | `return {frame=17799,poll=17799,x=1900,y=176,state=0,power=0,world=1,level=0}` | `48c0c193593b45a6746e3d29e64f1a633c2c19c289d168e229f3c942fdff7e11` | True; all10,240 RAM bytes |


The first branch clears the initial staircase. Its grounded endpoint is too
close to the next Koopa pair beneath a low brick row; a forward jump hits the
underside and falls into the enemies. The next branch includes retreat and
crouched forward shooting (`RDB`) and clears that encounter. These are ordinary
navigation failures, with no demonstrated runtime/source defect.

Every search directory retains its ROM, complete ordinary inputs, native search
log, target, unedited opaque discovery state, complete RAM image and independent
cold-boot receipt. An accepted reusable root is used only with the exact same
ROM and full input history. The eventual complete path still requires a fresh
power-on replay with the full physical-frame graphics/audio audit.


A generic-policy continuation from X901 dies at X1054 while descending onto a
Goomba. The subsequent `scc34-21-row-a` branch reaches X1400 with independent
cold-boot proof; no source defect is inferred from that earlier contact.

The existing parent-provided final34 component summary contains110 passing
Samus/Bill/Lance mapper cases (54 Samus,46 Bill,10 Lance), including combat,
inventory, energy drops, upgrades, forms, power-up effects, swimming and the
six-Flare limit. No group case appears in its failures. This is a review of
that exact frozen component run, not a fresh rerun and not evidence of an
ordinary six-stage clear. The referenced report hash and case list are retained
in `build/roster-through-2-2/scc34-group-component-receipt.json`.


The certified X1900 endpoint is already committed to a Goomba collision two
frames later; every immediate control action fails there. The next complete
branch revises from the preceding genuine pipe-top alternative (X1839/Y144 at
frame17738). Its revised tail passes independent cold boot before promotion.
No accepted prefix is overwritten.


The revised branch scc34-21-bricks-b is independently cold-boot verified
through X2300/Y176 at poll/frame18166, power0, world1/level0, with all10,240
RAM bytes matching. Its complete ordinary input SHA256 is 9df02c017d7ceed0bf9659ec4223d42580845e66fdcfa801c9ba426075ed815d.
It retains the genuine World1 history and safely replaces the doomed approach
to X1900. A jumping green Koopa is ahead at approximately X2386/Y181.

The next branch scc34-21-late-a is independently cold-boot verified through
X2895/Y176 at poll/frame18657, with all10,240 RAM bytes matching. Its complete
ordinary input SHA256 is b0901dca916373e1c679cf46dfd60013cdb173cf1b4b9d7d5e3371c1406d89c9. The late
pit, pillar and overhead brick supports were traversed with ordinary jumps.
Spring controls are being tested next; this endpoint alone is not a 2-1 clear.

The first continuation from X2895 dies two frames later while landing beside a
green Koopa. The certified state proves reproducibility, not safety: another
branch starts from its genuine earlier airborne poll18620 and revises the
landing timing. The spring was not activated in this failed continuation.
The separately preserved `scc34_samus21_spring_hold.lua` keeps A held after the
fresh spring-compression edge; it has not yet been exercised at the spring.

The later complete Samus packet above supersedes that intermediate spring
status: the native compression edge/held boost is exercised and the route
clears2-1 normally.

The ordinary spring continuation `scc34-21-spring-b-2-v0-mmc3` clears normal
2-1 and enters2-2 at frame20120. All six requested stages have now been entered,
with World1 and2-1 cleared; 2-2 remains incomplete. The exact discovery input
SHA256 is `db542ae59136be2b6a1883758595f26bbfb0228bf856c28757825e06a241d490`. The run dies
at frame21432, X1452/Y59 in2-2, rising into a nearby Blooper/actor. It used the
fresh spring-compression A edge and held A across the boosted wall crossing.
This was a discovery run without the full frame audit, not a final proof/video.

The coral search reached its180-second bound; its best safe floor state at
X1780/Y176, frame/poll21780, then independently passed the exact cold-boot
10,240-byte RAM proof (`search/scc34-22-coral-a`, basename `best`). Its input
SHA256 is `c7c112cadb9a16a08225ca5446b35d94d0d04671c968cf6b4bff70fa1646cccc`. This proof includes the real
2-1 spring/flag transition and2-2 traversal so far. A scoped next search targets
the real raised bank nearX2064/Y112 before attempting the taller bridge.

The next certified ordinary state is X2064/Y112 in2-2 at poll/frame22030, on
the real launch bank (`search/scc34-22-bank-a`, winning). Independent cold boot
matches all10,240 RAM bytes. Complete input SHA256: `4a3308bf77deaf7fa2f56369f5f2399288c9d16ddbd5d38d23bdba815175ec17`.
The subsequent policy continuation is testing the high underwater bridge and
normal exit, with no recording or emulated writes.

The first bridge-policy continuation waited8 polls and died to a Cheep at
X2079/Y120 while Samus remained at2065/Y112. The certified root already had
consumed current/previous A clear, so an immediate native jump was available.
`search/scc34-22-bridge-b` independently cold-boots to X2349/Y144 at22278,
on a real coral top beyond the bridge, matching all10,240 RAM bytes. Its exact
ordinary input SHA256 is `0349c5720bb8ee40be9ae432bca7aaa2d88f1f5488ad0d2442e7551f0438e57a`. The next
policy tests the normal exit and steps off coral only when solid floor lies
below the next step; true floor gaps/obstacles retain jump controls.

The following coral is one tile taller at2384. A full immediate held jump
from the first coral rises into a Cheep. `search/scc34-22-fishbank-a` tests
ordinary vertical/angled-fire timing, then independently cold-boots to the
upper rock bank X2500/Y48 at22513 (all10,240 RAM bytes). Exact input SHA256:
`6d9fe4da8c2e1cd9718b0c8d7c028f27baac1eeeb21f010e18035ebbae435f73`. The live map shows bank2496..2543, a
48-pixel real gap2544..2591, and the next bank2592..2639. Jumping across that
gap remains enabled; the next continuation tests the normal exit.

The first upper-gap continuation crosses normally but descends into a Cheep
at X2729/Y164, frame22712 (`scc34-22-tail-c-2-v0-mmc3`). A local branch from
the certified2500 upper bank revises the descent/angled-fire timing. This is
an ordinary contact failure; no water/collision/weapon runtime defect is inferred.

`search/scc34-22-lastfish-a` revises the upper-gap descent and independently
cold-boots to X2850/Y176 in2-2 at22820 (all10,240 RAM bytes). Exact ordinary
input SHA256: `09d3c4b1e4f6f9a4ea35bc9365e424af563674b01f3864796cf9cdfe8b4622b5`. The normal exit is
nearX3000. The next policy arms Right-only admission only after actual grounded
Y<=112 on the real upper step, preserving ordinary obstacle jumps beforehand.

## Focused ceiling repair component receipt

Prototype38d is a separate ROM, not a relabeling of the final34 controller
proof. Its focused `samus-zero-wall-contact.lua` passes both mappers:150 head
arenas,240 zero/toward/away/integer/subpixel wall arenas across both walls and
ground/air/ball/crouch,75 debris origins,19 real question pickups and one full
world mushroom rise. Jumped=false controls preserve source velocity; normal
ceiling displacement uses100/120 Q8.16 only when source jumped=true. A38b
negative control fails the first actual ceiling-separation assertion.

The old432-arena head fixture required an explicit authored-jump precondition:
its upward airborne state now sets source jumped=true. Its original case10
negative is retained. A jump-state-only outside control then exposed case67:
native boot-level streaming inserted unrelated pipe tiles19/21 into the
authored arena, producing a genuine side contact. Read-only parser write
receipts are retained. Outside controls with depth/bank-qualified per-update
terrain-stream task/scroll-accumulator isolation pass all432 arenas on both
38d mappers without changing the original displacement, contact, effect-origin
or playability assertions. Only after both outside controls passed was that
fixture correction migrated. Full provenance/hashes are in
`build/verification/samus-ceiling38d-focused-receipt.json`.

The runtime repair keeps a resident no-hit guard, performs rare ceiling repair
in the Samus bank, and appends two source-state bytes after all prior SRAM
allocations. Native reward/debris origins stay attached to their authored
cells. The full suite and a new-ROM ordinary controller route are separate
pending requirements; no clean final capture is claimed.

## Fresh38d controller discovery

This new chain uses only prototype38d MMC3,
SHA256 `850936f1b58047da23ef2f02243f66efe9eaa8d879ca97f912752aadbe83309a`.
The power-on feedback-policy run `scc38d-samus-a-2-v0-mmc3` clears1-1 and
enters1-2 at5169. Its ordinary engine8 adjacent trace has no horizontal steps
larger than2px through the failed descending combat atX1810/frame7363. This
is telemetry, not a full video/audio audit.

The real-input branch `search/scc38d-12-floor-actor-a` independently cold-boots
to groundedX1905/Y176 at poll/frame7454. A subsequent ordinary continuation
misses a moving lift; `search/scc38d-12-lift-a` independently cold-boots to
X2471/Y92 on a real ascending platform at8071. Both match all10,240 RAM
bytes, with no emulated patches. Walking Right across that support reaches
the actual normal bank/exit pipe. Continuation `scc38d-samus-c-2-v0-mmc3`
enters1-3 at9369, then fails in the first raised-bank gap.

`search/scc38d-13-upper-enemies-a` revises from genuine poll9810 and
independently cold-boots to X868/Y190 on a real moving support at10034,
matching all10,240 RAM bytes. Its complete input SHA256 is
`d56a31eb53a2bba495dd20f525b06b81989b2ce67514cefb7540f54a67da9431`.
This proof includes both earlier normal stage transitions. The next ordinary
continuation is still discovery. No38d six-stage clear,38e migration or final
capture is claimed by these partials.

The next38d branch `scc38d-13-late-platform-a` independently cold-boots to
X1717/Y80 at10878 (all10,240 RAM bytes). It takes damage and ends atpower0.
Its ordinary continuation clears1-3 and enters1-4 at12135. The first real
castle mushroom is collected at12537/X467/Y62; this is an actual world
pickup, separate from the arena coverage.

A failed coordinate-only drop policy remains supported atX488/Y64 until
timeout; it is not an accepted traversal. Read-only terrain inspection places
the upper used block at480..495/Y96 and the real lower island at464..511/Y160.
The corrected ordinary policy drops atX500, settles onY128, and crosses the
next lava gap. A firebar costs the mushroom at12596/X501/Y128. The next
ordinary firebar contact is a death, not a demonstrated engine defect.

`search/scc38d-14-firebars-a` revises from that real pre-contact controller
history and independently cold-boots to X1110/Y112, power0, at13220, matching
all10,240 RAM bytes. It includes all three ordinary earlier stage clears,
the actual castle pickup, lower-island drop and timed firebar crossings.
Prototype39a is being validated separately; these38d states/receipts have not
been relabeled or transplanted to it.


`search/scc38d-14-firebars-b` independently cold-boots toX1580/Y128,
power0, at13664, matching all10,240 RAM bytes. Its ordinary continuationJ
clears the castle normally and enters2-1 at15201. New2-1 discovery clears
the first elevated Goomba/stair using an earlier jump. A later policy pauses
on the genuine intermediate bankX548/Y112 until the paired floor Goombas
pass behind; this is avoidance, not proof of killing every enemy.

ContinuationN uses actual native Piranha DownY state to launch from a safe
waiting point and crosses the first pipe. It dies later atX822/Y176 under
the next block bank while a floor Koopa approaches. This is a controller
combat failure; no runtime defect is inferred. A bounded branch begins from
the same-ROM ordinary history atpoll17680. Every run remains on38d; the
older34 full clear remains qualified, and no final captures exist.


`search/scc38d-21-after-first-plant-a` independently cold-boots togrounded
X1011/Y176 atpoll17964, matching all10,240 RAM bytes. ContinuationP requires
at least48 remaining native Piranha timer ticks at full retraction before
crossing; it passes the second pipe atX1192. Later, giving a nearby floor
Goomba priority over pipe approach reaches the genuine next pipe support at
X1676/Y112/poll19251. The old crossing policy walks off that support into
the following gap; continuationR adds a fresh ordinary A edge while still
supported. These are partial controller discoveries, not final six-stage QA.


The38d partial's two movement candidates now have bounded actual-write
receipts. The3px1-3 step is normal guest integration of2px followed by the
native horizontal moving-platform carry of1px (`PositionPlayerOnHPlat`).
The castle step integrates1752 to1753, then the actual right-wall clamp writes
1753 to1745 withR0=1 and no ceiling receipt. This is distinct from34's repeated
16px ceiling march; tile/decoded-frame association is still pending. Receipt:
`build/verification/scc38d-movement-candidates.json`.

Later ordinary discovery reaches actual short-pipe supportX2032/Y128 around
poll20040. U's old scripted crossing then holds Right against the taller
pipe until the time limit; it is retained as a controller failure. V adds a
fresh jump from the genuine short-pipe support. No new runtime defect or
completed38d six-stage proof is claimed.


The next read-only receipt further qualifies that castle separation: the
native cell is blank placeholder$23 atR6=$030E/R2=$30, written during native
block bounce. It is not yet a proven visible solid-wall contact. The Lua
write callback reports the next PC$A2A2 (opcodeAD), following the actual
STA at$A2A0. These details are preserved in the movement receipt; the route
still requires placeholder/decoded-frame classification before clean QA.


`search/scc38d-21-winged-a` independently cold-boots to groundedX2539/Y176
atpoll20518, matching all10,240 RAM bytes. That endpoint is close to two
Goombas; a real floor retreat creates room before crouched fire. Subsequent
ordinary continuationAA clears the final pipe, bouncing-enemy span, native
spring/wall, flag and stage transition. It enters playable2-2 at22576.
All six requested stages have now been entered on38d, but2-2 is not cleared.
The first coral contact nearX308/Y112 endsAA at22815; a bounded controller
branch starts before that contact. No source migration or final capture is
claimed. AA's world/level/task/engine-qualified telemetry has no horizontal
steps greater than8px or canonical vertical steps greater than16px; this is
not decoded-frame/audio QA and retains the smaller movement qualifications.


`search/scc38d-22-firstcoral-a` independently cold-boots toX653/Y176 in2-2
atpoll23106, matching all10,240 RAM bytes with exact controller polls and
hardware frames. It clears the early coral obstacles. The ordinaryAB tail
continues from that genuine prefix. This remains38d discovery; no accepted39
or40 controller-route claim and no final capture is made.


`search/scc38d-22-lowcoral-a` independently cold-boots toX1700/Y176 at
poll24236, matching all10,240 RAM bytes. It revises the actual low-coral
approach rather than changing Samus physics. The next bounded discovery uses
that verified same-ROM opaque root to target the real2064/Y112 bridge launch
bank; any winner still requires independent full power-on controller proof.
The exact inputs and every failed tail remain preserved. Debug compression
of21 inactive duplicate discovery symbol files saved243,581,646 bytes with
verified decompressed hashes; no immutable proof root or active run changed.


The next late-water bank search did not reach its requested grounded2064/Y112
goal. Its independently cold-boot verified best is only floorX2049/Y176 at
poll24524, with all10,240 RAM bytes exact. A separate ordinary continuation
now tests a vertical jump onto the narrow coral support before attempting
the high bridge. This failed search is retained as partial discovery; it
is not a six-stage clear or a newer-build route.


Ordinary continuationAD mounts the2064/Y112 coral support and crosses the
high bridge by jumping vertically first, then holding Right only after
reaching the needed height. It reaches the late bank near2609 but approaches
its underside; that controller failure is retained. Its complete trace has
no adjacent same-room ordinary-engine X step above8px or canonical Y step
above16px. This remains a discovery trace, not decoded-frame/audio QA.


Later continuationAE lands on both upper banks at2509/Y48 and2610/Y48.
AF's upper-bank jump crosses the next actors; AG then supplies the next
coral jump and reaches a genuine late landing at2884/Y112/frame25568. The
next Cheep contact at2898 ends AG, so AH tests a fresh jump from that actual
landing toward the normal pipe. These failed ordinary tails remain pinned
to38d and do not establish a completed final route or every-enemy clear.


The38d ordinary six-stage route now has a full independent power-on proof:
`scc38d-samus-proof-a-2-v0-mmc3` replays all26,964 controller polls exactly,
finishes at hardware frame26,965 with zero deaths, and reaches responsive
2-3 at26,941. All six prior stages clear normally;2-2 pipe entry is actual
engine2 at3010/Y112/frame25,796 with Right alone. The final Cheep is actually
damaged and enters native death state34 at25,578 following crouched beam
fire. The fixed input SHA is
`8fd13494b4baa8bf5421bf5b178932679a54268e75ded5b595f23e6a299e9457`.

Full per-frame graphics/audio telemetry and a physical-bank/depth/opcode
qualified source jump observer ran without emulated patches or state loads.
There are zero illegal native guest stomps and zero large ordinary-engine
movement steps. Nine empty probe support rows are retained for native edge
and moving-platform review; they are not unsupported-jump findings by
themselves. The smaller castle blank-placeholder wall separation remains
qualified. This is38d controller proof, not accepted40/final ROM proof,
decoded-frame/audible QA, an every-enemy kill, or every-upgrade pickup run.
No recording has been made. Packet:
`build/verification/scc38d-samus-route-packet.json`.


Bill38d has now cleared1-1 and1-2 normally. Its first paired-Goomba branch
independently cold-boots to1004/Y176 at2039, the later underground floor
combat branch to2070/Y176 at8828, and the final-lift branch to2590/Y128 at
9443; each matches all10,240 RAM bytes. ContinuationD enters1-3 at12597,
then meets the first upper-bank Goomba at625/Y60. E tests real lower-bank
combat timing. There is no complete Bill or Lance six-stage proof yet.
Bill/Lance progress: `build/verification/bill-lance38d-controller-progress.json`.


Bill38d E passes the first upper-bank Goombas with ordinary lower-bank
waiting and prone fire. F applies that timing at the next bank, records an
actual ID6 native death-state34 at13874, and clears1-3 normally. Castle
entry is15669; the first firebar contact at778/Y112 ends F at16276. A bounded
controller branch starts before that contact. No complete Bill or Lance
six-stage proof or final capture is inferred from this partial progress.


Bill38d's first castle firebar branch independently cold-boots to1110/Y112
at16610, all10,240 RAM bytes exact. G continues from it, clears the castle
normally, and enters2-1 at18562. First stair Goomba contact at295 ends G at
18829; H tests an earlier ordinary jump before that elevated enemy. Bill
now has normal clears of all World1 stages, but no six-stage proof yet.
Additional inactive failed/aborted debug duplicates were compressed with
verified decompression, saving137,407,944 bytes; receipt
`build/verification/scc38d-disposable-debug-archive2.json`. Active and frozen
proof/checkpoint/search-root artifacts remain unchanged.


Bill38d H passes the initial2-1stair/pipes but bonks an overhead row and
descends into the1350floor enemies. I launches closer to the edge, clears
that span, and reaches actual upper-bank2053/Y48 support with a naturally
collected Flare weapon. Its stationary high-bank firing loop then runs out
of time. J waits for the actual plant's full retraction/fresh native timer,
crosses onto the genuine pipe support, and jumps onward. It reaches real
late floor2496/Y176, then meets the late Goomba pair near2567; K uses prone
fire before that jump. All evidence remains ordinary38d controller history.

H's purple/gray fatal screenshot is retained as an unclassified visual
candidate. I records playable sky22/mirror mask1E throughout; J records
actual2001writes06/1E and ends with a normal blue fatal snapshot. Thus no
sustained palette corruption or runtime defect has been established.


Bill38d K isolates the late floor combat: one Goomba actually enters death
state34, while the second remains alive and contacts Bill. L repeats the
real input prefix with a read-only projectile observer; a prone first Flare
sample has age1, phase15, Y205 from anchorY200, reaching ordinary floor208.
Source inspection establishes missing initial phase/left handedness and
sample-before-advance behavior, nonbrick terrain consumption, and an
incorrect visible-only cap. The independently frozen receipt is
`build/verification/bill-flare38d-source-runtime-negative.json`. It retains
the previous six-visible-Flare interpretation as corrected audit history.
The source global cap counts visible Flare plus its hidden center and any
old player bullets: admit iff O+2F<6 before adding the pair. Pickups do not
clear those old shots; Laser firing explicitly does. Normal/Machine/Spread
also use global dictionary counts. No runtime or shared fixture changed.

L's frame-limit endpoint is an ordinary policy mistake: its second Start
press preceded the required release of native pause-status bit7. M waits
for both timer0 and bit7 release, unpauses normally, fires Normal prone to
pass the late pair, and reaches the final2-1spring approach. Enemy contact
at2918/Y162 ends M at24760. All World1 stages have normal clears, but Bill
still lacks a complete six-stage proof and Lance38d has not been attempted.
No recording or final-hash certification is inferred.


Bill O walks off the real upper support instead of jumping, then records
the final ID0 Koopa's health75/50/25/0 and actual death state34 at24737.
The native spring/tallwall sequence clears normally; playable2-2 entry is
26072. The first underwater coral/Cheep contact ends O at276/Y154/26271.
All six stage entries are now present, but this is five completed stages,
not a six-stage clear. P lets Bill settle from real underwater entry before
using source-style floor jumps. Lance38d has not been attempted.
Additional inactive failed debug duplicates alone were compressed with
verified decompression: archive3 saves69,594,756 bytes, archive4 saves
81,193,882 bytes. Immutable proofs/checkpoints/search roots remain intact.


Bill P waits too long before its first underwater jump and gets blocked
at161 beside the first coral; its eventual death is a controller failure.
Q takes full source-style floor jumps and reaches746/Y91; its fatal image
shows a Blooper beneath Bill. A bounded same-ROM ordinary-input branch
starts from Q's actual floor607/Y176/poll26584 toward1000. Any promoted
branch must independently cold-boot all inputs and match all10,240RAM.
No new runtime defect or complete Bill/Lance six-stage proof is inferred.


Bill water-mid-a now independently cold-boots to grounded1052/Y96 at
poll26987 with power1. Complete controller polls/frames/target and all
10,240RAM bytes match, with no state loads during that verification. The
input SHA is d23388d46a6359f39a0fbbd20f1d6b01d9d3433a8c2714bc714cd5fee093fa95.
The current endpoint is the trailing edge of a genuine pillar, followed by
the1056..1136gap; the next ordinary floor jump remains route work. Packet:
`build/verification/scc38d-bill-water-prefix-packet.json`. This is still a
partial2-2 prefix, not a complete Bill six-stage proof or final visual/audio
QA. Lance38d remains unattempted. The emulator is closed; root's near30GB
space constraint currently precludes another bulk clone. Archive5 verifies
three inactive failed Bill debug copies, saving34,797,378 bytes; all inputs,
proof roots and checkpoint files remain intact.


While root42d validates, no new emulator or bulk clone was launched. Eight
older own failed34 Samus/Bill duplicate debug files were confirmed identical
to canonical34 and compressed with verified gzip roundtrips, freeing
92,548,256 bytes. All controller inputs, states, RAM snapshots, full proofs,
raw logs, negative screenshots and traces remain unchanged. Receipt:
`build/verification/scc-disposable-debug-archive6.json`.

Read-only Flare follow-up records source visible-extents expiry versus
native anchor clipping, a low-byte Y-wrap counterexample, phase precision
and late-state allocation options. These extra visibility cases are code
and source derived, not new emulator reproductions. The original frozen
Flare negative is unchanged. Addendum:
`build/verification/bill-flare-visibility-source-addendum.json`.


Root's explicit authorization extended reversible duplicate-DBG compaction
to completed proof-directory copies. Archive7 compresses only23 oldest own
completed search copies, each matching canonical34 or38d and a verified
gzip roundtrip, saving266,351,582 bytes. All608 protected input/state/RAM/
CSV/log/proof/negative-image/ROM/LBL files are hash-identical before/after.
Canonical checkpoints, full Samus proof and current Bill/water debug copies
remain plain. No emulator, route, source, shared fixture or runner change.
Receipt: `build/verification/scc-disposable-debug-archive7.json`.
