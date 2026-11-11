# Steve Hermann’s first companion

The private MMC5 candidate
`d4973088e4f5efdf09ac7c4cbcc7a090e7e121da02ede9c12534dd42a5204d04`
adds the Alpha–Alpha–Alpha reward. The existing 1-1 blocks at world X336,
X1248 and X1744 produce the three tokens. Normal controller input reveals
and collects them. The CPU replay settles on the last block at X1740/Y48
with six health and two lives. The companion appears 54 updates after that
checkpoint, when the original countdown crosses from `$31` to `$30`.

The live companion follows Steve using the original fixed-point orbit.
Fresh B starts its spinning shot and companion attack animation. The
51-update shot uses both original projectile cells and all three attack
poses. The six 8×16 body and projectile cells come from the original
cartridge’s CHR88. The native metasprite renderer projects and clips the
cells in screen coordinates. The projectile tests its center against
native enemy bounds, takes one point of enemy health, and uses the
ordinary defeat handler for the last point. Eight directed CPU checks
cover the four outside edges, the inclusive edges, an active enemy hurt
cooldown, and native Goomba defeat.

The orbit worker agrees with Shatterhand USA in 102,912 cases. The attack
worker matches 4,032 weapon updates, 3,552 projectile updates, 96 births
and nine spent-projectile resets. The live bridge takes 574 executable
bytes and the source worker takes 821. The companion transport borrows
two identical Roll CHR mirrors and keeps Roll’s compiled output identical
in the [transport checks](steve-shatterhand-companion-transport-1111.md).

The first hardware replay showed 21 projectile pairs using only tile
`$77`. The native catch-up cadence skipped alternating draws and starved
tile `$79` when selection used simulation parity. The renderer now advances
the visual phase on draw updates while the original shot clock retains its
simulation timing. The fixed Mesen run uses 2,228 controller samples in
3,528 physical frames, earns all three tokens and finishes at X1743/Y48
with both lives. Hardware OAM matches 27 companion pairs and 21 shot pairs
covering both donor projectile tiles. Receipt SHA-256 is
`96cd5404276f0ca491fdb55588240395f8e84b25ef559ec5273e63a495c796ff`.

Down+A assist, companion damage and lifetime across deaths or area
transitions, the seven other companions, and the playable armor are
pending. The source shot cue is tracked but has no host audio driver
yet. The private candidate stays out of Downloads and Current while
those token outcomes are incomplete.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-companion-live-proof-1111 --max-files 1 --timeout 140 -- python -B tools/audit/check_steve_shatterhand_companion_live_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-first-companion-proof-1111 --max-files 1 --timeout 90 -- python -B tools/audit/check_steve_shatterhand_first_companion_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-companion-native-1111 --max-files 2 --timeout 220 -- python -B tools/audit/replay_steve_companion_native_1111.py --output build/steve-companion-native-1111
```
