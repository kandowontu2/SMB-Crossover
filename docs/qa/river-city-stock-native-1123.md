# River City pickups in Easy 1-1

The replays start from the title on Downloads nightly `14b0b4c2`, select
the requested fighter, and use regular controller inputs. They record
the authored block bump, the mature item, collection, the pickup cue,
score or life credit, and 25 further River City movement updates.
They save no captures.

Alex passed the Mushroom check. He hit the block at X336, caught the
emerged item at X403 and recovered from 48 to 64 stamina. His own
power tier advanced from 0 to 1 and persisted with both lives.
Afterward the controller reached the Fire Flower block and kept moving
one pixel back and forth at X1242–1243. The replay timed out while
lining up for the head bump. The revised controller uses the remaining
distance directly to stop under the block.

Mesen receipt
`fc901ce8e56b14aaf5902b68603e0b42b97a14ab0ca881c341aad68b892d5789`.
Controller SHA-256
`f1fe9ea6c10a603fd0b8f4a81175def1ac18728fc2a53a8ed7d98674e5aad22e`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 210 -- python -B tools/audit/run_river_city_stock_1123.py --form alex --route upgrades --run
```
