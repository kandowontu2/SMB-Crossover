# Thomas Star and 1UP coverage

## Input and scope

The completed CPU route and sweep cases pin ROM SHA256
`15a683321cde608cfe15447e90ef58d5295a16a1a6b607434f98df37162ac533`.
Root installed that flower-lift candidate in Downloads during this audit.
The shared Metal candidate path was subsequently reused. The new tools read
Downloads by default and accept an explicit `--rom`.

The native generator now pins installed Karnov successor
`318a087735b4204c74274b4107efbc302bc15a674a7f6f9d3bed598cea90d08d`.
The new CPU tool accepts both exact images. Authentication reconstructs
15a683 in memory through `deliver_karnov_bomb_1113.previous_image`, which
proves the complete parent, forward transform and inverse. It additionally
compares Thomas's entire 8 KiB carrier and 16-byte cookie. Native syntax and
opening-input checks pass against the installed successor.

This audit adds two source tools and this report. The CPU tests write zero
files. Root owns native Mesen runs. The replay producer writes one Lua file
and emits its receipt to stdout. Gameplay code and the flower lift source
remain at their existing revision.

## Authored item availability

The availability check matches both complete level streams byte-for-byte
against the pinned ROM and decodes their native page-control commands.

| Area | Item | Stream bytes and offset | World left | Tile top |
| --- | --- | --- | --- | --- |
| 1-1 | Hidden 1UP | `0683`, offset 20 | 1024 | 128 |
| 1-1 | Star brick | `5706`, offset 40 | 1616 | 144 |
| 1-2 | 1UP brick | `9008`, offset 104 | 1424 | 32 |

The current 1-1 stream starts at ROM file offset 20956, with SHA256
`162fc0bf0e2e7bd2ecda0ac1bf3551ee5f45a3f116fa6343badda72005c0b4ec`.
The 1-2 stream starts at 22403, with SHA256
`fba6eb4acdb570dad659a78ddf66dd2b3b9375977695b7f0bf707a65cee75154`.

`src/game.s` initializes `Hidden1UpFlag` through `StartWorld1`.
`src/level_tiles.s` checks and consumes that flag in `Hidden1UpBlock`.
The actual CPU route calls that handler once at epoch 1222, with flag 1 and
Thomas X784/Y157. Subsequent observations find flag 0 and the real `$60`
block at X1024/Y128. A fresh 1-1 start therefore makes this item available.
The third-area coin threshold in `src/player.s` applies to later flag
re-enablement.

The 1-2 object uses the ordinary `BrickWithItem` table entry for item 8.
Its availability bypasses `Hidden1UpBlock`. Ordinary Thomas reach to that
ceiling-height brick remains unverified.

## Natural Star CPU route

The cold menu, opening, mushroom, four original pipe helpers, flower helper,
head contacts, authored item emergence and collection execute through actual
native GameLoop/NMI code in the CPU model. Controller input drives movement.

The successful route earns the mushroom at epoch 392 and the flower at 2962.
Both hosted transformations complete their 60 updates. It clears the first
floor gap using the original jump, then hits Star brick `$57` at epoch 3505,
Thomas X1617/Y153. The native Star actor starts at X1616/Y135, matures, and
reaches the collector at epoch 3643. Thomas stands at X1673/Y176, status 2,
with both lives. The collector erases the actor, starts Star timer 35 and
queues music 64. Eight subsequent updates retain active gameplay.

The complete natural Star CPU route repeats on installed 318a087 with the
same collection epoch, state and call counts.

The run records three `SetupPowerUp` calls, three collectors and 120 hosted
progression updates. Natural Star expiry and a post-collection enemy defeat
remain outside this receipt.

## First floor gap timing

An in-memory sweep clones the naturally earned flower approach at X1340.
It tests nine grounded takeoff thresholds, X1368 through X1376, with zero
and one update of controller delay. All 18 cases preserve the source jump.

| Selected threshold | Input delay | First rising state | First landing | Result |
| --- | --- | --- | --- | --- |
| 1371 | 0 updates | X1372/Y173 | None | Falls to engine 11 at X1419 |
| 1372 | 0 updates | X1374/Y173 | X1411/Y176 | Reaches X1432 grounded |
| 1371 | 1 update | X1374/Y173 | X1411/Y176 | Reaches X1432 grounded |

Those two cases clear. Earlier requests fall short. Requests starting at
X1373 or later find Thomas falling before an eligible jump can begin.

Root's actual Mesen Star attempt with queued X1371 input failed at the same
pit after earning both upgrades. The receipt is
`779c73de1a838101e07b5d6d707f9409ae70f1634d0ae4fe020b30f32280cf0d`,
with controller SHA256
`434eb2ba99ed51068600c509ee2e76e42629f64ccd0ba8271a52dd0773317095`.
The arc reaches X1393/Y149, then X1409/Y194 and death at X1419.

The successor controller samples current geometry at `inputPolled`, selects
Up at grounded X1372, and records at most 48 poll/movement observations.
The movement hook authenticates RAM3 address `$A103` and its existing entry
bytes. Observations include FrameCounter, source last/have-epoch fields,
source jump state/displacement, saved input and requested pad. `--gap-wait`
allows a bounded physical-frame pause before the ledge. Its default script
SHA256 is `834c5569777fda0cb31e1f59cab1c28c305e6cae9f09c81a1399fa82b112a5fc`.
Root's actual 318a087 run with that controller clears the pit and produces
the authored Star at X1616/Y135, with observed mature Y119. At physical
frame 4732, Thomas X1679/Y165 reaches its collector. The observer stops on
its common carry assertion. Receipt
`d3b7ccf54eba6a265ecb053f40d6bd5ca18ba39a7f1a3b57c54b9ca0a3780f22`
preserves this prefix.

## Immediate Star return contract

The earlier common pickup assertion required carry set. Current native
CPU tests execute explicit mature Stars through
`HandlePowerUpCollision → NrPickup → HuPickup → MarioSourcePowerupCollision`
at statuses 0 and 2. Both return A64 and P`$30`, with carry clear, actor
erased, floaty 6, floaty timer 48, sound 32, Star timer 35, music 64 and
unchanged status. Both remain outside the hosted freeze.

The Star branch in `src/mario_source.s` compares kind 2 with 3, then stores
35 and 64 before returning. That comparison clears carry, which the stores
and return preserve. The successor observer therefore requires carry clear
for the Star and carry set for the two hosted upgrades. It retains the
erasure, floaty, sound, timer, music and status assertions. Every collector
return is recorded before strict assertions, including registers, flags,
actor fields and sound observations.

The corrected controller SHA256 is
`c44cae59ac7d13437f06421620313853442de4e9d24bc5d99cc7972d0f49fd99`.
Lua 5.4 syntax and the 60-update menu/opening mock pass.

Root's actual exact-Downloads 318a087 run passes at physical frame 4746,
status 2 and both lives. Receipt SHA256 is
`a69f4b97d08a557a0120452b1c3a092fb4d5b61038fe4cc2a1f2362311d93f47`.
The natural Star reaches the collector at frame 4732, Thomas X1679/Y165,
actor X1675/Y146. The observed return has carry 0, A64, erased actor,
floaty 6, floaty timer 48, one sound-32 write, music 64 and Star timer 35.
Both earlier upgrades complete their 60 hosted updates. The same run
clears the first floor pit through normal polled input and finishes eight
post-Star logical updates in active gameplay. This is the complete natural
mushroom, flower and Star receipt. Full-stage continuation and natural 1UP
collection were the next qualification steps.

## Current full 1-1 continuation

Root's exact installed 318a087 full-stage run passes at physical frame 8823,
after 6115 Main updates. It earns the three natural items, completes both
60-update hosted transformations, uses all six pipe helpers and the flower
helper, then reaches active 1-2 at X40/Y48, status 2 and both lives.

Receipt SHA256 is
`081b1c56d079d2976086e4d841c54f3d177438d39cc35f581ad4d919778bb06c`.
Controller SHA256 is
`22a1ba43bb5b517c15b30843d4527cc3ba2f310c73fd8434daa8dfeda09b49c8`.
The new generator is `tools/audit/replay_thomas_star_stage_1113.py`.

The continuation reuses the qualified Star prefix, polls the first-pit
takeoff input, then uses the retained native foot/step probes and two late
platform carries. Its first draft accidentally extended the prefix's
four-pipe threshold to six, which prevented the flower approach. The
corrected generator uses an explicit four-pipe prefix. A subsequent strict
stage assertion stopped on the ordinary level-1/engine-5 transition. The
final generator waits with neutral input through that transition and
requires active engine 8 in 1-2.

All helpers used by this installed receipt belong to Thomas in stage 1-1.
Each starts at top Y192, with width 32. Left/center pairs are 400/416,
560/576, 688/704, 864/880, 1200/1216, 2560/2576 and 2816/2832.
The full-stage controller observes both late births offscreen and both
native carries/departures. This continuation adds no placement.

Natural 1UP collection remains the outstanding item in this report.

## Hidden 1UP approach

The nearest preceding authored pipe has left X912, width 32, top Y144.
The existing fourth helper has left X864 and center X880. Its original
initial top remains Y192.

A first ordinary approach enters the target region on the floor. Its
aligned floor jump reaches minimum Y149 at X1018 through X1040 without a
head collision. Later repeated jumps drift horizontally, so that run
provides one aligned floor-jump witness.

A separate six-case CPU sweep starts from the natural fourth-pipe crossing.
It releases horizontal input at X908/912/916/920/924/928, waits for a local
grounded state, advances to X936 and requests a fresh original jump.
All six reach the hidden-block region. Five launch from Y112 and one from
Y128. Every case is back at floor Y176 by X1010 through X1040. None reveals
a 1UP actor. All finish active with status 1 and both lives.

These finite approaches leave ordinary hidden-1UP collection open. The
1-2 brick provides a second authored location whose ordinary approach
still needs a route. This task has added no helper placement.

## Reproduction

Each CPU invocation is zero-output and uses its own bounded output name.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/thomas-availability-1113 --max-files 1 --timeout 30 -- python -B tools/audit/check_thomas_star_route_1113.py --mode availability
python -B tools/audit/run_bounded_build_v1.py --output build/thomas-star-route-1113 --max-files 1 --timeout 600 -- python -B tools/audit/check_thomas_star_route_1113.py --mode star
python -B tools/audit/run_bounded_build_v1.py --output build/thomas-star-return-1113 --max-files 1 --timeout 180 -- python -B tools/audit/check_thomas_star_route_1113.py --mode star-return
python -B tools/audit/run_bounded_build_v1.py --output build/thomas-gap-sweep-1113 --max-files 1 --timeout 600 -- python -B tools/audit/check_thomas_star_route_1113.py --mode gap
python -B tools/audit/run_bounded_build_v1.py --output build/thomas-oneup-sweep-1113 --max-files 1 --timeout 600 -- python -B tools/audit/check_thomas_star_route_1113.py --mode oneup-sweep
python -B tools/audit/run_bounded_build_v1.py --output build/thomas-star-lua-1113 --max-files 1 --timeout 30 -- python -B tools/audit/replay_thomas_star_1113.py --check-only
```

Root's single native queue owns the following invocation. The existing
private directory contains the previous controller, hence `--resume`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/thomas-star-native-1113 --resume --max-files 1 --timeout 300 -- python -B tools/audit/replay_thomas_star_1113.py
```
