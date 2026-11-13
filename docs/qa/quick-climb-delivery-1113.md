# Quick Man flagpole delivery — November 13

Candidate ROM SHA256:
`4641ca4fb72699c0478e31b831d4c4ea0ffd2227be7f8446666092d2cc26e1d3`

Parent ROM SHA256:
`a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a`

IPS SHA256:
`ce922a8793496839efea21d2a9e15c2a3849df59415537fc910a60b6450f8225`
(2,099,506 bytes; reconstruction from the existing clean headered SMB base
equals the complete tested candidate).

## Result and change

Quick's donor terrain adapter treated native climbable shaft cells as ordinary
walls, preventing normal flagpole contact. The five-byte hook now calls an
11-byte helper in the already copied Quick-owned tail B98D..B997. It masks
native climbables for donor terrain while preserving the native flag/climb
handler, solid base, other cells, registers and flags. Two authenticated cache
cookies change with the payload. Total41 changed bytes, no allocation growth,
graphics changes or helper-platform changes. Exact forward/inverse recipes:
`compose_quick_climb_material_1113.py`; source/proof commit `b2b337a7`.

Root independently repeats the finite suite:65,536 attribute/status cases,
39,936 tile/Y/status cases,7,680 signed-Y cases,225 foreign public callback
pairs across44 owners including Bass/Roll,146 real IRQ and146 lag-NMI cuts
through complete movement return, minimum SP166. Complete cold readback,
new-tail fault rejection, prior-cookie rejection and three publication/copy
lag-NMI cuts pass; cold minimum SP183. These foreign callback fixtures do not
claim44 complete character playthroughs. See `quick-climb-material-1113.md`.

## Native verification

The current default-settings Mesen controller naturally reveals, matures and
collects the mushroom at336, hidden1UP at1024, later ordinary mushroom at1248,
and Star at1616. Quick's no-growth policy keeps the later item a mushroom;
this is not a natural flower-grant claim. It clears the non-shortcut1-1,
executes native flagpole/climbing and castle flow, and then waits without
input for grounded active1-2 at X40/Y176/high1/state0, HP/maxHP40, lives3.

Frozen controller SHA256:
`963f00a2ca58167983ef7a25da989d01df03decc60eabdba654237f227105691`

Native candidate receipt SHA256:
`cd9be0d5a648dd026bd1df1eb345d6c0f3ba4ea0dd136a878136de4092fdfbcd`

The run lasts5,693 physical frames/3,622 updates. The controller makes a full
held-A jump over the solid pole base and releases shooting near the pole.
Its health observer excludes the next room's inactive forced-blank cache;
engine11 and life-loss checks remain unconditional. Active gameplay must
retain nonzero health. Earlier observer rejection at engine5/HP0 was not a
game death. The standalone recipe is `replay_quick_flag_jump_1113.py`.

The same final control policy on parenta3 fails without any native flag/climb
events: terminal X3170/Y0/high1, HP40/lives3, level0, route-stall. Baseline
controller `4cf7a11ceb37fea8bc606e9792c19ff8d18e68eccb27dc9f4c216e88d6cbe8d4`,
receipt `2a1931d01345ef5426ece4e5e438eb6c471a63597e92fca2aa1d159aef4fb89d`.
The fix therefore has a native positive/negative comparison with the same
input policy. No emulated position, actor, inventory or health writes occur.

## Delivery status

Private candidate, finite gates and native positive/negative checks are
complete. Downloads install/repeat and sole Current/Latest IPS refresh are
the remaining delivery steps. `deliver_quick_climb_1113.py` performs direct
replacement with memory-only rollback, no backup files, before/after patch
guards, exact installed replay, IPS roundtrip and remote asset verification.

Root retains one candidate and one controller in the shared two-file output.
No screenshots, videos, dumps or receipt files were created. Build preflight
at this checkpoint:3,123,068,226 bytes/19,998 files, below unchanged caps.
Jay's head/helper work and Steve's armor remain separate private candidates;
the full-roster/all-powerups goal remains unfinished.
