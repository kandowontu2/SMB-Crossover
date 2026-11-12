# Steve pose worker allocation

Private fixture `4bbc4011db1648eef85cd7d591255e85d4d0d691bb68e5073545be04cc5d4dd2`
extends the installed `235de3ed` lift build with a 512-byte executable
allocation at raw WRAM bank 2 `$CE00–CFFF`. This is preparation for the
original pose renderer. No renderer is connected and no ROM was published.

CHR307 stores the worker in its first 512 bytes and the eight original
throw-recovery cells in its second half. Recovery metasprites use even
tiles `$20–$2E`. CHR339 and the four existing CHR711 aliases retain the other
lift and throw poses. All 110 source sprite comparisons pass after moving
the recovery cells. Roll keeps the previously qualified blank-page aliases.

The optional loader copies CHR307 to `$CE00–D1FF` after the original cold
decoder returns. It then loads CHR336 and CHR338 at `$D000–D7FF`, restoring
the complete Laserbot/lift program over the temporary upper-half copy.
The worker and graphics are included in the existing cookie binding.
The loader is 118 bytes. Its default path still reconstructs the installed
nightly byte for byte.

The paired native CPU route earned all three Alpha tokens, waited for the
companion, and verified its full 51-update shot. Both images finished with
six HP and two lives at X1740/Y48. OAM, CHR mapping, VRAM, raw bank 3, and
the remaining raw bank 2 program/state matched. The original route never
accessed `$CE00–CFFF`. The candidate wrote and read exactly 512 bytes there
during cold initialization and made no hot accesses. The loaded executable
returned its expected marker when called directly.

The separate cold-path run rejected eight readback faults at `$CE00`,
`$CFFF`, `$D000`, `$D3FF`, `$D400`, `$D77F`, `$D780`, and `$D7FF`, plus the
existing upstream `$BC00` fault. It passed 54 forced-blank lag-NMI cuts and
preserved warm state. Both checks used the same fixture hash and generated
zero files.

The same fixture also passed paired cold entries and 80 input updates each
for Mike, Jay, and Steve. All entered gameplay at update 167. Application
state, OAM, CHR mapping and VRAM matched after each update. Jay and Steve
performed the expected 2,050 additional cold PPU reads; Mike performed none.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-pose-carrier-1111 --max-files 1 --timeout 300 -- python -B tools/audit/check_steve_shatterhand_pose_carrier_1111.py
python -B tools/audit/run_bounded_build_v1.py --output build/steve-pose-carrier-1111 --resume --max-files 1 --timeout 120 -- python -B tools/audit/check_steve_shatterhand_pose_carrier_1111.py --cold-only
python -B tools/audit/run_bounded_build_v1.py --output build/steve-pose-carrier-1111 --resume --max-files 1 --timeout 150 -- python -B tools/audit/check_steve_shatterhand_pose_carrier_1111.py --opening-only
```

The allocation still requires the actual pose selector, native OAM/PRG
ownership integration, and Mesen verification. The current tests do not
prove live artwork or a playable robot throw.

## Current selector constraint

Disassembling the installed bytes found that `JnSetPose` now occupies only
`$A276–A2BB` in PRG96. `$A2BC` begins a separate far-call gate. The historic
85-byte prototype envelope must not be used for a replacement. The live
routine calls `$80C2` for bank publication and `$C38C` for body selection,
then reads pointer tables `$C032/$C040`. It preserves the CHR byte on the
stack and enters the physical CHR far-call tail at `$A2A8`. Any pose hook
must preserve the adjacent gate and qualify the actual current stack/bank
contract. Source prototype text alone does not establish that contract.
