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

Use the ordinary shared queue for each pickup route. These runs write
no captures.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 225 -- python -B tools/audit/run_megaman_proto_stock_1123.py --form samus --route upgrades --run
```
