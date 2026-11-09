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

## Local receipts

- `build/mini-frame-budget-delivery-1108/verified-delivery.json`
- `build/mini-frame-budget-route-1108/capture/timing.json`
- `build/mini-frame-budget-idle-1108/capture/timing.json`
- `build/mini-frame-budget-power-1108/capture/result.json`
- `build/mini-frame-budget-fire-gate-1108/capture/result.json`
- `build/mini-frame-budget-1108/candidate.json`
