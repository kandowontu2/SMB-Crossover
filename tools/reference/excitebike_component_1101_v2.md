# Excitebike original source component — November 1

Run from the workspace using its bounded producer:

```
python tools/audit/run_bounded_build_v1.py --output build/excite-prince-component-1101-v2 --resume --timeout 180 -- python tools/audit/excite_prince_component_1101_v2.py
```

Use `--resume` only for this agent's existing unfinished output. It deliberately
has no qualified `source-stage.json` or `binding.json`. Root owns freezing,
integration, emulator tests and nightly delivery. No host or menu files changed.

## Delivered code and evidence

`excitebike-component.s` contains genuine instructions recovered from donor
`C:/NES/Excitebike (Japan, USA) (En).nes`, SHA-256
`4eac85fdf79ffb931103d910d6f9ae3b0db0affd1df833d5e2511055a5698489`.
The assembled code is 1,240 bytes with 76 original table bytes. The test layout
places code at A000 and tables at A900; each original RAM operand becomes
`ExState + original_address`, with ExState=C000. Logical state is 2,048 bytes;
these particular routines only use its lower 1,024 bytes. Host allocation still
requires an ownership audit. There is no direct hardware access or host ZP use.

Public entries:

| Entry | Original | Function |
|---|---|---|
| ExMotor | CD59 | One actor's acceleration, deceleration and tilt; X=actor0..3 |
| ExMotorAll | CD1F | Original four-actor wrapper, ready gate and start SFX queue |
| ExSlopePose | DCA0 | Translate original track-slope class to neutral bike angle |
| ExAirStep | DCF2 | Original airborne velocity/fraction/height update |
| ExAirLaunch | DD38 | Original launch initialization from current speed |
| ExFractionalX | DA58 | 8.8 speed plus accumulated fraction to integer delta60+X |
| ExTemperature | E359 | Heat/cooling, overheat state and original HUD cells |

The CPU comparison includes 2,304 explicit cases. All application RAM, physical
status flags, registers and SP match donor execution. PHP/PLP's synthetic B bit
is excluded. Expanding original STY zp,X uses an A/P-preserving sequence because
the 6502 has no STY abs,X. All host ZP bytes remain unchanged. The 2A/26 timers
and the 4C quarter-frame selector must retain their original cadence.

The sequencing test executes actual donor reset and Start/course setup for800
updates, then 1,020 updates of A throttle, B turbo, backward/forward lean,
up/down lane changes and coast. It calls the relocated component at genuine
donor routine boundaries; the rest of the donor NMI/terrain/render/audio order
continues unchanged. All application RAM, CPU ABI and PPU/OAM/APU output writes
match on every update, across 14,281 replacements. The natural ramp sequence
caught a missing indexed tail in the slope table; the full seven-entry table
is now recovered and represented in explicit fixtures.

`source-art.json`, `excitebike-body-patterns.bin` and `source-poses.png` provide
all23 source pose indices, 154 distinct patterns and original OAM geometry.
Packets come from executing E1F9/E1A3/D1C7; no invented pixels. The PNG is a CPU
preview, not a native capture. The original descriptor can consume nine cells;
sprite capacity/rotation and the NES eight-per-scanline rule need host tests.

## State/import boundaries for host integration

Actor0 owns speed90/94, X fraction0394, integer delta60, screen X80, screen Y8C,
orientationAC, airborneB0, crash98, recovery9C, throttle5C and slopeD4. The original
clock3F feeds quarter selector4C. Original launch/gravity fractions live at
0378/037C/0380/0384/038C. Temperature fraction/integer are03B5/03B6; overheat
uses03E0 and cooldown3C. Scratch00..0E is privatized alongside application state.
Audio results are queue bytesFB..FF; ExTemperature also writes private OAM2F0..FF.
These should be imported by host adapters, never treated as native SMB RAM.

The original controls are A throttle, B turbo, Left lean back, Right lean
forward and Up/Down change track lane. Source A and B speed caps are0320 and0340
(3.125 and3.25 pixels per original update); acceleration occurs on the actor's
quarter-frame phase. Turbo heat targets32, A targets17 and neutral targets8,
with the actual fractional arithmetic preserved. Excessive tilt can crash.

The original game has automatic ramp jumps and track-lane Y movement. Therefore
ExAirStep is not an SMB jump routine and D4 is not an SMB metatile. A side-view
adapter must explicitly define deliberate jumping, ground/support height,
landing/crash reconciliation, camera/world coordinates and safe script handoffs.
It must not feed arbitrary SMB tile IDs to these source tables. Preserve8.8
speed precision and map its delta to the native camera once per update.

Missing host work: native head/side/feet/camera/pipes/flagpole, enemy contacts and
damage, earned upgrades, health/death, audio channel ownership, lifecycle,
swimming, rendering leases, guarded dispatch/menu and native controller runs.
This is neither an integrated NES candidate nor a playable unlock. The bus is
explicitly untimed: PPU status readiness alternates, without raster/acoustic
simulation. It is not evidence of native timing or full donor-game fidelity.

## Prince of Persia audit

`prince-source-audit.json` records the actual USA donor (mapper2, PRG128KiB,
CHR RAM8KiB), its fixed-bank reset/NMI entries and one existing authenticated
262-pixel body packet. `prince-fixed-entry-disassembly.txt` is a bounded original
byte listing; `prince-body-patterns.bin` and `prince-source-body.png` retain its
nine-cell packet geometry. Only two exact indexed archive objects are read,
in memory. No archive trees are restored.

Prince still needs genuine actor/animation/input recovery and an assembled
component. Its CHR is uploaded to RAM, so raw ROM tile-number cropping cannot
substitute for the renderer's actual source. No Prince gameplay claim is made.
