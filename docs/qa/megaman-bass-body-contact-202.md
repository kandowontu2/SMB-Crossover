# Mega Man and Bass body contact: pinned Crossover2.02 audit

This records a pinned source audit, the resulting body-contact correction and
isolated ability verification. It does not claim a controller playthrough clear
or final recording.

The pinned SWF is SHA256
`6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af`.
All cited ActionScript files are under
`reference/crossover2/extracted/scripts/com/smbc/`.

## Source rules

| Situation | Source result | Evidence |
| --- | --- | --- |
| Ordinary MM/Bass body contact from any side, including descending | Hurt unless star/hurt invulnerability or a shell exception applies; no normal stomp/bounce/one-hit kill | `characters/Character.as:546,1776` and `enemies/Enemy.as:301` |
| Mushroom, ordinary slide/dash, slide jump, double jump, shooting, carried brick, Hard Knuckle startup, Pharaoh balloon, Water Shield or Rush | No additional body protection override | `characters/base/MegaManBase.as:1464` is the only MM/Bass `hitEnemy` override |
| Funded Charge Kick slide/dash against an Enemy body | Call `landAttack`; skip ordinary injury on every contact side | `MegaManBase.as:1216,1464` |
| Charge Kick exhausts its final4 energy at activation | Keep its paid attack-slide state until slide ends or weapon changes; do not require remaining ammo | `MegaManBase.as:1222,1226,1466` |
| Charge Kick vs susceptible body |75 damage on a newly entered contact, with MM hit-enemy cue; no stomp bounce | `data/DamageValue.as:50`, `MegaManBase.as:596,1492`, `Character.as:973` |
| Charge Kick vs armored Beetle/Bullet Bill | No damage; still protected from body injury; graphic persists; no projectile deflection cue | `Character.as:973,668`; `main/AnimatedObject.as:676`; `enemies/Beetle.as:31`; `enemies/BulletBill.as:61` |
| Continued overlap with same target | No second hit; a full no-contact update rearms a later contact | `Character.as:989,1146` (`C_HIT_DCT`/`L_HIT_DCT`) |
| Switch away from Charge Kick | Immediately clear attack-slide status. Switching back during the old slide must not restore it without a newly paid slide | `MegaManBase.as:692` |
| Leave slide state | Destroy charge-kick graphic; ordinary contact rules resume | `MegaManBase.as:1169,1189` |
| Lava fireball/Podoboo, Bowser fireball, firebar, hammer | Enemy Projectile contact still injures during Charge Kick; these are not Enemy-body contacts | `Character.as:2694`; `projectiles/LavaFireBall.as:7`, `BowserFireBall.as:14`, `FireBar.as:14`, `Hammer.as:8` |
| Star contact | Keep existing star defeat precedence | `Character.as:1782`; `Enemy.as:825` |
| Stationary Koopa/Beetle shell or shell no-hit timer | Ordinary Character contact does not injure; Enemy side initiates shell kick | `Character.as:1782`; `KoopaGreen.as:579,465` |

The source has no Top Spin weapon/attack symbol or obtainable upgrade. Both
MM/Bass weapon lists contain Charge Kick, and the shared class calls its
body-safe state `attackSlide`; inventing a separate Top Spin would not be a
2.02 behavior fix.

The base Character has aggressive pierce strength0 (`Character.as:668`);
armored enemies have passive pierce5. `LevObj.isSusceptibleToProperty` accepts
only aggressive strength >= passive strength. Charge Kick therefore does not
inherit Hard Knuckle's armor penetration. The source body nonpiercing callback
is empty, rather than a projectile bounce/destruction handler.

## Baseline ROM discrepancies and integration boundaries

`collision.s:ChkForPlayerInjury` sends every guest through native positive-VY,
vertical-overlap and `StompTimer` shortcuts to `EnemyStomped`. That grants MM
and Bass ordinary native stomps despite their source `canStomp=false`.

The current SS_KICK19 is a virtual actor centered at playerX+8/playerY+26.
It bridges damage type52 (75 damage), but there is no matching MM/Bass body
contact protection. Its `RgShotHits` mask lasts for the entire actor lifetime,
whereas source Character contact re-arms after separation. Armor also routes
that virtual actor through projectile deflection/destruction, unlike the
source Character's harmless nonpiercing callback.

A guest contact wrapper must preserve native Mario/Luigi, the existing custom
Scrooge pogo path, stars, stationary shell kicking, frozen-enemy platform
handling and explicit Samus protections. Source enemy projectiles represented
as NES enemy slots need explicit classification: native Podoboo and Bowser
flame must not accidentally gain Charge Kick body protection.

For MM/Bass the paid-start receipt plus actual active slide/dash state and
current selected Charge Kick are the protection predicate. Current `SsKick`
alone needs care: it can remain set after `InvSelected` becomes0 because the
normal reset is bypassed. Clear it when changing weapon, rather than allowing
switch-away/switch-back to revive an unpaid attack slide.

Use one authoritative body-contact damage event, with shared duplicate-hit
receipts if the existing virtual Kick enemy pass remains. Otherwise the same
native overlap can take75 twice. A body contact outside the virtual foot
rectangle still needs source protection and damage. Protected overlap remains
protected even if the target is armored, still flashing, or already hit in the
same continuous contact.

## Independent v24 baseline observations

`tests/megaman-bass-body-contact-probe.lua` and its Bass wrapper use actual menu
selection and ordinary Down+A. They create explicit flat terrain/actor/initial
health fixtures, record native contact dispatch, and never patch outcome,
registers, OAM, ROM, or program flow. The diagnostic's PASS only means recording
completed, and is not acceptance of source behavior.

The same two contradictions reproduce for both characters on both mappers:

1. A descending Goomba contact enters native `EnemyStomped` with source75 HP,
   player power1, and no injury.
2. A funded Charge Kick consumes the last4 energy, hits Koopa100→25, then its
   actual body overlap enters `InjurePlayer`: power1→0 and engine10 while MM
   slide/Bass dash remains active. Source says the paid slide is body-safe.

ROM hashes and all four logs are archived in
`build/verification/mm-bass-contact-v24/summary.json`. This supplies negative
controls for the shared wrapper fix; it does not justify changing any attack
constant or physics.

## Required acceptance cases

- Both MM/Bass, both directions, both mappers: ordinary descending/rising/side
  body contacts, all power forms, injury invulnerability, and nonzero stale
  `StompTimer`. No ordinary stomp, bounce, enemy HP loss or defeat.
- Ordinary slide/dash, Charge Kick selected while standing/jumping, and an
  empty-energy slide all retain ordinary injury.
- A controller-created Charge Kick funded with exactly4 energy consumes it
  once, retains body protection at0 energy, deals75 to Koopa100→25, and stays
  protected during the target's flash/continuous overlap.
- Leaving and re-entering the same living target produces another75 hit after
  one full no-contact update; continuously touching it does not.
- Armored Beetle/Bullet Bill survive unchanged, player remains unhurt, visual
  kick survives until normal slide end, and no projectile deflect cue is queued.
- Piranha, Spiny and the real Bowser body follow source body rules. Bowser's
  duplicate resolves to its primary HP once; a separate overlapping target
  maintains its own receipt.
- Podoboo, Bowser flame, firebars and hammers still injure a non-star Charge
  Kick user. Stars and explicit hurt invulnerability retain their existing
  behavior; do not globally suppress `InjurePlayer`.
- Weapon switch away/back cannot preserve/revive the paid slide attack state;
  slide exit ends protection immediately.
- Stationary shell kicking, frozen-enemy platforms, Mario/Luigi stomps,
  Scrooge pogo and Samus source protections remain independent positive controls.

## Scoped implementation staged after the source audit

Root authorized changes only after the source findings and v24 negatives were
reported. `special_weapons.s` now distinguishes receipt0 (no/fresh slide),1
(paid attack slide), and2 (ordinary/cancelled slide). Leaving the weapon during
an active slide closes its receipt; switching back cannot buy another attack
within the same slide. Funding consumes4 once and retains protection at0 energy.
The Kick actor remains graphical; actual body contact owns enemy damage.

`MegaKickBodyDamage` accepts the canonical target in X and temporarily bridges
source75-damage type52 into the existing damage/defeat/sound path. It preserves
all four primary projectile types, MmSlot, RgSlot, ObjectOffset, MmEnemySlot,
GuestBodyAttack and X/Y. Armored bodies skip damage and projectile-deflection
cues. `SpecialEnemyHit` bypasses its projectile lifetime mask only during the
isolated body bridge; root's shared previous/current contacts own cadence.
No extra SRAM was allocated by these scoped MM/Bass edits.

Root owns the shared wrapper and is moving guest body checks to every actual
physics update while retaining native Mario/Luigi cadence. A protected body
must not prevent a surviving stationary Koopa/Beetle shell from entering the
native kick path; a shell defeated by the attack must not be kicked or passed
to injury afterward (`KoopaGreen.hitCharacter:579`).

`tests/megaman-body-contact-202.lua` and `bass-body-contact-202.lua` wrap the
independent common fixture. It has22 cases in two directions (44 per character),
including native Bowser rear-only/both-halves contacts, source ordinary-shell
kick, paid Koopa shell100→25 plus kick, armored shell100 plus kick, and an
already wounded shell25 defeated by75 without kick/injury. The fixture pins
only explicit arena/actor initial state and, for Bowser, AI placement/facing;
actual body bounds, duplicate dispatch, attack, damage, defeat and SFX execute
normally. It counts the real native body halves reached and records health at
shell-kick/injury transitions, avoiding false positives from later cleanup.

All four originalv24 acceptance negatives reject its ordinary stomp behavior.
Unaffected selected-standing/empty-dash and hostile-fireball controls have been
exercised independently on v24 as fixture validation.

## Immutable v25 positive verification

The full44-case fixture passes for both Mega Man and Bass on both mappers:
176/176 cases. The two wrappers are now registered in `tools/verify.py`.
Logs, assertions and exact ROM hashes are preserved in
`build/verification/mm-bass-contact-v25/body-matrix.json`.

The authored flat arena locks its camera and clears pending area-parser work.
This prevents ordinary level streaming from replacing the test floor with a
real pipe during long sequential fixtures. Before that isolation fix, a
correctly kicked shell turned around at the newly streamed wall and injured
the player after its legitimate slide had ended. Fresh isolated shell controls
passed, and the completed trace identified the wall reversal; no runtime fix
was made for this fixture contamination.

Another28/28 regression runs pass across both mappers, archived under
`build/verification/mm-bass-contact-v25/controls/summary.json`: special pools,
special enemy rules, MM/Bass armor, Bass source movement,3216 source SFX register
comparisons per mapper, five Water exact oracles, lone Bowser/Bullet Bill and
Water performance. Water oracle coverage retains40960 signed orbit positions,
21504 expansion positions,1760 OAM pieces and2016 canonical corner outcomes per
mapper, plus actual left-facing summon/reveal behavior.

Water actual completed OAM DMA in100 full-orbit hardware frames is100 for Mega
Man on both mappers,99 for Bass MMC3 and100 for Bass MMC5. Full eight-ball
expansion completes44/62 (MM MMC3),58/62 (MM MMC5),42/62 (Bass MMC3),60/62
(Bass MMC5). All existing CPU/DMA/lag thresholds remain unchanged. Expansion
still has skipped display frames and is not described as lag-free.

ROM SHA256:

- MMC3: `d4b6fa258c28092d5533e6406897c3074bb53e819602ea34a8cbc466ff0252ac`
- MMC5: `dff6b1fa006f0362dff47bb92b36b002a776ae593f3a821bcac5a8823f3d5ccd`

Body-contact acceptance does not establish source-correct injury recovery.
The separate audit in `megaman-bass-injury-202.md` records the remaining native
shrink/freeze mismatch, which must be resolved before final parity claims.
