# River City pickups in Easy 1-1

The replays start from the title on the Downloads MMC5 nightly, select
the requested fighter, and use regular controller inputs. They record
the authored block bump, the mature item, collection, the pickup cue,
score or life credit, and 25 further River City movement updates.
They save no captures.

Alex passed the initial Mushroom check on `14b0b4c2`. He hit the block at
X336, caught the emerged item at X403 and recovered from 48 to 64 stamina. His own
power tier advanced from 0 to 1 and persisted with both lives.
Afterward the controller reached the Fire Flower block and kept moving
one pixel back and forth at X1242–1243. The replay timed out while
lining up for the head bump. The revised controller uses the remaining
distance directly to stop under the block.

Mesen receipt
`fc901ce8e56b14aaf5902b68603e0b42b97a14ab0ca881c341aad68b892d5789`.
Controller SHA-256
`f1fe9ea6c10a603fd0b8f4a81175def1ac18728fc2a53a8ed7d98674e5aad22e`.

The revised Mesen route passed both upgrades for Alex and Ryan on
Downloads `94fa7a02`. Each Mushroom raised stamina from 48 to 64
and advanced their own tier to 1. Each Flower restored stamina from
56 to 64 and advanced the tier to 2. Both replays ended at X1243/Y112
with full stamina and both lives, after 25 further movement updates.

| Character | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Alex | 2,536 | `0e0d0c705e5073f3196175c33ce861ac93db3b3ae1539584c24de867432e0e91` |
| Ryan | 2,536 | `54c4f120e57cfc8ce1356af8423b5fb50b29bcba20a0e01e8fc7c182a213c810` |

Both fighters also collected the hidden 1-UP from X1024 and the Star
from X1616 on the same nightly. Their 1-UP runs ended at X1051/Y176
with three lives. Their Star runs ended at X1647/Y176 with both lives,
the Star active, and the native music and 1,000-point credit observed.
Each run included at least 25 movement updates after collection.

| Character and pickup | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Alex, hidden 1-UP | 2,137 | `9c1cc6491f5bb04e0184a6313b5c2a4d42daa9ec26106e7f5fe39f248b8817bf` |
| Ryan, hidden 1-UP | 2,137 | `b5c4e72e00d1f82c7437418b3cc0f23fefcbf50b9bf8d2ba743ed92fa1840415` |
| Alex, Star | 3,269 | `33204fd786d3ac7e0c5bdb7e995a9f33d21745b6583051abc0d09c3b2c82ae84` |
| Ryan, Star | 3,271 | `d7ba1adba666ec75885443a5b6d3f852f6cffa9d18ea07ef5389db4913a90f41` |

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 210 -- python -B tools/audit/run_river_city_stock_1123.py --form alex --route upgrades --run
```
