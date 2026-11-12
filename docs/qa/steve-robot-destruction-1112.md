# Steve robot destruction

The detached worker matches Shatterhand USA
`fbdfaab40aedda270d7473be37566b59e68811d932740c105d84fa6b1a7f19e1`.
The source is `tools/reference/steve_shatterhand_robot_death_1112.s`.
The comparison harness is `tools/audit/check_steve_shatterhand_robot_death_1112.py`.
Live admission, collision rectangles, rendering and native audio binding belong to
the host integration.

## Damage admission and ordering

PRG8 `$8411–$8422` admits a nonzero robot actor with age `$06EC >= $0C`.
The enclosing dispatcher rejects robot contact while player armor `$05C2` is
nonzero or the incoming collision flag is negative. The source worker's
`SteveRobotDamage` begins after overlap has been admitted, corresponding to
`$844E`. Its A input is the donor collision flag.

Every positive admitted hit resets robot age to zero. The low nibble supplies
damage zero through seven. Nibbles eight through fifteen supply one damage.
An empty donor sound request receives `$33`. An existing request survives.
On a surviving hit, store the reduced HP. On a fatal hit, preserve the prior HP
byte, clear orbit angle, set throw timer `$20` and replace actor ID with `$FF`.
The worker compares all these fields and its returned A against the original
accepted-damage leaf for all 256 flags, seven HP values and two sound states.

An original `$83E2` contact probe checks eleven cases. Collision flag `$21`
damages the robot without damaging the enemy or setting the return receipt.
Flag `$01` sets the surviving actor to `$C1` in the checked overlap, including
when enemy cooldown age seven prevents new enemy damage. An eligible enemy
loses two HP from robot pose `$015E`; its earlier cue `$35` survives the incoming
damage leaf. Fatal robot damage overwrites the receipt with actor `$FF`.
Robot age eleven, player armor and flag `$81` reject the checked contact.

PRG13 `$A50F` increments surviving age on the following actor step, so an
ordinary hit is followed by age one in that same Main update. It saturates at
`$FF`. Destruction branches at `$A4C9`, bypasses that increment and retains age
zero. PRG13 `$A523` clears surviving actor bits seven and six after its update.
Apply that mask only after surviving dispatch.

## Destruction worker

`SteveRobotDeathTick` matches `$A4C9–$A50D`. Its caller admits actor `$FF`
and handles pause and player-scene scope. A new one-byte `SteveDeathDraw`
receipt reports whether this update calls the original body renderer.

While the timer is positive, decrement it and move Y by one pixel in Q4.
Clear all projectile type slots and request cue `$0A` on the one-to-zero
transition. Display the retained robot pose when clock bit one is clear.
The underlying pose remains stored on hidden blink updates.

Starting on the next update after zero, move Y by two pixels and advance actor
action `$20`. Its PRG13 `$BE08` rows are
`03 DC 01 03 DE 01 03 E0 01 03 E2 01 FF E2 01`.
The four poses each last three updates. Loading terminal `$FF` calls the
equivalent of PRG12 `$936E`, clears the actor and skips its body draw.
The complete sequence takes 45 updates and draws 28 times across every tested
clock phase. Normal polarity moves upward. Polarity bit seven reverses motion.
All additions retain the original 16-bit wrap.

Bind `SteveBotHP` to existing `SteveRobotArrival`, which owns donor `$06FC`.
Bind `SteveDeathPolarity` to existing `SteveBotRoomPolarity`, representing
`$05CB`. Bind pose and animation fields to the lift robot fields, as the throw
worker does. Timer, speed, auxiliary, aim and sound use existing throw fields.
The worker needs one additional draw receipt byte.

`SteveDeathClearShots` is a callback. The donor clears exactly
`$0700–$070F`, preserving projectile coordinates and other properties.
The live callback should clear Alpha and Laserbot type fields and their cached
draw tags at this transition. Preserve `$92/$93` across the callback because
the destruction step has already prepared its Y delta there. Projectile update
and drawing continue until that transition. Enter death dispatch before the
current actor-ID checks and Laserbot lifecycle rejection.

The default detached link places 271 bytes at `$AB80`, comprising 256 code
bytes and 15 animation bytes. Its SHA-256 is
`c54a0030a7e49d11829f111ea7a2e29b15567c5fc9d5e7b253e09964d67279b7`.
Entrypoints are `SteveRobotDamage=$AB80`,
`SteveRobotDeathTick=$ABC4` and `SteveRobotDeathReset=$AC5F`.
The audit's `link(donor, fields, origin=...)` accepts live aliases and a
relocated origin. This default position is a detached test location.

## Original graphics

The four destruction poses and their facings use donor CHR87. Each facing has
identical geometry. The native records total 44 bytes, plus optional lookup
offsets.

| Pose | Relative Y, X, donor tile, native attribute |
| --- | --- |
| `$01DC` | `(-8,-8,$57,$01), (-8,0,$57,$41)` |
| `$01DE` | `(-24,-8,$51,$01), (-8,-8,$53,$01), (-24,0,$51,$41), (-8,0,$53,$41)` |
| `$01E0` | `(-24,-8,$55,$01), (-8,-8,$57,$01), (-8,0,$57,$41)` |
| `$01E2` | `(-8,-8,$55,$01)` |

These attributes include the original age-zero hurt transform. Sixteen actual
`$A6DA` publication probes confirm base attribute `$03` or `$83` before
the fixed renderer. Record attributes XOR that base. The former robot body
uses native palette two during the initial blink. Destruction poses use palette
one. Inverted polarity additionally XORs vertical flip `$80`.

Donor tiles `$55/$57` already match host CHR711 cells byte for byte through
host tiles `$77/$79`, which the first companion projectile uses. Donor tiles
`$51/$53` need 64 additional CHR bytes. Their cell hashes are
`427b33e35dd47cb99565303d45d4bc31b5d847a47165a999d7d1266abd2300d4`
and `cd35323d1cdd053884f974758bfee4305c782b79f48ef166fde13fd8d1d0f78e`.
The harness emits their exact 32-byte payloads and all original records.
Their host CHR placement remains to be funded.

## Verification

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/steve-robot-death-1112 --resume --max-files 1 --timeout 100 -- python -B tools/audit/check_steve_shatterhand_robot_death_1112.py
```

Final invocation `92a24a` exited zero in 2.17 seconds. It compared 3,584
accepted-damage cases, including 606 fatal outcomes, eleven original overlap
cases, 1,200 destruction updates including sixteen complete sequences, and
sixteen original pose publications. The destruction comparison checks every
declared donor field, projectile type bytes and draw admission at the actual
`$A52E/$A531` boundary. The test callback clears the separate host fixture's
sixteen projectile type bytes.

All fixtures and compilation stayed in memory. The bounded invocation generated
zero files. The source remains detached pending live caller, CHR, renderer and
native audio integration.
