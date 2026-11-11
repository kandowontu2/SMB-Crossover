# Prince keeps his footing on the ordinary brick pair

Prince can release Up after climbing onto the ordinary bricks at world
X1600 and X1616, top Y144, after the second gap in 1-1. The source actor's
standing terrain query reaches behind the body into an empty column. The
repair uses the exposed SMB solid under the facing foot when the actor is
in the original idle pose and both the native grounding and the projected
sole agree. The previous moving support rules still apply. No level data
or helper platforms changed.

On the previous nightly `409d5a2e`, original update 3204 dropped Prince
from world X1587 to X1564 even though the native foot still touched the
first brick. On the candidate, the same update accepts the top at Y144
and the original idle action continues with X1587/Y112.

Two controller-only Mesen replays start from title and use the authored stage.
Both repeated with identical receipts after replacing the Downloads nightly.
The automatic-patch guard passed before and after replacement. No backup
ROM was created.

| Route | Terminal state | Canonical receipt SHA-256 |
| --- | --- | --- |
| Release Up and wait 20 original updates | X1587/Y112, idle, grounded, 4 HP, 2 lives | `29714b4d23560d7b0834abb8278d5522ca9790bc68b78580e837536a0a068f94` |
| Climb and jump past the live Koopa | X1713/Y176, grounded, 4 HP, 2 lives | `623c8d2385d18fcadc1331c0c459850227446b6a39bc93c0e79a4cf0f5bdcb82` |

The CPU checker traced the original terrain result through the full
standing decision, checked 1,273 unchanged material cases and 16 full
negative decisions, and injected 274 IRQ and 274 lag-NMI cuts. The patch
reverses to the exact previous nightly. Both replays and the CPU check
produce no captures or per-frame files.

The Goomba pair beyond the Koopa and the complete stage clear are still
open. The existing question block is reachable from below, but the
original climb at that approach finishes beyond its far edge. A retreat
to the previous bricks from X1689 keeps both lives but clamps the camera
past the approach needed to climb the pair from the right.

- Candidate ROM SHA-256 `ac2624467d4c3abc8988088ab22a4d2a0f52059e2e2d23373940fc9d17006066`
- IPS SHA-256 `924671aa4670c1948e2374cb759a847157eea63b0e5dc168ef405d3aee069f3c`
- Replay tail SHA-256 `20bb02bebee0949abf9e935927c8abd9c446e8f970254020a0c6420dd4b6e93f`
- Installed-run controller SHA-256 `11803da41c62bf1ac931a2ade0745362c0d8806864694bc724bd9f97c9df3375`

[Assembly](../../tools/reference/prince_exposed_brick_idle_1111.s) ·
[CPU checker](../../tools/audit/check_prince_exposed_brick_idle_1111.py) ·
[Delivery recipe](../../tools/audit/deliver_prince_exposed_brick_idle_1111.py)
