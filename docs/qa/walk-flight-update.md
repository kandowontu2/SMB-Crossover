# Walking, underground bricks, Pit flight and Rygar music

Both ROMs include these changes. **295 Mesen emulator cases pass** across
MMC3 and MMC5, including Mario's unchanged 19-field baseline trace over 521
frames. The result and hashes are in [summary.json](../../build/verification/summary.json).
These are emulator fixtures, not physical hardware tests or new full-level
controller clears. Earlier twelve-run recordings retain their earlier hashes.

| Build | SHA-256 |
| --- | --- |
| MMC3 | `11e2c98462d587ddf86875d5dcd3572f6e923119787351ad1c8a33dca8d14ad1` |
| MMC5 | `225da1be6491d2f99f2de1165b05b91bde780c09871a509fccdc7f5050b6eefa` |

## Bass and Rygar walking

Bass's former walk frames came from row zero of his sprite sheet: blinking
idle, slide and jump artwork. The corrected sequence uses the three normal
walking cells on row two, in source order **1, 2, 3, 2**, with the 100ms source
animation interval (six updates). The 100ms initial movement pause now has its
own step artwork. Movement physics and the buster are unchanged.

Rygar's old walking captures were not a clean walking sequence. Fresh native
controller-only captures identify frames **302, 309 and 316**, seven updates
per pose. The native arm/leg extents change, so centering each cropped bitmap
also shifted his torso. His new images use the original logical X origin at
`$0512`, with the original one-update OAM staging, instead of crop width.

Both animation clocks start with walking, reset on idle and reversal, and
preserve the separate attack/air poses. Both directions and multiple complete
cycles are exercised by `bass-walk.lua` and `rygar-walk.lua` on both mappers.

[Walking preview](../../build/walk-flight/walking.gif) ·
[Native Rygar capture manifest](../../build/rygar-audit/walk/manifest.json)

Optional regeneration uses `tools/reference/capture_rygar_walk.py`, followed
by the existing expanded-asset builder. The source ROM is pinned by hash and
never modified. The permanent capture reproduces all three generated images.

## Underground masonry

The middle platform in the native 1-1 bonus room uses terrain-generated `$52`
bricks. The port had marked all terrain-generated cells as protected, making
the middle platform indestructible while separately placed left-side bricks
could break. Protection now applies to the foundation; upper masonry is
breakable regardless of which parser path generated it.

`underground-bricks.lua` loads the real native bonus-room data and inspects the
actual parser results. Controller B throws Rygar's disk against the left
stack, all seven middle-platform columns and ceiling masonry. The floor and
pipe survive. Actor placement is an explicit stationary fixture; the tiles
and protection flags are not fabricated. The same test fails on the previous
ROM at the middle-platform classification assertion.

[Historical failure](../../build/verification/old-checkpoint-underground-bricks.log) ·
[MMC3 passing test](../../build/verification/smb-crossover-mmc3-underground-bricks.log) ·
[MMC5 passing test](../../build/verification/smb-crossover-mmc5-underground-bricks.log)

## Pit's flower-level flight

At flower power, release and press A again in the air, then hold it for up to
**60 active updates of lift**. Two wing phases flap behind the native body,
with separate horizontal/upward bow poses. Releasing A pauses flight; a new
press can use the remaining budget. Landing recharges it, including a jump
on the immediately following update. Lower power levels cannot fly.

Flight supplies 1.5 NES pixels/update of lift and cannot activate while
submerged or climbing. Power loss cancels it. An explicit head sweep prevents
continuous lift from repeatedly overriding SMB's ceiling-bump velocity and
pushing through a roof. Activation and first ceiling contact queue sound.
Hammer attacks retain their visible hammer poses during flight.

The flight tests cover power gating, activation, both wing/shot art states,
exhaustion, solid roofs and landing recharge on both mappers. This ability and
its wing artwork are requested additions, not original Crossover behavior.

[Flight preview](../../build/walk-flight/pit-flight.gif)

## Seven Rygar songs

The original Rygar audio driver supplies seven distinct stage selections.
The assignments below are adaptations for SMB's area types; numeric labels
are native driver IDs, not unverified soundtrack titles.

| Selection | Native song | Verified loop period, updates |
| --- | ---: | ---: |
| Outdoor | `$05` | 3,264 |
| Underground / pipe bonus | `$06` | 4,608 |
| Water | `$09` | 3,072 |
| Castle | `$04` | 4,032 |
| Coin heaven | `$0C` | 2,160 |
| Intro | `$03` | 768 |
| Star / hurry | `$0B` | 150 |

These are native APU-register captures, not synthesized approximations. The
extraction fixture invokes the original `$e000` driver with its `$0740` queue
and bank-3 selector; gameplay is frozen, and the original ROM file is unchanged.
All seven loops have at least two full matching periods. The compressed
playlist uses 161,905 bytes within the existing cartridge capacity.

The full playlist tests now compare 56 area/event selections against 400
independently decoded native APU shadow frames each, on both mappers. An
additional 4,500-update test crosses Rygar's castle loop and matches the native
trace throughout. Rygar's death/victory music still uses SMB fallback cues.
Audio remains frame-quantized and omits DPCM.

## Special attacks and Bass's upgrades

The [special-button audit](../reference/special-attacks.md) distinguishes the
exact linked six-character game from 2.02. In the linked build, S throws Link's
boomerang or Simon's axe; both exist here on Select. The other four have no S
action in that version.

The 2.02 inventories are only partly implemented. Bass's mushroom correctly
raises his basic-buster limit from three to four. His flower currently adds no
further ability: his seven special weapons, energy and selection are missing.
This update audits that gap; it does not claim those weapons were added.
