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

## Shinobi and Donkey Kong Jr.

The Downloads nightly `6201e3b6` took 96 video frames for 64 game updates
for each character, with no enemies active. In both runs, 32 frames had no
completed game update and 64 had one. Mesen recorded 64 skipped NMIs. The
walking sample began at X40 and finished at X56 for Shinobi and at X50 for
Donkey Kong Jr. This reproduces Donkey Kong Jr.'s previous opening cadence
and confirms that Shinobi also stutters in an empty area.

| Character | Controller SHA-256 | Mesen receipt SHA-256 |
| --- | --- | --- |
| Shinobi | `66fb56a605c859f0a57bf8572c0f6ec691eb6fb457957cc2ca938d9e6e30d0d4` | `54228608c734c4535be4de2407f33acef22be3d746730aa11357e7a09477162b` |
| Donkey Kong Jr. | `6c9a4f87bfa30d3488f0afbd7fd56dc2fb8d977383ccbd67899e8b7dfa4134eb` | `e46ba3e39e608f58418bb08147d993a4e3facdd42a05d1912b3c06f0068c4c83` |

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 8 --timeout 480 -- python -B tools/audit/run_roster_empty_cadence_current_1123.py 'SHINOBI' 'DONKEY KONG JR'
```

### Donkey Kong Jr. rectangle lookup trial

Private test build `b66f046e` computes the tile table address once per
collision rectangle check. It saved 383 CPU cycles per standing or
walking game update in the tested opening. The linked CPU suite passed
166 paired gameplay updates, 1,280 call cases, 75 IRQ cuts and 75 busy NMI
cuts. The change stayed inside Donkey Kong Jr.'s rectangle code and its
verification header. CPU receipt
`01a40fc48ccf751f53dd8f5e33e9ba7c71eb3aa3146842f49149d7a75f167084`.

Mesen still measured 96 video frames for 64 updates, with 32 frames
without an update and 64 skipped NMIs. The walking endpoint stayed at
X50. The test build stays private. Mesen receipt
`949d9838e0e47e15370bb9d515626899f4523a3ba4bce08332c621cc9ae291d3`.
Controller `429e0ff2c4ad58a8f385c3221c88a30b47634be89bc459e74755097936b3d864`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 8 --timeout 300 -- python -B tools/audit/run_dkjr_rect_cadence_1123.py
```

## Prince of Persia

The Prince stayed at X40 for the first 16 updates with Right held. With
Right held for 48 updates, he reached X92 at the same ground height.
The longer Mesen run spent 168 video frames on 96 game updates, split
between 48 idle updates and 48 updates with Right held. There were 72
frames without a completed game update and 120 skipped NMIs. All six
enemy slots stayed empty. The sample covers the delay before he begins
walking as well as his movement.

Controller `1512e50dcf140ca72abb4244e094e0812c8cdea948e5e635ba166093a8656a4b`.
Mesen receipt `880190c8d40864af564321b1bfbf96f7f82bc0ae7ee72a2c6fd7e50ee63540e0`.
The original shorter sample ended at X40 and failed its movement check,
receipt `ee6b119f69637ecdab677760198d0b0b7c778d6547c1336f2046dd3fe21bf6c3`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 8 --timeout 300 -- python -B tools/audit/run_roster_empty_cadence_current_1123.py 'PRINCE PERSIA'
```
