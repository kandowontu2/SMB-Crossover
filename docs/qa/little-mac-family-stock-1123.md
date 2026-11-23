# Little Mac family pickups in Easy 1-1

On Downloads nightly `14b0b4c2`, Little Mac took a normal hit from the
first Goomba and lost eight health. He hit the Mushroom block at X336,
let the item emerge, and collected it to restore health from 88 to 96.
The Fire Flower block at X1248 produced an item that gave him his first
boxing star. Both pickups played the native cue, awarded 1,000 points and
passed 25 further movement updates. He finished with full health and both
lives. The run took 1,859 Mesen video frames and saved no captures.
Receipt `e44a5e97d6385ce10c660f75aa749f13b2c62cad3c400c0b100ad6aa92bf6d97`.

Doc Louis and Mike Tyson passed the same normal-menu Mesen checks,
including the health recovery, boxing-star stock and 25 post-pickup
movement updates. Both finished with full health and two lives.

| Character | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Little Mac | 1,859 | `e44a5e97d6385ce10c660f75aa749f13b2c62cad3c400c0b100ad6aa92bf6d97` |
| Doc Louis | 1,843 | `fa9825015498e3490c3da43820f9016bf2a3c2829b2d58170eb72ab25ed0a326` |
| Mike Tyson | 1,857 | `43b5d1df41e91570141f7bcb5d6a7143f716d1b5575e4e37c6a7e5549e173e40` |

The linked CPU replays also passed from verified compiled-menu starts.
Little Mac's receipt is `26d7e9178e3d7580ba62876fad1a08b124bc13f55baf1404073a71bba40b68b4`,
Doc Louis's is `b70499dbc7cc7e3a4dc3b4591eeb34b6c9452a358fb9860f895fecc0032c7867`,
and Mike Tyson's is `cabcc1dbff45a65056091217d44f87334ab9348ac6c9db15c9188929506277ae`.

The original component tests cover the full 24-point heal, the three-star
maximum, and native Star and 1-UP collection in a prepared scene.
[Original boxing-star checks](little-mac-star-2026-10-24.md)

## Natural hidden 1-UP

Little Mac, Doc Louis and Mike Tyson each cleared the opening pickup
route, hit the hidden block at X1024 and collected the 1-UP in Easy
1-1 on Downloads `3af597a7`. In each Mesen replay the native extra-life
cue played, the life counter rose from two to three and the boxer
landed with all 96 health and three lives after 25 further movement
updates. No captures were saved. The Star pickup remains open for all
three.

| Character | Video frames | Mesen receipt SHA-256 |
| --- | ---: | --- |
| Little Mac | 1,572 | `d626d5ddee11f9fd2118a792adcea8ac761226efaf1d50c03d9822c484e3ecdf` |
| Doc Louis | 1,578 | `de21b6718332812e939a93ada751248f0ff00a168d3682e8cbe67ffcd8ebfaa8` |
| Mike Tyson | 1,563 | `10d7da95b3789e6903670cb4905991aa9d6e9a6d9b20da1a31d368fb978b6bdb` |

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_mac_family_stock_1123.py --form mac --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_mac_family_life_1123.py --form mac --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_mac_family_life_1123.py --form doc --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_mac_family_life_1123.py --form tyson --run
```
