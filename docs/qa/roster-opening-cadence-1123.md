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

### Prince opening CPU profile

The linked CPU test on `6201e3b6` measured about 45,459 foreground cycles
for each grounded standing update and 45,876 for each grounded moving
update. It counted 16 of each and started the walking sample after the
Prince began moving. Each game update ran 12 full checks of the two
16-byte owner headers, spending 6,876 cycles in those checks. Interbank
call handling took about 6,225 more cycles. The profile covers the empty
opening and counts CPU instructions through the original game routines.

The first call of a game update can keep its complete ownership check.
The Prince already records which game update ran his original movement.
Later callbacks could use that record after checking the live ownership
markers, with the existing validation as the fallback. This path still
needs ROM space and tests for stage loads, owner changes and interrupts.
The current dispatch can admit the Prince to that check within its
existing 11-byte selector at PRG bank 65, `$A76E–$A778`. After masking
bit 1 of the normalized owner, values 1 and 4 select owners 1, 3, 4 and 6.
The first callback still goes through the original full check at `$A779`.
Bank 85's current helper reads the wrong epoch address for the Prince.
Any patch must give his `$C0A9/$C0AA` fields their own branch in that
helper before making the selector change.

Linked CPU receipt `c1be1ac5780251632446de896306f462ab42218f48dab1e94ba623209b788a5f`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/prince-empty-current-1123 --max-files 1 --timeout 300 -- python -B tools/audit/profile_prince_empty_current_1123.py
```

## Shared sprite scan on the current nightly

The installed `c85cde8f` and the private renderer trial `53962dab` ran
the same 48 idle and 16 Right updates from the normal menu in Easy 1-1.
All enemy slots stayed empty. Both versions reached the same walking
endpoint for each character. The runs saved no captures.

| Character | Video frames, installed → trial | Frames with no game update, installed → trial | Skipped NMIs, installed → trial |
| --- | ---: | ---: | ---: |
| Donkey Kong | 64 → 64 | 30 → 14 | 30 → 9 |
| Bass | 64 → 64 | 29 → 28 | 29 → 28 |
| Steve Hermann | 66 → 64 | 31 → 32 | 34 → 32 |
| Mini Mario | 64 → 64 | 0 → 0 | 0 → 0 |

| Character | Installed Mesen receipt | Trial Mesen receipt |
| --- | --- | --- |
| Donkey Kong | `cce0f0726b41d8a73a7a6b8296a07227c08f0c1c2ef6c89ef0de538075f6ec42` | `2954624661621d8be0cb22b0caf658613fb86ca69e349ada08fa868f44046b8c` |
| Bass | `6ea9c3b12361068318d8fd0a804498a1f8ffddc4b23295df86156f930f6f0eb7` | `b4264e0b7b6ac8b29a8bf05d9e74465d3419c07472d4323f1b5fe789ba517588` |
| Steve Hermann | `c6765013ba5d5de345315e7ab20fa17527fff6996b18b935d0721f8ebb9797e7` | `7d3d789cc4b43524e47891ae7f5e168bd89887e9d48317c5815b5ae67848fa99` |
| Mini Mario | `b429b0fe7c4cbcd3cc238ca19b9767ec61ae434a7ae89bf8f995849383b341a8` | `b80bfeda4b9fdff05ecb07d8f834ccfb1981cc1b08f400640e5c9d48ed489deb` |

Bass and Donkey Kong spent about 803 CPU cycles on the shuffled world
sprite pass in the empty opening. The trial checks the sprite slots and
enemy IDs in groups. If any slot may draw, the original shuffled loop
runs. Mini Mario reaches a separate loop with its own Goomba renderer.
That loop uses the same empty check and keeps its own populated path.

The earlier `06610edf` benchmark saved roughly 467 cycles per empty
game update and cut Donkey Kong's no-update frames to 12. It used space
in the Castlevania audio mirror and was rejected for delivery. The new
trial fits in the renderer bank. It frees room by grouping writes that
hide unused sprites. The test verified the exact write order and
registers for all 64 aligned tail offsets and 256 full-clear inputs.

Six characters matched in 312 linked idle, walking, jumping and landing
updates. The new trial saved about 328 cycles for Donkey Kong, Bass and
Steve Hermann and about 330 for Mini Mario in those empty samples.
The linked suite exercised 235 IRQ and 235 busy NMI returns. The 1,488
sprite-scan cases included both frame parities and all 24 shuffle starts.
Sixteen additional fixtures compared the two compiled draw loops with live
world actors. Twelve produced identical ordered OAM writes for firebars
or small lifts. Four matched the original culled firebar outcome.

The compact clear adds work on populated frames, including up to 240
cycles in the tested fallback checks before the additional clear cost.
Heavy scenes still need native comparison before this change is ready
for Downloads. Steve's overall timing improved by two frames, but he
still missed an update on half of the video frames. The installed
nightly remains `c85cde8f`.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/roster-empty-draw-1123 --max-files 1 --timeout 430 -- python -B tools/audit/check_sparse_sprite_scan_1123.py 'DONKEY KONG' 'BASS' 'STEVE HERMANN' 'MINI MARIO' 'MARIO' 'SAMUS ARAN' --matrix --interrupts
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 8 --timeout 550 -- python -B tools/audit/run_sparse_sprite_scan_native_1123.py 'MINI MARIO' 'DONKEY KONG' 'BASS' 'STEVE HERMANN'
```
