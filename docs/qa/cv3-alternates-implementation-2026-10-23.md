# CV3 Simon alternates — private adoption contract

Current integration note: the original private packet below is historical. The
expanded roster now publishes camera position for all three companions. Sypha
and Alucard retain the source jump curve's timing and fixed launch direction,
with ordinary airborne X/Y displacement doubled for SMB geometry: 72px rise
instead of 36px. Ground speed, Grant, bat/climbing motion, the complete hurt
sequence, and externally supplied spring/stomp velocities retain their separate
rules. Continuous foot-crossing detection preserves Sypha's frozen-enemy
platform landings at the higher fall speed. Native 32/48/64px pipe landings,
the translated original 1-3 80px gap, and ability/injury/death arenas verify this
adaptation; they do not certify a campaign. The later single-cell block-attack
repair and source-audited native helper platforms are also integrated. The
older 36px measurements and limitations below describe the frozen first packet.

Base: frozen `kirby-roster-mg/source.zip`, never current main. The parent will compose this narrow change into MP. No main files were edited by this agent. This is a functional character core, not a claim of full campaign equivalence or Crossover parity.

## Selection and controls

Highlight Simon and press Select: Simon → Grant → Sypha → Alucard → Simon. Confirm with A/Start. Names, colored portraits, lives-screen bodies, in-stage names, body artwork and controls are live. Strict family5 + variant1..3 gates protect all legacy profiles.

All three: A jumps, B attacks, Down crouches, Down+B attacks while crouching, Up+B uses the one carried subweapon. Grants on walls/ceilings use B for the carried subweapon. Start retains normal pause.

* Grant: fast ground movement (1.25px/update), controllable airborne direction (1px/update), original held jump rises58px. Airborne contact while holding toward an admitted solid wall grabs it; keep holding toward it and use Up/Down to climb. Hold Up against an admitted ceiling and move Left/Right to crawl. A releases/leaps with a re-grab delay. Ordinary B is the USA close knife. Carried choices are dagger, axe, stopwatch. Dagger speed4, axe speed2 with initialY−5.5 and gravity0.25; four original axe rotation frames run6updates each. Stopwatch costs5hearts; other weapons1.
* Sypha: ground speed1; original fixed jump rises36px and keeps its launch direction. B is the short staff. Carried Flame uses the exact nine-step original expanding flame displacement/pose/timing table; Ice launches the original three velocity vectors and swaps symmetric endpoints each update, giving the original six-direction pattern; Lightning has three homing orbs with original32-angle aim/vector/turn arithmetic. Ice freezes admitted native enemies; falling onto a frozen Goomba supports the player; staff contact shatters it.
* Alucard: speed1 and original36px jump. B fires a free fireball; two upgrades add the original upward and downward diagonal fireballs. Down+A transforms to/from a bat (36updates); reverting requires head clearance. Bat acceleration/friction and caps are original numeric values, including1.25X/1Y caps. Entering costs1heart, then flight drains1per60updates. Bat cannot fire.

## Health, items and native scene integration

Each companion owns64health units (16bars), initial10hearts, maximum99hearts, one carried subweapon, and an Alucard shot level0..2. Life loss resets those records; area changes clear live attacks/temporary state. The three records do not write Simon's old inventory owner or another profile's inventory. Fresh-game ExRAM clear retains only the shared menu variant byte.

SMB acquisition is explicit adaptation: mushrooms heal16units and enable the next flower stage. Flowers visibly emerge as private native powerup actors; Grant/Sypha flowers cycle dagger→axe→stopwatch or Flame→Ice→Lightning and add5hearts; Alucard flowers add one fireball diagonal, or heal at full power. Native48-update emergence and normal collection collision run before the reward; no automatic block-head pickup. Stars/1-ups retain vanilla item behavior. Private reward illustrations use actual original projectile/item artwork, including the original stopwatch shape. Two independent falling heart drops carry original1/5heart values; their25%enemy-drop probability and SMB locations are adaptations. They never overwrite or consume an enemy slot.

Health damage mapping is adapted to native enemies: ordinary4, Hammer Bro8, Bowser16;16update recoil and64update protection. Empty health enters the native death path. Frozen admission,180update freeze, enemy hit receipts, native score/defeat response, two heart slots and terrain tests are SMB adapters. This package does not claim original CV3 enemy HP/weakness tables for SMB enemies.

Native SMB terrain, scrolling, powerup objects, collision resolution, injury/death, score and world graphics remain in charge. Character probes have an explicit solid-metatile allowlist. No ground mutation or enemy deletion is used to fake climbing/platforms. Native body profiles are14px wide, with24px Grant /32px Sypha-Alucard /13px crouch-bat heights; this is a declared SMB body-profile accommodation, not an exact original hitbox claim.

## Resources and exports

* Variant `$5FE7`; persistent region `$5EA0..5EDF` (actual records through`5EB2`); active-only transient `$5C00..5CFF`. No original SRAM moves. Ice symmetric endpoints occupy`5C72..7D`. Transient storage belongs to Kirby while CV3 is inactive.
* PRG82/A `CV3_CORE`4143B,84/A `CV3_COMBAT`4369B;83/C Grant+Sypha art5428B;85/C Alucard art2268B. These sizes are from the frozen link map.
* CHR460..523 fixed physical64KB at`$73000..82FFF`;34body pages460..493, spare494..517, stable special pairs Grant518/519, Sypha520/521, Alucard522/523. UpperCHR bit2 is actually published through the production mapper ABI; this is not a header-only expansion.
* `Cv3SetPose`: X=authored pose index, updates `SmPosePtr`, `ObjectMetasprite`, `SmChrBank`, `Cv3BodyChrUpper`, `Cv3BodyBankC`. Body descriptors use existing Samus-indirected body rendering; shots/items retain that character's same C bank throughout the frame. No NMI-window race through a foreign C bank.
* Fully resident `Cv3ResidentRosterBank` selects C83/C85 only for strict active variants, else indexes exported `Cv3LegacyBanks`. It adds21CPUcycles over the old direct table read on the ordinary resident path. Fully resident terrain/body gates use cached native profiles. They do not call SMC/farcall from NMI.
* Fixed holes:60B total in the existing136B `SwitchAreaCHR` span (bank leaf29B, terrain leaf31B);30B of the existing37EA tail of the55B `ExpandedCollisionBox` span. No ExpandedCollisionAdder or new bank4-tail ownership.
* Only the existing `KbDrawDispatch` admission changes: Kirby or Simon enters the shared cold dispatcher, strict CV3 draws itself, inactive Simon tail-calls `RosterDrawShots`. Root's Chip/TMNT outer dispatch must be retained when composing this MG diff.

## Art and palette proof

236 body pose/facing records are extracted by executing the original USA renderer at1A:8079, not traced from a fan sheet.30 original native OAM samples authenticate that call convention. The corrected source decoder uses NES MSB-first bits; three independent original screenshots match1,284 opaque pixels exactly after preserving the original rotating OAM priority. An earlier individually mirrored-tile candidate is retained as a negative and is not the adoption ROM.

All installed body and weapon opaque locations survive8×16 repacking. Main body palettes are exact. Effects map original colors22→stable SMB30 and25/34→27 where needed, with original ink on stable world3black. No world palette2 writes. The original source's color changes across arbitrary scene palettes and its exact per-frame sprite priority are not claimed. Optional extra outlines use the existing option; source ink remains visible with outlines off.

Body palettes are cached, not requeued every frame. The retained negative native powerblock fixtures show why: a continuous palette VRAM command blocked `BlockObjMT_Updater`, left collision metatile23 after a bump and launched the emerging mushroom. Corrected tests prove the native spent-block replacement, emergence and later pickup. Parent is auditing this ordering in other profiles separately.

## Evidence and qualifications

Frozen candidate SHA256: `62931852ebd443628040de9a930a4b49190f3ec865bc1f0255cace1e5b1e4ce8`.

* `component-proof.json`:240 complete DrawAll body cases,576 complete projectile pixel cases,180 pickup quantity cases,9 stale-stamp cases. Actual production farcalls and10-bit CHR hardware publication execute in the instruction arena.
* `motion-oracle-proof.json`: actual original-ROM instructions compare460 jump,3462 bat-axis,2432 Lightning aim,2048 Lightning turn,288 Ice endpoint,56 Flame sequence cases. These prove numeric leaves, not all game-loop ordering.
* `release-grant/proof.json`: controller-only cold menu/Select entry, then an explicitly bounded native collision arena;1,448frames/1,440NMIs/1,382IRQs. Jump58, crouch knife, dagger,96px wall climb/step-over, physical mushroom, injury and death.
* release-sypha and release-alucard receipts:1,469frames/1,461NMIs/1,403IRQs each. Jump36; Sypha also native Goomba freeze→support→shatter; Alucard bat entry/flight/reversion. Both test physical head-bump mushroom emergence, side-jump pickup, injury and death.
* Every tested NMI preserves all33 shared SMC bytes and restores actual A/C banks and shadows. Actual writes select special pages518..523 with5130upper2.
* Flag-off MMC3 is exactly KB`4720972962f8faf6c8e45536f95001e79ae66c7141dcbfa09c768440fa039c00`; ordinary MMC5 exactly KB`0ab6ac031ae9c80a6e516ce29130e041cfe2e34da5bfb447d78a514fbd2739e6`.

Limits: no full campaign/replay claim. Sypha/Alucard cannot clear every tall native pipe with their genuine36px jump; source-audited helper platforms still require the parent's pending native-platform integration. Grant's allowlisted climbing is an SMB adapter, not a verbatim CV3 wall/corner engine. Frozen enemies do not yet receive the original blue freeze tint; compact status HUD and some attack/spawn timings/collision rectangles are adaptations. CV3 attacks currently damage enemies; attack-based SMB brick/question-block activation is not implemented in this packet. The existing Simon/Castlevania music/SFX driver is inherited; this is not a full original CV3 audio port. No player should be told these limits have been resolved.

## Primary references

Original USA ROM SHA`085ec6395681c7ebfda19c2986069c21a3d27738cc61ada76249de70a07ed7d3`; pinned disassembly `https://github.com/vinheim3/castlevania3-disasm` revision`3272648f2bbf95f6cb11d947feca73b852a99f10`.15,042 annotated player instruction bytes were verified against the original. See retained `reference/source-manifest.json`.

Original code anchors: renderer1A:8079; fixed jumps1C:98BF and Grant1D:A112; bat-axis1D:A889/A929; dagger velocity1D:B48D; axe1D:B483/B487 and animation group0/index8; Flame1D:B390/B3F6/B440; Ice1D:B823/B8A9/B8F1/B8FD; Lightning1D:B1AB/B208/B259/B2BB/B30A; Alucard diagonals1D:B00A; Grant wall-cast body tables1D:BB8E. Primary manual reproduction was inspected at`https://manuals.plus/m/4509ea3117f150f6a6562d23d298ea881cec5c1d75b644807d1ea826631af430`.
