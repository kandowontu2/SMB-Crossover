# Empty opening timing in Easy 1-1

Mesen started each character from the installed MMC5 nightly `ffd70810`.
The sample counted 48 standing and 16 walking game updates. No enemy slots
were active during the sample. Each character moved right during the walking
portion. The runs saved no captures.

| Character | Video frames for 64 game updates | Frames with 0 / 1 / 2 updates | Walking X before and after | Skipped NMIs |
| --- | ---: | ---: | --- | ---: |
| Steve Hermann | 66 | 31 / 6 / 29 | 40 to 53 | 34 |
| Bass | 64 | 31 / 2 / 31 | 40 to 54 | 31 |
| Donkey Kong | 64 | 32 / 0 / 32 | 40 to 45 | 32 |

Bass and Donkey Kong averaged one game update per video frame. They still
showed severe stutter because about half the frames ran no game update and
about half ran two. Steve showed the same pattern and took two extra video
frames. The skipped NMI count measures a separate event from completed game
updates per frame. These samples cover the empty opening only.

| Character | Controller SHA-256 | Mesen receipt SHA-256 |
| --- | --- | --- |
| Steve Hermann | `c17278e3c320d395f8dac02547a83aa3355dba33d8f1f8148197fbf4708911b0` | `afad30f3191c31b5f2553f02a461be1db34bc034233ad9c8340afe8469862e71` |
| Bass | `aa3be9fc0098d3020bbc69142a3444eb9659d5b68b8e040b47dd9f54f91ae855` | `9ca8ba37975d900d9c9a7dabd4dcde80d7165de782f5c8f03fb9cd7c0bcda0da` |
| Donkey Kong | `7995168e09a3e0f9deceb695ed3914d00d0d1bdd2ed2a18b4da4ab49a8d15ebc` | `9ddbb5220d4aab56f7bbc98079125f2c706794ecc491bc0c1d540938e1f806ff` |

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 390 -- python -B tools/audit/run_roster_empty_cadence_1122.py 'STEVE HERMANN' 'BASS' 'DONKEY KONG'
```
