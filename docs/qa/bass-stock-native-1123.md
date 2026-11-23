# Bass's powerups in Easy 1-1

Mesen launched the actual Downloads nightly `ffd70810` and selected Bass
through the ordinary menu. Bass hit the block at X336, then physically
collected the Mushroom at player X405/Y176. The pickup started the original
growth animation and set ownership bit zero. The run observed tier one
after the 60-video-frame transition, the 1,000-point award and 25 further
movement returns with both lives.

The run completed in 958 video frames and saved no captures. Controller
SHA-256 `6d17d88949e860ff63c4cf77fff07264da6beb701b8f203b741f5c3d0c9912eb`.
Mesen receipt SHA-256
`d551a00906a1d1a9ec7bf6bf36713a9ecd2366614cbf7673296f6f8b4cb65527`.

The first controller held Right and B continuously. Bass's normal ground
firing rule prevented movement. The verified controller fires in short
bursts near an actual enemy and releases B while walking.

The Fire Flower run started with that same Mushroom pickup. Bass bumped
the X1248 question block from below. It revealed Hard Knuckle, which
emerged and remained available for a jump from the right. Bass collected
it at X1263/Y130. The inventory changed from `0x01` to `0x09`, the pickup
cue played and the score rose by at least 1,000 points. He returned to the
ground with the weapon and both lives after 25 more movement updates.
The replay ended after 2,114 video frames with no captures. It covers
acquiring Hard Knuckle. Selecting and using the weapon remain separate
checks.

Controller SHA-256
`44822536e5c342b2e9d9b62225b7fc27670559cc54c7941404d0df397b94f835`.
Mesen receipt SHA-256
`a363d8595ea6f633fddad958213f997b4d5ef1cebd84cfd71f0f32b5eaea72b8`.

## Hidden 1-UP on `27e01af3`

Bass hit the hidden block at X1024 and collected the mature 1-UP at
X1050/Y167. The native award increased lives from two to three. After at
least 25 more movement updates he stood at X1050/Y176 with three lives
and his Mushroom upgrade. This run took 1,845 video frames and saved no
captures. Mesen receipt
`446f8e4b4fe7c8064c875b31f3006d74df790da8edfc2c001b0ac9d926b97039`.

## Star on `27e01af3`

Bass hit the brick at X1616 and collected the mature Star at X1667/Y137.
The timer started at 35, Star music played and the game awarded 1,000
points. Bass had lost his Mushroom upgrade to an enemy earlier in this
run. After 25 further movement updates he stood at X1668/Y176 with two
lives and the Star timer at 34. The run took 2,745 video frames with no
captures. Mesen receipt
`64cf45e04c74d37d61116ea93ecbcfaa43043e3da852c0bb78111d231e5d044d`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 200 -- python -B tools/audit/run_bass_stock_1123.py --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 215 -- python -B tools/audit/run_bass_remaining_stock_1123.py --route flower --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 225 -- python -B tools/audit/run_bass_remaining_stock_1123.py --route life --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 225 -- python -B tools/audit/run_bass_remaining_stock_1123.py --route star --run
```
