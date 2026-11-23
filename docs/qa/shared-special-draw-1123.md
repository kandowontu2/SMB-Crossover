# Shared projectile draw timing

The previous MMC5 nightly `ffd70810` used five character dispatchers before
the common projectile renderer. A linked CPU trace from Bass's normal 1-1
opening measured 6,277 cycles for the complete sprite draw while standing
and 6,087 while walking. The shared projectile dispatch accounted for about
1,261 of the standing cycles, including its render work. The main loop also
runs other work during this window.

The private `609ebde6` trial took a shorter path for Bass and high roster
IDs. Roll returns directly when his alternate is selected. The other IDs
still run the original dispatchers, including Zelda II Link's special draw
rule. The new routine uses 39 bytes of padding following the Rush call's
return. It leaves Rush, the adjacent shot pose and the renderer intact.

The paired linked CPU test matched native and guest RAM, OAM, VRAM, mapper
state and the live caller stack across 36 normal updates per character.
The paired tests also measured the same normal NMI cost.

| Character | Main cycles saved per update |
| --- | ---: |
| Bass | 447 |
| Donkey Kong | 451 |
| Mini Mario | 0 |
| Roll | 11 |
| Zelda II Link | −87 |

The `−87` means Zelda II Link's fallback uses 87 extra cycles. The proof
covers the empty opening through the ordinary character menu. Source receipt
`25695b767f91e7062237268bda1cea483485529593a8a6abb0a4fe042998076e`.

Mesen measured the following counts across the same 64 game updates.
Zero-update and double-update video frames measure uneven timing that the
average can hide. No enemies or captures were present.

| Character | Installed frames with 0 / 1 / 2 updates | Private frames with 0 / 1 / 2 updates | Private receipt SHA-256 |
| --- | ---: | ---: | --- |
| Bass | 31 / 2 / 31 | 29 / 6 / 29 | `88da199e2b0a398a0d1b98c4a4a3899fa7be523564d597fc82e394d7c742fba0` |
| Donkey Kong | 32 / 0 / 32 | 27 / 10 / 27 | `0afd911078384d3627fc16a1af647e42bc7c40366ce8bd7616a748ab0e8a015e` |
| Mini Mario | 0 / 64 / 0 | 0 / 64 / 0 | `36095f520a5492ef764c5e0308c61776c715f7099d7fe420ce2b82905cbb3dd1` |
| Roll | 0 / 64 / 0 | 0 / 64 / 0 | `309aa5495e857b0861ce71f2c3b001876189095a5b77f7f5a33529b2eac3fd0c` |
| Zelda II Link | 20 / 24 / 20 | 32 / 2 / 31 | `0c930eb2a2fe1e50bce0464470367bec28ff3285a22156f3d27dec5f39905547` |

The Zelda II Link run regressed from 64 to 65 video frames and went from 20
to 32 skipped NMIs. This trial was rejected for delivery. His installed
receipt is `abca297264083463a5e1168edd706f3790486c7e3a34725653bab05db9f22d50`.
Roll's installed receipt is
`ea16aacb69f80d3745594c1d01fa72de3f07750065913159ebad91ec23750b78`.

## Direct dispatch test `27e01af3`

The revised private test fits all five exceptions into 42 bytes in the
same padding. Roll, Mike and SMB3 return before the shared renderer. The
turtles still clear the shared CHR flag. Zelda II Link still bypasses the
shared renderer for his alternate. Every other owner uses the same
projectile renderer as before.

The linked CPU comparisons passed 36 normal updates each for nine
characters. The saved cycles per update were 442 for Bass, 438 for Donkey
Kong, 375 for Zelda II Link, 283 for Leonardo, 184 for SMB3 Mario, 87 for Mike
Jones, 445 for Link, eight for Roll and zero for Mini Mario. Receipt
`b2fee945150e44fac943b1285e7f2c0cd08d03bb1e7f931f2d75b5bccd5d210e`.
The actual IRQ and busy-NMI handlers returned safely at 27 reached caller
and helper instructions each, receipt
`a2acd42ee989e1908771d768e559133bfbb3e35db36396620bc41694bbee68e2`.
Five paired 72-update controller tests using B, Right and jumps matched the
same gameplay, OAM and PPU state throughout. In the Bass test the live
projectile pool held a shot in all 72 compared updates. Receipt
`8c7b6e5cf0893a02a4f0bf09b5e46fca52d1cc6f4c1cc723ce9adffdb7dc70ca`.

Each private Mesen run completed 64 game updates in 64 video frames. Zelda
II Link improved from 20 to 11 frames without a game update and 20 to six
skipped NMIs. Bass and Donkey Kong each improved by two zero-update frames.

| Character | Private frames with 0 / 1 / 2 updates | Private skipped NMIs | Private receipt SHA-256 |
| --- | ---: | ---: | --- |
| Zelda II Link | 11 / 42 / 11 | 6 | `4189d79b06754bdc1e3cc6922783eee257e86577a70d3d7b966b371b81b29d5a` |
| Bass | 29 / 6 / 29 | 29 | `536e015ca53177e949c058084415c458e223663c7a6bb1eca687f6643d4c423f` |
| Donkey Kong | 30 / 4 / 30 | 30 | `64725848b8e9cc36234440888e2ac1e43413c24b0d36cb74623510239f012adf` |
| Mini Mario | 0 / 64 / 0 | 0 | `67cedb4f97e594fdb3afc4eb09743efbc952bebadf6fae051a2421dbcf92d600` |
| Roll | 0 / 64 / 0 | 0 | `dd7eee33fd276699bdbd78117fe883d93c9bf01156ca6cc1e637041db485ff1d` |

The first Donkey Kong Jr. replay stopped at the final stairs on `27e01af3`.
It reached X2911/Y144 with two lives and 99 on the timer and gained no
height on the first final stair. Mesen receipt
`798cac49c31a2595fc4234efba2cefb615481d0451d4868920a01796b7df6186`.

The initial Grant controller fell at X1118 before the Fire Flower. Mesen
receipt `a932cf3e37f54188bcd6305232c219e336fcca9a5c1f551b429348ef615b3c98`.
A controller-only change waited for grounded takeoff at X1095/Y176. Grant
accepted the jump at X1099/Y171 and landed on the far bank at X1145/Y176.
He collected the Flower, threw the dagger and ended with both lives and
full HP after 2,037 video frames. Mesen receipt
`d3189e986859f6b327198bfa0061cef577c62d1ba4a489d397bc7e3bbad10cf4`.
The tested ROM matched in both attempts.

A controller-only backoff after the first failed stair jump passed the
first two risers. The same private ROM stopped at the third riser at
X2943/Y112 with two lives and 95 on the timer. The first-riser replay
SHA-256 is `4dd52e15a897f90c1ce546987d17716b793cf678a9fa85366005945a783402f3`.
Mesen receipt `79948d396f4c76f9ceaac5b37afdea13c01ea413166efd6db4646517cb9c0d2c`.
The original failure and the later third-riser failure both remain
reproducible through separate controller factories.

## Downloads nightly

Extending the same backoff to each of the first three risers cleared the
staircase and the stage on the unchanged `27e01af3` ROM. Donkey Kong Jr.
reached X40/Y176 in 1-2 with two lives and 25 grounded movement returns.
The terminal event occurred at video frame 17,381. Mesen receipt
`6193901229240e9ff9f98ec1bcb282c3763348f731b02be48a40482b16023108`.

Downloads initially received the tested `27e01af3` bytes. Mesen launched that
file directly and exactly repeated the private opening timing receipts for
Bass and Zelda II Link. Patch guards passed before and after replacement.
The DK Jr. Flower lift build retains that renderer and passed both of
its native routes. The installer below uses `ffd70810` as its input. [Combined build and lift tests](dkjr-flower-lift-native-1123.md)

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/shared-special-draw-1123 --max-files 1 --timeout 520 -- python -B tools/audit/probe_special_draw_routing_1123.py 'ZELDA II LINK' 'LEONARDO' 'MIKE JONES' 'SMB3 MARIO' 'BASS' 'DONKEY KONG' 'MINI MARIO' 'ROLL' 'LINK'
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 360 -- python -B tools/audit/probe_special_draw_routing_1123.py --native 'ZELDA II LINK' 'BASS' 'DONKEY KONG' 'MINI MARIO' 'ROLL'
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 440 -- python -B tools/audit/run_shared_special_draw_routes_1123.py
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 170 -- python -B tools/audit/run_shared_special_draw_routes_1123.py --grant-first-pit
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 420 -- python -B tools/audit/install_shared_special_draw_1123.py
```
