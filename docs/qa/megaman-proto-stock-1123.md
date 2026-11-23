# Mega Man and Proto Man pickup tests

Both characters earned the Mushroom and Fire Flower in Easy 1-1 from
the installed `28708fa9` MMC5 nightly. The replays start from the title
screen. Proto Man is selected with Select on Mega Man's roster slot.

The Mushroom emerged from the block at world X336. The Fire Flower
emerged from the block at X1248. The replay observed each sprite after
it rose out of its block, followed the native collection and pickup
sound, then verified the new power level after the growth sequence.
Each pickup stayed active for at least 25 further movement updates.
Both characters finished with the second power level and two lives.

| Character | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Mega Man | 2,352 | `56ca73bf1d30114a488023df0a018746c796e3bbee43dd83fd95cdf107d9ff96` |
| Proto Man | 2,257 | `21234148306429e7d8a7b0ec5bafda2ffa02f7ff17643fc4aef199a1712124e2` |

The first replay walked left into a Goomba at X1210 while the Flower
was emerging. The revised input stops and fires before crossing its
path. No game code or ROM bytes were changed for these tests, and the
runs wrote zero captures.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 360 -- python -B tools/audit/run_megaman_proto_stock_1123.py --run --form megaman --route upgrades
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 360 -- python -B tools/audit/run_megaman_proto_stock_1123.py --run --form proto --route upgrades
```
