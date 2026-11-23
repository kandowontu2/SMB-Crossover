# Mario the Tank pickup tests

All four standard pickups have recorded passes. The Mushroom and boots
that replace the Fire Flower were collected from normal blocks on
`7ec9cd5c`. [Mushroom and boots test record](checkpoints/2026-11-01/mario-the-tank-natural-powerups/receipt.json)

The hidden 1-UP and Star were collected in Easy 1-1 on the installed
`59e1a591` MMC5 nightly. Both replays select Mario the Tank through the
character menu and use normal controller input. They observe the original
pickup handler and score or life award, then check 25 more movement
updates with the player grounded at the finish.

| Pickup | Result | Video frames | Mesen receipt SHA-256 |
| --- | --- | ---: | --- |
| Hidden 1-UP | Hit the hidden block at world X1024. Collected the moving 1-UP at player X1076 and received a third life. Stopped safely on the near side of the pit. | 1,143 | `e4c2d95fdf30cdf18a7507d089dee7457b263834a1bfa195d75faf11f066210b` |
| Star | Hit the block at world X1616. Collected the bouncing Star at player X1727, started Star music and invincibility, and earned 1,000 points. Finished with two lives and the Star still active. | 1,669 | `b53a8cdb17162c82944af5593e5508914f8a65f7ac7c8bdee1ac49202196eec7` |

Both runs wrote zero capture files. Using the boots against enemies and
terrain still needs a playtest.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 360 -- python -B tools/audit/run_mario_tank_stock_1123.py --run
```
