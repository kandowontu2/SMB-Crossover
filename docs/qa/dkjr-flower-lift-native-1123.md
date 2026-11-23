# Donkey Kong Jr.'s 1-1 Fire Flower lift

The Flower lift uses the native 32-pixel vertical platform, actor `$25`.
It starts at world left X1264, center X1280 and top Y192. Its vertical
oscillation is centered at Y176. In the first passing Mesen run it was
created with the camera at X977, 287 pixels before the lift's left edge.

The initial replays stopped at the second pipe. The passing controller
waits when the character is standing on the floor and the native state
briefly shows a fall. It jumps onto the existing second-pipe platform
while it rises. This input change passed the route on the same test ROM.

The combined `d1a40df1` candidate includes the shared draw optimization.
Its ROM changes are disjoint from the lift changes. It passed both Mesen
routes with ordinary controls and no captures.

| Test | Result | Mesen receipt |
| --- | --- | --- |
| Mushroom and Fire Flower | Hit the X1248 Flower block, collected the mature Flower at X1263/Y112, earned 1,000 points and finished the 60-frame growth. Stayed grounded for 25 movement updates with both lives. | `9d971218cfb5a793f31c1f0398874c17f0221c7074c639db6a26ce3a5ff4412e` |
| Full 1-1 | Passed the stairs and flagpole and reached X40/Y176 in 1-2 with two lives and 25 grounded movement updates. | `e648805599a3a29eebe5c5622861b24d58be8d2e7d2943a5292bb15b78be3bd5` |

The existing horizontal support also appeared during the Flower run at
world left X1408, center X1432 and top Y208. It occupied slot 4. The runs
reached their terminal states at video frames 9,116 and 17,534 respectively.

The exact `d1a40df1` candidate was installed in Downloads. From that path,
Mesen confirmed that Donkey Kong Jr. could enter 1-1 and complete the
64-update standing and walking test in 96 video frames. Patch guards
passed before and after delivery. Downloads opening receipt
`1458d1256e1b1bc26882649dab2a4372e3ec3d62357cffbe1e723088f3ca102c`.

## Hidden 1-UP and Star follow-up

Two linked-code replays on `bcc26bb5` checked Donkey Kong Jr.'s reach
with his own movement. After riding the existing lift at X944, he
jumped from X977. He reached the hidden 1-UP's height before he reached
its column at X1024. The block stayed hidden. Receipt
`4e73741d7f949f5f3fe78a47a42684a99c4034c84c38a3ff44c667dd484ab28f`.

At the Star brick at X1616, a real Koopa bounce brought his head within
four pixels of the underside. The brick stayed intact. A later standing
jump also fell short, and he kept both lives through 25 more grounded
updates. Receipt `0b13cbd47742f2d91e638d72bdfb6d0f9b74048f1ee746df7e9ac912237f97c1`.
Both pickup checks remain open.

Mesen also cleared 1-1 on a private build with two additional lifts.
The native vertical platforms had left edges at X1008 and X1632, with
centers X1024 and X1648. Both started at top Y192
and moved around Y176. Each spawned 287 pixels ahead of the camera. The
existing gap platforms still worked, and DK Jr. reached 1-2 with both
lives and 25 grounded movement updates. This run verified the level route.
The two pickup runs are still pending. The lifts are private.
Mesen receipt `e5c110217da4b6e3b3ec9b4f56a594a299ce53a4b457734f36cc51b1ce1f1f0c`.

The hidden 1-UP route on that private build released the actual item
from X1024 in Mesen. DK Jr. then entered his original hard-landing state
before he could reach it. Receipt
`a58c049e434f44b3a082df91760a87f530942511b2f9c8c8db183c4ba7fa36d4`.
A linked-code run reached the item and gained a life under different
platform timing. That source result leaves the actual Mesen pickup open.

A second linked-code run aimed for the 1-UP while the same lift rose.
It collected the real item, gained a third life and kept it through 25
grounded movement updates. Receipt
`04a468f0b62c12f24ec296103b7220d16d65045caa294b5787b4e340a681c6fb`.
With the same controls in Mesen, DK Jr. started the jump two movement
updates after the request, by which time the lift had risen two more
pixels. The jump missed the block from that height. Receipt
`5ff7c6f2369df14ae2e2030f6c89094162c2a7792f769e040f4e676cbe984eaf`.

Requesting the jump at top Y164 gave Mesen time to accept A by top Y162.
DK Jr. hit the hidden 1-UP at X1024, collected it while it was rising,
and reached X1070/Y176 with three lives and 25 grounded movement updates.
Mesen receipt `920ef37f7a21f510aca50b170e0805f725d83647f437446851835011c74b0c94`.

The Star route in the linked build hit the brick at X1616, collected the
item while it rose, and earned 1,000 points. The Star timer and music
started, and DK Jr. completed 25 grounded movement updates after stepping
off the lift. Receipt
`96354953caa973b573a5822aa0d8d4954b1c91c658fc3a0ce6e8fdc2ca3a854f`.
On the combined `a8727de4` test build, the same Star route waited until
the platform was rising at top Y178 before pressing A. Mesen reached
the lift with both lives, but that jump missed the underside of the brick.
Receipt `3d663641d0d5c2cec2e1d65fe93a89b9bbd30ecd5a23a1720c4298099b8d1387`.
Requesting A at top Y176 made the jump start even higher, at lift top
Y175 and source origin Y158. DK Jr. remained healthy on the lift, but
the brick stayed intact. Receipt
`c4d6e19d06c63edbfcd17b3c11cbe85f1deb90eb35b4cf68a241b63ad65a3cf3`.
Requesting A on the rise at top Y180 accepted the jump at Y178.
It hit the real brick and spawned the Star at X1616/Y136. DK Jr. fell
left of the lift and entered the hard-landing state before reaching the
Star. Receipt `a5ab8edab1e7f133fc38833c53a21e54e728344ec49a759eccd0730820ce25ee`.
Pressing Right as the Star appeared produced the same receipt. Both
runs first touched down at X1614/Y176, left of the lift's X1632 edge.

### Star collection with the lift directly under the block

Test build `c6915886` moves that native lift one tile left. Its left edge
is X1616, its center is X1632 and its initial top is Y192. It uses the
native vertical platform motor and oscillates around Y176. DK Jr.'s
original hard-landing check still governs the exit.

Mesen hit the X1616/Y144 brick from the rising lift and collected the
Star at player X1631/Y130 while the lift was at Y162. Star protection
and music started on collection. The game awarded 1,000 points and
DK Jr. reached X1665/Y176 with two lives and 25 grounded movement
updates. No captures were written. Receipt
`1f93a372927ab70c7ea7b5385541a962b939fb12089f8fb4de3b815bf562b81e`.

The same ROM passed the normal hidden 1-UP route. DK Jr. hit X1024/Y128,
collected the item during emergence, and retained three lives through 25
grounded movement updates at X1070/Y176. Mesen receipt
`df8b083336e753422887712d728b56a2a81e83974247b7e3d231b00541cf9589`.

The above-ground 1-1 run recorded both lifts entering the level 287
pixels ahead of the camera. DK Jr. finished the flag sequence with both
lives and completed 25 grounded updates in 1-2. The run took 18,059 video
frames and wrote no captures. Mesen receipt
`c0e399e79b1ca7e0501af44e91ff0eb9855cb7aca3bc8b4834a2e72f61f73f46`.

Mesen repeated the Star pickup from Downloads on the same `c6915886`
ROM. The receipt matched the test run exactly. Both patch guards passed.
The hidden 1-UP and Star join the previously verified Mushroom and Fire
Flower as completed 1-1 pickup tests.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/run_dkjr_flower_draw_native_1123.py --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/install_dkjr_flower_draw_1123.py
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-life-star-source-1123 --max-files 8 --timeout 600 -- python -B tools/audit/probe_dkjr_life_star_1123.py --kind star --limit 5200
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 8 --timeout 560 -- python -B tools/audit/compose_dkjr_shinobi_1123.py --run star --star-top 180
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 8 --timeout 560 -- python -B tools/audit/compose_dkjr_shinobi_1123.py --run star --star-under
```
