# Native Luigi movement and guest camera recovery

Luigi now runs Mario's actual movement engine. The two requested dry changes
are a 51/256-pixel stronger initial upward velocity and one-eighth less ground
braking. Acceleration, run limits, air control, gravity, jump release, climbing,
springs, moving platforms, collision sizes and death use Mario's routines.
Water uses the same MarioWaterMovement path, including whirlpool forces.

Measured jump heights in all three power forms:

| Jump | Mario | Luigi |
| --- | ---: | ---: |
| Standing, held A | 66 px | 73 px |
| Running, held A | 83 px | 90 px |
| Early A release | 31 px | 34 px |

The independent physics control was captured on immutable v18, before the
Luigi rewrite. It contains 39 controller-driven arena trials and 4,992 rows.
The fixture explicitly initializes both native horizontal fractions and the
moving platform's real counter/phase. V22 Mario matches every reference row
on both mappers. Luigi matches all environmental trials and acceleration
prefixes, with only the requested dry jump/braking differences. Native enemy
contact death matches all 209 Mario control rows. The actual 2-2 pit control
also checks 452 identical fall/life-loss rows; Luigi's room initialization takes
four additional hardware frames. These arenas do not establish a level clear.

The guest camera defect was reproduced by driving right, introducing one short
native side-contact scroll hold, and continuing right. Matching camera speed
to player speed preserved an overshoot indefinitely. Guests now recover one
extra pixel per moving update until they return to the normal follow point.
Scroll lock and side-contact holds still apply. Mario and his Luigi alternate
retain the original camera behavior.

The camera matrix passes all 11 guest movement profiles on both mappers:
normal and recovered positions are 112 pixels from the camera's left edge.
The independent v18 negative leaves Mega Man at 128 pixels after the hold.
The native Mario/Luigi controls retain their original 130-pixel held-contact
result. The camera moves monotonically, by at most five pixels per update.

Scrooge's refined pogo contact checks the actual contacted enemy rectangle
before body injury, resolves both Bowser halves to their shared health, and
protects only that same enemy's short hit flash. V22 passes ordinary 58-pixel
jumps, 84-pixel pogo rebounds, ledge recovery, both Bowser halves, facings and
collision parities, without general invincibility or protection from adjacent
immune enemies. Samus's suitless crouch artwork and 432 head/block contact
cases remain covered separately.

V20/v21 are rejected checkpoints: a shared Luigi water check masked the guest
ID in A before subsequent gravity/fall dispatch, altering several other guests.
V22 replaces the masks with explicit comparisons that preserve the original
guest ID. All affected Bass/Ryu/Sophia/Scrooge movement fixtures pass again
without changing their expectations.

Evidence:

- `build/checkpoints/roster-audit-v22/manifest.json`
- `build/verification/mls-v22-recovery-summary.json`
- `build/verification/root-v19-focused-summary.json` (camera and Samus controls)
- `tests/mario-native-physics-reference.json` and its pinned compressed trace
- `build/verification/flame-v22/summary.json` (separate Flame palette correction)

V22 is accepted against 623 regression case slots across both mappers. The
original full-suite report retains 608 passes and 15 failures. Those failures
were resolved by fixture-only corrections: exclude unrelated bank callbacks
from the Windmill source model; use a coherent visible approach and actual
contact events for all 28 flagpole cases; and check Luigi's native spring
velocity/forces instead of the retired guest state. The two spring reruns
cover 112 actual contacts. Source equations, real contact, bounded displacement,
full actor pools and next-room control requirements remain enforced.
`build/verification/accepted-roster-audit-v22.json` binds the original report and
all corrected reruns by hash. Production ROMs did not change during these reruns.

Mario's v22 fixed controller replay is verified through 2-2 into active 2-3
with zero deaths. Its native-audio recording is encoded and every video frame
has passed the automated review; sampled contact-sheet inspection is recorded
separately. `build/roster-through-2-2/final-recordings-v22.json` tracks the final
videos. The other 13 roster recordings remain pending.
