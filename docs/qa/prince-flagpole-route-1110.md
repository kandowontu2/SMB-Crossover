# Prince after the second gap, November 10

The exact 49295a Downloads CPU replay and its in-memory source reconstruction
reach X1547/Y176 at update 1856 with four HP and two lives. The player is in
original running action 1, frame 11, facing right. The next native actor is
the live slot 0 green Koopa, ID0, at X1706/Y184. The camera covers
X1425–1680. The replay uses the translated third-pipe starting scene from
the [transport proof](prince-sonic-transport-1110.md), then native GameLoop,
the authored terrain and enemy parser, ordinary NMI, and controller input.

Eight direct running A windows between a 27- and 177-pixel enemy gap admit
original action 4. Contact happens at X1661–1683 and Y169–178 while the
Koopa is alive. The fatal source response is action 85 and HP4→0. Current
terrain includes the Y144 tiles `$51` at X1600 and `$57` at X1616. Early
running and immediate standing attempts from the second-gap return also
meet the live Koopa before reaching X1740. The traces establish contact.
The first incorrect collision write, if any, remains unlocated.

The 1554 brake threshold triggers at the next observed ground position,
X1557/frame 12. Neutral settles at X1594 with the active Koopa already at
X1678. Standing A admits action 3 on update 1914. The run ends at X1650 on
update 1944 with the live Koopa at X1662 and Prince in fatal action 85.
All eight actor-gap waits also admit action 3 and reach fatal contact.

| Supported A request | Koopa gap 60 | Gap 74 | Gap 88 | Gap 102 |
|---|---:|---:|---:|---:|
| X1542 | X1580/2100 | X1598/2076 | X1608/2052 | X1618/2032 |
| X1566 | X1604/2044 | X1622/2020 | X1632/1996 | X1642/1976 |

Each cell gives the fatal player X and update. The first wait checker let
the idle timeout carry into the A request. The final rerun resets the
progress clock at the state transition and records all eight admissions.

## Retained physical control

Private image `529e51490f610f690ad16c84a868615820cf4e438154127925e15feb5fd7bff1`
has a controller-only Mesen witness beyond this Koopa. The retained report
is `build/prince-koopa-standing-v2-native-1110/capture/full11.json`, SHA-256
`9156c420422c1a24a2a8ff4d8ab456438fc60ac1819a4139e86a0236024dfcfb`.
It records zero helpers and zero emulated writes.

| Native event | Main update | Position and source state |
|---|---:|---|
| Far bank of second gap | — | X1443/Y176, running 1/frame 8 |
| Reverse running A | 3053 | X1452/Y176, left run frame 6, Goomba gap 56 |
| Reverse landing | 3089 | X1342/Y176, action 4/frame 43 |
| Both Goombas retired | 3318 | X1315/Y176, standing pose 15 |
| Forward running A | 3377 | X1346/Y176, right run frame 6 |
| Brake before Koopa | 3477 | X1554/Y176, right run frame 13, phase 1 |
| First observed active Koopa | 3494 | Slot 0, X1711/Y184, leftward |
| Standing A request | 3522 | X1587/Y176, supported pose 15 |
| Standing A admission | 3523 | Original action 3 |
| Beyond the Koopa | 3626 | X1708/Y176, running 1, HP4, two lives, slot 0 inactive |
| Next fatal contact | 3713 | X1817/Y176, action 85, HP0 |

The standing jump reaches Y174. The older controller keeps the camera at
X1302–1557 while Prince turns, uses original careful action 42, and reverses
across the gap. This leaves room to settle X1315 and start the forward run at
X1346. The newer CPU route settles at X1351 before its standing return and
the Koopa is already active by X1547. Reproducing the older camera and enemy
birth conditions through actual controls is the next route. The private
result reaches X1708. Current-image flagpole and castle remain open.

## Reproduction

The default command binds the in-memory source reconstruction to SHA-256
`49295acff1d70349119b599882a2ec0b4e2f58d21f153c90b2228dc9aceee2a7`.
`--installed` reads the same exact revision from Downloads while that
revision is installed. Later nightlies use the source reconstruction.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python tools/audit/run_bounded_build_v1.py --output build/prince-flagpole-route-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_prince_flagpole_route_1110.py
python tools/audit/run_bounded_build_v1.py --output build/prince-flagpole-route-1110 --resume --max-files 1 --timeout 600 -- python -B tools/audit/check_prince_flagpole_route_1110.py --wait-koopa
```

The checker emits only stdout. Full 1-1 and natural powerups remain open.
