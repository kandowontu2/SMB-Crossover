# Roll's pickups in Easy 1-1

Mesen tested the installed MMC5 nightly `ffd70810` from ordinary menus and
controller input. Both runs chose Roll from Bass's slot and saved no captures.

| Pickup | Native result | Video frames | Mesen receipt SHA-256 |
| --- | --- | ---: | --- |
| Hidden 1-UP | Head hit X1024. Collected at player X1047/Y124. The game granted life three, updated the saved life count and triggered the extra-life cue. | 1,266 | `5cde4753813a7cbf358cf2469c750ecdf5ef17eba48a56232a827af45b3abffb` |
| Star | Head hit the brick at X1616. Collected at player X1670/Y146. The timer started at 35, Star music began and the score rose by 1,000 points. | 2,054 | `ee6159fe9da279c3d75e2fd06463248dd1ea1c4765887eba864410e08643f59c` |

The 1-UP replay continued for 30 movement returns after the extra life,
ending on the ground with three lives, 28 HP and 28 energy. The Star replay
continued for 32 movement returns after activation, ending on the ground with
the Star active, two lives, 24 HP and 28 energy. Roll had taken an ordinary
hit before the Star.

In a third run, Roll collected the first Mushroom and took a Goomba hit
that reduced her health from 28 to 24. She reached the Flower with 26 HP.
She spent four energy on a charged shot, then jumped in from the right to
collect the Fire Flower from the X1248 block. The native pickup restored
health from 26 to 28 and energy from 24 to 28. It also awarded 1,000 points
and queued the pickup cue. Roll finished grounded at X1257/Y112 with both
lives after 25 further movement updates. The route took 1,852 video frames
with no captures. Mesen receipt
`283359f58b93bc2c0960069eec4cb65ea33a1a38b8ea29e874c14240fa4143f8`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_roll_stock_1123.py --route life --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_roll_stock_1123.py --route star --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_roll_flower_1123.py --run
```
