# Link, Simon and Ryu enemy effects in Crossover2.02

Pinned source is `reference/crossover2/extracted/scripts/`; the source SWF has
SHA256`6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af`.
This audit describes enemy effects, separately from player injury motion.

| Attacker | Stop | Stop animation | Flash | Enemy knockback |
| --- | ---: | --- | ---: | --- |
| Link sword/thrust, shooting sword, arrow, bomb |400ms|yes|400ms|none registered|
| Link ordinary/magic boomerang |3000ms|no|none|none registered|
| Simon whip and thrown weapons |400ms|yes|none|none registered|
| Ryu sword, Jump Slash and thrown weapons |none|no|400ms|none registered|

The character defaults are registered in Link.as367..375, Simon.as331..338
(`HIT_DEL=400` at293), and Ryu.as383..390. LinkProjectile.as72,
SimonProjectile.as93 and RyuProjectile.as120 copy their character defaults.
LinkBoomerang.as60 instead registers its own Stop3000 with stopAnim=false,
pierce10, and no Flash.

Link's constructed `knockBackFx` is dead scaffolding. Its direction setters
do not register a property; `knockBackProp` appears only at its declaration in
the entire pinned script tree. LinkProjectile likewise constructs/sets an
unregistered effect. The active player injury boost in Link.takeDamageStart
is a separate behavior and must not be confused with this unused enemy code.

`Enemy.checkAttackProps()` first checks invulnerability, then iterates
`StatusProperty.PROP_ORDER`: PIERCE, STOP, KNOCK_BACK, INVULNERABLE,
TRANSPARENT, FLASH. A failed pierce returns before later effects. A resisted
STOP alone does not reject damage or FLASH. Bowser has passive STOP7 and
Lakitu STOP10; strength0 character stops cannot freeze them. Ordinary enemies
accept strength0. An enemy killed by the attack removes all status effects.

`StatFxStop` stops physics and own timers; its true stopAnim also stops
animation. A new Stop replaces an existing one only if its full duration is
greater than the old remaining time. Applying an accepted Stop removes an
existing Flash. Link's normal attack then applies a new Flash afterward,
because FLASH follows STOP in property order. Thus Link's Stop+Flash coexist.
An equal or shorter rejected Stop does not remove the existing Flash.

`StatFxFlash` starts at palette phase1 and refreshes both phase and duration on
replacement. Its interval is `AnimationTimers.DEL_FAST=int(1000/30)=33ms`;
the NES adaptation rounds this to2 completed60Hz updates.400ms is24 updates;
3000ms is180. Flash is a palette effect, not target invulnerability or STOP.

The authoritative original-skin palette sheet is
`reference/crossover2/images/308_com.smbc.graphics.skins.BmdInfo_palette_000.png`,
SHA256`4279c9f0878822ba75043fc966c551af59237b44a6e628f273a8caeee603e194`.
PaletteSheet.getXPos gives enemy theme0 column0 at x24; subsequent palette
rows lie at x24+68*column. The Goomba item1 Flash rows are:

| Extracted row | Default brown becomes | Default skin becomes | Default black becomes |
| --- | --- | --- | --- |
|0|#fc9838|#fcd8a8|#d82800|
|1|#00a800|#fcfcfc|#fc9838|
|2|#d82800|#fcfcfc|#fc9838|
|3|#000000|#fcbcb0|#c84c0c|

The initial applied sequence is1,2,3,0, then repeats. Other enemy items remap
their own default RGB order. Four independently phased Flash palettes plus
ordinary enemies and the layered player exceed the four NES sprite palettes;
an adaptation must document its hardware palette mapping instead of claiming
literal RGB parity from timer correctness.

The immutable25 negatives are
`build/verification/link-simon-v25-focused-effects-negative-d/summary.json`.
Actual controller B hits cause75 damage to a surviving live enemy; immediately
before its native movement, Link/Simon incorrectly have12 STOP updates rather
than24, and Ryu incorrectly has12 rather than0, on both mappers. Ryu uses the
source crouch slash to reach a standing short Goomba; the high standing sword
correctly misses that low target. Earlier standing-target watchdog probes are
preserved and excluded as evidence of the effect contract.

The profile/contact batch already passes all17 focused wrappers on both
immutable25 mappers. These effect negatives intentionally describe additional
work and do not revoke those movement/damage/order positives or claim complete
enemy-effect parity.


## Effect batch evidence

All6 immutable27 full hit trajectories pass `focused-effects-first-c`:36 native
updates, source STOP24/0, FLASH24, own timers, frozen/resumed pose, actual OAM/DMA
and unchanged global sprite palettes. Earlier failures were draw-entry/DMA phase
tagging and hidden stale OAM counting; no runtime patch fixed those fixtures.
`effects-properties-a` passes actual-Select boomerang180 updates with continuing
animation plus18 Link/10 Simon property arenas, both mappers.7 Ryu arenas pass
`effects-properties-d`; prior miss came from resetting previous-button latch
while the previous case still physically held B. All34 prior movement/contact/
weapon slots pass `focused-regression-a`.

Hardware mapping source rows0/1/2/3 uses existing palettes2/1/2/3; rows0 and2 share
red/orange. No fifth palette, global writes or simultaneous player/pickup
recoloring. Exact RGB parity is not claimed. Phase timing is two completed
updates. Actual-DMA `effects-properties-b` confirms both27 Bowser rears miss
phase2 (normal1 versus primary2). Pending29 validates/follows its primary and
applies palette once after completed actor draw, avoiding common per-tile cost.
Its independent positive is pending; no route/capture completeness is claimed.


## Immutable29 renderer acceptance

`build/verification/link-simon-v29-focused-effects-accept-a/summary.json`
passes all16 slots on both mappers: the3 complete source hit trajectories,
180-update animated boomerang STOP, actual-DMA Bowser front/rear FLASH and all3
replacement/resistance/armor/death property wrappers. The Bowser rear negative
on27 remains archived. This accepts the scoped effect/renderer batch; it does
not complete the held Link/Simon/Ryu injury migration or gameplay routes.

## Immutable31 empty-effect CPU gate

31 preserves every nonzero effect and cleanup path but skips the bank call
when all6 STOP,6 FLASH and6 frozen-pose bytes are zero. The post gate runs
after LinkDeferredThrust, so effects created by the deferred source attack
are processed in the same completed update. No new persistent mask or SRAM
is used. All662 isolated cleanup/deferred arenas match30 byte-for-byte across
30 observed state fields, including paused, dead, absent and stale-pose cases.

All48 scoped31 slots pass after the source trajectory observer is moved from
the intentionally skipped zero-effect helper to the always-executed native
GetPlayerOffscreenBits post tail. No timer, trajectory, pose, damage or DMA
assertion was removed. The original two observer-anchor negatives remain
archived; all16 effect wrappers were rerun from one frozen corrected source.
Bound results and exclusions are in
`build/verification/scoped-pipeline-v31-evidence.json` and
`build/verification/lsr-effects-gate-v30-v31-comparison.json`.
This is CPU admission/cleanup acceptance, not injury or route completeness.
