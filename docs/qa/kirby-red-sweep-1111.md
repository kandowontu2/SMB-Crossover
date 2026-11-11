# Kirby returning red shell and ledge contact

The pinned `c8bd2e2c` physical replay used the 4-3 Start Level menu to reach
the stage. Kirby naturally inhaled the red Koopa born at X448, swallowed it
for copy 3, and defeated the separate red Koopa born at X624. That shot hit
at age 3 and Kirby retained HP6 and both lives. The earlier replay covers
the outbound shot. Its receipt is `aed82618f6fc0bbd7ed0a6073c1a81efe68e36f25ed4bba270f587ed34af94a7`.

The directed CPU check on `8c1ebb1b` ran the linked `CopyAttack` and `Shots`
code. Both launch facings moved three pixels per update and changed signed
direction at age 32 while retaining their original launch-facing byte. Two
of the four cases crossed a world X page boundary. The same check passed on
the Jay successor `6cb828b3`.

The ledge fixture places a native box-3 Red Koopa at `(626,150)` and runs
`MoveD_EnemyVertically` between two complete shot updates. The target
moves to `(626,151)`. Its bottom edge touches the shell at Y172 while the
old shell center is still `(648,180)` for a rightward shot or `(621,180)`
for a leftward shot. The following sampled centers `(651,180)` and
`(618,180)` both miss. The fixture uses real projectile, enemy gravity,
collision, and defeat code with directed starting coordinates. A natural
ledge miss remains unobserved.

The source proposal expands the red shell's X contact range only over the
three pixels it just traveled. It takes the direction from the current
velocity, so the age-32 return sweeps toward the previous center after
reversing. The native vertical bounds and the
terrain-before-enemy order still apply. Green shells retain point contact.
The patch reuses the existing 163-byte helper at physical PRG 74 `$AB19`
with no new RAM or bank assignment. It changes 153 bytes. The rest of
`6cb828b3`, including Jay, DK Jr., and Sonic, is byte-identical.

The in-memory candidate is
`11896ba69bd35f2a2ab760137288dde09af97b0c6e00152aabcdffbfd1479bba`.
Both directed corner cases and both age-32 return cases now reach the
native defeat routine. Tests covered 1,536 red and 1,536 green boundary
pairs across the 12 native box profiles, 16 hidden or unsupported box
rejections, and a terrain-first pair. All 64 complete green-shot pairs
matched the native results and mapper writes. Their cycle delta ranged
from 27 fewer to three more. The equivalent-outcome red leaf delta ranged
from 15 fewer to 100 more. The interrupt check passed 72 lag-NMI cuts,
72 scanline IRQ cuts, and one nested IRQ. Physical cadence and a current
native 4-3 replay remain to be measured.

- Source `tools/reference/kirby_red_sweep_1111.s`
- Installed reproducer `tools/audit/check_kirby_red_return_1111.py`
- In-memory proposal and tests `tools/audit/check_kirby_red_sweep_1111.py`
