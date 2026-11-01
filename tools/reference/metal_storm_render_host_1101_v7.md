# Metal Storm: original rendering and entity lifecycle, v7

This component is not selectable admission or an installed ROM update. It adds
the original visible body/projectile art and original entity lifecycle to the
frozen v6 constructor, terrain, gravity, movement and projectile component.
The native renderer, physical CHR selector, CHR publisher and far-call SMC used
by the CPU model are exact emitted bytes from the installed `0ffb1d79...` build.
Only 1,059 code/data bytes and 43 small symbol records are retained as witnesses.
There is no copied ROM, PRG bank, debug tree or state snapshot constructor.

## Compiled fragments and required placement

| Fragment | Proposed arena | Bytes | Space before reserved boundary |
| --- | --- | ---: | ---: |
| Original actor, ctor, native terrain and step adapters | A3:A000..BF92 | 8,083 | 77 before BFE0 |
| Renderer, entityAI, metadata and tables | C2:CD00..D631 | 2,354 | 2,478 before DFE0 |
| ROM eligibility/header frontgate | test ROM9000..9083 | 132 | **Unfunded** |

The actor image cannot absorb the renderer. Parent integration must explicitly
fund a resident transport/frontgate, cache carriers and six physical CHR pages.
Body physical pages800..804 and shot page805 are test fixtures, **not grants**.
Their values are imported constants so a real allocation changes no physics.
The existing proposed raw owner35 remains Sophia's alternate; v7 does not edit
menu tables, readiness, a service dispatcher or the current ROM.

External frozen inputs remain in the v6 lab and previous compact packets.
The build recipe reads only the specific existing include files it needs.
It does not extract the historical archive or reproduce a dependency tree.

## Original source recovered

* Bank4:8EAE..8EF2 is the normal/upgraded shot entityAI: two-frame spawn delay,
  original lifetime decrement, impact X correction and conversion to type83,
  and original inactive/Xpage80 retirement.
* Bank4:8E54..8EAD is original impactAI, including even-clock progression and
  its alternate mode's signed/gravity-aware offsets. All instructions are
  semantically relocated; no replacement movement clock is introduced.
* Fixed EEAE..EEC5 is the exact zero-delay impact retirement leaf. Its positive
  delay branch is a fail-fast laboratory boundary, not a permissive stub.
* The qualified projectile path at DB9B now allows negative visibility6A8
  when source600 is positive. This is the actual original branch previously
  absent from v6's minimal visibility preflight.

The source frame order is actor AD8C (including DCAE clock increment), entityAI,
then rendering. Original even53 draws body then shots ascending; odd53 draws
shots descending then body. The native bridge follows this order. The C2
lifecycle call occurs once in the accepted step, before animation metadata,
input sampling and native displacement publication. Duplicate/pause epochs
do not age shots or advance animation.

Qualified source objects are negative80/81 in slots1..3 with source600=0A,
or negative83 with600=05,618=0 and630 in0..2. Impact phase2 is the real
terminator; phases3/4 read following donor data and are unreachable after that
terminator. They are recovered in the art audit but are not admitted as poses.
GravityFire/type82, donor enemies/platforms and active slots4..23 stay rejected.

## Native drawing and art

The 208 original body contexts use 144 exact original8x16 patterns packed into
five1KB pages, plus the original 1,002-byte compact metadata. A pose needs at
most two pages. Reflection uses original X=24-dx and gravity Y=18-dy geometry,
attributes and original OAM cell order. Source metadata includes OAMY+1; the
native packet subtracts that one pixel before the actual native producer.
No generic Sophia/MegaMan animation or fabricated gravity velocity is used.

The 104 reachable shot contexts use five original patterns in one1KB page:
normal shot, upgraded horizontal, doubled upgraded vertical and two impact
frames. Upgraded vertical drawing has the original forced/cleared H-flip bits;
impact metadata ignores shot orientation. Both were verified against actual
original F282 output, rather than guessed from a spritesheet.

Odd tile IDs use spriteP1 windows4/5 for the body and6 for shots. Native sprite
P0 windows0..3, spritewindow7 and all background windows8..11 are retained.
The selected owner clears stale `SsChrActive` so its window4 does not inherit
another character's override. Only `Player_SprAttrib` priority20 is inherited.
`MsRenderGraphics` clears the generic pose and sets its pointer to an empty C2
pose; future host callers must retain the authenticated C2 mapping while using
that pointer and replace it on retirement/reentry.

The exact original palette packet is:

```
3F11: 26 0F 15
3F15: 21 20 01
```

`MsRenderColors` appends those two native queue packets only if the current
offset is below72. It never writes the universal/background palette or a
background-color control. **Palette1 is also used by native world objects.**
Authentic player palette recovery is proved; an integration must allocate or
adapt palette ownership and check actual enemies/powerups before admission.

Source worldX is converted to screenX by subtracting the native camera exactly
once. Original signed240-page Y is converted to native linear YHigh1. Original
movement fractions and gravity state are never copied into generic velocities.
Native MetaspriteRenderLoop supplies clipping, guest rotation and its all-or-
none capacity rule. This deliberately follows native OAM capacity semantics.
Source visibility6A8..6AB is based on the actual native OAM cursor change.
At partial screen edges or capacity rejection this can differ from donor
clipping; the composed suite records141 such field differences and excludes
only those visibility bytes from its durable source-state equality claim.

## ABI, cache and interrupt boundaries

`MsRenderGate`, `MsGraphicsGate` and `MsColorsGate` preserve A/X/Y/P except C,
which reports acceptance. Before any C2 opcode, the ROM fragment requires raw35,
source readyA7, OperMode1, engine8 and all16 bytes of both C2/DFE0 and C3/BFE0
fingerprints. Every corrupted header byte and all four eligibility failures
reject without executing C2 or changing its RAM. These are eligibility and
fingerprint checks; actual cache mapping/loading/readback remain external.

Warm renderer services preserve native R0..R7 ($03..0A), the three public
far-call SMC operand bytes, current A/C bank mappings and registers/flags.
Actual FarCallCommon changes its own internal bank immediates, as normal.
No part of native NMI scratch00..02 is borrowed. `MsObjectLifecycle` preserves
AXYP; its source leaves do not borrow foreground R0/R1. Its caller owns the
source step's existing foreground pointer preservation.

Renderer save/scratch is C81A..C83C and its33-byte native packet is C880..C8A0.
Source actor state is C000..C7FF, including saved foreground bytes C7FE/C7FF.
V6 source/host fields C800..C819 are retained. The constructor clears only
source state, preserving the separately placed C2 renderer.

Imports from the actual host are: MetaspriteRenderLoop, X5SetPhysicalChr,
FarCallCommon, SafecallA_SMC, FarcallJmpTarget_SMC, CurrentBank, CurrentBankC,
ScreenLeft_X_Pos, ScreenLeft_PageLoc, Player_SprAttrib, CurrentOAMOffset,
SsChrActive, VRAM_Buffer1, VRAM_Buffer1_Offset, ObjectMetasprite, SmPosePtr,
SelectedCharacter, OperMode, GameEngineSubroutine and foreground R0..R7.
Art page constants and draw/CHR native bank constants are explicit imports.

Minimum standalone SP was202, with 13,397 maximum modeled cycles in the full
composed fixture. This is not a real Main/ISR stack-reserve or raster timing
proof. Parent must retain the required12-byte Main interrupt reserve and run
actual SMC/ISR cuts on the final composed transport/candidate.

## Evidence and reproduction

All artifact producers run through the bounded wrapper, using this same one
unfinished root until frozen:

```
python tools/audit/run_bounded_build_v1.py --output build/metal-storm-render-host-1101-v7 --resume --timeout 180 -- python tools/audit/prepare_metal_storm_render_assets_1101_v7.py
python tools/audit/run_bounded_build_v1.py --output build/metal-storm-render-host-1101-v7 --resume --timeout 180 -- python tools/audit/prepare_metal_storm_render_host_1101_v7.py
python tools/audit/run_bounded_build_v1.py --output build/metal-storm-render-host-1101-v7 --resume --timeout 180 -- python tools/audit/check_metal_storm_render_host_1101_v7.py
```

A fresh reproduction needs its own new root and the archived witness; do not
resume or rewrite this qualified output. The capture tool's original path/hash
records a historical input, and must not be rerun against an unrelated current
O/debug pair. No current mutable O input is used after witness capture.

Aggregate tests:208 original body pixel contexts,104 reachable shot contexts,
36 camera/clipping cases,20 native capacity/rotation cases,5 palette-queue
cases,36 full-header/eligibility failures,768 original lifecycle pairs and576
constructor/terrain/actor/lifecycle/draw frames. The last suite covers both
gravity directions and285 frames with shots,576 duplicate epochs and576 pause
epochs. It compares durable actor state0480..074F except the four explicitly
native OAM-visibility bytes. Scene/map/audio callbacks8874,9ED7,FF18,FF39 are
effect-free controlled ports in both models, not implemented gameplay claims.

The single preview PNG is composed from actual native-producer pixels in the
passing CPU fixture; it is not an emulator capture or proof of raster cadence.

Remaining admission gates: actual cache/carrier/CHR/palette allocation and
loading; selected/menu/service transport; original health/hurt blink/death;
GravityFire/remaining upgrades; native enemy/block combat; source scene/audio;
camera/transition lifetime ownership; actual Main/ISR and SMC cuts; original
music/SFX; native menu and full1-1/powerup playthrough qualification.
