# Steve Hermann’s Shatterhand movement

The detached 6502 worker matches **467 updates in 11 controller sequences**
against the original US cartridge. Each comparison checks world X/Y in Q4,
signed post-update velocity, locomotion state, and facing. The controller
boots the donor through its ordinary opening. Three donor OAM observations
at frames 2400, 2436, and 2450 also match the existing hardware receipt.

| Original input | Observed behavior |
| --- | --- |
| Right or Left from rest | The first update publishes zero displacement. Each directional update then adds two Q4 units of velocity up to ±22, or 1.375 pixels per update. |
| Ground reversal and release | The first reversal publishes the old velocity, halves it with arithmetic rounding, and then applies the new direction. Releasing applies four Q4 units of drag after the previous velocity is published. |
| Air steering | Directional changes retain momentum and apply two Q4 units. Neutral applies one Q4 unit of drag. |
| Tap A from rest | Launch state on update 1, first displacement −74 Q4 on update 2, 45.125-pixel apex on update 20, landing on update 39, idle on update 48. |
| Hold A from rest | Six subsequent held updates reinstate the launch velocity before gravity. The 68.25-pixel apex occurs on update 25. Landing occurs on update 49 and held A exits recovery on update 50. |
| Down and A | Down wins a simultaneous press. Entering crouch stops that update’s horizontal displacement. Residual velocity can carry into the crouch while it brakes. A press during crouch or held through its release does not launch. |
| A release and repress during a jump | The original hold window stays exhausted. The tested four-update hold, three-update release, and repress reached 54.375 pixels. |

The worker implements the unarmored opening’s ordinary locomotion. The
donor’s movement routines use `$9AB2/$9C6D` for steering, `$9C8A` and
`$9F09` for crouch, `$9EAE` for landing recovery, and `$A012/$A0C8/$A2C2`
for jump control. The first jump update stores −78 Q4 without displacement.
The gravity step adds four Q4 units, capped at +96. The harness supplies a
flat floor at original Y `$1900` Q4 and lets the linked worker resolve
velocity and locomotion state. It exercises no slopes, walls, damage,
attack locks, armor, or companion-robot movement.

The installed punch release is `409d5a2e3b8ca1fdf6fa4512cac399310c44c1837b88b9f7d2a1e5bde858d280`.
A separate transport-only composition places the relocated worker in
physical CHR167, which is an exact blank row on that release. The current
selector census covers 88 finite domains, 49 exact table reads, four native
map mirrors, and the compiled weapon readers. PRG65’s cold wrapper grows
from 157 to 159 bytes within its existing 162-byte allocation. The fourth
metadata row loads into raw bank 2 at `$DC00`, with `$DC00..$DFDF` available
below the authenticated `$DFE0` header.

The in-memory transport image opens all three Mike-family variants after
167 real CPU Main updates. Each variant matches 50 more controller updates
against the installed release in modeled gameplay, OAM, VRAM, and CHR
registers. Mike issues zero cold PPU reads. Jay and Steve each issue 16,400
reads, an increase of 2,050 during the cold load. All three issue zero warm
reads during the replay.

The existing authenticated Steve-only fallback is raw A3 `$BF22`. It
receives movement from PRG96 with Y `$E0` and preparation from PRG86 with
Y `$D6`. Raw bank 2 is already mapped at C2. The present `CLC; RTS`
returns the movement call to the stock routine at PRG96 `$A2CB`. One
available byte at raw A3 `$BFDF` funds reassembling the resident combat
segment with a three-byte jump at that seam. A live bridge must check Y
before claiming the movement call and preserve the preparation fallback.
The replay observed 50 calls from each Steve caller and zero from Mike or Jay.

Claiming the movement call skips the stock prologue at PRG96 `$A2CB`.
Preserve its `JnEnsure`, `JnInputs`, effective tier, clock, hurt timer and
host-profile updates. `JnInputs` publishes the B edge used by the existing
Steve punch. Donor crouch state 3 needs native state 0 and a crouch flag,
since native state 3 means climbing. On the launch update, publish negative
native Y speed from the armed velocity while displacement remains zero, so
the native floor check sees the ascent. Publish the integer horizontal
world delta to `$0701` before the native scroll call. Native terrain resolves
after movement and scroll. Check resolved X/Y and speed before the next
projection, including side corrections, ceiling hits, support carries and
landings. Only a descending donor-air update resolved onto native support
should start donor landing recovery. The native floor routine also runs
while standing. When the native floor check leaves Steve falling after a
grounded projection, start donor gravity on the next update. See the
[live bridge qualification](steve-shatterhand-move-live-1111.md) for the
resulting integration and native 1-1 opening.

| Binding | SHA-256 |
| --- | --- |
| Shatterhand (USA) | `fbdfaab40aedda270d7473be37566b59e68811d932740c105d84fa6b1a7f19e1` |
| Worker source | `ff2b8b96c0a93dc9c5d3a8e7b65e3bf98764d2b92798be7cd488ecf5d30f1751` |
| Detached 286-byte worker | `f8e9a194e5eb9cf9299800ac506d771249e58a096e8aad4cea9061704293e1a4` |
| Transport-only ROM | `400dff82aa1beee208576657b7e30511dbee816afb65205e2bee73e3dda71062` |

The transport-only image has authenticated cookie
`a710200aa5278a05cdcf0e105cfcf105`. Both checks write zero files. This
qualification produced source and in-memory results.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-shatterhand-motion-1111 --max-files 1 --timeout 240 -- python -B tools/audit/trace_steve_shatterhand_motion_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-shatterhand-motion-1111 --max-files 1 --timeout 240 -- python -B tools/audit/check_steve_shatterhand_motion_carrier_1111.py
```
