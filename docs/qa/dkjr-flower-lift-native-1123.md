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

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/run_dkjr_flower_draw_native_1123.py --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/install_dkjr_flower_draw_1123.py
```
