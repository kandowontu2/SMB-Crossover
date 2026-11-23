# Chip and Dale's Easy 1-1 pickups

In Mesen on Downloads `3af597a7`, Chip and Dale each took a hit from
the opening Goomba, going from three health to two. They hit the first
Mushroom block at X336, followed the item along the ground and collected
it at X406/Y176. The native pickup restored full health, played the cue
and awarded 1,000 points. Both characters kept their health and two
lives through 25 further movement updates. Each replay took 801 video
frames and saved zero captures.

| Character | Mesen receipt SHA-256 |
| --- | --- |
| Chip | `3f8197c5a95b0c7a808a4b1bf9415e8b44f918004ee118554fa20c0868675766` |
| Dale | `427a155419a1318d2af970c0b8e9ef5ae61485a507341a1c67c923dcc482c4df` |

Both then passed the Fire Flower block. A second Goomba reduced their
health to two. The Flower from X1248 restored it to three, awarded 1,000
points and played the pickup cue. Both finished at X1259/Y112 with full
health and two lives after 25 more movement updates. Each replay used
1,634 video frames.

| Character | Flower Mesen receipt SHA-256 |
| --- | --- |
| Chip | `ff3856975814e1aa4c55d32da043446138bfedbede35ddd8a21ceba6a989de07` |
| Dale | `31cff7f350f85380ad6f4fa172816b103540ff72f22a9cd1e07fa6c2182affd7` |

On Downloads `06336f15`, both collected the hidden 1-UP from X1024.
The native cue played and the delayed award raised their life counters
to three. Both finished at X1039/Y176 with full health. The Star replays
hit the block at X1616 and collected the moving Star. Invincibility,
Star music and 1,000 points followed. Both retained two health, both
lives and an active Star through 25 more movement updates. Every replay
saved zero captures. Both now have four standard pickup passes.

| Character and pickup | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Chip, hidden 1-UP | 1,396 | `685781b52d24a0fa9ae8d52d9e7a96c0aaee61676c898845f99da2d57bbe4516` |
| Dale, hidden 1-UP | 1,396 | `672c884be12fcea432675f6a8b71b2ef9de89fd37b0d75e07a17ae83346d7af3` |
| Chip, Star | 1,873 | `6b6fb600ee133e0dfe69d165aabe3741c399dad9e6028f1261f40926a5658c86` |
| Dale, Star | 1,873 | `170d0bf81553e710e587a5f2b467be096cf681d8633465e72388e4b1ba3cb945` |

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_chip_dale_stock_1123.py --form chip --route mushroom --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_chip_dale_stock_1123.py --form dale --route mushroom --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_chip_dale_stock_1123.py --form chip --route upgrades --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_chip_dale_stock_1123.py --form dale --route upgrades --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_chip_dale_stock_1123.py --form chip --route life --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_chip_dale_stock_1123.py --form chip --route star --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_chip_dale_stock_1123.py --form dale --route life --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_chip_dale_stock_1123.py --form dale --route star --run
```
