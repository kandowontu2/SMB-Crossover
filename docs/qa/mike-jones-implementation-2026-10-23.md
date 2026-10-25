# Mike Jones core M handoff

Frozen private candidate: `build/mike-kd-private/mike-m.nes`, SHA-256 `31d31ad56af24c94ef8a6df1062123881bf9608296062b26db601abcab2c37e2`.

This packet adds a working StarTropics profile with original source pixels and measured original health, upgrade gates, movement cadence, jump curve and attack frames. It is a documented side-view adaptation. It does not claim a source-exact StarTropics engine, full campaign completion, or complete utility magic/audio.

## Integration boundary

- Raw character ID 16, root menu slot 15, root name index **31**. Private MJ proof uses name 20; do not copy that index into main.
- `owned/` contains the new source and 4 KB CHR. Incbin paths in these files are normalized to workspace-relative paths. `exact-private-overlay-source.zip` preserves the exact MJ private compilation tree, including its private absolute paths, for evidence/reproduction on this workstation.
- `common-hooks-vs-MJ.diff` is narrow contextual evidence against checkpoint MJ. Root main MU has outer M3/Vv/Tn/Cd dispatches; compose exact ID16 admission through that current chain. Do not replace current shared files with the private MJ versions.
- `private-menu-reference-vs-MJ.diff` and private selector/packed atlas changes are proof-only. Supply `art/mike-portrait.png` to the root full-menu generator. Root must retain all existing portraits and names.
- Define/include `mike_jones_state.inc` before the new modules and include `mike_jones.s` in the expanded-only block after the legacy profiles. The module exposes Jn* symbols; explicit debugger exports are listed in the manifest.
- Retarget the existing same-sized movement, graphics, portrait, weapons, death, injury-start/status, private powerup drawing/rise/collision, collection, visibility, enemy-drop, reset, status-name and special-draw farcalls through their Jn dispatches. Legacy fallbacks in the private dispatch file point to MJ and need the root current chain.
- Existing native head bridge calls `JnHeadDispatch`: ID16 goes directly to `BlockBufferColli_Head`, others fall through the current root head chain. Native big collision adder and bounding box both return profile 0. No new resident side/bbox bridge is required.
- `JnBodyDispatch` follows the common Easy/Hard body-contact policy. `JnInventoryDeathDispatch` selects Mike only and calls `JnLifeLost`; reset calls the prior reset chain then `JnAreaReset` (the latter exact-ID guards itself).
- `JnGetColors` performs existing face/world palette restoration and backdrop setup before the source body palette. No per-frame palette queue is added. `JnGraphics`/pose changes do not queue palettes, so used-block replacement is not starved.
- New raw-ID table admissions are limited to the resident graphics C-bank table (raw16 = **97**), player palette guard, menu registry/name/preview, and private pickup/draw guards. Do not widen legacy CHARACTER_COUNT or the 12-family inventory arrays.

## Resource receipt

| Resource | Use |
|---|---|
| PRG 96 / A000 | MIKE_CORE: core, movement, dispatch |
| PRG 97 / C000 | MIKE_GFX: body/weapon/item metasprites |
| PRG 98 / A000 | MIKE_COMBAT: attacks, pickups, renderer |
| CHR 708..711 | 4 KB actual use; 708 body, 709 common-upper copy, 710 attacks, 711 items |
| $5F30..$5F3F | Persistent half-heart HP, capacity, owned tier, selection, ten ammo counts, star/food parity, stage |
| $5C00..$5CFF | Active-only transients; exact ID16 guards and area/life reset |
| $5FE3 | Reserved variant byte, unused |

CHR reservation 708..755 retains 44 KB spare. Native enemy windows 2/3 remain unchanged (MJ native pages 17/18). Actual physical publication uses the high latch **2** with low bytes 196..199, not truncated low-only CHR indices. Resident graphics table selection remains purely resident; no farcall or shared SMC is invoked from NMI. Total resident footprint does not grow; the private resident table's two-byte addition consumes fixed SwitchAreaCHR padding. Root already has a reserved raw16 row.

Audio reservations PRG99..102 are unused and may be released. The original source engine has been acquired and inspected, but this core deliberately retains the existing Pit music/SMB SFX fallback.

## Controls and upgrades

A jumps. B uses the selected weapon. Select cycles stocked special weapons and returns to the unlimited primary. A fresh second B while Asterisk blades fly splits the two tracks.

- Start with three full hearts. HP is stored in half-heart units, with up to 22 full hearts.
- Owned Shooting Star works only at six or more filled hearts; owned Super Nova works only at eleven or more. Falling below those source thresholds reduces the effective primary automatically. The 135-case oracle compares this rule against the original ROM's actual machine code.
- Yo-yo retracts. Shooting Star and Super Nova use original source attack graphics with increased reach/damage. Current tier and selected weapon/ammo are visible in the HUD.
- Bat, Slingshot, Fire, Miracle Mirror, Asterisk, Bola, Spikes, Baseball, Super Laser and Mega Laser are selectable. Their identities and pixels follow the original manual/game; their trajectories, damage, SMB hazards and terrain behavior are documented conversions. Mirror converts a contacting Bill or Bowser flame into a free reflected laser. Spikes applies bounded screen damage. Mega Laser has two separated beams. No special projectile destroys SMB terrain.
- The measured original ground step is 16 px/14 updates, converted to continuous 8 px/7 frames. The original 38-frame jump has a 17 px apex; the side-view jump multiplies that curve by four vertically (68 px) and doubles airborne horizontal carry. Native first-brick headbump and pickup collection passed with this conversion. Water strokes and vines use explicit SMB adaptations.

## Physical reward delivery policy

| Item kind | Delivery and effect |
|---|---|
| 1: Big Heart | Mushroom block reward; adds one full heart capacity and refills health, capped at 22 |
| 2: Shooting Star | First flower-class reward; grants owned tier 2 |
| 3: Super Nova | Next flower-class reward; grants owned tier 3 |
| 4..13: specials | Subsequent flower-class rewards stock/refill the first empty special weapon |

Collecting a block reward alternates the next native mushroom/flower delivery. Reward type is frozen when revealed. Actors emerge for the standard 48 updates, cannot be collected while still inside the block, and must physically contact Mike to grant anything. The natural first-block test observes the real target cell changing from bumped $23 to a used block, rather than only observing a spawned item.

Enemy deaths spawn physical small hearts (one in four) or stars (three in four) as an authored SMB delivery rule. A small heart restores one full heart; five stars restore one full heart. The primary can retrieve a nearby drop at reach. Restoration clamps to capacity. Mushroom/flower food never invokes native Mario growth.

Special ammo, selection and partial stars clear on life loss or a new SMB world/level; ordinary same-level pipe areas preserve gear. Capacity and owned primary persist. Fatal damage leaves zero HP throughout the native death animation; the next live entry refills health. Easy permits the shared stomp policy; Hard uses body contact.

## Validation and limits

All final native evidence binds candidate M. The final ordinary-controller tests prove menu entry, movement, jump/attack, a real Goomba defeat, stationary first-block head collision, visible emergence, physical Big Heart collection/healing and actual used-cell replacement. They use no emulator memory writes.

The arsenal and death tests are explicitly labeled RAM-arranged component fixtures after a normal menu start. They prove health gates, physical pickup effects, ten stocked special cycles in both directions, source attack releases, target defeats, Mirror reflection, Asterisk second-B splitting, pickup SFX queueing and native fatal/death/new-life behavior. They are not route certificates. The first left-facing Mirror fixture D failed because its Bill was moving away before the windup completed; D is retained, and E corrects only the enemy arrangement, with no gameplay patch.

Pure CPU checks add 135 original machine-code health cases, 20 owner/reset cases, four stage/life cases and 3,328 terrain attribute/no-write cases. Expanded-off builds reproduce both existing MMC3 and MMC5 ROM hashes exactly. Large debug/source CSV files are retained as verified lossless gzip archives.

Not yet implemented: native StarTropics music engine, Medicine inventory and utility magic such as Lantern/Rod/Snowman/Stop/Slow/Anklet. No campaign/AV pass is claimed. Earlier discovery failures and candidates remain under the private work directory and its verification logs. The initial author scripts predate later hand fixes; the frozen owned source and exact private overlay are canonical.

Primary references: local original StarTropics USA ROM (hash in verification/original-rom.json), Nintendo original/electronic manuals in the private references folder, actual original component captures, source-pixel/orientation receipts in art/, and the original machine-code health oracle. Original-game debug/inventory arrangements are source component fixtures, not ordinary campaign routes.
