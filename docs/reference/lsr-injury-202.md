# Link, Simon and Ryu injury audit

Pinned 2.02 hashes and hurt HRect matrices are saved in
`lsr-injury-source-202.json`. Source motion, art and audio component matrices
pass both provisional34-b mappers. A separate independent geometry query
exposed the prior Link14px table error. Its two-byte final34 correction now
passes44 profile queries and actual Link motion/roof/head tests on both mappers.
This is component evidence, not final build acceptance or a stage proof.

| Rule | Link | Simon nonclassic | Ryu |
| --- | --- | --- | --- |
| Attacker-relative VX, Flash px/s |500|150|150|
| Initial VY |preserve|-300|-385|
| Initial grounded state |preserve|force air/jumped|force air|
| Facing |toward attacker|toward attacker|toward attacker|
| End |strict32 NESpx overshoot, matching wall,1200ms fallback|landing|landing|
| Normal/submerged gravity |1300/500|1500/750|1400/500|
| Final fall cap |800; water-room500|none|700|
| Recovery immunity |1250ms=75 updates|same|same|
| Recoil appearance |opaque plus palette cycling|opaque|opaque|
| Recovery appearance |palette cycling continues|source alpha0.65|source alpha0.65|
| Hurt HRect height, NES |15|25|25|

Source: Link.as1261-1338, Simon.as983-1050, Ryu.as1342-1425,
Character.as2198-2244/2404-2417, AnimatedObject.as318-371.
All disable input/nonInteractive, lose mushroom/upgrades, and keep the world live.
No class calls flickerStart. Link never assigns recovery alpha.

Link keeps VY/onGround, cancels flip/thrust, and returns before ordinary
checkState/movePlayer. Its endpoint is exact fractional start nx+64Flashpx;
strict overshoot is checked before movement. Only overshoot clamps position;
72 updates is fallback. Matching wall contact ends during collision. Released
jump friction is retained but bypassed until recovery. Common submerged-ground
90 speed cap and water250 falling pre-cap apply before gravity.

Simon cancels attacks and uses ordinary gravity; DAMAGE_BOOST_GRAVITY300 is
unused. Ryu detaches from walls and retains jumpSlash through upgrade removal;
hitEnemy840-848 can still landAttack during recoil. Landing clears it and
requests RyuJump. Noninteractive head bumps preserve bricks/question blocks
(Brick.hitCharacter240), while physical collision and hazards remain.

The independent Link table audit is saved under
`build/verification/guest-injury-v34-migration/link-hrect-source-audit.json`.
All playable frames1..38 share HRect sprite14/shape13, scaleY3.749939 and
translateY-600twips: nominal height15 and exact top-15NESpx. Ending frames39..45
are15.5 nominal and have no ordinary player control. Existing native Link
box18/headadder9 used top18 (height14); the final34 correction changes only
those two Link-exclusive Y entries to17. Horizontal, side and feet entries stay
intact. Simon/Ryu hurt matrices are50Flashpx high (frames17/62), body16/head7.

Simon.takeDamageStart forces airborne. Simon.landOnGround immediately calls
takeDamageEnd. The actual native head-query spy passes throughout all28 injury
arenas: every locked Simon query is airborne, and post-collision landing ends
hurt before another query. No runtime workaround is added for a fabricated
state0+locked Simon. The fixed hurt body16 remains tested in reachable states.

`src/lsr_injury.s` exports Prepare, Start, Movement, Tick, AfterCollision, End
and Palette in SPECIAL_ROSTER. Helpers preserve X/Y/ObjectOffset. Prepare runs
before InventoryHurt and returns bit0 (Link friction/Ryu Jump Slash), bit8
(source jumped). Start saves A before the6502 PHX/PHY macros clobber it.
Link uses5 persistent bytes (four endpoint bytes plus flags), initialized on
start. Simon/Ryu use a nonzero lock sentinel until landing. Tick and
AfterCollision return carry set for source recovery. Shared recovery starts
75 protection on that same update.

The physical raw controller latch stays intact during LSR recoil; parsed
actions are masked, existing projectiles/effects continue, and new attacks are
blocked. Recovery reseeds physical histories. Source sendPlayerBtns restores
flags and does not synthesize held A/B press events.

Two source details matter. Link.takeDamageStart requests label `walk`, but
the timeline has `stand`(1), `walkStart`(2), `walkEnd`(3), with empty suffixes.
CustomMovieClip.gotoAndStop maps the missing label to int0 then clamps frame1;
actual hurt art therefore stays stand. Character.groundAbove assigns
VY=100Flashpx/s only while jumped; otherwise it retains VY. Simon damageBoost
sets jumped; Link retains it and Ryu wall detach sets it. Real native ceiling
receipt is translated post-collision to100/120 or retained VY, with Sfx_Bump.

Link's source30Hz replacement palette uses two logic updates per phase, row
order2/3/1. NES rows are16/30/27,01/30/21,30/16/0c; only$3F11..13 change.
Source-global phase becomes injury-anchored; colors follow nearest NES colors.
Simon/Ryu are opaque during recoil; source0.65 recovery alpha is explicitly
approximated by13/20 temporal visibility. This is not exact composited RGB.

LinkTakeDamage(Zelda NSF17) and SimonTakeDamage(Castlevania3 NSF70) are pure
DMC. The old four-channel generator rejected their lack of audible tonal
channels; exact mapped captures preserve161/193 bytes, rate15, DAC0, noIRQ/noLoop.
Evidence: `build/verification/lsr-injury-dmc-audit-a/summary.json`. Generator
appends IDs21/22 as64-aligned fixed DMC and23/24 as tonal RyuTakeDamage
(NinjaGaiden35)/RyuJump(33). Existing20 IDs are unchanged. DMC owner2 reuses
the shared hardware completion guard, no new SRAM. The mixer normalizes DAC0
on completion, an explicit endpoint adaptation shared with Water Shield.

Fresh immutable28 and33 actual-Spiny source-entry negatives are retained.
Provisional34-a exposed a real missing wall collision-bit receipt; root's
34-b correction passes matching-wall motion/source equations. Latest28-arena
motion/protection matrices pass both b mappers for all three characters, as do
64 endpoint cases,16 actual-DMA primary-body composites, DMC lifecycle and all
24 source streams. Body pixel evidence excludes independent shield/whip
submovie composites. Scoped packet:
`build/verification/lsr-injury-v34-focused-evidence.json`.

The old native scripted-injury fixture now retains six profiles0/6/7/8/11/12;
4/5/10 are replaced by the source fixtures. Exact original and migration
hashes remain in `build/verification/guest-injury-v34-migration`. The migrated
six-profile fixture passes both b mappers. No final recordings are accepted
for this provisional injury build.

Follow-up source limits established after fixture freeze: the separate raw
normal-frame audit is `build/verification/lsr-normal-hrect-readonly-v34.json`.
Simon normal stand/whip/throw is30px, rising jump25, falling/after-air-whip
stand30, crouch15.75. Ryu ground stand/walk/attack is27, airborne/wall/climb25,
crouch15.75. Current34 intentionally retains older31/13 normal tables; the
new normal-query controls establish preservation, not source identity.

I initially missed Simon.groundAbove966-978 changing the frame during hurt.
Unless ST_ATTACK, it selects FL_JUMP_FALL=`stand`, recomputes the30px HRect,
and places the player under the ceiling using that height. During hurt,
checkState returns early and retains that stand frame until recovery.34 still
uses fixed25 hurt geometry/art after a ceiling hit; its current fixed25 oracle
does not prove this transition. This is an explicitly open source behavior
gap for a subsequent coherent batch; frozen34 runtime/tests remain unchanged.
