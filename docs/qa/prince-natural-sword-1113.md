# Prince earns the sword on the current nightly

Actual Mesen on Downloads
`aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1`
passes the natural mushroom and flower route. The flower emerges from its
authored block, matures, and is collected atX1260/Y112. The native actor is
erased and the original sword inventory becomes1, acquisition action91.
Both lives andHP4 remain at6,717physical frames/2,898 source commits. The
earlier route includes one ordinary enemy injury; this is not a no-damage run.

Controller SHA256:
`917390d92024d2a1b3a0b2dd6ae7ba2c26874dabb8329ab278d60db48700614b`

Native receipt SHA256:
`ec714a5992c75275e330ad0ee724565a260ecba5a652698501cf4356967e95a6`

No ROM bytes, physics, source positions, items or inventory are modified.
No helper is added. Downloads automatic patch guards pass before/after.
The original sword combat, draw/parry/attack/sheath and enemy geometry have
separate earlier directed qualifications. This natural pickup replay ends
at acquisition and does not claim another native sword enemy defeat.

## Original controls resolve the access problem

The frozen12f55c86 controller retreats toX1214, then repeatedly jumps below
the ledge without collecting the mature flower. Up+Right instead runs past
the item; its actualMain/NMI model result endsX1398/Y177, sword0, after2,666
updates. That negative controller is adc4870dddd3029b7c6e7ec9fe544ead0bbf694769dd4f0a231bf4b9a8aee950.

`check_prince_flower_natural_continuation_1113.py` now clones the actual
naturally earned2,541-update prefix in memory, atX1214/Y176, HP4, mature
flower present. Eight neutral updates, two Right updates, sixty neutral
updates, then heldUp allow the original climb from the row's right side.
On reachingY114, Left crosses the row and collects the flower. The passing
continuation takes344 updates, endingX1260/Y112 with inventory1 and actor0.
It supplies controller input only; there are no fixture actors or position
seeds. This is CPU/Main/NMI evidence, separate from the native result above.

The initial260-update diagnostic horizon ended while that climb was still
in progress atY118/action10. Extending the measured case to420 made the
natural collection visible; the short horizon was not proof of unreachable
geometry. Unused source-mode/facing diagnostic labels were corrected from
the original animation-pointer fields to their actual618/615 addresses
before the final passing continuation. Verdicts use actual native X/Y,
health, lives, sword inventory and actor erasure.

`check_prince_natural_sword_1113.recovery_controller(raw)` freezes this input
sequence into the existing full route. Its first native attempt reached
the row atX1289/Y113 but the replay checked the old climb age immediately
after switching to the walk phase. Receipt
`a960125e240b14763aaba2eb37aa3570bcccd8b94da6bd89f031f7694624c432`
is that observer failure, not a gameplay freeze. Returning after the phase
switch fixes the stale-age check; final917390d9/ec714a59 pass above.

The unchanged baseline recipe stays pinned toa3 and12f55c86. Explicit typed
Jay/Quick inverses recover that recipe input in memory; the complete Prince
packet and cookie must match before controller generation. ActualCPU/Mesen
execution uses aa501 and reports its real hash. No fake Downloads launch is
claimed for the in-memory recipe input. Generated outputs remain the one
existing Lua file; there are no new captures, ROM copies or receipt files.
