# Requested third-row roster: source controls and implementation contract

Research only,2026-10-22. No new character is implemented by this document. The
24-page player's guide remains the immutable current-HR edition. These are
custom additions to this ROM, not characters with official Crossover1.0/2.02
profiles. Original-game facts, explicit user requests, and proposed adaptations
are separated below. Manuals establish controls/progression, not exact
acceleration, attack timing, hitboxes, invulnerability frames or sound register
traces. Those require original-game captures or pinned program analysis.

## Primary sources retained/read

Local primary PDF hashes/URLs are recorded in
`build/player-guide-agent/roster-research/primary-manuals.json`. Bounded contact
sheets and selected full source pages were visually inspected. The user's
Gradius and Pit sheets are retained unchanged under
`reference/user-sprites-2026-10-22/manifest.json`.

| Profile | Primary evidence |
|---|---|
| Kirby | [Nintendo printed manual](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAAPE.pdf), printedpp9,13–21,26; [electronic controls](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAAPE_en.pdf), sections1,5 |
| Chip/Dale | [Capcom original booklet scan](https://www.digitpress.com/library/manuals/nes/Disney%20Chip%20'n%20Dale%20Rescue%20Rangers.pdf), bookletpp8–11, PDFpp5–6 |
| Little Mac | [Nintendo printed manual](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAATE.pdf), printedpp5,9; [electronic controls](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAATE_en.pdf), sections1,5 |
| Mike | [Nintendo electronic manual](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAAZE_en.pdf), sections1,6–8; [original booklet](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAAZE.pdf) |
| SMB3 Mario/Luigi | [Nintendo printed manual](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAACE.pdf), printedpp6–9,24; [official suits explanation](https://www.nintendo.co.jp/wii/vc/vc_smb3/vc_smb3_05.html); [official actions](https://www.nintendo.co.jp/wii/vc/vc_smb3/vc_smb3_06.html) |
| Vic Viper | [Nintendo-hosted Konami manual](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NABRE.pdf), printedpp4–7; [electronic manual](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NABRE_en.pdf), sections1,3,5 |

## Kirby — Adventure controls, separate health/copy state

**Original:** A jumps; Up inflates and A flaps; B inhales while normal, spits a
star when something is held, and emits an air pellet while inflated. Down
swallows held contents. Crouch plus A/B slides. Select ejects a copied ability;
one active copy prevents inhaling another enemy. Damage also ejects it as a
recoverable star. Water has swimming and a water-gun attack. The printed health
display explicitly starts at six vitality bars. Some enemies grant no ability;
multi-enemy swallowing can yield a mixed result. These are original restrictions,
not evidence for SMB enemy powers. [Nintendo manual](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAAPE.pdf)

**User requirement:** six life units; Mushroom/Flower heal; inhale, Down swallow,
spit star; a distinct copied attack for each eligible SMB enemy.

**Proposed port contract:** keep `Health0..6`, `CopyKind`, `MouthEnemy`, inflated
state and attack phase separate from native `PlayerStatus`. A held enemy is
captured once, removed from the native pool through its ordinary cleanup, and
converted either to a spit-star projectile or to the enemy-copy table entry.
Select discards the copy; it must not run the old generic weapon-cycle handler.
Show the copy icon/name and six health segments without changing world palettes.
Mushroom/Flower healing amount is a port balance choice; cap at six and retain
proper emerge/collect animations/SFX. A healing pickup must not select a copy.

SMB-family copy assignments are **new game design**. A concrete distinct-family
proposal is Goomba=ground charge, greenKoopa=rolling shell, redKoopa=returning
shell, Buzzy=armored guard, HammerBro=hammer, Blooper=water jet, grayCheep=water
shot, redCheep=wave shot, Paratroopa=high jump, Lakitu=cloud hover, Spiny=needle,
Piranha=bite, Podoboo=flame, BulletBill=bullet dash. Normalize cannon/frenzy spawn
IDs to the same Bullet Bill family; retain genuinely different color/family
entries where the user wants distinct copies. Firebars, platforms, pickups and
script actors are not swallowable enemies. Boss swallowing/defeat-star behavior
needs an explicit authored rule; do not accidentally erase Bowser's controller
or rear duplicate. A copy table requires positive coverage for every native
ordinary-enemy family and an explicit rejection entry for every other ID.

## Chip / Select Dale — authentic carried-object interaction

**Original:** A jumps; B picks up or throws; Up+B throws upward; Down crouches,
and hides in a held box. An eligible enemy touching the box is defeated and
consumes it, with exceptions. Down+A drops through a ledge. Each Ranger starts
with three hearts and briefly becomes invulnerable after damage. Select displays
status; Start pauses. [Capcom booklet](https://www.digitpress.com/library/manuals/nes/Disney%20Chip%20'n%20Dale%20Rescue%20Rangers.pdf)

**User requirement:** Chip portrait, Select toggles Dale while highlighted;
original box carry/throw/hide toolkit.

**Proposed port contract:** same physics/toolkit, two genuine body/palette
variants; selection alternate is a menu action only. During play retain B's
three-state interaction: empty→pick up, carrying→throw, carrying+Down→hide.
Crates need a real world object and a source coordinate receipt, not an
unrestricted attack generated from thin air. Add explicit crate supply points
or an authored block-to-crate conversion policy; this is SMB adaptation, not a
claim that SMB terrain was crates in Rescue Rangers. Protect ground, pipes,
question-block payloads and helper actors. Hiding requires a separate box
collider, valid enemy-type mask and one-shot consumption. Down+A drop-through
applies only to native one-way ledges/platforms; never to solid ground.

## Little Mac — running art with an acknowledged platforming adaptation

**Original:** A/B are right/left punches; Up changes them to jabs. Down guards,
double-Down ducks, and Left/Right dodges. Start spends a star on an uppercut.
The star cap is three; taking a punch loses one and knockdown loses all. Hearts
are punching stamina, distinct from the health/stamina meter.
[Nintendo booklet](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAATE.pdf)

**User requirement:** use the training-cutscene running sprite; Flowers supply
up to three super-punch stars.

**Proposed port contract:** A must remain platform jump and Start must remain
pause, so use B for a jab, Up+B for a high jab, Select for a one-star uppercut,
and Down for a short guard/duck. These mappings are intentional adaptations.
Running/air steering has no side-scrolling Punch-Out source equivalent; do not
advertise literal original physics. Keep star count0..3 distinct from HP or
native growth tier. A Flower adds a bounded star; an empty special press causes
neither an attack nor unsigned underflow. The uppercut's active collision window
and source animation must agree, and guarding needs a typed attack mask rather
than blanket invulnerability. Cutscene running and ring fighting are different
source views; obtain authentic directional/attack frames before promising a
complete animation set.

## Mike Jones — original weapon names and health gates

**Original:** A jumps, B attacks, Select cycles weapons; Start opens the weapon
selection pause. The basic Island Yo-Yo upgrades to Shooting Star at six filled
hearts and Super Nova at eleven. Special weapons include fire, slingshot,
baseball bat, bola, baseball, Super Laser Gun, Mega Laser Gun, spikes and Twin
Cross-Blades; the latter can split when B is pressed after the throw. Super
Laser holds99 shots and Mega Laser20. Small hearts heal one, medicine five,
and a big heart raises capacity then fills it. Nintendo's electronic edition
renames the first weapon Island Star, so keep the NES Yo-Yo naming when using
the original source. [Nintendo manual](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAAZE_en.pdf)

**User requirement:** original Mike weapons, upgrades and life system.

**Proposed port contract:** separate health/current capacity from equipment
ownership; the six/eleven tests concern filled health, not just acquired capacity.
Specify half-heart versus whole-heart damage units before choosing HP storage.
Store each limited weapon's ammo and keep Select cycling among usable weapons,
returning to the basic weapon. A health drop must reduce the effective basic
weapon correctly. Use a real extend/retract attack, not a permanent long
rectangle; its enemy/block hits share one per-swing receipt. Source grid-based
top-down movement cannot literally remain unchanged in an SMB side view; retain
the source jump/attack identity while documenting that adaptation. Item spawn
and special-weapon acquisition points must be authored; they are not supplied by
the original SMB maps.

## SMB3 Mario / Select SMB3 Luigi — complete forms, separate from SMB1 slot

**Original:** B runs, attacks and holds a stunned shell; releasing it kicks.
A controls jump/swim, with hold duration affecting jump height. Raccoon/Tanooki
have tail attacks, falling control and P-meter flight; Tanooki adds Down+B
statue protection. Frog changes swimming and cannot crouch. Hammer throws
hammers and its crouch protects against enemy fireballs. Normal powers include
Super, Fire, Raccoon, Frog, Tanooki and Hammer. Starman is temporary invincibility;
Magic Wing is a separate flight modifier.
[Nintendo actions](https://www.nintendo.co.jp/wii/vc/vc_smb3/vc_smb3_06.html),
[suits](https://www.nintendo.co.jp/wii/vc/vc_smb3/vc_smb3_05.html),
[original booklet](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAACE.pdf)

**User requirement:** separate SMB3 portrait with Select Luigi alternate;
all normal SMB3 powers, randomized replacements at Flower blocks.

**Proposed port contract:** two cosmetic identities share one SMB3 movement/form
engine; preserve the existing SMB1 Mario/Luigi separately. Record the actual NES
physics profile before adding a distinct Luigi jump. Native Mushroom still
grows small→Super. Flower sites spawn an actual randomized Fire/Leaf/Frog/
Tanooki/Hammer pickup, with its proper icon, rise, collection and form-change
sequence; this random distribution is a requested ROM rule, not SMB3 behavior.
Include P-Wing as an explicit modifier if full power coverage includes it.
Do not confuse the map-screen Hammer item with the Hammer Suit, and do not
replace ordinary level items with map-only flute/anchor/cloud actions. Kuribo's
Shoe is a vehicle/enemy interaction, not another ordinary form in this list.
Keep tail, fireball and hammer target masks distinct; statue protection must
expire and restore the exact prior form/foot position. Both Easy and Hard retain
SMB3's normal stomps because that belongs to the character's original toolkit.

## Vic Viper — NES weapon bar, two Options, native camera ownership

**Original:** the NES manual calls the ship Warp Rattler. A fires; B activates
the highlighted power-bar entry. Red capsules advance Speed→Missile→Double→
Laser→Option→Shield; Double and Laser exclude one another. Up to two Options
follow and duplicate the ship's acquired guns. The shield has a final-hit red
warning; blue capsules destroy weak on-screen enemies. Select is a title-menu
control, not the in-flight upgrade button.
[Konami booklet](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NABRE.pdf),
[electronic manual](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NABRE_en.pdf)

**User requirement:** full bar/weapons/Options/shield, autoscroll until native
end-of-level camera lock. User sheet449×141 is retained unchanged; original ROM
revision/palette provenance still needs verification.

**Proposed port contract:** keep original A=fire/B=buy to avoid an unnecessary
input swap. Use four-direction local ship motion plus one native camera owner;
worldX is cameraX+screenX, so camera advancement cannot also be integrated as a
second player movement step. Pause, death, pipe transit, area transition,
native end lock and flag/castle finish each suspend or transfer that owner.
Two Options use a bounded delayed-position queue and no body collision. A ship
plus two Options, shield and shots can exceed eight sprites per scanline; retain
the native rotating OAM budget, bound simultaneous shots, and collide lasers as
one interval per attack/target rather than every visual segment. Upgrade state,
capsule cursor, speed tier, Option count and shield hits are separate values.
Source exact speed tiers, shield durability/contact masks and option delay
require original-game measurement. Do not assume arcade four-Option rules.
Test narrow pipes, water,4-4/7-4 maze triggers and castle end locks explicitly;
flight/autoscroll does not remove native transports or level scripting.

## Shared implementation and capacity constraints

Preserve old IDs0..12. Use a profile+variant registry for new portraits, physics,
art, contact policy, health model, equipment model, menu alternate count and
audio. Dale/SMB3Luigi are presentation variants; do not duplicate physics/state.
Root has accepted seven positions in the added row, with other requested
characters/alternates audited separately. Its latest total is32 identities.

Dispatch new profiles before old `ExpandedMovement` indexes
`SelectedCharacter-CHARACTER_PIT` into seven-entry tables. The current inventory
has12 owners and8-bit `char*16` indexing: raw new IDs at/above16 wrap that index.
Use explicit equipment-owner mapping or a separate selected-profile inventory;
do not grow raw selected IDs through existing arrays without migrating callers.
New profiles do not acquire fabricated official1.0/2.02 differences. Retain their
source toolkit in both modes and apply the agreed Easy contact policy only where
meaningful; keep original SMB3 stomps in Hard as well.

Main HR SRAM is6000..7FFC, so appending even a modest character state slab would
overflow. Root's helper start is mapper-specific: MMC3`$736a`, MMC5`$7382`, with
the next original allocation fixed at`$7400`. Its current private91-byte helper
layout leaves59 bytes on MMC3 and35 on MMC5, before any separately proven
unused-field removals. Use the35-byte common bound rather than assuming the
MMC3 gap is available on both. Prove actual unused fields by references before
repacking that private gap.
Larger ephemeral new-profile state can overlay an inactive guest-owned region
such as `RgMeleeBlocks` only after auditing all unconditional readers and reset
paths. Selected-character ownership must be explicit. Preserve shared movement
fractions, native actor pools, live music RAM and persistent settings.

MMC3 CHR packing currently uses255 of2561KB pages; MMC5 uses247. Raw MMC3 audit
has209 distinct1KB chunks,47 duplicate chunks, but **zero duplicate aligned2KB
chunks**. Most duplicates are mandatory fixed native halves of special-art/HUD
pairs. Ordinary MMC3 supports256KB CHR; MMC5's larger capacity alone cannot make
the two builds equivalent. [MMC3 register reference](https://www.nesdev.org/wiki/MMC3),
[MMC5 register reference](https://www.nesdev.org/wiki/MMC5)

Do not run `tools/reference/pack_chr.py` as an audit: it writes main assets and
calls other builders. A separate offline analyzer must prove tile reachability,
pose co-residency, fixed native tiles and 2KB even/contiguous constraints before
repacking. Reuse the existing8×16 renderer and exact source pixels, mirror/alias
identical frames, and avoid new black-mask layers by default. Initial **budget
targets, not measured capacity promises**, are Kirby6KB, Chip/Dale4KB, Mac2KB,
Mike4KB, SMB3Mario/Luigi8KB, VicViper2–4KB plus menu/UI pages. All real poses,
weapons, wings, pickups, palettes and variants must fit the measured final
packing; do not silently drop attacks or expand only the ROM header.

Required proof before each profile enters a player's guide: natural title/menu
selection, alternate selection, every power pickup visibly emerging, damage/
death/heal, ordinary+special attacks on enemies/blocks, cramped-geometry poses,
water and transitions, all relevant Easy/Hard contact rules, overload flicker,
and native SFX/music coexistence. Include actual controller replays and frame
review; manuals and synthetic CPU calls alone are not runtime parity proof.
