# Crossover parity audit

The later [twelve-character source re-audit](../qa/roster-source-audit.md) supersedes assumptions below where it identifies additional mismatches, including Simon's dry fall cap and overload in all whip forms, and the added roster's movement, weapon and asset errors. Passing implementation regressions is not proof of source parity.

The [2.02 inventory migration](../qa/remaining-inventories.md) supersedes the old two-power-up progression and enemy health below for inventory characters. This historical numeric audit remains the reference for the older movement model.

Reference: the hosted SWF pinned in `crossover.json`, rather than the later v3
release. Values use a 60 Hz update and coordinates halved to NES pixels.

## Implemented behavior

| Behavior | Hosted rule used by this port |
| --- | --- |
| Start | Power 1, helmetless, ordinary buster |
| Mushroom | Power 2, helmet and charge; jump power unchanged |
| Flower | Power 3, red/yellow suit and stronger fire shots |
| Horizontal acceleration | 600 Flash px/s² = 1/12 NES px/frame² |
| Running cap | 150 Flash px/s = 1.25 NES px/frame |
| Coasting | Multiply by `(1e-7)^(1/60)`; snap below 5 Flash px/s |
| Jump | -580 Flash px/s = -4.833333 NES px/frame |
| Gravity | 1100 Flash px/s² = .15277778 NES px/frame² |
| Jump release | Multiply upward speed by `(1e-6)^(1/60)` before gravity |
| Dry fall cap | 700 Flash px/s = 5.833333 NES px/frame |
| Underwater | Cap .75; jump -4.583333; gravity .069444 NES units/frame |
| Underwater fall cap | 250 Flash px/s, applied before gravity |
| Slide | Down+A; speed 2.5, distance 62.5 NES px; stop after crossing endpoint |
| Water slide | Speed 1.875; distance 50 NES px |
| Vine | 130 Flash px/s; A/B new presses ignored; fresh horizontal input exits |
| Enemy bounce | -2.5 NES px/frame |
| Spring | Default -3.333333; boosted -7.166667 NES px/frame |
| Shoot pose | 200 ms / 12 frames |
| Charge onset | 550 ms / 33 frames |
| Outline stages | 800 ms / 48 frames; 1100 ms / 66 frames |
| Full charge | 1450 ms / 87 frames |
| B release | Weak shot from frame 48; full shot from frame 87 |
| Sliding attack | Cannot shoot; releasing a charge discards it |
| Projectile speed | 430 Flash px/s = 3.583333 NES px/frame |
| Normal / weak / full damage | 25 / 50 / 75 |
| Fire / weak fire / full fire damage | 34 / 50 / 100 |
| Full charge piercing | Passes defeated enemies; stops on survivors/boxes |
| Brick | 34 health: two normal hits, one fire hit |
| Question box | Activates on a shot |
| Coin brick | Per-block 14-coin limit and six-second window |
| Normal death | 300 ms particle delay + 2500 ms before losing life |
| Pit death | 2500 ms delay |

Enemy health includes Goomba 100, Koopa 125, Piranha 75, Hammer Bro/Lakitu 200,
Spiny 100, Blooper 175, swimming Cheep 75, flying Cheep 50, and Bowser 600 or 900
in the hammer-throwing worlds. Beetles, Podoboos, and Bullet Bills block shots.
Automated damage assertions cover Goombas, bricks, and full-shot piercing, rather
than independently exercising every species.

Art uses the hosted body, independent head/hair outline, projectile states, and
death-particle frames. Charge colors use nearest NES palette entries. Native music
routing and charge onset/loop/release are checked on both mappers. Mario's title
switch size regression is covered too. See `build/verification/summary.json` for
the exact tested ROM hashes and the current test cases. The OAM regression also checks
that pose changes and injury blinking leave no old sprite fragments, rejected
flipped draws preserve prior OAM, and the full twelve-particle burst stays drawn.
Block-alignment cases check the rendered bounce and reward column against the
struck map cell, including leading edges, wide charges, and page crossings.

## Known differences and unverified boundaries

- Entry teleport remains incomplete. Pickups now use the held pose, 60-frame freeze, replacement-color cycling and power-form changes; scripted transitions still retain SMB flow.
- A surviving enemy records the two-frame flash timer and plays a hit effect,
  but the white silhouette flash is not rendered yet.
- Enemy collision uses native positions with an expanded body box, rather than
  every Flash enemy's fractional hurtbox. Solid probes/player collision profiles
  are rounded to NES pixels.
- Half-pixel shot spawn heights and some ceiling-clearance boundaries remain
  rounded. Active-pose water boundaries use the source hit rectangles and
  fractional positions; see `water.md`. Slide continuation under ceilings needs more edge coverage.
  The source's low-speed snap during direction reversal also needs a boundary audit.
- The intro recording starts partway through MM2 Boss Show; this port starts the
  full sequence. Short effects have not all been matched waveform by waveform.
- Injury, invulnerability, pipes, flagpoles, and scripted transitions retain some
  SMB states/timers. Equivalence to every hosted transition is unverified.
- Outer death particles are opaque; the hosted build uses alpha blending. Crowded
  scenes are subject to the NES's sprite limit and may flicker/drop sprites.
- No all-32-level completion replay, full enemy matrix, PAL pass, or physical
  hardware/flash-cart test has been performed.

These are open implementation/verification items. The current build should not
be described as fully or frame-exactly matching the website.


## Additional roster

Samus has source-based immediate movement, jump/spin, Morph Ball, three beams and three bombs, short/long/wave upgrades, bomb boost, upward firing, native Metroid music, and a six-piece death burst. Tests cover trajectory constants, native pickups, combat, terrain protection, both pipe sides, OAM and respawn. Her first two suits can head-break bricks; the hosted wave suit bumps them instead. Some half-pixel weapon offsets and ceiling boundaries remain rounded.

Bill, Link and Simon are playable with all three power states, hosted graphics, their main/special weapons, shared enemy health and block interactions, music, lives portraits, and upgrade animation. Their controls are documented in the README. Camera follow, projectile allocation, damage and native audio routing have dedicated emulator checks.

These later modules are not a complete frame-exact port. Outstanding details include Bill's six-shot machine-gun burst pause and some animated aiming combinations; Link's exact boomerang acceleration/turning and full death-spin sequence; Simon's fractional fall cap and corpse motion; source-specific spring behavior for the later roster; per-enemy white hit silhouettes; and some scripted level-entry/exit animations. Simon's second jump, replenishment on a stomp, and resuming movement after clearing a wall are implemented; a replay clears all four native 1-1 pipes. Normal Bill/Link/Simon deaths currently use simplified poses/timers.

Bill's area music is identified as Contra Jungle, Energy Zone, Base, and Alien Lair. Link's overworld/water/castle and win cues match Zelda's overworld/title/dungeon/Triforce music. Simon's overworld/water/castle/hurry/win match Vampire Killer, Wicked Child, Nightmare, Poison Mind, and Game Complete. The exact Link/Simon underground recordings and intro edits are not positively identified; current native substitutes are retained. Short effects are not all matched waveform by waveform. Contra DPCM percussion and Zelda DPCM effects remain disabled pending fixed-bank sample storage.

Palette sharing constrains some weapon colors. The shared world-object palette retains red/white/tan in every Simon form, including upgrade flashes. His axe uses a separate black outline and white/tan blade tones in place of the hosted purple shades. Link's secondary weapon palette is an approximation. NES palette-compatible colors are merged where possible; Simon's separate black outline requires extra sprites. The long flame whip still exceeds eight sprites across its widest row. The complete Mega Man/Bill/Link/Simon sprite list rotates hardware priority, so overloaded rows alternate visible parts. Hardware sprite limits still cause flicker in crowded scenes.


## Twelve-character roster

Pit, Rygar, Luigi, Bass, Ryu and Sophia are playable additions. They use dedicated sprites, signatures, upgrades and lives portraits, with collision, water, combat, sound-mixing and respawn checks on both mappers. Bass now has individually acquired weapons, per-weapon energy, selection and stored-inventory recovery. Its seven special attacks have focused native-fixture coverage; exact contact effects, weapon-specific sounds and some animations still differ. The other advanced inventory migrations are incomplete. Pit uses unfinished published source plus original NES art; Rygar is a new NES adaptation. See [the detailed implementation and limitations](expanded.md) and [Bass inventory verification](../qa/bass-inventory.md).
