# Quick Man's second Mushroom in Easy 1-1

The Downloads nightly `ffd70810` passed Quick Man's two authored upgrade
blocks in Mesen with ordinary controller input. After the first Mushroom
at X336, a Goomba at X719 reduced his health from 40 to 36. The block at
X1248 ejected his second Mushroom. Quick Man collected it at X1284/Y176,
which restored 40 HP and earned 1,000 points. The pickup cue played and
the replay continued for 25 movement updates with both lives.

The run took 1,971 video frames and saved zero captures. The Mesen receipt
SHA-256 is `9c44abf8b715c61e45b41d143401e5eb2e33de5de0d0cdeacda9edca958f3296`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_quick_second_food_1123.py --run
```
