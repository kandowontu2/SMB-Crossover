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
