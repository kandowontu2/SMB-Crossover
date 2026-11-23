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
these two routes.

## Charged Buster in Easy

Both characters fired after earning the first and second power levels
from the same normal blocks. Each trial began with a fresh B press and
an ordinary pellet. Releasing B at 47 updates reset the counter.
Releasing at 48 or 87 updates fired the partial or full charge. The
replay checked the Buster sound cue and recorded each charged shot
moving 10 world pixels by age three.

| Character | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Mega Man | 2,719 | `efcd41aff3507c6c344fcb4cb6616ed91e96b2298e2b26bb68f34d0ef5462993` |
| Proto Man | 2,442 | `07fe1a2102f44ccf13b54e3b1c1e1cc5a28d79ea4bca0c9229e77a8fc84ef6d3` |

Both runs finished with the second power level and two lives in Easy
1-1. These checks cover charging, spawning and travel. Charged-shot
damage, sprite appearance and the other weapons still need review.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 360 -- python -B tools/audit/run_megaman_proto_charge_1123.py --form megaman --run
```

## Charge upgrade in Hard

The Mushroom at X336 awarded Charge in the inventory for both heroes
while leaving the Buster equipped. Each replay kept both lives and
verified releases at 47, 48 and 87 updates from the first earned power
level. The same Buster sound and projectile movement checks passed.

| Character | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Mega Man | 1,119 | `79e2786d6000527580295f64476d1e631ec78ba962f6e0c59beb0e92d113d0b0` |
| Proto Man | 1,095 | `cf00da7c8af9338f11d8c37dd0356a23c14113c58af01e02f1cf5ad7ea13670c` |

Add `--hard` to the replay command to test the inventory award and
first Buster power level. The four Easy and Hard Buster replays ran
from Downloads `28708fa9` and wrote zero captures.
