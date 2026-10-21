# Bass inventory and selection

Reference: the pinned Crossover 2.02 `Bass`, `MegaManBase`, `MegaManProjectile`,
`StatManager` and `MegaManPickup` sources under `reference/crossover2/`.

## Play

After the mushroom, powerup blocks reveal separately acquired upgrades instead
of applying an invented third Bass buster tier. Select cycles owned weapons;
it skips unowned upgrades and the passive Energy Balancer. Start pauses, then
Left/Right chooses backward/forward; Select while paused selects the buster.

| Selection | Attack | Energy cost |
| --- | --- | --- |
| Super Arm | Hold B while contacting empty masonry to lift it; a new B press throws it | 8 on lifting |
| Metal Blade | B, with eight directional aims | 4 |
| Hard Knuckle | B; Up/Down steers after startup | 8 |
| Pharaoh Shot | B fires; holding B charges the overhead balloon; release launches a medium/full shot | 4 small, 8 charged |
| Charge Kick | Down+A dash | 4 |
| Flame Blast | B fires a falling seed that becomes a contact flame | 4 |
| Water Shield | B creates eight appearing orbiting balls; another press expands the completed shield | 16 to summon |

Each weapon starts at 112 energy. Exhausted upgrade pools offer large weapon
energy. Energy Balancer can refill the least-filled owned weapon when the
current selection does not need it. Damage stores the inventory; mushroom then
recovery flower restores it. These behaviors use native block/pickup objects.

## Reported selection, display and brick-lock problems

The selector now clears held Super Arm state, charge, movement locks and
projectiles before equipping another weapon. Damage also clears active weapons.
The HUD uses the source weapon icon, a seven-cell energy bar and exact numeric
energy. Its text is encoded once, and all artwork sits inside the visible
32-pixel HUD. It leaves the native character, score, coin, world and time fields
in place. The HUD now crops the complete sixteen-pixel source icons: the old
crop omitted their upper halves. World upgrades use distinct source icons,
including the animated Energy Balancer, with stable world palettes instead of
the selected suit's changing colors. These NES palettes preserve mushrooms
and enemies; they cannot reproduce every Flash RGB color simultaneously.

Native audio interrupts previously restored the character's graphics-data bank
even when they interrupted drawing from a separate weapon-data bank. The NMI
now restores the interrupted bank. Sprite-data lengths are also checked before
rendering, preventing an invalid byte count from looping through memory.

`tools/audit/reproduce_special_bank_fault.py` creates a diagnostic ROM with those
two protections disabled. The NMI audit detects incoming bank 13 returning as
bank 34 in that control. The shipping ROM passes the same interrupt audit. This
isolates the bank fault; it does not prove the exact timing of the user's freeze.

## Verification

The tests use explicit starting map/actor fixtures and real controller attack
input. They are not controller-only level clears or physical cartridge tests.

- `bass-inventory.lua`: native question-block reveals, eight unique upgrades,
  energy refill, all seven weapon selections and attacks, return to buster,
  source icon/text/bar, switching away from a held brick, damage and recovery.
- `bass-special-weapons.lua`: independent source costs, shot pools, directional
  speed, knuckle startup, Pharaoh charge, kick, flame conversion, water orbit
  and expansion, Super Arm lift/throw, and 1,140 real NMI bank restores.
- `bass-special-enemies.lua`: Metal Blade passes through an enemy it defeats
  and is consumed by one that survives; Knuckle and full Pharaoh continue
  through successive defeated enemies.
- `bass-arm-question.lua`: question reward, four thrown-brick fragments,
  neighboring masonry and continued main-loop progress.
- `bass-arm-question-stress.lua`: sixteen throws across both directions,
  world-page parities, coin/upgrade blocks and varying interrupt phases, with
  a native Koopa present.
- `bass-pickup-art.lua`: 64 combinations of world pickup and selected suit,
  reconstructed from actual DMA OAM/mapped CHR and compared with frozen source
  pixels. It also checks every pixel of the full HUD icons and mushroom colors.
- `bass-pickup-rise.lua`: a native question-block reveal rises exactly sixteen
  pixels in 48 active updates, respects a timer freeze and keeps block alignment.
- `bass-energy-drops.lua`: real controller-created shots defeat Goombas; pinned
  random draws exercise no drop, small/big drops, exact 8/40-unit recovery and
  routing through the Energy Balancer.
- `bass-pharaoh-follow.lua` and `bass-pharaoh-stock.lua`: independently modeled
  subpixel drift/clamps across camera/page boundaries; a separate balloon while
  the first shot flies; low-stock charged release; and star-powered free ammo.
- `bass-flame-contact.lua`: all four surface pivots/orientations, rotated source
  art and the full 45-update flame animation. Its ceiling case explicitly gives
  a controller-created seed an upward test velocity to isolate that contact.
- `bass-armor.lua`: ordinary weapons visibly deflect from native armored enemies;
  Knuckle pierce strength 10 overcomes their strength-5 armor; reflected/upward
  shots leave the live pool.
- `bass-source-sfx.lua`: 3,216 register comparisons against the exact NSF tracks
  selected by 2.02 `MusicInfo`, plus refill looping/stop and music restoration.
- `bass-water-audio.lua`: real Water Shield input plays the embedded source clip
  through native DPCM from fixed ROM. Checks duration, IRQ/loop configuration,
  controller reads during DMA, independent music and selection/pause/death cleanup.

The source SFX provenance is recorded in `docs/reference/bass-sfx.json`. Water
Shield is an MP3 in the SWF; `bass-water-audio.json` records its seek/sample
counts and native NES DPCM adaptation. That lossy codec is not PCM-identical
to Flash playback. NSF effects retain their captured frame-level registers.

`tools/verify.py --mmc5` registers these alongside the existing full roster suite.
Current results and ROM hashes are in `build/verification/summary.json`.
The October 16 Bass source-audit checkpoint passed all 365 cases on MMC3 and
MMC5. Its retained manifest is `build/verification/bass-source-parity-summary.json`,
with the complete run in `bass-source-parity-suite-final.log`.

Two old Bass tests used a single hardware-frame input pulse that can fall
entirely inside a lag interrupt, where the game does not poll the controller.
Their press windows now span two/three hardware frames, below the automatic
fire interval. All original movement and damage assertions are retained.

## Follow-up: repeated upgrades, emergence and Knuckle backdrop

The 2.02 `StatManager.getRandomUpgrade`, `prepareNextUpgrade`, `setTier` and
`addCharUpgrade` choose randomly from available upgrades, remove acquired
weapons, and allow missed upgrades to return on a later tier pass. When Bass
owns the complete inventory, `maxTierUpgrades` returns big weapon energy.
An item already revealed in the world is not removed when another copy is
collected. Consequently two copies can coexist if both were offered before
ownership, across passes over uncollected upgrades; the exclusion applies to
new rolls of an already owned weapon.

The native selector now independently excludes owned items. Previously it
relied only on the viewed bitmap; an owned Knuckle could be selected again if
that history differed. It also starts a fresh pass over uncollected items
after exhausting the revealed choices. `bass-upgrade-random.lua` reproduced
the duplicate with the old ROM and checks 35 native block reveals, including
an owned Knuckle, a missed Knuckle on the next pass and full-inventory energy.

Private pickup artwork used the source bottom pivot against SMB's origin
without its eight-pixel draw offset. The corrected pivot places a completed
16-pixel icon directly on the block top. `bass-pickup-contact.lua` failed the
old alignment and now checks a head bump, full emergence, an uncollected world
icon and a later controller jump collecting it. These centered/lower-block
fixtures did not initially reproduce automatic collection. The later head-bump
investigation below reproduces and fixes it at normal 1-1 block height.

The reported black/blue backdrop after Knuckle remains unresolved. Additional
checks cover repeated selection and ground/air fire, 32 block-impact cases on
both page parities, a dense masonry/coin fixture with bounded VRAM writes,
and controller movement/fire/selection through the first four native 1-1
pipes. These inspect the universal background color; they are limited emulator
fixtures, not proof that the original report cannot occur.

The follow-up suite exposed a separate real MMC5 graphics-bank fault. The new
per-art bank table stores raw ROM bank numbers, but its dynamic `$5116` switch
omitted MMC5's ROM-select bit. Some weapon frames therefore read mirrored
work RAM as sprite data. Water Shield reproduced a renderer loop that stopped
the main loop while lag NMIs continued. The switch now sets the ROM bit;
`bass-special-weapons.lua` watches every active-play `$5116` write and fails the
pre-fix ROM directly. The source Water Shield fixture now completes again.

The Water Shield controller audit compares each completed native controller
read with the packet latched at `$4016`, rather than comparing a cached input
byte on later hardware frames. It checks released, firing, left and right
packets in all four DMA scenarios. Its death fixture uses an armored Beetle
that survives the shield and checks cleanup after actual body-contact death.
These are test-observation corrections; the controller reader was not changed.

The final follow-up run passed all 377 emulator cases across MMC3/MMC5,
including Mario's unchanged 521-frame/19-field baseline replay. The retained
manifest is `build/verification/bass-pickup-followup-summary.json`; the run is
`bass-pickup-followup-suite-final.log`. This supersedes the 365-case checkpoint
for those ROMs. It predates the head-contact and menu changes below.

## Head-contact fix and player outlines

The user's trigger clarification led to a real reproduction in native 1-1:
a head bump on the first upgrade block could collect the item on its next
update, while it was entirely hidden inside the block. Depending on the
takeoff/contact position, Bass's hurtbox penetrates a few pixels into the tile.
Native mushroom emergence normally delays collision checks; the custom upgrade
rise had removed that delay without constraining the exposed collision area.

`InventoryPickupCollision` now disables contact before any pixel has emerged
and clips rising private pickups to the area above their original block top.
The block top is derived from the native rise state and Y position, so bounce,
camera and page boundaries do not move the contact plane. Mature pickups and
native mushrooms/flowers/stars retain their existing collision behavior.

`bass-head-upgrades.lua` checks all eight upgrades over 32 real head bumps,
covering head edges, 144/160 block heights and page seams. The native 1-1
capture also fails the pre-fix ROM and leaves the item uncollected after the
fix. `bass-pickup-exposed.lua` checks that a player above the block can still
collect the exposed pixels before the 48-update emergence completes.

The character menu now has a PLAYER OUTLINES option below the second roster
row. OFF filters explicitly tagged pure-black extra sprite masks from player
poses. Mixed face/skin sprites and black already present in the normal body
palette remain intact. The option applies to previews, lives screens and
gameplay, and persists through actor resets, character changes and deaths until
reset. Hardware OAM never receives the software tag bit.

Normal builds identify those masks from the packed CHR plus each pose's actual
bank mapping via `tools/reference/tag_player_outlines.py`. No reference SWF or
original ROM is needed. `player-outlines.lua` uses real menu controls and checks
preview sprite counts and gameplay/death persistence; `player-outlines-render.lua`
compares all twelve characters' ON/OFF DMA-OAM/CHR pixels. In those previews,
only extra black pixels disappear and every colored/face pixel is preserved.

Hard Knuckle's reported black backdrop is still not reproduced. The native
capture includes grounded and airborne firing and captures each hardware frame
for rendered-pixel review; that result is not a claim that the report is fixed.
Both mappers produced 395 consecutive screenshots. Three sky probes retain at
least one blue pixel in every frame, with no frame showing three black probes;
the universal background palette also stays at `$22`. The probe evidence is in
`build/verification/knuckle-native-render-review.json`. The corresponding
`smb-crossover-mmc3-knuckle-head-review.mp4` and MMC5 clip are silent 60 fps
reconstructions of those screenshots, not an audio/SFX audit.

The final 2026-10-16 run passed **387 emulator cases** across MMC3, MMC5 and
the Mario baseline. Mario's 19 state fields match for all 521 replay frames.
Evidence: `build/verification/player-outlines-head-contact-suite-final.log` and
`build/verification/player-outlines-head-contact-summary.json`.
The earlier run caught an outdated D-pad-help screen address in the menu
test after the requested layout change; the corrected assertion passes here.

| Build | SHA-256 |
| --- | --- |
| MMC3 | `efd974858caebc9f238cd111bb3da7a75c8d0a116cead8b0f757e3e656f06939` |
| MMC5 | `deb7b0b9b196853f5a08c3211b9d39eb045d7287562b4b429ce8896ea2f83471` |

## Remaining source differences

This is the Bass-first inventory migration. Other characters' new inventory
tables are prepared but their legacy gameplay remains enabled until their
weapon migrations are complete. Mega Man shares the new core but still needs
its own source art/palettes and complete Rush behavior checked.

The source audit above closes the previously listed Bass pickup, energy-drop,
sound-selection, flame-orientation and Pharaoh-following gaps. Timing remains
quantized to NES updates, palette/art sharing obeys hardware sprite limits,
and these emulator checks do not establish complete source or cartridge parity.
No physical-console verification or new exhaustive full-level video audit has
been completed for this checkpoint.
