# Bass's first Mushroom in Easy 1-1

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

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 200 -- python -B tools/audit/run_bass_stock_1123.py --run
```
