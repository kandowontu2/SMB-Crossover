# SMB Crossover for NES

A native NES adaptation built on [SMB1Base](https://github.com/smbstudio/smb1base), with **13 playable characters across 12 selection slots**, plus Lance Bean as Bill's alternate: Mario, Mega Man, Samus, Bill Rizer, Link, Simon Belmont, Pit, Rygar, Luigi, Bass, Ryu Hayabusa, Sophia III, and Scrooge McDuck. Select on Mario switches to Luigi; Scrooge occupies the former Luigi slot. MMC3 and MMC5 are supported.

The guest characters use code constants and art extracted from [the requested hosted game](https://www.smbgames.be/smb-crossover.php). This is a playable port in progress. [The parity audit](docs/reference/parity.md) records differences from the Flash version.

The current provisional v49 build corrects Ryu's upward block response and preserves the START/OPTIONS menu. Regression coverage comprises759 unchanged passes plus the independently source-backed ceiling fixture on both mappers:761 staged passes, with the original two failures retained. Focused head and behavior checks also pass. Full roster routes, all upgrades, source geometry and final recordings remain in progress; see [the current evidence and limits](docs/qa/roster-provisional-v49.md).

Bass's [inventory audit](docs/qa/bass-inventory.md) covers separately collected
weapons, complete source HUD/world icons, enemy energy drops, the exact NSF
effect choices, Water Shield's source clip adapted to native DPCM, and weapon
contact/charging rules. The [remaining inventory update](docs/qa/remaining-inventories.md) covers the other 2.02 inventories, attack effects, Luigi alternate and Scrooge.

Bass's upgrade blocks choose randomly from eligible weapons. Already owned
upgrades are excluded; missed upgrades can return on a later pass. After the
complete inventory, blocks provide large weapon energy instead.

The [roster corrections](docs/qa/roster-fixes.md) resolve the original audit's 27 measured mismatches, along with art, input, death, audio and rendering findings. All 78 independent numeric source rules now match on both mappers. Remaining inventory, effects, audio and collision differences are documented; none of the twelve characters is certified as source-identical. The [original audit](docs/qa/roster-source-audit.md) retains its historical findings and checkpoint hashes.

## Play

Open `build/smb-crossover-mmc3.nes` or `build/smb-crossover-mmc5.nes` in a NES emulator. The static title offers START and OPTIONS. Up/Down chooses a row; A or Start confirms. START opens character selection. Left/Right cycles the roster; Up/Down switches between its two rows. Select on Mario toggles Mario/Luigi; Select on Bill toggles Bill/Lance. On other portraits it advances the selection. Only the highlighted character's name appears beneath the color preview. A or a fresh Start press begins; B returns to the title. Start pauses during gameplay.

OPTIONS contains **PLAYER SHADOWS** (default OFF) and **BEHAVIOR** (default 1.0).
Up/Down highlights a setting; A, Start, Select, Left or Right toggles it. B returns
to the title. Shadows OFF omits extra black mask sprites while retaining normal
body colors and face details. Behavior 1.0 lets the roster stomp ordinary enemies;
2.02 retains the previous character-specific contact rules. Special body attacks,
hazards and underwater rules keep their existing priority. Preferences persist
through selection, gameplay and deaths until reset. Character select contains
only character selection. See [menu validation](docs/qa/menu-options-v49.md).

| Character | Controls and upgrades |
| --- | --- |
| Mario | Original SMB controls and power-ups |
| Mega Man | A jumps; Down+A slides; B fires the selected weapon. Starts helmetless. Mushroom adds helmet/charging. Further blocks reveal separately acquired weapons. Select cycles acquired weapons; paused Left/Right cycles backward/forward and paused Select returns to the buster. His eight special weapons include Rush Coil; Rush falls in on the facing side (Up summons directly above), waits, springs for 12 energy and departs. Special weapons use his own source arm poses and suit colors. |
| Samus | A jumps; Down crouches, then a second Down enters Morph Ball when acquired; A or Up exits. B fires a beam or plants a bomb in ball form. Up+B fires upward. Mushroom adds long beam. Blocks then supply Morph Ball, missiles, Ice Beam, Wave Beam, Varia and Screw Attack separately. Select fires a missile; Down+Select toggles missile mode, then B uses missiles. Ice freezes surviving enemies; Varia protects against firebars; Screw Attack damages during a spin. Her first two suits can break bricks with her head. |
| Bill / Lance | Select while highlighting Bill toggles Lance Bean, with his own Crossover 2.02 graphics. Both use the same Contra controls and upgrades: A jumps; B shoots; D-pad aims, including diagonals. Down crouches. Blocks supply the machine gun, spread, laser, flare and two Rapid upgrades individually. Laser launches four segments; flare travels in a circle around its moving center. Rapid upgrades increase bullet speed. |
| Link | A jumps; B swings the sword; Select uses the selected boomerang, bow or bomb. Up/Down in the air thrusts the sword. The short boomerang also works without a mushroom, as in 2.02. Mushroom strengthens the sword; blocks supply bow, bombs, magic boomerang, red ring and blue ring. Arrows/bombs use separate ammo; blue ring protects against his own bomb. |
| Simon | A jumps; release and press A again in midair to double jump. B uses the whip; Up+B or Select uses the selected axe, dagger, holy water, cross or stopwatch. Down crouches. Blocks supply whip strength, subweapons and Double/Triple Shot. Subweapons share hearts; the stopwatch costs five and freezes enemies for three seconds. |
| Pit | A jumps; B fires arrows, including while ducking; Up+B fires upward. Select uses the hammer. Two arrows can be active. Mushroom adds long arrows; flower adds fire arrows and winged flight: release and press A again in the air, then hold for up to one second of lift. Landing recharges flight. |
| Rygar | A jumps; B throws the returning Diskarmor, including while ducking. Down crouches. Its chain extends/retracts with the disk; upgrades increase reach. Wall contact starts its return and enemies take damage once per throw. |
| Luigi | Mario's movement with a modestly higher jump and slightly less traction. A jumps; releasing it shortens the jump. B runs and throws fireballs after the flower. Select while highlighting Mario chooses Luigi in that same slot. Mushroom gives his large form. Fireballs bounce and preserve blocks. |
| Bass | A jumps; release and press A again for a second jump. Down+A dashes; jump during the dash for extra height and momentum. Hold B for the buster; the D-pad aims. Mushroom increases its shot limit from three to four. Further blocks reveal Super Arm, Metal Blade, Hard Knuckle, Pharaoh Shot, Charge Kick, Flame Blast, Water Shield and Energy Balancer separately. Select cycles acquired weapons; paused Left/Right cycles backward/forward and paused Select returns to the buster. B uses the selected weapon; Charge Kick uses Down+A. The HUD shows its source icon, name and remaining energy. |
| Ryu | A jumps; B swings the sword; Up+B or Select uses selected ninjitsu. Jump against a wall to cling; Up/Down climbs and A jumps away. Blocks supply shuriken, Fire Wheel, windmill shuriken, Fire Dragon Ball, Jump Slash, sword extension and the maximum-ninjitsu scroll. Airborne B with Jump Slash selected spins the blade. Ninjitsu shares one ammo pool. |
| Sophia III | A jumps. B fires the cannon; Up+B fires upward. Mushroom adds hyper shots. Missiles, homing missiles, hover, Crusher, wall climbing and ceiling attachment are separate block upgrades. Select launches a standard missile triplet or a homing missile. After acquiring hover, press A again in the air and hold; fuel regenerates when inactive. With the corresponding upgrades, Up attaches to a wall/ceiling. Aim and fire away from an attached surface; A releases the ceiling. |
| Scrooge | A jumps. B swings the cane. Down+B while airborne engages pogo; holding it continues bouncing after landings. DuckTales body/cane/pogo frames and Amazon music come from native captures. |

Samus cannot stomp ordinary enemies in Crossover 2.02. After collecting Screw Attack, her active spinning jump damages eligible enemies; ordinary contact still hurts her.

All thirteen and Lance appear on the lives screen. Guest growth pickups hold the current pose and run a 60-frame color/form transition; Luigi alternates small/large forms when growing. Mega Man/Bass inventory upgrades are separate pickups and do not repeat the growth transition. Guest weapons use enemy health, activate question blocks, and damage breakable bricks while preserving terrain. Luigi's fireballs preserve blocks. Mega Man's ordinary buster still takes **two hits** to break a brick.

For Samus, Bill, Link, Simon, Ryu and Sophia, **pause with Start, use Left/Right to select an acquired weapon, and press Start again to resume**. Paused Select returns to the primary weapon. The HUD shows the selected item and ammo. Mega Man/Bass also cycle with Select during play.

The [special-button audit](docs/reference/special-attacks.md) distinguishes the linked game's S attacks from Crossover 2.02's larger weapon inventories. The [Bass inventory update](docs/qa/bass-inventory.md) records weapon selection, HUD and interrupt fixes and their remaining limits. The [walking, brick, flight and music update](docs/qa/walk-flight-update.md) covers the preceding changes.

Water follows the pinned hosted source: Mario and Luigi press A repeatedly to paddle; the other guests use underwater ground jumps, with Simon and Bass retaining their second jumps. Luigi shares Mario's swimming and whirlpool behavior. Gravity and jump release remain character-specific for the other guests. Bottom walking caps at 0.75 NES pixels per frame, while airborne movement keeps each character's own limit. Mega Man can slide underwater; Samus can use Morph Ball and bombs. Water-surface detection follows the active hit rectangle, including fractional pixels. See [the water reference](docs/reference/water.md).

Guest projectiles receive reserved OAM slots and rotate allocation order. Mega Man and all guests from Bill onward also rotate the complete hardware sprite list, so crowded rows share visibility instead of permanently losing the same body parts. Bill's upgraded bullet uses one sprite. Guests preserve the world's red/white/tan palette for mushrooms and other objects; Simon's axe uses black outlines with white/tan blade tones. Redundant body color layers are combined where NES palette colors match. The NES limit remains eight sprites per scanline.

Guest lag interrupts retain the physical CHR banks with the previous hardware OAM. New pose banks are applied on the next complete frame; a late interrupt cannot combine old sprite tiles with a new graphics bank. MMC5 retains the NES CPU speed and eight sprites per scanline; dense crowds can still slow down and flicker. The [matched crowd benchmark](docs/qa/crowd-performance-v33.md) separates logic speed, redraws and hardware sprite loss. The ordinary-enemy visibility shortcut improves several crowded scenes while preserving all 14,400 paired gameplay-state samples; both ROMs pass 731 component regression cases.

The [v34 component update](docs/qa/roster-audit-v34.md) fixes repeated camera pan at guest wall contacts, restores Luigi's native wall collision, and adds Link/Simon/Ryu injury behavior and source DMC cues. It covers 753 component cases across both mappers through an initial frozen run and four corrected fixture invocations. Known source geometry and crowded-scene performance gaps remain documented.

The [v35 crowd update](docs/qa/crowd-performance-v35.md) skips a redundant bounding-box calculation for fully visible ordinary enemies. Both ROMs pass one frozen 755-case regression run, and all 14,400 matched crowd gameplay samples remain unchanged. Several scenes deliver frames more often; Samus/Mega Man still have 30-draw crowd cases. Further source fixes, performance work and final roster recordings remain in progress.

The [v36 update](docs/qa/crowd-performance-v36.md) caches filtered animation poses, avoids redundant banked work, and prevents stale wall contact from cancelling Ryu's ground jump. All 14,400 paired crowd gameplay samples remain unchanged. Its 759 component slots are covered by a frozen run and four corrected input-fixture invocations; the original one-frame input failure is retained. Dense Samus/Mega Man scenes still skip redraws, and final roster verification and recordings remain in progress.

The [v37 follow-up](docs/qa/crowd-performance-v37.md) reduces score, sprite-header and empty weapon work. Its 759 component slots include two corrected bank-qualified observer invocations after the original Link fixture failed; the negative is preserved. All 14,400 matched crowd gameplay samples remain unchanged. Several dense scenes improve, three draw less often, and Samus still has 30-draw cases. The audio-budget profile includes the preceding NMI and identifies further MMC5 mixer work to optimize.

The [v39 audio and ceiling update](docs/qa/crowd-performance-v39.md) passes one frozen 761-case regression run on both mappers. It fixes Samus's ceiling displacement and firebar cache initialization, and reduces MMC5 native audio work. Samus's four-Goomba walking scene improves from 30 to 60 redraws per 60 updates compared with v37; the heavier six-Goomba scene improves from 90 to 63 physical frames but still skips redraws. All 14,400 paired gameplay samples remain unchanged. Four scene regressions against v37, ongoing Mega Man lag, source geometry gaps and unfinished final roster recordings remain documented. Outlines default off and their option row is gold.

The [v40 audio update](docs/qa/crowd-performance-v40.md) passes one unchanged-fixture 761-case run. MMC5 uses its hardware multiplier for native MM3 audio and omits unused state copies; MMC3 stays byte identical to v39. Compiled CPU and actual hardware-write comparisons preserve sound output. All 8,400 paired crowd gameplay samples match across seven characters. Mega Man's four-Goomba standing scene improves from 30 to 44 redraws per 60 updates, while the crowded walking case still skips redraws. Source geometry, further lag work and final roster recordings remain in progress. Accepted ROMs are in `build/checkpoints/roster-audit-v40/`.

The [v41 component update](docs/qa/roster-component-v41.md) fixes Simon's unused air jump after walking off support and skips empty Mega Man/Bass special-weapon loops on MMC5. Staged validation covers all 761 current-ROM slots: MMC3 stays byte identical to its complete initial checks, and all MMC5 slots run again after a retained Water Shield budget failure was corrected. All 9,600 paired crowd gameplay samples match. Default outlines-off four-Goomba walking redraws improve from 30 to 35 for Mega Man and from 37 to 44 for Bass. Dense scenes still lag; small counterexamples, source geometry and a newly traced catch-up-frame HUD race remain documented. Accepted component ROMs are in `build/checkpoints/roster-audit-v41/`; final roster fixes and recordings remain in progress.

The [v48 terrain update](docs/qa/roster-component-v48.md) reduces MMC5 settled-Goomba collision work. All 761 unchanged-fixture regression cases, 82,272 strict compiled CPU cases, 128 actual native receipts and fresh 403-file rebuilds pass. All 13,200 paired crowd updates preserve 204 gameplay fields; six-Goomba rows with equal redraw counts save approximately 1,343 foreground CPU cycles/update. Dense scenes still skip redraws, and timing/visibility counterexamples remain, including Ryu physical-frame regressions. All 1,199 captured RGB frames match; ordered same-frame audio values and ownership match, while literal PCM differs with write timing. MMC3 remains byte identical to v45–47. Outlines default OFF and the option row is gold. ROMs are in `build/checkpoints/roster-audit-v48/`; full roster/weapon/recording work remains open.

The [v47 renderer update](docs/qa/roster-component-v47.md) reduces MMC5 walking-Goomba sprite work. All761 unchanged-fixture regression cases,14,608 compiled CPU cases plus128 native receipts and fresh402-file rebuilds pass. All13,200 paired crowd updates retain204 gameplay fields. Six-enemy repeated tests save about128â€“143 CPU cycles per update; dense scenes still skip redraws and individual timing/visibility counterexamples remain. All1,199 captured RGB frames match; same-frame ordered APU/queue data and ownership match, while literal PCM differs with register-write timing. MMC3 stays byte identical45/46. Outlines default OFF with a gold option row. ROMs are in `build/checkpoints/roster-audit-v47/`; full roster/weapon/recording work remains open.

The [v46 component update](docs/qa/roster-component-v46.md) skips empty Samus beam/bomb loops on MMC5, saving142 CPU cycles per idle update. All761 unchanged-fixture regression slots,8,508 compiled CPU cases,138 native caller cases per mapper and fresh401-file archive rebuilds pass. The paired3,600-update crowd check retains all204 gameplay fields, but redraw/visibility counts do not improve. MMC3 stays byte identical45. Outlines remain off by default with a gold option row. ROMs are in `build/checkpoints/roster-audit-v46/`; dense-scene lag and the full roster/weapon/recording audit remain open.

The [v45 component update](docs/qa/roster-component-v45.md) repairs normal Ryu sword admission against Koopa head rectangles and makes Bill Flare pass through non-brick terrain. All761 regression slots pass after a bank-aware Link test-hook correction; the original failure is preserved. Source-backed native components, compiled helper checks and fresh archive rebuilds pass. Dense-crowd flicker and the full roster/weapon/recording audit remain open. ROMs are in `build/checkpoints/roster-audit-v45/`.

The [v44 component update](docs/qa/roster-component-v44.md) reduces MMC5 native tile-probe work by33 CPU cycles per probe and fixes Ryu active Jump Slash cancellation on wall attachment. All761 unchanged-fixture emulator checks pass; paired crowded-scene and repeated-phase tests preserve all204 gameplay fields. Dense-scene flicker and the full roster/weapon/recording audit remain open. ROMs are in `build/checkpoints/roster-audit-v44/`.

The [v43 component update](docs/qa/roster-component-v43.md) corrects Ryu wall/vine sword admission and rejects wall Jump Slash while preserving legal wall projectiles and airborne attacks. All 761 unchanged-fixture emulator checks and 68 independent source-derived Ryu cases pass. ROMs are in `build/checkpoints/roster-audit-v43/`; full routes, all weapon/upgrade checks, audiovisual review and recordings remain in progress.

The [v42 component update](docs/qa/roster-component-v42.md) protects catch-up graphics publication, bounds catch-up work, and reduces MMC5 native MM/Bass audio overhead. All 761 unchanged-fixture emulator slots pass in one full run; 20,326 compiled audio cases and 6,000 paired crowd updates retain their checked state. The HUD corruption cause, rejected prototypes, individual redraw regressions and a remaining three-frame native-input gap are documented. Outlines stay off by default with a gold option row. ROMs are in `build/checkpoints/roster-audit-v42/`; dense-scene lag and the full roster/weapon/recording audit remain in progress.

The loading screen also waits for queued VRAM columns to be consumed before producing another set, preventing pipe-exit background corruption during lag.

Level exits reserve actor slots for the pole and castle flags even when enemies fill the pool. Springs retain their actor index during guest launches, and high rebounds above the screen stay alive. Castle firebars render after guest OAM clearing with graphics independent of the player. See [the world-object and Lance checks](docs/qa/world-objects-lance.md).

The camera follows every character. Scroll-register timing is checked during normal movement, charged shots, and overloaded frames with native enemies active. Brick fragments render after sprite allocation, keeping debris visible without overwriting characters on skipped draw frames. Each guest has native NES music. Shared block, coin, reveal and flagpole sounds mix with it; MMC5 uses its two extra pulse channels for those tones, preserving both native pulse music voices. Brick shatter uses the NES noise channel. MMC3 temporarily shares the corresponding native voices.

## Build

Python 3 and Pillow are required. Windows uses the supplied cc65 tools; elsewhere install cc65 and put `cl65` on PATH.

```sh
python tools/build.py
python tools/build.py --mapper mmc5
python tools/build.py --baseline
```

Both NES 2.0 cartridges contain 512 KiB PRG, 256 KiB CHR, and 8 KiB volatile WRAM. Generated assets, the packing fixtures and audio provenance are included; building requires no downloaded reference files, original game ROMs, Java or ffmpeg. Pillow is used by the automatic injury-art packing step. [Architecture notes](docs/architecture.md) describe optional regeneration and source provenance.

## Verify

Mesen 2 is required. Set `MESEN` to its executable or use `--emulator`; the runner also detects `C:/mesen2/Mesen.exe`.

```sh
python tools/verify.py --mmc5
```

The suite covers the selection slots and alternates, lives portraits, movement, upgrades, multi-hit combat, brick/question-block behavior, protected terrain, pipes, music, death/respawn, OAM allocation, and camera/HUD scrolling. It compares 19 Mario state fields against the baseline for 521 frames. Fixtures combine controller replays with explicit emulator state setup.

Results and exact ROM hashes are saved in `build/verification/summary.json`, with adjacent screenshots and logs. These checks are not a complete playthrough or a physical cartridge test.

Separate [World 1-1 controller replays](docs/qa/world-1-1.md) cover the original six characters at their pinned checkpoint. The [added-character replay audit](docs/qa/world-1-1-expanded.md) contains twelve further videos, both routes for each new character, and timestamped unresolved findings. The [Contra performance audit](docs/qa/contra-performance.md) measures the later spread-shot optimization on both mappers. The six added characters also have native pipe traversal, water, combat, pickup, lives, sound-mixing and respawn fixtures on both mappers. See [their implementation notes](docs/reference/expanded.md) for source versions and remaining parity differences.

[SMB1Base's original README](docs/SMB1BASE.md) retains its credits. Game code, artwork, and music retain their original authorship.
