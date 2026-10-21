# Mega Man/Bass injury: pinned Crossover2.02 contract

This records the independent source contract, preserved baseline failures and
focused injury acceptance. Controller traversal and final recordings remain
separate work; no full MM/Bass clear is claimed by these explicit arenas.

Pinned SWF SHA256:
`6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af`.
Source paths below are relative to
`reference/crossover2/extracted/scripts/com/smbc/`.

## Entry and eligibility

`Character.as:2198` rejects damage while `takeNoDamage`. A character without
an active Mushroom dies; otherwise the Mushroom is removed and normal
difficulty removes the other upgrades before calling `takeDamageStart`.
`Bass.as` inherits all the following behavior from `MegaManBase`; it has no
injury override. `MegaManBase.as:615` updates the weapon vector on damage.
If the prior weapon is no longer active, `updateWeaponsVec:650` selects the
normal buster, refreshes suit/ammo/charge state and destroys old player
projectiles, Rush and a carried Super Arm brick when selection changes.

`MegaManBase.as:2078` then:

1. Sets the static `takeDamage` body pose and plays
   `SFX_MEGA_MAN_TAKE_DAMAGE`.
2. Sets `takeNoDamage`, `disableInput` and `nonInteractive` true.
3. Enters `ST_TAKE_DAMAGE`; leaving slide calls `endSlide:1189`, destroying
   the Charge Kick graphic. Held inputs are released.
4. Sets VX opposite the existing facing: facing right gives -80 Flashpx/s,
   facing left gives +80. The attacker location is not used, and facing is
   not turned around. VY is reset to zero.
5. Starts flicker, creates the damage splash and sparks, and starts a
   single-cycle450ms `GameLoopTimer`.

Constants are `MegaManBase.as:249`: flicker70ms, recoil450ms,
post-recoil no-damage1250ms and recoil speed80 Flashpx/s.

## Motion and input during recoil

This does not freeze the level. `movePlayer:799` returns during damage, so
there is no horizontal steering or normal ground step. `checkState:932`
also returns, preserving the damage state and bypassing normal air-jump
release friction. The button manager gates gameplay presses and releases
on `!player.disableInput` (`managers/ButtonManager.as:236` and later cases).
Jump, shot, slide, select and directional control cannot replace recoil.

Normal actor physics still executes. `main/AnimatedObject.as:236,362` applies
gravity if airborne and integrates VX/VY, then ordinary terrain collision
resolves walls and floors. `MegaManBase.as:337,558` supplies dry gravity1500,
water gravity500 and terminal downward speed700 Flashpx/s. The common
underwater check additionally clamps falling speed before gravity; the
existing source water boundary/cap behavior still applies. Recoil must not
defy gravity or ignore walls. At a ground edge it falls normally.

At the established port scale (2 Flashpx per NESpx,60updates/s), the initial
recoil is +/-80/120 = +/-2/3 NESpx/update. Dry gravity adds1500/7200 and
water gravity500/7200 NESpx/update^2. These conversions come directly from
source units, rather than from runtime fixed-point tables.

## End, invulnerability and timer ordering

`takeDamageEnd:2112` drops the splash reference, re-enables input and
interaction, sets neutral/stand, and sets VX zero only if grounded. It then
starts the separate1250ms no-damage timer, checks the normal state and
resends currently held physical buttons. In air, recoil velocity persists
until normal input/movement takes over. Facing is still unchanged.

The450ms recoil and70ms flicker use `GameLoopTimer`; its `update` adds
`level.dt*1000`, compares against the duration and retains a periodic
timer's remainder. `Level.as:2139` updates these timers before actor motion.
The1250ms timer is a `CustomTimer` wrapping Flash `Timer`; it retains its
remaining real duration across pause/resume. A deterministic60Hz port
normalizes recoil to27elapsed update intervals and the subsequent no-damage
duration to75intervals, with correct phase at entry/end. Injury begins during
collision after the hit frame's actor movement. On the update reaching450ms,
the timer's end event runs before actor movement, so normal control can resume
on update27; this must not be mistaken for27additional fully locked recoil
displacements. Total protection is therefore
about1700ms, not1250ms measured from the original hit. A70ms flicker phase
requires a retained time accumulator, rather than a constant four-update
toggle. Pause/lag policy must remain explicit in the shared injury API.

`noDamageTmrLsr:2129` invokes the common listener, clears `takeNoDamage`
(unless permanent invulnerability), restores full visibility and stops flicker.

## Exact effect behavior

`graphics/MegaManSimpleGraphics.as:81` anchors the static damage splash at
source NX and `NY-height/2`, follows that center every update, and sets its
visibility to the inverse of the body. `MegaManBase.flickerTmrHandler:2103`
keeps the splash opposite the current body visibility. The character's
take-damage-end event destroys the splash.

Three separate damage sparks are created. They follow source NX plus
-24,0,+24 Flashpx and source NY-height plus -8,-14,-8 Flashpx. Those offsets
are not multiplied by facing. Their source animation ticks every130ms and
each destroys itself on passing its `damageSparkEnd` frame. Their visibility
does not alternate with body/splash. Effects choose the actual Mega Man or
Bass simple-graphics skin. The unused50ms splash constant must not replace
the active70ms character flicker timer.

## Immutable v26 negative observations

`megaman-injury-probe.lua` and `bass-injury-probe.lua` observe real body
injury in the explicit flat arena used by the validated contact fixture.
They do not write injury outcomes, timers, control flow or program counters.
Both characters and mappers reproduce both facing-direction negatives:

| State two hardware frames after injury | Source | v26 observed |
| --- | --- | --- |
| Facing right VX | -2/3 NESpx/update |0 |
| Facing left VX | +2/3 NESpx/update |0 |
| Recovery | moving recoil while level runs | native engine10, TimerControl253 |

Four logs and full compact CSV traces, including ROM hashes, are preserved in
`build/verification/mm-bass-injury-v26/summary.json`. A diagnostic PASS means
these known negatives were reproduced; it is deliberately not registered as
an acceptance test and does not claim injury fidelity.

## Required independent acceptance matrix

- MM and Bass, both facing directions and both mappers: real susceptible
  body injury, no Mushroom death, star and existing no-damage controls.
- Ground, airborne, water and surface cases: recoil direction/zeroed VY,
  regular gravity/fall cap,27-update lock and no steering/attack/jump/select.
- Recoil into side walls/pipes, page seams and off a platform edge: normal
  background collision without clipping or a global frozen world.
- New or previously held controls at recoil exit: normal input resumes at
  the source boundary, grounded VX is zero before resending, and no startup
  step is created during the locked phase.
- Second contacts during recoil, late invulnerability, and immediately after
  its expiration: no repeated upgrade loss until the source window ends.
- Upgrade/charge/weapon cleanup, Charge Kick exit and weapon actor state;
  actual source sound cue and completed-DMA hurt pose/effect pixels.
- Retained70ms body/splash opposite phase, independent three-spark130ms
  frames/offsets and complete cleanup at source end boundaries.
- Existing Mario/Luigi injury, ordinary guests, body protections, scripted
  flagpole/pipe/spring state and Water exact/performance controls remain
  separate regression requirements.

## Provisional v27 implementation and focused results

Root owns the shared source injury clock/input/visibility hooks. The scoped
`src/megaman_injury.s` helpers run in SAMUS, preserve caller X/Y/ObjectOffset,
use existing source audio mappings and share the common Q16 integration path.
Entering damage clears charge, slide/dash/paidkick and input-related motion
state. Recoil ends before movement on the update reaching450ms. Grounded exit
sets VX zero; airborne exit leaves it for normal movement/input handling.

An additional raw timeline check found that `MegaMan` frame14 `takeDamage`
retains stand's HRect matrix translateY -960twips (48Flashpx/24NESpx), while
frame15 `jump` uses -1100twips (55Flashpx/27.5NESpx). Recoil therefore keeps
the fixed24NESpx hurt waterline even airborne. The helper computes that
water state and enters the shared integrator at a zero-cost `IntegrateX`
label after the ordinary water check. Bass's gravity and fall cap are
initialized explicitly because its normal movement setup is bypassed.

The first immutable v27 passes56 actual-impact arenas across both characters,
directions and mappers, comparing1456 independent floating-source recoil
updates. This includes dry/wet ground and air, water surface, page seams,
26locked movement steps before the update27end, a separate75interval
no-damage counter, held controls, a moving unrelated world actor and caller
register/offset preservation. All176 body-contact controls also still pass.
Logs and fixture/source hashes are in
`build/verification/mm-bass-contact-v27/injury/summary.json`; contact logs are
in the adjacent `body-matrix.json`.

Two independently diagnosed boundaries remain for the next checkpoint:

- A deterministic controller-receipt fixture authors only raw/parsed input
  latches at the shared movement entry, representing fresh input arriving
  after the first lock mask. v27 correctly fails the source zero-action
  assertion. Root is adding an input guard after parsing. Ordinary controller
  fixtures still exercise real held input; authored receipts are separately
  labeled isolation fixtures, not a claim that an NMI was forcibly scheduled.
- The32-case profile-call matrix rejects v27's airborne Mega Man hurt body
  profile13: source frame14 requires standing12. The corresponding background
  profile must be3. Bass already retains standing3/12 and needs no new guard.

All six mapper/character/profile negatives are archived in
`build/verification/mm-bass-contact-v27/diagnosed-negatives/summary.json`.
The independent raw-SWF effect
oracle is `tests/fixtures/megaman-bass-injury-source-art.json`, generated by
`tools/audit/build_mm_bass_injury_source.py`; it contains both skins, source
hashes and the exact four effect frames. MM/Bass splash/sparks are identical
white pixels.

## Accepted v28 motion, input and geometry

The immutable v28 focused matrix passes all14 runs:56 ordinary injury arenas
and56 deterministic input-receipt arenas compare2912 numeric recoil updates;
the deterministic runs inject1456 input-only receipts. All64 body/background
profile cases and176 contact controls pass on both mappers. Raw-input arrival
does not create shots, weapon cycling, jumps or steering during locked recoil.
The shared parsed-input guard and MM-only standing hurt profile address the
v27 negatives without changing the source motion assertions. Evidence and
source/ROM hashes are in `build/verification/mm-bass-injury-v28/summary.json`.

## Source injury effects in v29

The private hurt-body composites use logical player-window banks81/82. Both
contain the same seven white-effect pattern pairs plus their unchanged hurt
body patterns. The packer first asserts that both logical slots are unused;
Samus's80 remains untouched. This leaves the shared world/weapon window free
for inventory icons and preserves the old physical CHR prefix. The resulting
ROM uses254/256KiB on MMC3 and246/256KiB on MMC5.

Only the10 existing hurt records and their bank-table entries relocate. The
independent immutable28→29 ROM comparison in
`tools/audit/check_mm_bass_injury_packing.py` verifies all88 referenced body
parts retain exact pattern bytes, palettes, flips and offsets; all198 other
MM/Bass records and every prior physical CHR byte remain identical. It also
checks that only logical map keys81/82 change. The compact report is
`build/verification/mm-bass-injury-v29/packing-invariants.json`.

The renderer follows the source70Flashpx display mask, distinct from its
48Flashpx collision HRect. Splash anchors at feet minus half display height,
retaining the fractional half-pixel phase; spark anchors use the three raw
unmirrored source offsets. The splash is inverse to the70ms body flicker,
while the three independent sparks advance every130ms and end after frame3.
At the450ms end event the ordinary buster/body bank is restored even when the
body is hidden. The effects stop before the first normal recovery draw.

`megaman-bass-injury-pixels.lua` compares completed hardware DMA OAM, mapped
CHR and actual PPU palette colors with the independent raw source masks. Each
theme/character wrapper covers both directions, outlines on/off, ground and
airborne fractional anchors. Every live effect phase is checked, concurrent
private Super Arm pickup pixels remain intact, and clean recovery frames
cannot retain the private hurt bank. These are explicit isolated art arenas,
not controller-playthrough evidence.

All58 focused v29 runs pass on both mappers. The16 art wrappers cover128
actual-impact cases,10043 source-DMA images,18168 hardware parts,3190 concurrent
pickup images and9308 clean recovery frames. The motion/input/profile/contact
matrices retain the v28 counts and assertions. Special/armor, Bass movement,
normal busters, pickup art, lone Bowser and every Water exact oracle also pass.
Eight art wrapper names are now registered in `tools/verify.py`. Source/ROM
hashes and all58 logs are archived under
`build/verification/mm-bass-injury-v29/summary.json`; aggregate art counts are
in the adjacent `art-totals.json`.

Water performance bounds remain unchanged; expansion still has measurable lag:

| Mapper | Character | Orbit DMA / hardware frames | Expansion DMA / hardware frames |
| --- | --- | --- | --- |
| MMC3 | Mega Man |100/100|45/63|
| MMC3 | Bass |99/100|40/62|
| MMC5 | Mega Man |100/100|58/62|
| MMC5 | Bass |100/100|56/62|

These results accept the scoped injury implementation and preserved ability
controls. Full roster integration, real MM/Bass routes through2-2 and final
audio/video capture remain separate requirements.
