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
