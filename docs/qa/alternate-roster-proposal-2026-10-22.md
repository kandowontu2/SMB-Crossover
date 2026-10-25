# New Select alternates: source and implementation proposal

Prepared 2026-10-22 by the level-audit agent. Research/design only; no main source, ROM, level candidate, or existing audit was changed. The frozen authored-level candidate remains separate. This proposal concerns the user's new characters, not claims about official Crossover 2.02 characters or maps.

## Recommended scope

| Existing selection | Select cycle on character screen | Gameplay implementation |
|---|---|---|
| Scrooge | Scrooge / Darkwing Duck | Separate Darkwing movement, gun, cape, hanging and progression. Do not inherit pogo. |
| Link | original Link / Zelda II Link | Separate side-view sword/shield physics and RPG progression. |
| Mega Man | Mega Man / Proto Man | Intentionally share the installed Mega Man movement, collision, weapons, upgrades and Easy/Hard rules, as requested. Distinct graphics/name/music. |
| Final position of the new third row | Leonardo / Raphael / Michelangelo / Donatello | One TMNT1 movement engine with four source weapon profiles. |

Mario/Luigi and Bill/Lance remain their existing Select cycles. Select changes the highlighted variant before starting; only the highlighted character's name appears below the colored preview. In gameplay Select retains each character's weapon/magic function. No new universal third-button command is necessary.

The parent confirmed the complete requested roster contract: preserve the first two rows of six and add a third row of seven, with TMNT last. Select alternates do not consume extra portraits. Simon's Select cycle also adds CVIII Grant/Sypha/Alucard while keeping Simon first (Trevor is represented by the existing Simon selection). The complete plan is **19 portraits / 32 playable identities**: current 14 identities + Kirby 1 + Chip/Dale 2 + Mac 1 + Mike 1 + SMB3 Mario/Luigi 2 + Vic 1 + turtles 4 + CVIII alternates 3 + Darkwing 1 + Zelda II Link 1 + Proto Man 1. Research for the additional six third-row families and the CVIII moves is parent-owned and not supplied by this report.

| Third-row menuSlot | Future base ID | Requested identities |
|---|---:|---|
| 12 | 13 | Kirby |
| 13 | 14 | Chip / Dale |
| 14 | 15 | Little Mac |
| 15 | 16 | Mike |
| 16 | 17 | SMB3 Mario / Luigi |
| 17 | 18 | Vic |
| 18 | 19 | Leonardo / Raphael / Michelangelo / Donatello |

IDs 13..19 above are an explicit future candidate plan, not enabled characters or placeholder stubs. Store explicit directional neighbors for the 6/6/7 layout, rather than adding six modulo the selection count. Only actual completed implementations become selectable. The menu must not expose a blank position or unfinished profile as a playable entry.

## Primary evidence and limits

Original manuals establish commands and mechanics; they do not supply frame-perfect movement and attack tables. The retrieved Zelda II disassembly is community reverse engineering, not Nintendo source, and has not been compared against an original ROM binary. Several prose comments disagree with the actual byte tables. Numeric results below use the bytes.

| Evidence | Identity / retained copy | What it establishes |
|---|---|---|
| [Capcom Darkwing Duck manual](https://www.nesfiles.com/NES/Darkwing_Duck/Darkwing_Duck.pdf) | 1992 NES manual; `darkwing-original-manual.pdf` | Controls, gas adaptors/costs, health and refills. |
| [Nintendo Zelda II manual](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAASE.pdf) | Official Nintendo English NES manual; `zelda2-nintendo-manual.pdf` | Level categories, controls, magic, pickups and learned techniques. |
| [Zelda II disassembly](https://github.com/FiendsOfTheElements/z2disassembly/tree/c4c3a4c7d4156b41f54f726dc40644d45812ad29) | Commit `c4c3a4c7d4156b41f54f726dc40644d45812ad29`; README credits Trax via Lemmy | Actual level, spell, motion, damage and drop code/data. |
| [Ultra TMNT1 manual](https://bdjogos.com.br/manuais/351-teenage-mutant-ninja-turtles-nes-manual-usa.pdf) | `NES-U2-USA`, 1989, original first NES game; `tmnt1-original-manual.pdf` | Turtle weapons, controls, equipment and recovery items. This is not TMNT II/III. |
| [Capcom MM3 soundtrack](https://store.steampowered.com/app/1484350/Mega_Man_3_Sound_Collection/) | Official track list, track13 “Proto Man (BLUES)” | A genuine Proto Man musical identity. |
| [MM3 native score source](https://github.com/lsmmega/mm3/tree/8ecd0a9247ed17709e8cd9cc692c38288daa2bc5/audio/music) | Same pinned revision already credited by our MM3 import | Native whistle, ending and staff-roll scores; isolated assembly size probe. |

Retained evidence is in `build/verification/alternate-roster-research-agent/`. `source-tables.json` records raw tables, locations and hashes. `resource-snapshot.json` records the actual linked main build and source hashes. `manifest.json` hashes this report and evidence. These are dated snapshots; the parent is concurrently developing a different native-platform candidate.

## Darkwing Duck

### Confirmed original rules

A jumps; B fires; Down ducks; Up raises the cape; Select toggles the carried special gas; Start opens pause/status. He shoots while crouched, grabs eligible ledges/hooks automatically, and releases with Down. The manual's hanging paragraph contradicts its control chart about A/B, so exact hang/drop inputs need an original-game trace.

Health has four quarters. Only one special adaptor is carried. Heavy Gas falls and sends floor shockwaves both ways, costing 2; Thunder sends two forward diagonals, costing 2; Arrow attaches to walls for traversal, costing 3. Found adaptors are physical pickups. Small/large gas restore 1/10; first-aid restores one quarter/all health. Cape blocks many thrown objects, not every hazard. [Original manual, printed pp7–14](https://www.nesfiles.com/NES/Darkwing_Duck/Darkwing_Duck.pdf).

### Proposed SMB integration

Use a distinct Darkwing profile behind Scrooge's menu family. A dedicated state machine owns grounded walk, crouch-shot, jump-shot, cape, hanging, release and hurt. Keep body and muzzle rectangles separate for every pose. Cape tests only a documented projectile allowlist; it must not make pits, firebars or contact damage harmless. Its appearance is original sprite art, not a black overlay posing as a cape.

Use the existing physical upgrade and independent drop presentation. A basic power block produces a first-aid pickup; an advanced block produces a gas adaptor. A small authored area/cell lookup cycles Heavy → Thunder → Arrow among these advanced blocks, with a repeatable recovery supply later. This lookup is an SMB adaptation, not a claim about Darkwing's original item locations. Picking up a different adaptor replaces the carried adaptor; do not grant permanent access to all three under an “original” label. The active gun HUD shows adaptor icon and gas count. Basic gas remains available without consuming special gas.

Arrow Gas requires a real wall attachment and rideable support, with original lifetime/limits still to be measured. Reuse the ROM's native platform actor/carry path and the parent's admission policy. If no genuine slot is available, retain a pending attachment or reject it consistently; never clear an enemy or firebar to make room. A disappearing arrow must detach a rider safely. Heavy shockwaves follow walkable floor and do not destroy ground, pipes, stairs, castle scenery or question blocks. Each weapon needs an explicit block-interaction policy; no policy should inherit Scrooge's pogo mutation code.

Required original measurements before a fidelity claim: horizontal acceleration/braking/cap, held/released jump curves, air steering, hang snap rectangle/regrab delay, cape activation/protection frames, crouch transitions, basic-shot cap/cadence/speed, special weapon trajectories/damage/lifetimes, gas maximum and adaptor pickup ammo behavior. These numbers were not established by the manual and are intentionally absent here.

## Zelda II Link

### Confirmed original rules

A jumps, B uses the sword, Select casts the chosen spell, and Start opens the submenu. Shield height changes with posture; upward/downward thrusts are learned. Attack/Magic/Life reach level 8. Life levels reduce damage; containers increase maximum life. Magic levels reduce spell costs. Level-up selection can be deferred. Game-over resets current EXP while retaining attained progression. There are eight spells; jars restore magic, fairies restore life, and P bags grant EXP. Spell effects wear off on scene changes. The Handy Glove enables sword-breaking palace blocks. [Nintendo manual, printed pp18,22–25,31–34,43–46](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAASE.pdf).

### Source-derived numeric contract

These are candidate NTSC source values, pending binary/runtime authentication. Threshold arrays contain the seven next-level costs and the max-level extra-life cost; they are not cumulative lifetime totals.

| Category | Source thresholds |
|---|---|
| Attack | 200,500,1000,2000,3000,5000,8000,9000 |
| Magic | 100,300,700,1200,2200,3500,6000,9000 |
| Life | 50,150,400,800,1500,2500,4000,9000 |

Source: pinned `src/prg0.asm`, CPU `$9659..$9688`. Use the `.byt` values; the adjacent Attack comments contain different older values.

| Spell | Native cost at Magic levels 1..8 |
|---|---|
| Shield | 64,48,48,32,32,32,32,32 |
| Jump | 96,80,64,64,40,32,24,16 |
| Life | 140,140,120,120,100,100,100,100 |
| Fairy | 160,160,120,120,80,80,80,80 |
| Fire | 240,160,120,60,32,32,32,32 |
| Reflect | 240,240,160,96,80,64,48,32 |
| Spell | 240,224,192,160,96,64,48,32 |
| Thunder | 240,240,240,240,240,240,200,128 |

Source: pinned `src/prg0.asm`, `$8D7B..$8DBA`. Native units are half the manual's displayed magic-point scale:32 internal units/container,16 displayed points. The meter cap is `(containers×32)-1`. Cast only learned spells, on a new Select edge, after an affordability test; subtract the actual level-dependent cost.

Sword base power at Attack 1..8 is `2,3,4,6,9,12,18,24`; Thunder base power 50 (`prg7.asm:$E66D`). This does not establish SMB enemy HP or resistances. Horizontal velocity uses sixteenth-pixel units: acceleration±1, cap±24 =±1.5px/update (`prg0.asm:$93B1`, integrator `prg7.asm:$D1CE`). Jump integer bytes `FB,FB,FC,FC`, initial fraction `80,00,F0,80`, sword phase delays `6,6,32` are retained raw in JSON; preserve their update order rather than guessing height or total attack lockout.

The source drop routine uses separate weak/strong six-kill counters (`$05DF/$05E0`). Weak selection is7/8 blue jar and1/8 small P bag; strong selection is4/8 red jar and4/8 larger P bag. Selection indexes the per-enemy randomizer `$051B,X &7`, not a global independent25% roll. Blue jar restores32 internal units; red fills the magic cap. Life spell queues96 internal life units, animated through the refill routine. Source: `prg7.asm:$E84F..$E8BC`, `$D3E9..$D41C`; detailed reset persistence still requires tracing. Enemy drops are not generic hearts.

### Proposed SMB integration

Start with Attack/Magic/Life 1 and four containers of each type. Implement Link's sword/shield, learned thrust flags and eight spell records as a separate profile. Keep current overhead-Link boomerang/bomb logic out of this profile. Display compact LIFE/MAGIC meters and EXP/NEXT without moving the gameplay split. The pause panel chooses a learned spell and shows levels/cost; gameplay Select casts it. The level-up panel freezes gameplay/timer safely, offers only affordable categories, supports deferral, then restores the HUD and OAM state.

Use actual learned abilities and permanent items with physical icons. Proposed campaign delivery is a deterministic table keyed to existing power blocks, with no random duplicate scrolls: first eight spell-scroll awards follow Shield, Jump, Life, Fairy, Fire, Reflect, Spell, Thunder; insert Downthrust, Handy Glove and Upthrust at documented early/middle campaign awards. Container awards and recovery follow separate heart/magic pickup records. The exact cell table must be enumerated and route-tested before implementation; original Zelda II towns/palaces do not define locations in SMB. Retain the two source drop counters and jar/bag presentation. Assign SMB enemy EXP/drop groups explicitly in a new table; “weak” and “strong” are design mappings, not source-defined Goomba properties. Award each death once, avoiding shell-combo duplication and zero-HP repeat hits.

Source-style spells are feasible, with world adaptations stated explicitly: Shield damage reduction; Jump alternate native jump profile; Life capped animated recovery; Fairy flight/body conversion; Fire sword projectiles; Reflect approved projectile reflection; Spell transforms eligible small enemies into one declared SMB substitute; Thunder applies one source-power attack to each eligible visible enemy. The last two require a new SMB susceptibility table. Neither should mutate terrain. Glove affects an allowlist of breakable bricks and never question blocks or structural tiles. Carry active-spell flags across frames but clear them at actual area transitions as the source requires. Treat pipe entry/exit as transitions, and verify flagpole, death and continue reset paths independently.

Keep source costs/thresholds initially. Calibrate the *new* enemy EXP and item placement against full SMB routes before promising that all levels/upgrades are attainable. Do not quietly flatten Life into extra hearts or replace the system with the current two-hit mushroom state. Unknowns still include the exact source damage formula/resistance classes, hitbox timing, full-health sword-beam rules, learned-tech collision windows, all drop-counter reset sites and source refill edge cases.

The original overworld inventory also needs an explicit compatibility boundary. Handy Glove has a direct brick interaction. Candle, Hammer, Raft, Boots, Flute, Magical Key and Cross serve original map/visibility/door contexts that SMB does not currently provide. Do not drop nonfunctional icons or invent universal terrain destruction for them. Their SMB equivalents require separately authored situations; the proposed first implementation preserves RPG/combat progression without claiming to recreate Zelda II's overworld quest. [Nintendo item list, printed p46](https://www.nintendo.co.jp/clv/manuals/en/pdf/CLV-P-NAASE.pdf).

## Proto Man

User-directed contract: same Mega Man gameplay. Share the existing Easy/Hard motion dispatch, slide/swim, jump, charge, special inventory, energy, pickups, damage, death and helper admission. Do not add the MM9/10 double-damage rule, shield immunity, a two-shot cap or another movement model without a new user request. A scarf/shield in the artwork does not imply a new collision ability.

Use separate body/pose banks, silhouette, name, palette and weapon overlays. Mushroom/flower transformations, selected-weapon graphics and suit/helmet distinctions must be reviewed for every installed Mega Man pose. Reuse actual Mega Man attack timing; art cannot extend or shorten its hitboxes accidentally. Preserve palettes used by world mushrooms and sprites.

The official MM3 soundtrack identifies the 15-second Proto Man theme. The pinned source already used by our audio import contains `protoman_whistle.asm`, `ending.asm` and `staff_roll.asm`. Isolated assembly with the current imported macros gives 78, 1,302 and 1,401 bytes respectively; whistle instrument 38 is already in the 65-entry retained instrument table. The current game import keeps the title score and SFX, with most music pointers zeroed: choosing an unused ID does not play the whistle. [Official soundtrack](https://store.steampowered.com/app/1484350/Mega_Man_3_Sound_Collection/), [pinned original score source](https://github.com/lsmmega/mm3/tree/8ecd0a9247ed17709e8cd9cc692c38288daa2bc5/audio/music).

Proposed playlist: whistle for selection/lives intro, original MM3 ending score for ordinary stage play, with staff roll or an explicitly selected original MM3 stage score supplying additional contexts. Do not loop a 15-second intro forever. Preserve the score's own channel synchronization/loops. Continue through the buffered APU mixer so firing, energy recovery and world SFX do not overwrite music registers. An original-score identity is established; playback parity is not yet tested.

## TMNT1: four native weapon profiles

### Confirmed original rules

The first NES game gives Leonardo katana overhead coverage, Raphael fast sai strikes, Michelangelo nunchaku coverage near his feet, and Donatello bo coverage above/below. A jumps (repeated A swims), B attacks, Select switches primary/found equipment, and Start opens the information/turtle selection screen. Equipment includes single/triple shuriken, returning boomerang, Kiai and ropes; pizza restores health. Original turtles have individual health and can be captured/rescued. The manual does not provide exact reach, damage or frame windows. [Ultra manual, printed pp5–9](https://bdjogos.com.br/manuais/351-teenage-mutant-ninja-turtles-nes-manual-usa.pdf).

### Proposed SMB integration

The final slot's Select order is Leonardo → Raphael → Michelangelo → Donatello → Leonardo. Repaint the actual highlighted sprite and its name, keeping one menu position. During gameplay A/B retain native commands; Select toggles the carried found weapon. The profile table contains four independent attack scripts, not one staff graphic recolored four ways.

Represent every attack phase as duration, body pose, weapon tiles/offset, active hit rectangle, direction transform, native damage and per-enemy repeat-hit gate. Include standing, crouching and aerial cases, plus separate strike recovery/retrigger rules. Extract exact NTSC weapon scripts from an authenticated original-game trace/disassembly before populating the numerical tables. No source here proves a ranking of all four cooldowns, a pixel reach value, or universally equal attack power. In particular, do not import TMNT II/III special moves, arcade dashes or modern mask colors by assumption.

Use a distinct TMNT movement/swimming profile when the source traces are available; do not quietly give the turtles Mario physics. Proposed pickups: mushroom-type awards are physical pizza, advanced power-block awards are source equipment icons. Catching a returning boomerang must restore its reusable charge only once. Kiai and triple shuriken need real trajectory/concurrency budgets, and the shared sprite scheduler must rotate overloaded effects rather than dropping one turtle's entire attack. Ropes have a source map-context use; do not claim meaningful SMB rope behavior until explicit legal attachment locations are authored and audited.

The requested character-screen cycling can ship without importing the original four-capture campaign. SMB shared lives/level progression are a deliberate adaptation. If original in-level team switching is included, add it to the Start panel with independent health/equipment records, a captured mask and an explicit death/rescue policy. Do not make ordinary gameplay Select cycle turtles, because it already switches equipment in the original. Keep any midair switch from granting free invulnerability, resetting fall speed, duplicating ammo or restoring health. Full team/capture behavior is additional scope beyond merely four Select alternates.

## Easy/Hard policy

These new profiles are not established Crossover1.x/2.02 implementations. For Darkwing, Zelda II Link and turtles, a defensible default is original-game movement/weapons in both modes, Easy using the ROM's user-requested enemy stomping compatibility and Hard using original contact/attack rules. Apply Easy stomp through an explicit capability flag, preserving spikes and firebar hazards. Do not advertise this as an original Crossover setting for characters absent from that source. Proto Man inherits Mega Man's existing mode-specific behavior exactly. The new profiles need their own helper-admission masks derived from measured jump abilities; copying Scrooge or overhead Link's mask is not proof.

## Architecture and capacity contract

### Observed current main build

| Resource | MMC3 | MMC5 | Consequence |
|---|---:|---:|---|
| Declared PRG | 512KB | 512KB | There is no unallocated new 8 KB bank. |
| Linker-unassigned PRG total | 21,864B | 21,270B | Fragmented, includes parent-reserved level/helper ranges; not an approved budget. |
| CHR physical1KB banks used | 255/256 | 247/256 | Only1KB /9KB graphics headroom. |
| SRAM segment span | `$6000..$7FFC` | same | Only3 trailing bytes; inner padding requires ownership proof. |
| Global metasprite IDs | 252 | 252 | Only4 IDs remain in the8-bit global path. |
| Existing selection/family counts | 12menu /13family | same | Per-family tables are not automatically per-variant tables. |

These are hashed observations of the main HR image/debug files in `resource-snapshot.json`. Its apparent bank `$18` and`$1A` free spans are already reserved by the parent native-platform/authored-level work and must not be allocated again. The frozen level candidate's own 1,416 B and the parent's native helper are additional consumption not reflected by the main snapshot.

`SelectedCharacter` currently indexes many 13-entry family arrays and mask tests. `MenuCharacters` is `0,1,2,3,4,5,6,7,12,9,10,11`; menu navigation is `+6 mod12`. Existing `MarioVariant`/`BillVariant` are independent. `CrossoverPatchStatusName` appends Lance at `CHARACTER_COUNT`; changing that count silently moves Lance's name index. `InvOwned*`, stored/view arrays and `InvSelected` have 12 records, `InvAmmo` has 192 bytes (12×16), and Scrooge is currently excluded. `InventoryHasRaw` does not itself prove that a new profile index is safe. New profile IDs must never directly index these arrays.

### Recommended data shape

Keep old family IDs and RAM/public symbol addresses stable. The complete parent roster plan has 20 base family IDs 0..19, 19 menu slots and 32 playable identity records, with 13..19 only future candidate base IDs. These are different spaces; a movement engine can serve several identities without sharing their display or persistent state accidentally.

| Key | Meaning | Required indexing rule |
|---|---|---|
| `menuSlot` | Portrait position 0..18 in the 6/6/7 grid | Only preview, neighbors and the local variant list. |
| `variantID` | Local choice within that portrait | Mario/Bill/etc two-way cycles; Simon and TMNT four-way cycles. |
| `movementProfile` | Physics/update/collision callback identity | Explicit aliases allowed; Proto uses Mega Man by user request. |
| `equipmentOwner` | Persistent progression record/pointer | Independent of portrait, variant, base family and movement engine. |
| `ActiveProfile` | Resolved playable identity descriptor 0..31 | Links the four keys to names, art, music and capabilities. |

A descriptor references movement/update/draw/collision callbacks, source physics data, palette/CHR family, display-name ID, audio playlist, `equipmentOwner`, stomp capability and helper policy. Existing fast dispatch remains the default for unchanged characters. Do not feed new base IDs or identity IDs directly into current ammo code: `InventoryIndex` shifts four times into an 8-bit offset, so owner 16 wraps to 0. Preserve existing 12 records or migrate through an explicit 16-bit owner-pointer accessor; neither raising `CHARACTER_COUNT` nor lengthening the first table fixes the arithmetic. Capability masks likewise need explicit widened storage or per-profile bytes beyond 16 families.

Use explicit menu-family/variant tables and name IDs. Across the complete requested roster, new variant choices require9bits (Proto 1, Zelda II 1, Darkwing 1, CVIII 2, Chip/Dale 1, SMB3 Luigi 1, turtles 2), beyond existing Mario/Bill choices. Reserve two bytes for the new choices or a byte-per-family table with explicit size accounting; the earlier subset-only one-byte estimate cannot cover the complete roster. Cache the active profile once at selection/reset, not inside every tile draw. The name mapping must cover all variants on selection, HUD, lives screen, ending, continue and cheat-level entry. Sparse directional-neighbor tables prevent modulo errors. Prefer per-profile private pose pointers like the installed Samus/Scrooge paths; do not consume one of the final four global IDs for every animation frame.

New persistent state planning target for **this report's subset** is roughly 64–96 bytes: Zelda II levels/EXP/HP/MP/containers/spells/techniques/drop counters, Darkwing health/adaptor/gas, menu variants and optional turtle records. This excludes state for Kirby/Chip/Dale/Mac/Mike/SMB3/Vic/CVIII and is not the full 32-identity budget. It is a design estimate, not a measured free allocation. Use a single active movement/attack scratch union where lifetimes are exclusive. A potential 29-byte tail exists after `MmRushLandDirty+16` in the existing 512-byte MM audio slab, but it is **not allocated by this proposal** and has a whole-slab clear lifecycle. The unsupported inventory rows for Mario/Pit/Rygar/Luigi are another possible repacking source, requiring a full read/write/call-path audit before reuse. Neither the parent's `$736A..$73FF` helper gap nor the final 3 SRAM bytes can fund the whole addition.

### Storage plan and explicit gates

Before character implementation, produce a complete pose/tile census and a candidate packed-CHR report. Planning estimates for **this report's subset**, not extracted asset counts: Proto 2–4 KB, Darkwing 6–8 KB, Zelda II Link 4–6 KB, four turtles together 6–10 KB =18–28 KB incremental CHR before further sharing. The other requested families/variants require additional art beyond this subtotal. Original sprite extraction must decide the actual sizes. Sharing mirrored body tiles and common turtle parts may help; do not omit crouch/hurt/swim/weapon frames merely to fit. The current one-byte logical→physical CHR maps and special-family overlays also need an addressability audit.

For a standard mapper-compatible pair of builds, the first option is verified tile deduplication/repacking and pose-bank reuse. If that cannot recover the exact required headroom, a mapper/hardware decision is needed. Standard MMC3 does not gain usable PRG/CHR capacity from a larger header alone. CHR-RAM streaming changes the cartridge contract and needs a backend plus selected-profile loading at menus; it also consumes compressed PRG space. MMC5 extended CHR requires its high-bank mechanism and correct IRQ/restoration, not merely raising the header count. Do not silently publish a board-incompatible “MMC3” image. See the community hardware research for [MMC3 capacity](https://www.nesdev.org/wiki/MMC3) and [MMC5 upper CHR bits, $5130](https://www.nesdev.org/wiki/MMC5).

Prototype code/data planning target for this subset is 8–16 KB before three new music drivers/scores, graphics loader changes and any team UI; the remaining 32-identity roster adds more. There is no proof that all this fits the remaining fragmented main space after native helpers. Native score data is preferable to more captured APU streams; the current expanded playlist already consumes 20 nearly full 8 KB music banks. Proto's three scores total 2,781 B, but bank `$0B` has 472 B unassigned on MMC3 and only 2 B on MMC5. Sixteen-bit MM3 score pointers require reachable music data throughout playback. Either repack same-bank cold code or provide a resident, tested data-window switch/restoration trampoline; a farcall to a score label is not a song reader. Retain the buffered APU writer path.

## Concrete implementation order and acceptance

1. **Resource and selector candidate.** Pin both ROMs/debug/source, account for the parent's merged reservations, then prove CHR/RAM/PRG fit. Add profile/name/navigation tables in a private candidate with address assertions. Enumerate all 32 requested identity records and 19 portraits, with unavailable implementations remaining disabled; verify Select cycles each completed family, neighboring navigation, silhouettes, colored preview, highlighted name, lives/HUD names, continue and resets. Existing 13 families must retain their original dispatch and table bounds. New base IDs 13..19 remain a plan until complete implementations exist.
2. **Proto Man.** Import real pose art and source scores. Differential controller replay versus Mega Man must match position/velocity, collision, damage, shots, energy and item outcomes byte-for-byte, allowing only presentation/audio state differences, in Easy and Hard. Test every weapon, crouch/slide, water, death, flagpole and block action.
3. **Darkwing.** First authenticate original movement/cape/hang/gun traces, then implement the measured profile and three gas adaptors. Verify costs 2/2/3, physical pickups, replacement, dry fire, refill caps, crouch muzzle and Arrow rider lifecycle. Test full actor/OAM load with enemies/firebars present; verify immutable terrain and question-block contents.
4. **Zelda II Link.** Authenticate source byte/version match. Implement independent levels/meters, source costs, affordability, animated recovery and six-kill groups before spells. Retain exact threshold arrays; unit tests cover every level/spell/cost edge, meter cap and counter group. Then add original sword/shield/learned techniques, source-style magic and the explicit SMB item/EXP/resistance tables. Verify pause/level-up doesn't corrupt the scroll split, timer, OAM, music or bank restoration.
5. **TMNT1.** Obtain authenticated source/trace tables for all four primary weapons and movement. Implement one measured engine with distinct attack scripts; compare poses/hit rectangles/active windows against original video frame-by-frame. Then add found-equipment pickups and water controls. Keep the shared-life versus team-capture adaptation documented.
6. **Campaign and hardware verification.** For every new profile, exercise both 1-1 routes, 1-2 bricks/powerups, 2-2 swimming, helper gaps, maze transitions, cannons/firebars, all exits, Bowser and continue. Retain native controller replays and inspect sprite overload/score/pickup frames. Check worst-case frame time with projectiles, drops and native actors on both mappers; verify ordinary enemies/firebars are never displaced to admit an ability. Extend the player guide only after the implemented controls and progression are verified.

Not yet established: authenticated Darkwing/TMNT numeric movement and weapon scripts, complete native graphics census, Zelda II binary match/reset/damage details, final SMB upgrade cell/EXP tables, or a fitted dual-mapper allocator for the entire expansion. Those limits prevent an honest “perfect original implementation” claim today; they do not prevent the concrete profile/selector and source-data work described above.
