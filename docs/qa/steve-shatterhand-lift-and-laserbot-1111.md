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

The same private ROM can earn the Alpha–Alpha–Beta pattern naturally.
The controller punches the exposed third token at X1744 to switch it
to Beta and collects it at X1732/Y44. Pattern `$25` settles with six
health and two lives. Actor ID 3 appears 54 updates after the route
settles. The grant is live in the candidate. Laserbot’s attack still
needs to be connected to the actor and renderer.

The 580-byte detached Laserbot source matches 8,064 donor emitter
updates, 640 births and 12,288 projectile updates, including 4,320
drawable pairs. It covers the held-B charge and burst, mirrored firing,
standing and crouching slopes, cooldown, and segment movement and
sprite choices. The donor decrements segment power on enemy contact
and keeps the beam active until that power runs out. Native damage,
sound, body and projectile integration remain open. The donor OAM
points to CHR90, with body tiles `$41/$43` standing and `$45/$47`
crouching. The muzzle uses `$57`, the standing beam uses `$59/$5B`,
and the crouching beam uses `$5D/$5F`. The crouching cells are exact
horizontal and vertical mirrors, leaving eight distinct art cells
after mirroring. The known blank host tails on CHR710 and CHR711 hold
seven cells. The lift and Laserbot also need additional authenticated
executable storage before they can both run in the crossover.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-lift-source-proof-1111 --max-files 1 --timeout 65 -- python -B tools/audit/check_steve_shatterhand_lift_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-laserbot-core-proof-1111 --max-files 1 --timeout 120 -- python -B tools/audit/check_steve_shatterhand_laserbot_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-laserbot-grant-1111 --max-files 1 --timeout 150 -- python -B tools/audit/check_steve_shatterhand_companion_live_1111.py --laser-grant
```
