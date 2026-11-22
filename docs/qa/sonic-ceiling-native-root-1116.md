# Complete Sonic ceiling repair: native qualification

## Natural pickups in the November 22 nightly

The [stock-item replay](../../tools/audit/run_sonic_natural_stock_1122.py)
starts from the normal title and uses controller input through the roster
and 1-1. On the installed `a6d91e36` nightly, Sonic and Super Sonic each hit
the brick at X1616/Y144, collected the Star after it emerged, and triggered
the native timer and music. Both finished with the Star active after 25
original movement updates. These tests used the current Master System
movement port.

| Form and item | Physical frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Sonic Star | 2,368 | `85ec618d2aef160c84f221d7581f8b443c02ae448a1d6e75c808378c4bdcaf3d` |
| Super Sonic Star | 2,392 | `30eb2743f368c77bad01f7480b7729be443dc19eade97bfb8b9287d1089ae851` |
| Sonic Fire Flower | 3,068 | `4c6845cc39d93f091ed97028207b5ad35a0b98a85dd3513e2a06316e92f53512` |
| Super Sonic Fire Flower | 2,813 | `7cc7b4dee9c6020a1536b9de277c0f190860fa487df488b4cf51f7e37d023717` |

The Sonic Star controller hash is
`bf553fd1c4b976fddba459e6f507e2b51fcc757a5c6e9431dc9b0251d99025f2`.
The Super Sonic Star controller hash is
`1dfa78fba450f945a62806fcd4b54cb3afeb58b7777156fe4ffe456a9f7eb0cf`.

For the Flower, both forms earned the Mushroom at X336, returned underneath
the row to reveal the Fire Flower at X1248/Y144, and jumped onto the row
from the right. Super Sonic dropped to the floor earlier on the left to
avoid an enemy on the row. The collector advanced each form from tier 1 to
tier 2 through the normal powerup sequence. Both continued another 25
original movement updates at tier 2.

The Sonic Fire Flower controller hash is
`da245b3cabf74354ac1f060ebb1f04c0301bb8572afdbf3e45338d7eaa3129c3`.
The Super Sonic Fire Flower controller hash is
`3f6e27e6fa2eaf0183670fb793102d3ed6da70b8b86d3e2c7a8f044c64e504f6`.

## Sonic 3 movement reference

The frame bridge still runs the Master System motor. The held-jump latch,
rolling state, and acceleration tables come from that source. The native
frame bridge generates its active prefix from the same motor, so a future
movement change has to reach the native frame path as well as its fallback.
The retained bindings authenticate both paths and their current pickup tests.

The recorded code reference target is the standalone USA Genesis revision
listed in [the donor inventory](additional-alternate-donors-2026-10-31.json).
The local donor's SHA-256 matches the inventory. Sonic Retro publishes a
standalone Sonic 3 source entry at revision `5ce79296`. Its movement code
still needs to be checked against the local donor. [Sonic Retro standalone source entry](https://github.com/sonicretro/skdisasm/blob/5ce792968973cdf6a5b4858a01d28af9d9f151b7/buildS3.lua)

The public nightly remains1327. Proposeda2d9 is94 owned/91 changed bytes,
with all5526 original movement bytes unchanged. Both source full stages,
natural1UP routes, header/lifecycle/IRQ and shared-family checks pass; see
`sonic-ceiling-complete-a2d9-source-1116.md` and the independent root ABI note.

## First private life run9824: retained observer negative

Actual Mesen9824 returns exit1, receipt
`3d8600aa4e6d7dde2286ba32910e9c0166e4d819e269043f930bdcf441765b31`.
It executes exacta2d9 with factory9b2cfa82 / Sonic Luae361cd27. The failure
is the final hardcoded rings5 expectation inherited from the source route.
Actual first-active rings0 and pre/post-pickup rings0 are recorded; the
replacement observer must compare actual captured resources. The source
prefix earns five from its retained RingConstruct/RingProject scene fixture:
SceneTilesC378..C37A are7A/7B/7B under World0/Level0/Area5. This does not
make five rings a required inventory for every native route.
No game-byte change is justified by this failure.

The actual hidden60 head at routeMain616/birth617 succeeds. All eight
subsequent original returns have Timer0, cleared hold flag and gravity
velocities56 through448, despite heldA. A later genuine jump collects the
fullC0 kind3 actor1026/103 at hero1036/97, boxes[84,105,96,129] versus
[74,112,86,124], positive3x13. Original popup11/erase/cue32 occur, actual
life INC at routeMain688 changes2→3/cue64, followed by25 original returns.
At the final assertion routeMain714 has rings0/status0/hurt0/sourceStar0,
life3 at1028/160; no pending scope or new capture files remain. Overall
GameLoop entries/returns1028 and original/Main entries/returns714 balance.
These observed mechanics do not convert the failed receipt into a pass.

The wrapper restores the existing candidate slot to1327 in finally.
Downloads1327 and its clear automatic-patch guard are unchanged. The Super
case was not reached after the first failure. This candidate is not yet
eligible for installation. Full native routes and corrected preservation
checks remain pending; no video, image, backup or release is produced.

## Private full-stage2047: both forms pass

Frozen full factory75e04f0c / Sonic Luab74ff9b9 / Super Luaf1b8c39c
pass both cases, exit0, on exacta2d9. No images, game seeds or new files:

|Form|Receipt SHA256|Total Main|Route Main|Original/host returns|Physical frames|
|---|---|---:|---:|---:|---:|
|Sonic|88f1d54f83f80a15f45d01138dfe9f86b5ab27e4f49adcc2d109f88318af3a5c|2974|2660|1466|5030|
|Super Sonic|a7a3a0fc08b25995b63f3383df197daeddca0661e590d52e57046f689c7cf554|2995|2660|1466|5056|

Both genuinely reach flag at routeMain1407, castle1469 and next-level
entrance2225. Each then completes25 living grounded originalC1 updates in
underground1-2,40/176, lives2, native state0/source flags136 and no pending
scope. Main/original/host entries and returns balance; the timer helper
executes once and returns once. Rings5 at the flag/castle and their intended
new-area reset0 are observed, not imposed on the different1UP route.

The full observer has no leaked rings5 life assertion. These stage passes
do not close the separate9824 failed observer or certify steady60Hz. The
candidate slot is restored to1327 afterward; Downloads remains unchanged.
Corrected native life preservation tests remain the last installation gate.

## Corrected private life84495: both forms pass

Factory09b1f486 uses the same ordinary controls and game gates, with actual
pre-head resource snapshots compared at collector, immediately before/after
life INC and after25 new original/public returns. Source callbackbdae2171
and dirty-resource predicate cases pass. No game bytes changed froma2.

|Form|Native receipt SHA256|Total Main|Route/original/host returns|Physical frames|
|---|---|---:|---:|---:|
|Sonic|a248b9547f263a38aa181e74eda366bbb34ecae9a303b8e9da1854ef9b9cb67f|1028|714|1782|
|Super Sonic|7b0aec0409f3887918af469a6c55f70becf30ccd6ead91560b285fd7027b8dd8|1048|713|1804|

Both have real hidden60 head616/birth617 and eight returned Timer0/gravity
updates. Sonic collects the fullC0 actor at route683 and earns life3 at688;
Super collects at682 and earns it at687. Physical overlap is positive3x13
and1x13 respectively. Popup11, erase, new cues32/64 and the actual delayed
life writer occur. Captured rings0/ringLives0/hurt0/privateStar0/status0
remain exact through both operations and25 new returns, with no pending
scope. Final Sonic1028/160 and Super1032/149 are airborne, life3; these item
cases do not claim grounded endpoints. The separate full-stage cases do.

All four private native gates now pass. Candidate is restored to1327 before
installation. Delivery grants authorize only exacta2 and require matching
actual Downloads repeats before a verified-delivery claim. The old9824
negative remains recorded; no60Hz or audible fidelity claim is made.

## Delivered a2: exact installed repeats pass

After source pushaeb80ec8, Rootinstaller10241 directly replaces
`C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`,2097168 bytes,
with exacta2d9d1218504dedf186cfe352ee4c927160529af4f8d09fe6e2aafccfae477c7.
The existing shared candidate matches byte-for-byte. CLI automatic-patch
guards pass before installation on1327 and afterward on a2 with no sidecars.
No backup, new ROM copy, patch asset or release is created.

Actual Downloads27306 passes both corrected1UP cases and45911 passes both
full-stage cases, exit0. All four complete receipt SHA256s match their
private counterparts in the tables above exactly. Thus both forms reveal
the real hidden block, stop held ascent at the ceiling, collect the1UP with
actual resources preserved, clear1-1 and complete25 living grounded original
updates in1-2 from the installed launch context. No helper is used or moved.

The fix owns94 bytes/changes91 over1327; all5526 original movement bytes,
graphics, music and every unowned byte remain exact. The underlying ladder
of prior delivered repairs stays intact. Mini's20-byte weapon repair and
Rogue's2-byte missile repair remain separate source candidates at this
delivery; they are not silently included or claimed tested here. Start a
fresh game after reopening the ROM so its loaded source-code pages refresh.

## Original rolling, spin dash and variable jump

A source candidate based on `a6d91e36` adds stationary Down+A charging,
release to launch a spin dash, momentum-based rolling and separate tap and
held jump heights. The implementation is newly written for this NES mod.
The assembly keeps the existing terrain, camera, sprites and controller
bridge. The normal walking and braking trace without a roll matched the
prior build for 224 updates.

The bounded CPU checks measured a 28.25-pixel tap jump and an 80.5-pixel
held jump. Holding A through landing triggered one jump. Charging and
release worked in both directions, with up to 6.5 pixels of travel per
update. The native constructor, ceiling contact, pause, game-engine freezes
and failed terrain sweep preserved their expected behavior. The run executed
1,188 CPU invocations and produced zero files.

The in-memory candidate fingerprint over `a6d91e36` is
`d1b2138dc59e714ae653cbb7067cb32766f5f14de24965f7c980b81dac48903c`.

### Private Mesen motion checks for both forms

The same motion patch on the verified Beans nightly produced private
candidate `3466637dc3e75d7768eb6ba3c49af03e548e24a44a027394e3934b22579605cf`.
The Sonic and Beans changes cover disjoint ROM bytes. Both characters
started through the real roster and ran the test on the opening 1-1 floor.
For each, a two-update tap rose about 35 pixels and a 20-update hold rose
about 81 pixels. After both jumps, the player held Down, tapped A twice,
released Down and started rolling at 4.5 pixels per update. The body stayed
24 pixels high during the roll and the feet stayed on the floor. Each run
verified 118 complete movement returns with two lives and no injury.

| Character | Physical frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Sonic | 581 | `1e1bf5e307af15b7fefce4ce9580860e62842e6621aaac3d0296047179f48087` |
| Super Sonic | 602 | `768b1f44362771dc0ee85b13ecd1155f4cadea3393bbfc65da2fb2f5a99158b9` |

The test slot was restored to the verified Downloads ROM after both runs.
The candidate's full stage routes, affected pickups and interrupts still need
verification before delivery. Other Sonic 3 behavior and Super Sonic's
distinct mechanics remain open.

### Recovering a stopped airborne roll

The private `3466637d` run reached the tall pipe with Sonic at X712.
The roll rose above the lip, but repeated Right+A jumps could never pass
it after the side sweep reset horizontal speed to zero. The candidate kept
zero horizontal speed for an airborne roll even while a direction was held.

The successor `8f8d4a13` restarts an airborne roll at one pixel per update
when the player holds a direction and horizontal speed is zero. Existing
wall sweeps still prevent movement into solid tiles. The CPU fixture places
a stopped roll above a real swept pipe shape and confirms motion from each
side. The 224-update walking comparison, jump, charge, ceiling and rollback
checks also pass. The scope of this change is the Sonic roll recovery. The
installed Beans nightly remains the named base for the composed candidate.

The first private Mesen run with the fix cleared the tall pipe and reached
X1489 alive. It stopped on the replay's body-width assertion during the
update that ended an ordinary hurt animation. The returned body was still
28 pixels wide on that update. The replay now accepts both authentic body
widths and waits for injury input suppression to end before making a new
jump decision. The pipe-crossing receipt is
`76c11385354f09416b390f9b0dad118f5de25b8036a779177473128c9ee6e1d1`.

## Return to running after a slow roll

The next Mesen run reached X1605. Sonic stayed curled on the ground while
Right was held and slowed from 0.53 to 0.27 pixels per update before an
enemy contact killed him near the Star block. Receipt
`594505366d15984a746339cd8eac6819475f8e0d84ed67013e3d4e0db21be77c`.

The private `fe58e7d9` candidate restores the normal running controls
when a grounded roll is slower than one pixel per update and the player
holds the direction of travel. Down still keeps Sonic curled. The
CPU checks cover both directions, show the exact same foot position
through the pose change and confirm acceleration resumes. Faster
rolls, opposite or neutral input, airborne travel and injury retain
their previous behavior in the matched controls.

Mesen confirmed seven actual transitions from roll to run in 1-1,
including X1529 to X1530 near the earlier failure. Sonic reached X2459
before falling into the final pit at X2448–2479. The replay launched a
single jump from the flat ground at X2324 and reached the far side below
its rim. The next route brakes before the staircase and jumps again
from its raised floor. Receipt
`a8b34163edf4ba301b323322890fdecab5fbb71b3e4784ffd5c678327ab72a89`.
This test used a private candidate. The Downloads build still has the
verified Beans repair.

## Steering into the final staircase

The revised replay launched from X2430/Y112 and crossed the final pit.
It reached the staircase before the flagpole at X2888. From that step,
a fresh jump carried only 16 subpixels of horizontal speed and the
airborne roll retained that speed. Sonic repeatedly landed on the same
step. Receipt
`0a32456da1349913075423f1cf52a37c9a21d4e9e20b6d53d02454e15fb4ad84`.

Private candidate `c40ca81a` applies the existing one-pixel steering
recovery to very slow airborne rolls while the matching direction is
held. The source checks cover both directions from 16 and 136 subpixels.
Vertical motion, pose, charge and flags match the prior frame. Ten
control cases also match for faster rolls, neutral or opposite input,
Down and injury. Stationary wall recovery, both normal walking directions,
jump height, charge, ceiling contact and rejected-frame rollback pass.

The first Mesen run on `c40ca81a` observed four airborne transitions to
one pixel per update. The changed pace brought Sonic into an enemy at
X2010 after a jump. He died before the staircase. Receipt
`7e1e6d5fdb6a8e6bd7945435f9433e420e1700fe9b213da903bf017048a4ffb1`.
Super Sonic reproduced the same lethal contact at X2010 while rolling.
His test also observed four airborne recoveries. Receipt
`f3ad57db40743061e1d5a3c7c8c891558187658ee4657806a8e51cc2f9d1f87c`.

The current enemy-collision path sends Sonic through the legacy guest
handler at PRG10:`$B5A1`, which disables native stomps and ignores his roll
and air-spin state. The private motion changes leave that path intact. Both forms'
full-stage runs and the dedicated spin-hit check remain open.

## Native spin defeats

Private `59e1a591` routes Sonic's existing body contact into his
authenticated combat handler. A moving ground roll or airborne spin can
defeat a live Goomba or standard Koopa through the native defeat routine.
The handler uses the normal score popup and sound. Walking, charging,
stationary ground rolls, injury and unsupported enemy contacts retain
the ordinary injury path. A descending spin can bounce without changing
the upward velocity of an ascending attack.

The exact `c40ca81a` successor changes 214 bytes. Bounded CPU checks
recorded 144 defeats across both forms and all six actor slots, rejected
1,536 corrupt-header cases with the correct actor slot preserved, and
matched the previous dispatch for foreign owners and Kirby. The actual
native collision entry distinguishes overlap from disjoint hitboxes, and
ordinary injury matches the parent. The full-route controller observes the
actual defeat return, the live actor becoming defeated, and its score
popup. Source qualification creates no ROM or emulator captures.

The first full Sonic replay on `59e1a591` defeated four Goombas at
X1526, X1794, X2045 and X2760. Each native return set the defeated state,
awarded the Goomba popup and queued the enemy-hit sound. Sonic reached
the flag at frame 3,849, the castle at frame 3,944 and the next-level
entrance at frame 4,992, with two lives.

The replay then stopped on its own readiness assertion when the
underground level reported engine 8 at X40/Y48. The native entrance
had begun falling before Sonic's movement owner finished loading. The
observer now waits for that handoff without input and still requires
25 grounded movement returns in 1-2. First replay receipt
`31cf7b8f474dd250f3f8a65996d7c622065df32c177401be8ac1569d574ba6b6`.

Both complete private replays passed. Each defeated four live Goombas
while spinning, climbed the final staircase, and crossed the flag,
castle and next-level entrance states. Each waited one native return for
the underground handoff, then ended at X40/Y176 with two lives after
25 grounded source and Main returns in 1-2. These tests created no
capture files.

| Form | Physical frames | Native receipt SHA-256 | Controller SHA-256 |
| --- | ---: | --- | --- |
| Sonic | 5,658 | `97003aac6624560c660eb51580631c15d958b1119247f75f6e8772f3d9733c81` | `3c2e48641dc04bca3d94f78ccc1d8562b9223e0062cdf2791c00369f053c7d4d` |
| Super Sonic | 5,673 | `2952a5effe7b7ebbe6d9d8c8b0842ceb969211568d91ac25a3fc0b80b74ff457` | `d4ceab5565878691b76789a1699d9a1c93c8581355e0a84e3a3e45d72ca201c4` |

The linked CPU interrupt check reached all 115 active contact instructions
and compared 889 real IRQs and 889 busy NMIs against the prior handler state.
It also reached 40 nested IRQs and completed 3,556 contact continuations.
The native register, stack, scratch and mapper effects matched. Minimum
stack pointer was 180 in foreground code and 159 in the handlers.
Receipt `3fafd9f659cbf5b90c4f16b7d84864b2ddb89a9b61243857f4f7c5bb3e6623ad`.

## Verified Downloads nightly

The Downloads file was directly replaced with the exact tested
`59e1a591d5ea31d62dafa9332990598b74b5b0852194ef7cc7ad22788196b723`
build. Each form cleared 1-1 and reached its grounded 1-2 endpoint again
when Mesen launched that Downloads file. Both full receipts matched the
private runs above byte for byte. The installed ROM and shared test slot
match, the same-name patch guards passed, and the run created no backups
or captures.

### Enemy-free idle and walking cadence

Both forms were measured separately from the actual Downloads nightly. Each
completed 48 idle updates over 96 video frame intervals, then 16 updates
holding Right over 32 intervals. The 129-frame inclusive window recorded 64
gameplay returns, a maximum of one per frame, and 96 skipped game NMIs. Both
moved from X40 to X47 during the walk. All six enemy slots stayed empty.

The linked CPU trace measured 14 full code-header checks per update. The
checks and their caller used about 9,142 cycles per update. The original Sonic
movement routine used about 6,450 cycles. This trace identifies repeated code
checks as a target for reducing the measured empty-area lag.

| Form | Mesen receipt SHA-256 | Controller SHA-256 |
| --- | --- | --- |
| Sonic | `4dd200d50a27d42340217fab5756c3fae87f0154c100ae9eaf2c1aed447a8400` | `c26cbaa64d18e16309702a89c6dca2e51b78cb2ee6b8e96378e879af3a4d633c` |
| Super Sonic | `100bb0a7c4a5a55c9a18cd00be38c4ef6c68275050cfeb57335c44d9152702e8` | `9dfbe6daffafb6cdb3ae46f97a44feb7a42569b16e214a88138f787b34b0de02` |
