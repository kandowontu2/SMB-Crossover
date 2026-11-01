# Metal Storm original object/frame callback component

**Source component only; no selectable admission, current ROM edit or resource
grant.** Frozen v5 remains unchanged. New output root:
`build/metal-storm-objects-host-1101-v6`. No mutable native ROM/debug is read.

## Implemented behavior

The real FF27 targetDCAE increments original53 once, calculates the original
camera window, then processes object slots23 down to1. Player slot0 animation
advances in the unchanged actorADC8..ADE1 **after** FF27 returns. This order is
preserved; no native replacement clock or generic projectile velocities exist.

The component relocates441 original instructions from:

| Original source | Implemented scope |
| --- | --- |
| DCAE..DCF6 | Exact frame increment and23→1 object processing order |
| DA8F..DB1A | Original visibility window test and object retirement |
| DD48..DE0F | Signed X/Y integration, original240Y rules and object animation |
| DF33..DFF2, E1ED..E2C3 | Original horizontal/vertical projectile contacts and snap response |
| DD06..DD0B, DE91..DEA1, E04C..E05D, E32B..E32E, DB9B..DB9F | Genuine qualified negative-object dispatch/return paths |
| D783..D7AE | Original bank shadow/state/AXYP effects; hardware writes become private log bytes |
| 8BCF..8BF8 | Original empty-platform pass, including clears113..116 and existingAB53 reconciliation |
| FC5E..FC8D | Actual reset validation/initialization of gravity controls119/11A |

Standard/upgraded original projectile types80/81 in slots1..3 are qualified;
the original actor actually creates them in slots2/3. Pose, signed12px motion,
animation and window culling come from donor instructions. Original660 shot
fields are retained as source data; this packet does not invent a lifetime
countdown or claim the unported scene/renderer lifecycle processes it.

Source DD06's positive metadata path, enemy slots4..23, generic object gravity,
GravityFire type82, and active native platform objects are **not implemented**.
`MsNativeObjectsReady` rejects those forms before any actor update, and rejects
negative717 before it could create unsupported GravityFire later in a step.
Five integrated object rejection cases and the GravityFire-before-spawn case
verify that source state and clock remain unchanged. The imported
`MsObjectUnsupported=$5020` is a fail-fast laboratory boundary, never an
admitted native service or a permissive RTS. A resident dispatcher must retain
this preflight; unsupported upgrades cannot be enabled with this component.

Original D783 normally switches to donor metadata bank6 (physical12/13).
Qualified negative types skip that metadata read, so the host adaptation
retains all logical source bank fields and register outputs while recording
the two register writes privately. It does not remap native PRG or pretend
positive object metadata is available.

## Constructor and animation corrections found through composition

The first original actor on the actual reset/Start route is frame525, with
119=00,11A=80,11F=00 and5A0=01. The pure9371 constructor does not seed119/11A.
V5's cold clear therefore needed the actual FC5E reset leaf: otherwise Up+A
would write00 instead of reversing gravity. V6 calls that recovered source
leaf after the v5 pure constructor. V5 itself remains frozen and unmodified.

The original rendererF2EA..F2F7 loads the animation mask at metadata(state+5)
into5A0. `MsNativeAnimationMask` uses all eight exact original actor bytes,
preserves AXYP, and writes only5A0. It runs for the initial pose and after the
actor step, matching the source renderer's position in frame ordering. This
preserves natural pose timing before native OAM rendering is integrated; it
does not claim the rest of F282's palette/hurt-blink/OAM effects are ported.
Sixteen direct original-renderer leaf pairs prove every mask/state and the
typed wrapper's AXYP contract.

## Terrain and native boundary contracts

V5's static terrain/contact callbacks remain in the same composed component.
Actor FF1E maps native solid non-climbable terrain toE0. The new projectile
query adds08/10, producingF8 for that same solid terrain, because original
normal/upgraded projectile contact code tests those distinct flags. Donor
hazard02/04 remain clear. These flags select genuine donor collision responses.
Native block transaction/breakage effects are not added by this mapping.

All original source state is privateC2:C000..C7FF. V5 source/world displacement
and constructor interfaces retain their contracts. Foreground03/04 is the
only borrowed pointer; public actor/step/constructor restores it. Native
NMI00..02 and R2..R7 are never borrowed. New private fields:

| Address | Owner |
| --- | --- |
| C2:C818 | Last logical donor mapper select |
| C2:C819 | Last logical donor mapper data |

`MsNativeObjectsReady` retains A/X/Y andP except carry (C1 qualified/C0 reject).
It mutates no source fields. `MsNativeAnimationMask` retains all AXYP.
`MsNativeShotTileQuery` retainsX, returnsY0/pointer03/04 and volatileA/P,
matching the typed callback contract consumed by the source projectile code.
The bare internal FF27/8BCF entries retain actual source AXYP results; they
are not standalone resident-dispatch ABIs and require a qualified owner.

`MsHostStep` now checks object eligibility before source motion, then retains
original actor→FF27→player animation→renderer mask→input ordering. Source
controller31 still receives current host input **after** its actor step.
`MsNativeApplyDelta` remains a separate once-only boundary before native
camera processing, as defined by v5. No screen/camera delta is added twice.

## Actual code budget and resource limits

The first private link was9294B. Monotone relaxation replaces414 genuinely
long conditional encodings with equivalent6502 short branches, saving1242B;
437 explicit short conditionals are checked against their emitted opcode and
exact target. Two compile passes converge. Only private actor/object labels
move; no existing native host code, symbol or caller is edited.

Final actor+v4 ABI+v5 ctor/terrain+v6 object cluster is **8052B atA000..BF73**,
leaving **108B before the owner headerBFE0**. This is a component layout proof,
not a grant of A3/C2/CHR/resident resources. Header authentication, cache
transport, menu admission, body/projectile graphics and any new code funding
still require parent integration review. No extra resident ROM is assumed.

## Verification scope

All fixtures stay in memory and only aggregate receipts are written:

- 1536 original FF27/composed callback pairs; all23→1 object orders match.
- 82 real projectile terrain responses;576 original window retirements;
  six8-bit source-clock wraps.
- 32 original bank-state/AXYP pairs and75 original control-reset pairs.
- 736 preflight cases, including362 unsupported object rejections.
- Six constructors from poisoned private RAM, followed by576 original actor
  frame pairs: walking, jumping, gravity reversal, horizontal/up/down shooting,
  both source shot slots and native epoch wrap.
- 576 duplicate-epoch cases and576 pause cases without source advancement.
- Five composed unsupported-object atomic rejections and rejection of the
  GravityFire flag before actor spawning.
- Actual donor reset/Start route through first actor frame525, independently
  confirming the original control pair and initial animation mask.

Whole-frame pairs run the real donor FF27 and8BCF instructions, versus the
compiled callbacks and relaxed actor. Original8874/9ED7/FF18/FF39 scene/map/
audio APIs remain explicit effect-free test boundaries **in both engines**;
their production effects are not claimed. The renderer comparison isolates
its real F2EA mask leaf; it does not execute a fake whole renderer.

Frozen v5 independently proves all256native metatile attributes against the
actual0162287e helper. V6 uses controlled block buffers and known solid61/air
semantics, not a current native ROM copy or a newly claimed helper audit.

Minimum standaloneSP202 includes nested actor/object code. Maximum13396cycles
is cold construction, not steady-frame timing. Real Main caller stack and
its12-byte interrupt reserve, NMI/IRQ/SMC entry, mapper/cache ownership,
graphics, enemies/combat/health, GravityFire, audio, scene transitions,
flagpole/pipe/springboard behavior, menu access and full1-1 playthrough remain
required **native admission gates**. This packet is not a nightly ROM.
