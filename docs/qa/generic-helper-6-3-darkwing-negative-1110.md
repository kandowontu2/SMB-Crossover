# Darkwing 6-3 route limit

The private `dad68311` replay selected Easy Darkwing and 6-3 through the real
Start Level menu. All other cheats stayed off. Darkwing jumped from X246
to the first low canopy. The second jump began on frame 886 at X327, Y176
toward the low canopy starting at X384. Active play reached X369. Native
death began on frame 923 at X370, Y244 and camera-left X258. The replay
did not reach the Arrow pickup or the record 20 entry window.
[Native result](../../build/generic-helper-6-3-darkwing-1110-v1/capture/result.json) ·
[Terminal image](../../build/generic-helper-6-3-darkwing-1110-v1/capture/terminal.png)

The two low canopies have top Y208. Between them is a canopy spanning
X336–383 at top Y144. Darkwing's ordinary 50-pixel jump cannot land on the
middle canopy from the first low canopy's top. The route aimed for the
lower far canopy while the head probe crossed into the overhead tile's
column. The replay did not record the exact head collision. The first
authored stock platform is the vertical lift at X448, beyond this gap.
The first authored Arrow opportunity is the X880 power-up. The native
recovery cache requires a vertical pipe and does not accept tree tiles.
[Level and actor streams](../../src/level_tiles.s) ·
[Darkwing movement](../../src/darkwing_core.s#L78) ·
[Recovery gate](../../src/darkwing_recovery.s)

No stock-platform retry is staged for this obstruction. This run supplies
no actor-capacity verdict. Kirby's native Up flight remains an independent
way to reach the 6-3 drop and helper window while leaving Darkwing's Arrow
pressure test open.
