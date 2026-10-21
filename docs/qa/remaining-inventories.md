# Remaining 2.02 inventories and character-menu update

This update uses the pinned `reference/crossover2/extracted/scripts/com/smbc/`
2.02 classes, `main.xml` timelines and default skin sheets. The older hosted
six-character progression is superseded for inventory characters. Pit and
Rygar keep their separate ROM additions. Scrooge is a DuckTales addition,
not a character from Crossover 2.02.

## Playing

There are twelve portrait slots. **Select on Mario switches between Mario and
Luigi**. Select on Bill still switches between Bill and Lance. **Scrooge
occupies the former Luigi slot**. Only the highlighted character's name appears
under its colored preview. Outlines remain a separate option below the roster.

Start pauses gameplay. **Paused Left/Right selects an acquired weapon; paused
Select selects the primary weapon. Start resumes.** Mega Man and Bass also
cycle forward with Select during gameplay. B uses their selected weapon.
For the other inventory characters, Select uses the selected special action.
Simon and Ryu retain Up+B as another special input.

| Character | Individually acquired systems |
| --- | --- |
| Mega Man | Super Arm, Metal Blade, Hard Knuckle, Pharaoh Shot, Charge Kick, Flame Blast, Water Shield, Rush Coil and Energy Balancer. Mushroom grants charging. Special arms use Mega Man's own 2.02 body/arm sheet and suit indexing. |
| Samus | Morph Ball, missiles, Ice Beam, Wave Beam, Varia and Screw Attack. Mushroom grants long beam. Select fires a missile; Down+Select toggles missile mode for B. Ball B plants bombs. Ice survivors stop for 360 logic updates and provide a solid platform. Screw Attack protects contact during a spin and defeats enemies; Varia protects against firebars. |
| Bill / Lance | Laser, flare, machine gun, spread and two Rapid upgrades. Laser emits four segments and cancels old bullets. Rapid changes projectile speed independently of the selected gun. |
| Link | Bombs, bow, magic boomerang, red ring and blue ring, plus the mushroom's short boomerang. Arrow and bomb supplies are separate; the blue ring protects against Link's bomb. |
| Simon | Whip upgrades, dagger, holy water, stopwatch, cross, axe, Double Shot and Triple Shot. Subweapons share hearts. Stopwatch costs five and stops native enemy movement for 180 logic updates while the player remains controllable. |
| Ryu | Shuriken, Fire Wheel, windmill shuriken, Fire Dragon Ball, Jump Slash, sword extension and maximum-ninjitsu scroll. Special attacks share ninjitsu; airborne B with Jump Slash selected activates its spin. Normal flips and Jump Slash have distinct source frames. |
| Sophia | Standard missile triplets, homing missiles, hover, Crusher, wall climbing and ceiling attachment. Mushroom grants hyper shots. Movement abilities require their own acquired upgrade. |
| Scrooge | Cane swing on B and airborne Down+B pogo. Holding pogo continues ground bounces. Native DuckTales OAM/CHR captures supply standing, walking, jumping, cane and pogo graphics. The Amazon music is a native APU capture with a verified 2,304-update loop. Events use the existing shared Mario adaptation. |

Power-up blocks reveal eligible unowned upgrades as actual world objects.
The 48-update rise and exposed pickup rectangle prevent a head bump from
collecting an item still inside its block. Owned upgrades remain excluded;
missed items can return in a later reveal pass. At the completed inventory,
2.02's own fallback policy applies: weapon energy for Mega Man/Bass,
arrow/bomb ammo for Link, missiles for Samus/Sophia, and no replacement item
for Bill, Simon or Ryu.

Enemy ammo drops use the 25% source chance. Samus missiles refill by two;
Link arrows/bombs by two; Sophia standard/homing stocks by six/two. Simon's
small/big hearts add one/five and Ryu's small/big ninjitsu adds five/ten,
with their 80/20 size split. Drop ammo type is captured at spawn, so changing
the selected weapon cannot change an item already on the ground. Shared pools
and maximum stock are used for spending and refilling. Source upgrades and
ammo have independent world/HUD icons and do not recolor native mushrooms.

## Implementation details that affect correctness

- Extra projectiles share the existing ten-slot actor pool. Their update,
  damage, terrain and draw dispatches use distinct IDs, preserving primary
  attacks. Fire Wheel/Dragon pass through defeated targets; holy fire and
  other persistent attacks use per-projectile hit masks/timers.
- Inventory characters use 2.02 enemy health, including the final 1,100-HP
  Bowser. The ordinary buster still needs two hits on a 34-HP brick.
- Rush falls from above, lands with his feet on native ground, waits, springs
  for twelve energy and uses spring/exit/flying frames before departing.
  Summoning/waiting consumes no energy.
- Converted weapons use a rotating CHR-family producer order. Only sprites
  matching the currently selected physical family are emitted in a frame.
  Empty draws and inactive source-audio overlays have quick exit paths.
- Mega Man's original body graphics are packed into shared banks while
  retaining the common projectile tile prefix and logical pose table. This
  frees CHR for new poses without increasing the 256-KiB cartridge limit.
- Audio overlays save the music image and claim only the NSF clip's channels.
  Bank changes inside NMI use explicit save/restore, avoiding the main
  thread's self-modifying far-call trampoline. Mega Man's audio returns to a
  fixed-bank wrapper before restoring his active graphics bank.
- Projectile motion helpers remove expired shots through local returning
  paths. They do not jump out to an outer update loop with a return address
  still on the stack.
- Scrooge is included in portraits, power-up color/pose transitions, exits,
  firebars and the ordinary/boosted spring tables. Luigi's gameplay ID and
  physics remain intact behind Mario's Select alternate.

## Verification and limits

`tools/verify.py --mmc5` registers the inventory, energy-drop, Rush, Samus
passive, source-audio and Scrooge tests alongside the existing regressions.
The final `build/verification/summary.json` records the exact ROM hashes and
completed cases; `remaining-release-suite.log` records the full run. Explicit
arena, inventory and actor fixtures are identified in the Lua tests. They are
not controller-only full-level clears.

The audio oracle independently compares 3,448 register values across seventeen
new NSF effects, including clip lengths, channel ownership and restoration.
The existing Bass source-audio and DPCM checks remain separate. New inventory
checks collect real private pickups through native collision, then use actual
controller input and check source costs and projectile pools. Drop checks kill
a native Goomba with controller attacks and walk into its world ammo, including
a selection change after the item appears. Big heart/ninjitsu checks are separate.

The OAM checks sample completed draw transactions. A physical-frame callback can
interrupt a partly built CPU sprite buffer; that buffer has not yet been sent
to the PPU. Existing lag checks separately verify committed OAM/CHR consistency.
The Bill differential oracle preserves its original 2,400 cases and transforms
only newly spawned gun velocities and their first integration step from the
2.02 speeds, rather than replacing the oracle with current emulator output.

This is a functional NES adaptation, not a certification of frame-perfect Flash
parity. Native tile collision boxes and Q8.8 extra-projectile positions are
quantized. Sophia's homing steering remains axis-directed rather than the
source's continuous `atan2` vector/rotation; sprite orientations and some
weapon impacts/flashes are approximations. Source default palettes are reduced
to available shared NES colors. The auxiliary CHR window and eight-sprite
scanline limit require flicker. Long looping clips are bounded by the captured
180 updates; MP3-only beam effects and Scrooge's common action sounds retain
NES adaptations. Scrooge does not implement DuckTales' entire object-carrying,
chest-loot or health system. No new all-level clear, PAL, physical cartridge or
hardware/flash-cart verification is claimed.

## Full inventory suite build

The final run passed **429 emulator cases** across MMC3/MMC5, with all nineteen Mario state fields matching the original baseline for 521 frames. Hardware was not tested.

- MMC3: `a6e038cec9a263d3d42a815b6162b3823ca6d81f558c65b4a5c6bacab630101e`
- MMC5: `8954412ad1eabcebb2a4ee177dd3252091dd79d1bf30738e83ae1275a38455f9`

## Scrooge graphics correction

The subsequent Scrooge graphics build corrects native DuckTales facing:
unflipped native tiles face left, and the Right-input captures have horizontal
flip set. Standing, walking and action poses now follow the renderer's
right-facing convention. The static select portrait was stale and incomplete;
regenerating Scrooge now also rebuilds the menu CHR and nametable from the full
standing sprite, including cane and feet.

Twelve focused emulator cases passed across MMC3/MMC5. The new pixel oracle
compares the actual menu background and DMA OAM/CHR against independent native
DuckTales silhouettes: the complete 24x29 standing portrait and all three walk
poses in both controller directions. Related checks cover roster navigation,
Mario/Luigi alternates, Scrooge launch/pogo, all twelve outline previews, lives
portraits and both power-up transitions. Screenshots were inspected for both
mappers. The full 429-case suite above was not repeated for this asset fix.
Current hashes and logs are recorded in
`build/verification/scrooge-graphics-summary.json`.
