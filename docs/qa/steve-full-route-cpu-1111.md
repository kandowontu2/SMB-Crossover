# Steve Hermann’s controller route through World 1-1

The CPU replay selects Steve through the Mike-family menu and runs the
normal Main update on the exact installed MMC5 image
`e6b152e26b43449115a7ff21903ae756346052e55dbdd94d8751e8c3a0951f23`.
It defeats the first naturally spawned Goomba with a punch, clears all six
native pipes and three gaps, reaches the flag at X3161/Y135 and the castle
at X3266/Y176, and enters active underground 1-2 at X40/Y48. Steve retains
6 HP and both lives throughout. The final transition occurs 3,513 CPU Main
updates after clearing the first pipe. The replay uses no helper platforms.

| Native obstacle | World span | Grounded arrival X/Y |
| --- | --- | --- |
| Pipe 1 | X448–479 | 499/176 |
| Pipe 2 | X608–639 | 664/176 |
| Pipe 3 | X736–767 | 796/176 |
| Pipe 4 | X912–943 | 972/176 |
| Gap 1 | X1104–1135 | 1158/176 |
| Gap 2 | X1376–1423 | 1434/176 |
| Gap 3 | X2448–2479 | 2507/128 |
| Pipe 5 | X2608–2639 | 2652/176 |
| Pipe 6 | X2864–2895 | 2897/160 |

The third-gap approach needs two jumps. From X2398/Y128, tap A with Right.
Release Right once airborne at X2411 or later. Original air drag brings
Steve onto the upper stair at X2427/Y112. Walk right to X2436 and hold
Right+A for nine updates. That jump crosses the gap to the far staircase.
Holding Right throughout the lower-stair hop overshot the usable takeoff and
fell into the gap at X2467–2469. The successful route uses the same ROM and
original jump as those unsuccessful attempts.

The automatic 1-2 entrance advances the side-pipe timer while Steve waits
at X160/Y176 with the native priority bit `$20` set. The longer replay
observes the timer count down from 151 to 31 before the next area loads.
The first 3,400-update trial stopped during that countdown.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-shatterhand-route-1111 --max-files 1 --timeout 240 -- python -B tools/audit/replay_steve_route_1111.py
```

The CPU replay writes zero files. A separate physical controller replay is
required to qualify the route in Mesen.
