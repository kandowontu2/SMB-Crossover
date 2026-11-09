# Mini Mario frame budget, November 8

The MMC5 build `e90d30c1c9636be6eb304a7b3b1506b862f8171dc2773d809482e25b0a5417df`
uses the same three 1-1 lifts, two native 4×4 fireball collision boxes and
Game Boy Color moving and impact art as `fc7d4554`. It still has busy-stage lag.

| Same controller-only 1-1 route | Previous build | New build |
|---|---:|---:|
| Active video frames | 3,084 | 3,022 |
| Gameplay updates | 2,597 | 2,597 |
| Frames with no controller read | 1,132 | 998 |
| Lives on entering 1-2 | 2 | 2 |

The empty-area replay had 180 idle updates in 180 video frames. Walking in
both directions, braking, jumping and landing also advanced every frame. The
earned mushroom completed its growth sequence. A separate Fire Mini fixture
had 60 powered idle updates in 60 frames. Both native shots reached OAM DMA
together when firing left, right or up. It verified all four moving phases,
both impact tiles and a staged Goomba hit. The fire tier was staged for this
fixture.

## CPU changes

- Native side probes read each of two duplicated block cells once. The guarded
  branch saves 300–336 cycles and matched 2,800 CPU cases.
- Mini runs the existing projectile drawing code from its authenticated WRAM
  overlay. This removes the draw bank switch and saves 82–158 cycles in the
  compared GameCore updates. The four graphics frames stayed byte-identical.
- The Mini renderer uses a smaller Goomba draw loop. One actor saves 47–53
  cycles and five save 247–265. Other characters retain their actor loops.
  Their full legacy OAM clear takes 15 additional cycles once per call.
- Repeated visits to a used lift window take 99–116 fewer cycles. The admission
  proof includes 781 nested IRQ contexts at the linked GameLoop stack depth.
- The audio change preserves ordered hardware writes and reduces the work in
  the mixer and cue decoder, including a tested lag interrupt.

The composed build matched 96 linked GameCore updates across four fixtures.
The average saving ranged from 457 to 713 cycles per update. The earlier
profile at world X758 still provides a lead for further work. The old build
spent 36,700 foreground cycles there and made 96 mapper far calls. Four side
queries passed through the SMB2 check, a same-bank call and two more guest
dispatches before reaching Mini's native tile filter.

## Follow-up build

Build `37bb9c1a69b993edda540c75cbe256aeac75396d55d34d9daf3d4de86deebeeb`
cleared 1-1 in 2,931 active video frames with 2,589 gameplay updates and
846 frames without a controller read. It boarded and departed all three
lifts and reached active 1-2 with both lives. Empty-area movement and 180
idle updates advanced on every video frame. The earned mushroom and the
two-shot graphics fixture also passed.

The shorter side dispatch saves 318 cycles per Mini fallback query. The
shared Mario the Tank path reached its loaded side handler 708 times on
both sides of that change. The floor preflight also covers decorative pipe
tops while preserving native Down entry on warp pipes. A live sample at
world X759 read `$13` at the left foot and `$00` at the right. At that spot,
the final candidate used 30,931 foreground cycles and 34,754 elapsed cycles.
The intermediate side/audio build used 35,088 foreground and 38,782 elapsed
cycles on the same terrain with the same actor count. Its original floor
probe treated the decorative pipe as a fallback.

The actor loop now enters the common Goomba motion and terrain paths with
less dispatch work. Other ordinary actor dispatches pay eight additional
cycles. Audio macros use their resident program bank and keep their ordered
hardware writes. The individual side, floor, actor and audio changes passed
linked interrupt tests. The floor test used native GameLoop stack depth.

In a five-enemy CPU fixture, ordinary Mario used about 25,700 foreground
GameCore cycles and Mini used 27,500 before interrupt work. Busy scenes still
miss frames. The new replay's most expensive sampled update was at X782
with 33,565 foreground and 38,472 elapsed cycles. The highest concentrations
of missed reads were at X640–767, X768–895 and X1920–2047.

## Parser and lift follow-up

Build `a08d839b187fc6866a3fd3658200c2f26b8e3724b3b4de3b5e7d2a65702598d2`
completed the same 1-1 route in 2,922 active video frames with 2,590 game
updates and 832 frames without a controller read. It retained both lives,
all three lift crossings, the earned mushroom, and both original fireballs.
Empty-area movement and 180 idle updates advanced on every video frame.

The shared parser now clears the brick-health and coin-hit columns in a
single pass. The former blank 18-byte gap between the bank 2 level segment
and the level-variant bridge holds the loop. The change saves 154 cycles per
guest column. The 10,752 paired CPU cases preserved terminal registers,
memory, and all three maps. The separate IRQ and lag-NMI sweep included
temporary column pointers. It allowed the fixed IRQ's timing-only `BIT R0`
read and checked for all other reads or writes to those pointers.

The platform callbacks skip inactive Ryu work for other profiles. A live
Mini lift costs 457 fewer cycles per tested update. The typed Zelda II
route keeps its existing callback and the Ryu path retains its source
behavior. IRQ and lag-NMI cuts also passed for the lift change.

The busiest update on the new replay was near X1513 at 37,148 elapsed
cycles. Busy-stage lag remains.

## Terrain drawing and Mini terrain reads

Build `ee9b3f55` completed the same route with both lives and all three lifts.
It used 2,885 active video frames and 2,590 game updates, with 774 missed
controller reads compared with 832 on the previous build. Empty-area movement
and 180 idle updates ran every frame. The mushroom and two fireballs passed
their separate native replays.

Each pair of native graphics columns renders the same metatiles. The left
column sets their palette bits and the right column now reuses those bits.
The right column still produces its graphics packet and its final scratch
state. Across 5,120 paired cases the right pass saves 508–522 cycles and
the left saves 34. The 1-1 replay observed 290 pairs with matching metatile
data and preexisting palette bits. Both actual interrupt paths preserved
foreground state across 759 cuts each.

Mini's physics also avoids rereading a native metatile when successive probe
points are in the same cell. The owner-only update saved 86–436 cycles over
232 CPU-tested game updates, with 3,403 interrupt checks. Busy gameplay still
exceeds the frame budget near the crowded pipes and blocks.

## Local receipts

- `build/mini-frame-budget-delivery-1108/verified-delivery.json`
- `build/mini-frame-budget-route-1108/capture/timing.json`
- `build/mini-frame-budget-idle-1108/capture/timing.json`
- `build/mini-frame-budget-power-1108/capture/result.json`
- `build/mini-frame-budget-fire-gate-1108/capture/result.json`
- `build/mini-frame-budget-1108/candidate.json`
- `build/mini-busy-pipeline-delivery-1108/verified-delivery.json`
- `build/mini-busy-pipeline-final-qa-1108/route/capture/timing.json`
- `build/mini-busy-pipeline-final-qa-1108/route/capture/instruction-sample.json`
- `build/mini-busy-pipeline-final-qa-1108/fire/capture/result.json`
- `build/mini-floor-decor-async-1108/proof.json`
- `build/mini-active-actor-1108-v1/funded-v3-CPU.json`
- `build/mini-audio-transport-1108-v4/irq.json`
- `build/mini-side-dispatch-irq-1108/proof.json`
- `build/mini-parser-lift-delivery-1109/verified-delivery.json`
- `build/mini-parser-lift-qa-1109/route/capture/timing.json`
- `build/parser-dual-shadow-1109/proof.json`
- `build/parser-dual-shadow-irq-1109/health-batch-async-v3.json`
- `build/mini-active-actor-1108-v1/lift-bridge-v5-CPU.json`
- `build/mini-columns-transport-delivery-1109/verified-delivery.json`
- `build/mini-columns-transport-native-1109/route/capture/timing.json`
- `build/mini-columns-transport-native-1109/route/capture/column-pairs.json`
- `build/mini-column-graphics-1109/proof.json`
- `build/mini-column-irq-1109/irq.json`
- `build/mini-kernel-transport-1109/v2/irq.json`
