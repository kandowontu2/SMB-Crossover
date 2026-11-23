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

## Hidden 1-UP and Star

The replay bumps the hidden block at world X1024 or the Star block at
X1616, then moves to the right of it while the pickup rises. Mega Man
caught the 1-UP at player X1056/Y139, played the extra-life sound and
received a third life. He caught the Star at X1672/Y150 and received
the timer, music and 1,000-point award. Proto Man earned the same
effects from both pickups. All four runs reached the ground with the
earned effect after at least 25 further movement updates.

| Character and pickup | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Mega Man, hidden 1-UP | 2,060 | `ef3c943639c2db46cf1015f259efff86b52b537476ec1a7aca7dff9bf60a6871` |
| Mega Man, Star | 2,880 | `b479fb406275254a67eec1184955569cac2a9126c0f495a43f61fc3c3049213b` |
| Proto Man, hidden 1-UP | 1,948 | `196919964fc3aba08786e5b287efcb40efc2dbb18622ecccdac61f9bebcc356c` |
| Proto Man, Star | 2,737 | `9254db84287d211d2f19dab59771618cfb793ea4a9b410e038c01bcca77f08b0` |

Use `--route life` or `--route star` with the same commands to replay
these two routes. Charged shots and the rest of the move set still
need review.
