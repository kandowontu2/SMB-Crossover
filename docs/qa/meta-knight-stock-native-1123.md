# Meta Knight pickups in Easy 1-1

Mesen started `82e8da0e` from Downloads. The replays highlighted Kirby,
pressed Select once and started Easy 1-1. Both food pickups followed real
enemy contact, so the tests could observe health restored by the reward.
The items emerged from their original blocks, used the expected Mushroom
and Fire Flower sprites, and disappeared on contact with the heal animation.
Meta Knight kept both lives, with no copy ability or flight.

- **Mushroom.** The block at X336 released the Mushroom. He followed it
  off the row and collected it at player X420/Y150, healing from five HP
  to six. He finished at X428/Y176 after 81 more character updates.
- **Fire Flower.** After earning the first Mushroom, he reached the block
  at X1248 and jumped from the left to reach the Flower. Contact at player
  X1236/Y101 healed four HP to six. He finished on the block row at
  X1252/Y112 after 25 more character updates.

| Replay | Video frames | Controller SHA-256 | Mesen receipt SHA-256 |
| --- | ---: | --- | --- |
| Mushroom | 976 | `5e9f11dbd751516230115ac5f871d3ea83be5b06cf092480e4542b2fa2633650` | `e26b1d7e6f9ba0f485965a31e4dbe906fb84c4fd41f73de90d4776eb970006b3` |
| Mushroom and Fire Flower | 2,281 | `8cfb2aa0019aa5d82fef1c5401f208e8cc4ec766a5b69a70dc794371702f6d17` | `90426a2ec986255816a2e25028993bf7798ea8146012d59c68d8b50c19672b1b` |

The replays used controller inputs and saved no captures.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_meta_knight_stock_1123.py --route mushroom
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_meta_knight_stock_1123.py --route flower
```

## Hidden 1-UP and Star

- **Hidden 1-UP.** After the Mushroom, he jumped from X1023 and hit the
  hidden block at X1024. He caught the moving 1-UP at player X1054/Y176.
  The life counter rose to three and the game queued the life sound. He
  finished at X1063/Y176 with four HP after 25 more game updates.
- **Star.** After both food pickups, he crossed the pit and hit the Star
  brick at X1616. He jumped to intercept the Star at player X1715/Y118. The
  game started invincibility, queued the Star music and awarded 1,000 points.
  He landed at X1725/Y176 with four HP, both lives and the active Star
  after 25 further updates.

| Replay | Video frames | Controller SHA-256 | Mesen receipt SHA-256 |
| --- | ---: | --- | --- |
| Hidden 1-UP | 2,016 | `578e778161537dacef1e981173152f502f5cad17f365a5982e824b57946cade3` | `70bf372984136388aaa68f253a41e45375259de06afc35204eccb3532d78ef0a` |
| Star | 2,996 | `7f48f91b81c3df223648ace0f765df8d96f276e56286de4780a90aec365174ee` | `9a52888db95f6bcab9665f03d142d3ea13a307e7cdad4c27167be0065b3f6f07` |

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_meta_knight_stock_1123.py --route life
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_meta_knight_stock_1123.py --route star
```
