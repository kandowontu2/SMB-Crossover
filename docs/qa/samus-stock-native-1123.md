# Samus's normal 1-1 pickups

Samus Aran entered Easy 1-1 from the normal character menu on Downloads
nightly `28708fa9`. The replay observes the original Samus movement
routine and the native block and pickup handlers.

Samus hit the block at X336 from below. The Mushroom rose, finished
emerging and reached X411 before collection. The native pickup sound
queued and the growth sequence finished with the first power level.
Samus kept that level until at least X523/Y176, past the 25-update
follow-up check, with two lives.

Later in the same run, Samus turned left while lining up beneath the
Fire Flower block at X1248. A Goomba at X1230/Y158 hit her at
X1239/Y176. The replay stopped before the Fire Flower emerged. The
Mushroom check had already passed.

| Run | Video frames | Controller SHA-256 | Mesen receipt SHA-256 |
| --- | ---: | --- | --- |
| Mushroom passed, Fire Flower approach stopped by injury | 3,351 | `8ecbc1ec4da22099c7ec12e1e962c12410b19e2e04ec106aac8e97844266e6d3` | `3574450e85e21589fcd8930ec2e66b6395d55099b6d984a76811025dbc4018f9` |

The hidden 1-UP attempt with the first revision reached X1018–1019 and
alternated Left and Right beneath the block until the run timed out. The
test now steers from Samus's current position and allows her to stop.
Her horizontal speed follows the current input, so the robot replay's
braking calculation was unsuitable. The first Star traversal stopped
when it met the same elevated Goomba in the approach to X1248.

| Earlier attempt | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Hidden 1-UP approach timed out | 5,521 | `e38229a6762515587ede78032a3eb9157530150f44dfcba563b6321e3d6e7b07` |
| Star approach stopped by injury | 3,351 | `140d392e054354da8083c945076dafae27abe92703b1e061dcadda5c2d8bb251` |

The revised steering passed the Mushroom again and lined up beneath the
Fire Flower block without oscillating. A Goomba contacted Samus on the
first jump at X1241/Y167. Move the takeoff clear of that enemy before the
next Fire Flower run. The revised run took 1,915 video frames. Mesen
receipt `896f1b368c0c6d070f9101d64ea3ee7106e17e22f6d365eceb4a66182a78437c`.

## Hidden 1-UP

With the revised steering, Samus hit the hidden block at X1024 in Easy
1-1, then met the fully emerged 1-UP at X1046/Y126. The native reward
popup appeared, the delayed credit raised the life count from two to
three, and the extra-life sound queued. She kept all three lives through
the follow-up movement check and landed at X1049/Y176.

The Downloads replay took 1,968 video frames. Mesen receipt
`dac18393b573e245db5d6c24be4d11e2ab3d01f1e5fed86dcf62856fc5130879`.
Controller SHA-256
`2cbb9394cd2044082a3deabf634106d5d25fd2aebd0eb5cc7abe2694b859a3de`.

## Fire Flower

The revised approach collected the Fire Flower from its normal block at
X1248. Samus let the item finish emerging, then jumped up from the left
and collected it at player X1235/Y100. The pickup queued its sound and
granted the second power level. She kept the upgrade through 26 more
movement updates and landed at X1235/Y112 with both lives.

| Run | Video frames | Controller SHA-256 | Mesen receipt SHA-256 |
| --- | ---: | --- | --- |
| Mushroom and Fire Flower | 2,142 | `d176207812f0e11c6090e6858eba2d2afd897e194866cec25e40f1a8c4354271` | `f3936de6c50ec4f15e8872610914be16443f676f9fd26bb456914f4343497e64` |

The later Star replay stayed low past the elevated Goomba and reached
the Star approach. A green Koopa hit Samus at X1585/Y176 while she
was standing and firing. The next replay jumps past the Koopa before
lining up under the Star block. The stopped run took 2,804 video frames.
Mesen receipt `c3b9eb603f34a14243cbac9196825b12f16ef3218d4ab01d68f45eea8c86d9c4`.

## Star

Samus jumped past the Koopa, hit the normal Star block at X1616 from
below and collected the fully emerged item at X1656. The native timer,
Star music cue and 1,000 points passed. She landed at X1648/Y176 with
both lives and the Star still active after the follow-up movement check.
All four standard pickups have passed in Easy 1-1.

The Downloads run took 2,922 video frames. Mesen receipt
`a960990b780ca6695eeb4596ca62081ba2c7d81c8713794e92d31f14faf1af90`.
Controller SHA-256
`305e92564f07dcfd54bec4a25c5ed5572f1b64b177233ac5d4380496878a620d`.

Use the ordinary shared queue for each pickup route. These runs write
no captures.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 225 -- python -B tools/audit/run_megaman_proto_stock_1123.py --form samus --route upgrades --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 225 -- python -B tools/audit/run_megaman_proto_stock_1123.py --form samus --route life --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 225 -- python -B tools/audit/run_megaman_proto_stock_1123.py --form samus --route star --run
```
