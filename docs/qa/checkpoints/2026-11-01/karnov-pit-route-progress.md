# Karnov 1-1 route progress

Current nightly SHA256: `58e50db6ceead7c3706087c92d6e49014f05ff8b80b000be30c27b4e7dfa11f2`.

Controller-only run `build/karnov-pit-route-1101-v1/probe/capture` crossed both tall pipes and the first pit. The previous route jumped too early at world X1054; delaying the next jump until X1090 passed the gap. No ROM change, RAM writes or cheats were used.

The run ended in death at maximum world X1222 after3559 gameplay frames. The endpoint screenshot was inspected and shows the enemy group beyond the first pit. This is **not a stage clear** or proof of a collision defect. The controller still disables shooting after X530 to isolate the earlier pipe movement test; restore combat input beyond the pipes for the next attempt.

Retained output is one compact position trace, two PNGs and bounded emulator logs. No video or frame sequence was captured.

Two subsequent runs in `combat-probe` and `ground-probe` restored shooting beyond X1140. Both crossed the first pit, but ended in enemy contact at maximum X1235 and X1189 respectively. Their endpoint screenshots were inspected. The grounded run visibly sends standing shots above the approaching Goomba; the next controller attempt should exercise the original crouch/fire behavior before treating this as a projectile collision defect. No stage-clear claim is supported by these runs.
