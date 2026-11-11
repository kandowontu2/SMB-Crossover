# Prince of Persia at the brick after the second gap

The installed MMC5 ROM `4df817587ea5b0aff3f278a4201976745bad4d9dd1b2a99d6cb5fd3b9c74dadc`
passed a controller-only Mesen route from the title to the authored brick
at world X1504–1519, top Y144. It took 6,791 physical frames and retained
both lives and four HP. The route uses the four existing pipes and the
original level terrain, with zero helper platforms.

| Event | Original updates | Player position or actor witness |
| --- | ---: | --- |
| First gap far bank | 1885 | X1175/Y176 |
| Earlier running jump across the second gap | 2219–2253 | X1330→1440, Y176 at the banks |
| Standing jump back across the gap | 2335–2385 | X1457→1371, Y176 at the banks |
| Both Goombas fall into the actual gap | — | Slots 0 and 1 each pass X1408/Y206 and then retire |
| Standing jump back to the far bank | 2715–2765 | X1360→1441, Y176 at the banks |
| Original ledge reach | 2901 | X1496/Y173, action 8, mode 2 |
| Right foot on the exposed brick | 2961 | X1491/Y112, action 10, pose 15, native grounded state |

## Displacement on the next Right input

The same cold route with Right after the climb isolates the displacement at
original update 2964. RAM2 `$C42A`, in the translated world placement, stores
source X1476 over X1499. The return PC is `$A7BE`. The inputs are raw query
X1467, cell base X1440, original cell index 9, horizontal placement offset
36, surface Y145, and material 0. The native export at RAM2 `$C398` then
publishes X1468 over X1491 and the actor enters original fall action 7.
The ledge's only solid point under the initial body is its right foot at
X1504. The next two authored solids are X1600–1631 at the same Y144 top.

This isolates the first backward write to the translated placement path.
The visible native position still has the old X when that instruction runs.
The next investigation is how the original placement request obtains the
leftward empty cell immediately after the 16-pixel brick climb. The exact
Goomba and Koopa side-contact differential independently supports retaining
the original unarmed injury response. [Contact proof](prince-side-contact-1111.md)

The passing climb receipt is `ae659fef41fa2c510a1d9863329d2f5c22a35b9332969eecaebdac6c9f857a6f`.
The displaced run receipt is `e286b59322d4be06bb98c0844d8ef0f13bc928729b3291cebf2f5547f83a953e`.
The assembled controller SHA-256 is `f171d01ea4c31c8d451fa4efaf295fe09e0f079b848c906c7acfa212733d2167` for both runs.
The full-stage clear, the Koopa bypass, and the natural power-up route remain
open. The installed ROM and release were unchanged by this investigation.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/prince-late-physical-1111 --max-files 1 --timeout 200 -- python -B tools/audit/replay_prince_koopa_1111.py --output build/prince-late-physical-1111
python -B tools/audit/run_bounded_build_v1.py --output build/prince-late-physical-1111 --resume --max-files 1 --timeout 200 -- python -B tools/audit/replay_prince_koopa_1111.py --output build/prince-late-physical-1111 --koopa-mode ledge
```

The second command reproduces the negative with exit code 1. The task uses
one generated Lua file and stdout receipts, with zero captures or state dumps.
