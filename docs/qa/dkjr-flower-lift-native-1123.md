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

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/run_dkjr_flower_draw_native_1123.py --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/install_dkjr_flower_draw_1123.py
python -B tools/audit/run_bounded_build_v1.py --output build/dkjr-life-star-source-1123 --max-files 8 --timeout 600 -- python -B tools/audit/probe_dkjr_life_star_1123.py --kind star --limit 5200
```
