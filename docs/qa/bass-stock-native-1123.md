# Bass's Mushroom and Fire Flower in Easy 1-1

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

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 200 -- python -B tools/audit/run_bass_stock_1123.py --run
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 215 -- python -B tools/audit/run_bass_remaining_stock_1123.py --route flower --run
```
