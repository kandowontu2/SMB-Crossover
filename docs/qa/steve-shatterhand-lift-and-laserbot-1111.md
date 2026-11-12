# Steve Hermann’s lift and Laserbot

## Private build on the current nightly

The first companion now composes on the Sonic and Super Sonic nightly
`c4568faf4f472d4d6c3915c9b4258d5c04d6dcbb562b3e5602a5d580bb3046a2`.
The resulting private ROM is
`484d159fee570e6646252a24b3d01d6a9ddd17c70af2172d536f510dc34d0eb9`.
The pickup transport uses Roll’s identical CHR371 mirror for its fifth
row. The sixth and seventh rows still use CHR379 and CHR375. All three
Roll slots now read the exact same bytes from CHR367. This keeps all
Sonic CHR pages, code and mapper bindings byte-identical to the nightly.

The compiled checks cover 24 Roll publishers, 72 matching 1 KiB images
and 60 matching opening OAM/CHR samples. Thirteen corrupt readbacks
fail authentication, 31 forced-blank interrupt cuts return safely and
warm calls retain state with zero CHR reads.

| Physical regression | Result |
| --- | --- |
| Steve | Three Alpha tokens, the first companion and both shot tiles reached hardware OAM. Both lives retained. Receipt `8d922fd16b6a74ca744b5e21f53fa59c41a6670f2a75a41b312e97a58402a0ad`. |
| Sonic and Super Sonic | Both portraits and both complete 1-1 routes match the published Mesen receipts after substituting the candidate ROM hash. |
| Jay | Cleared 1-1 and fired five held-B shots from the earned machine gun in 1-2. Receipt `0fcc75599a17041605e650a684c47d9833ac5cf4bfde8c0e768351c927abd28d`. |

## Lift controls and timing

Shatterhand crouches with Down. Holding A while already crouched starts
the robot’s approach. Once it engages, releasing Down while keeping A
held starts the lift. The donor controller trace traverses player states
4, 5, 6 and 7. The robot approaches and latches, its grip animation runs,
then Shatterhand rises one pixel per update while A is held and terrain
allows it. Letting go of A during the approach returns him to crouch.
Letting go while rising returns him to airborne motion.
[Jaleco instruction manual](https://www.thegameisafootarcade.com/wp-content/uploads/2017/03/Shatterhand-Game-Manual.pdf)

The detached 509-byte worker reproduces the donor’s decision and
animation clocks in 72 cases and 3,666 updates, including 12 complete
lifts, gravity polarity, early release, lost support, lost robot, and
the B throw decision. Its seven animation sequences come from the
donor cartridge’s indexed tables. The fixture delegates terrain to
controlled support and headroom inputs. Live terrain, attached body
rendering and the thrown robot trajectory still need integration.

## Laserbot

The updated private ROM `7fcf58df189d70586e46ecc0fcbf7fc219d3c09dba25da383d4e91ccc8fb4973`
earns Laserbot through the Alpha–Alpha–Beta pattern. The CPU controller
punches the exposed third token at X1744 and collects it at X1732/Y44.
Pattern `$25` settles with six health and two lives. Actor ID 3 appears
54 updates after the route settles. The Mesen controller uses a three-update
B pulse on the third jump to register the switch with physical input polling.

The 580-byte detached Laserbot source matches 8,064 donor emitter
updates, 640 births and 12,288 projectile updates, including 4,320
drawable pairs. It covers the held-B charge and burst, mirrored firing,
standing and crouching slopes, cooldown, and segment movement and
sprite choices. The live bridge advances segments with the preceding
orbit delta before updating the bot and emitter. It keeps the donor’s
eleven-slot allocation and advances slots 0–7. Contacts use native
enemy hitboxes and HP, and segments spend that HP from their penetration
power. Nine directed contacts passed, including a defeat and an exhausted
segment. The sound uses the crossover fire cue on the original cue events.

The eight unique art cells come from donor CHR90. The crossover uses
CHR710/711 for both body poses, the muzzle, and both beam slopes. The
two crouching beam cells share a tile with combined horizontal and
vertical flip. The last cell reuses Mike’s transparent item-zero tile
after its metasprite was made empty. Six pickup controls and the first
companion’s 51-update attack remained identical in the art-only check.

Mesen verified both body poses, the muzzle and both beam slopes in
hardware OAM, with 86 body-pair frames and 31 shot-pair frames. Steve kept
both lives. Receipt `1843913a56777a6c194526f6d0d5b5979cd82c0d596688d4d3a67cc77899c3c6`.
The same ROM passed the first companion’s controller route and eight
native contact cases in the CPU test.

The 1,114-byte Laserbot program uses the new authenticated loader and
leaves 806 bytes in its executable range. The final companion host uses
631 bytes. The lift, original Laserbot sound, naturally spawned enemy
contacts, and a full stage regression on this exact ROM remain open.
The Downloads nightly and GitHub IPS remain on `c4568faf`.
[Late carrier proof](steve-shatterhand-late-companion-transport-1111.md)

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-lift-source-proof-1111 --max-files 1 --timeout 65 -- python -B tools/audit/check_steve_shatterhand_lift_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-laserbot-core-proof-1111 --max-files 1 --timeout 120 -- python -B tools/audit/check_steve_shatterhand_laserbot_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-laserbot-grant-1111 --max-files 1 --timeout 150 -- python -B tools/audit/check_steve_shatterhand_companion_live_1111.py --laser-grant
python -B tools/audit/run_bounded_build_v1.py --output build/steve-laser-mounted-proof-1111 --max-files 1 --timeout 175 -- python -B tools/audit/check_steve_shatterhand_laser_live_1111.py --first-regression
python -B tools/audit/run_bounded_build_v1.py --output build/steve-laserbot-native-1111 --max-files 2 --timeout 230 -- python -B tools/audit/replay_steve_companion_native_1111.py --laser --output build/steve-laserbot-native-1111
```
