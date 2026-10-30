# SMB Crossover for NES

Play Super Mario Bros. with characters from across the NES library, each bringing their own movement, weapons and upgrades.

This is a native NES adaptation of [Super Mario Bros. Crossover](https://www.smbgames.be/smb-crossover.php), built on [SMB1Base](https://github.com/smbstudio/smb1base). The latest expanded MMC5 development checkpoint has **52 playable characters and alternates**, with **80 visible identities across 32 selection slots**.

**Status: playable, actively developed, and unfinished.** Character behavior, graphics, sound and performance are still being tested and corrected. MMC5 is the recommended target for the full roster.

The October 30 playable-roster update (`18de0155`) unlocks **Super Maaa, Rogue Dawn, Goku, Gimmick and Donkey Kong**. **28 starred identities remain COMING SOON.** Kamikaze Mario now uses sprites from **Kamikaze V1**, with Mario's native drawing, physics, abilities and palette. Donkey Kong has a larger full-body preview; Burns, Smith, Iron and Beans use their original Contra Force gameplay sprites and colors. Rogue Dawn's new-game health, recursive area reset, and missing menu/lives portraits are fixed. Checks include every menu identity, Rogue's cold-start movement, a Kamikaze 1-1 clear, and 288 comparisons with native Mario. Performance and broader roster playthroughs remain in progress. See the [exact builds, checks and limits](docs/qa/expanded-playable-roster-2026-10-30.json); the frozen source is retained under `docs/qa/checkpoints/2026-10-30/expanded-playable-roster/`.

The earlier October 30 roster-menu checkpoint (`5b09a3ed`) introduced the four-row, 80-identity menu, with 47 playable and 33 pending identities. Arthur occupies the final slot; Quick Man joins Bass/Roll and Thomas joins Ryu/Shinobi. See its [checks and limits](docs/qa/full-roster-menu-80-2026-10-30.json). These later development checkpoints are separate from the prepared build commands below, which target the earlier 37-identity build; their exact source inputs are retained in the linked checkpoint archives.

The October 30 update (`ec2f23ed`) keeps Alex and Ryan's original black details visible with **Shadows ON or OFF**. It changes only their two rendering checks. Both characters passed menu, lives-screen and gameplay checks with each setting, alongside comparisons of all 18 poses in both directions against the original graphics. Arthur already retains his black detail independently of the setting; crowded scenes still cause sprite loss and remain under review. See the [repair checks and limits](docs/qa/required-player-ink-2026-10-30.json).

The October 28 development build (`85afad50`) removes an unnecessary second weapon scan during Bill/Lance's ordinary gunfire and moves their selected-gun icon clear of the HUD lettering. Bill passed the focused Hard gun suite and cleared 1-1 without deaths or cheats on this exact build. The ordinary MMC3/MMC5 ROMs remain unchanged. Laser/Flare's intermittent weapon indicator, crowded player sprites, and broader lag work remain open; this is not a constant-frame-rate claim. See the [checks and remaining limits](docs/qa/bill-hud-inert-adoption-2026-10-28.json).

The preceding October 28 development build (`32694243`) fixes Zelda II Link's Glove failing to break bricks in Easy mode. The original failure was reproduced in the emulator; the repair passed earned-upgrade tests in both modes and a canonical rebuild. A separate native check verified visible spell and upgrade panels and restoration of the world graphics when closing the menu. See the [repair checks](docs/qa/zelda2-glove-adoption-2026-10-28.json) and [menu checks and limits](docs/qa/zelda2-panel-current326942-native-v2-2026-10-28.json).

The preceding October 28 development build (`ee1152a4`) fixes Chip/Dale's repeated HP updates running past the rendering deadline, their brief HP0 startup display, SMB3 forms retaining protection after damage, and Darkwing being pulled into terrain by a falling Arrow. Chip, Dale, Mike, Darkwing, Vic Viper and both SMB3 variants have cleared 1-1 on this build without deaths or cheats. Both SMB3 variants also passed current focused gameplay tests and a separate native check of the Tanooki statue graphics, protected contact and release. See the [checks and limits](docs/qa/roster-rendering-injury-adoption-2026-10-28.json).

The preceding October 27 development build (`5a0a37a9`) corrects Kirby's copied-enemy icon and green-shell colors, and restores Mike's original bat swing shapes and timing. The individual repairs passed focused native tests; the combined build preserves every other ROM byte and is still undergoing the full roster audit. See the [repair checks and limits](docs/qa/kirby-mike-polish-adoption-2026-10-27.json).

The preceding build (`bdf9ca2b`) preserves earned Castlevania equipment and hearts when gaining a 1-Up, and removes a second stopwatch countdown. Source checks cover Grant, Sypha and Alucard in both modes; a native Grant test confirms a real 1-Up preserves his earned dagger and hearts. Full-roster testing remains open. See the [repair checks and limits](docs/qa/cv3-life-watch-adoption-2026-10-27.json).

The preceding build (`ab221e81`) fixes missing Mega Man/Proto Man body sprites during weapon attacks and a redundant Proto Man palette update that ran past the rendering deadline. Both passed their Hard-mode earned-weapon tests and cleared 1-1 with no deaths or cheats, reaching playable 1-2. See the [repair checks and limits](docs/qa/mega-proto-body-palette-adoption-2026-10-27.json).

It retains `9ea11eab`'s removal of a repeated enemy scan during Bill/Lance's ordinary gunfire. Bill cleared 1-1 in Hard mode with the rendering guards enabled. This reduces unnecessary CPU work; the recorded comparison does not establish a faster route or constant frame rate. See the [build checks and limits](docs/qa/bill-early-cache-adoption-2026-10-27.json).

It retains the preceding `6be48337` Samus missile-icon fix. Checks recorded on that earlier build cover Samus's items and HUD jump, Bass's items in both modes, Pit's upgrades and flight in both modes, and 1-1 clears for Link, Simon and Rygar. See the [Samus checks](docs/qa/samus-fixed-hud-adoption-2026-10-27.json), [Pit checks](docs/qa/pit-current6be-components-native-2026-10-27.json) and [roster progress](docs/qa/current-roster-progress-2026-10-27.json) for each tested ROM and mode.

It also includes `4a0394b0`'s alternating body-sprite priority for Mega Man and Proto Man, and its fix for a scrolling jump caused by repeated palette updates running past the rendering deadline. Both cleared Hard 1-1 without a death and reached playable 1-2 on that build. See the [rendering checks and limits](docs/qa/mm-body-palette-adoption-2026-10-27.json).

It retains `2082c19a`'s Proto Man level-start palette fix and `8487c439`'s correction to Bass's airborne head collision and block separation. Bass cleared 1-1 in Hard with zero deaths and no cheats, and an independent replay matched the inputs, trace and all 4,340 captured PPU frames. See the [Bass checks and limits](docs/qa/bass-corner-adoption-2026-10-27.json).

It retains `fb2a608e`'s fixes for the audio test's stretched note timing and screen flicker. Sustained overworld playback was checked for all 37 identities, including stable menu pixels; Mario's note timing matches normal gameplay playback. See the [audio checks and limits](docs/qa/music-test-timing-adoption-2026-10-27.json).

It includes the character-labelled music/SFX browser and four additional cheats: mid-air jumps, screen wrapping, a frozen timer and full power. The [earlier menu checks](docs/qa/frontend-adoption-2026-10-27.json) also exercise Mario's new cheat behavior in gameplay. The broader roster audit is still in progress.

It includes the Bass weapon-HUD and graphics/bullet-overhead repairs from `3b112e1d`. That earlier build passed 32 controlled Bass weapon cases across Easy and Hard, plus a thrown-brick/question-block regression. Those checks remain specific to their recorded build; see the [results](docs/qa/inventory-timing-adoption-2026-10-26.json).

It retains Luigi's Mario-based movement with a modestly higher jump and less traction from `641460e2`, the character-select and level-start HUD fixes from `731c918b`, earlier Castlevania sound repairs, reduced Chip/Dale movement overhead, and clearer Parodius power-bar lettering. See the [Luigi results](docs/qa/luigi-profile-adoption-2026-10-26.json) and [earlier timing results](docs/qa/presentation-timing-adoption-2026-10-26.json).

The last complete 37-character 1-1 suite ran on `3cee18ca`: 36 identities cleared in Easy and Bass in Hard, each with an independent replay. Those results remain specific to that build; further checks on the latest build are in progress. See the [1-1 results](docs/qa/current37-1-1-2026-10-26.txt).

All 37 identities now have a recorded 1-1 clear in the recent build lineage, and every implemented powerup has a native collection-and-effect witness at least once. These checks span several ROM versions; they do not certify the whole roster on the latest build. See the [item coverage and limits](docs/qa/all37-powerup-once-coverage-2026-10-28.json).

Crowded scenes still cause partial player sprites, including Mega Man, Sophia and Octopus. Final-build playthroughs, graphics, the other mode and shortcut routes, sound and performance still need further work; see the [current roster checks](docs/qa/current-roster-progress-2026-10-27.json). Results from earlier builds remain labelled separately.

## Features

- A three-row character select screen, with alternate characters chosen using Select.
- Character-specific movement, attacks, equipment, health and resource systems.
- Easy and Hard behavior settings, optional player outlines and six cheat options.
- A character-labelled music and SFX browser in expanded MMC5.
- SMB levels with Crossover-inspired changes and the original platform actors to help different movement styles traverse them.
- Native character music and sound support, with additional audio work still in progress.
- Full graphical Gradius and Parodius upgrade bars in the expanded MMC5 build.

## Roster

Highlight a character and press **Select** to cycle the alternates in that slot.

| Selection slot | Characters | Highlights |
| --- | --- | --- |
| Mario | Mario / Luigi | Familiar SMB controls; Luigi jumps a little higher and has less traction. |
| Mega Man | Mega Man / Proto Man | Buster, slide, charge upgrade, acquired weapons and Rush Coil. |
| Samus | Samus | Beams, Morph Ball, bombs, missiles and suit upgrades. |
| Contra | Bill Rizer / Lance Bean | Directional shooting, crouching and Contra weapon upgrades. |
| Link | Link / Zelda II Link | Sword and subweapons; Zelda II Link has EXP, stats, spells and health/magic. |
| Castlevania | Simon / Grant / Sypha / Alucard | Whip and double jump, climbing, spells, or bat transformation. |
| Pit | Pit | Arrows, hammer and a limited flight upgrade. |
| Rygar | Rygar | Returning Diskarmor and reach upgrades. |
| Bass | Bass / Roll | Bass has directional fire, dash and weapon inventory; Roll has her own attacks and health. |
| Ryu | Ryu Hayabusa | Sword, wall movement and ninjitsu. |
| Sophia III | Sophia III | Cannon, missiles, hover and surface traversal upgrades. |
| Scrooge | Scrooge McDuck / Darkwing Duck | Cane and pogo, or gas gun, guarding and adaptors. |
| Kirby | Kirby / Meta Knight | Inhale, swallow and copy powers, or grounded sword combat. |
| Rescue Rangers | Chip / Dale | Carry, throw and hide in crates. |
| Little Mac | Little Mac | Punches, stamina and up to three stored star punches. |
| StarTropics | Mike Jones | Heart-dependent primary weapons and collectible specials. |
| SMB3 | SMB3 Mario / Luigi | P meter, flight and Fire, Raccoon, Frog, Tanooki and Hammer forms. |
| Gradius / Parodius | Vic Viper / Octopus / TwinBee / Pentarou | Flight, automatic level scrolling and ship-specific upgrade bars. |
| TMNT | Leonardo / Raphael / Michelangelo / Donatello | Distinct primary weapons, directional attacks and collectible secondary weapons. |

## Build and play

You need **Python 3.10 or newer** and **cc65**. Windows compiler tools are included; on other systems, install cc65 and put `cl65` on your PATH. The main build uses the prepared assets already in the repository.

From the repository root:

```sh
python tools/prepare_guest_audio.py
python tools/build_mmc5_expanded.py
```

Open **`build/smb-crossover-mmc5-expanded.nes`** in an emulator with MMC5 support. Mesen 2 is used for development and testing. The build also produces a `.build.json` receipt containing the ROM's SHA-256 hash.

To use a different compiler location:

```sh
python tools/build_mmc5_expanded.py --compiler /path/to/cl65
```

These steps have been checked against a clean export of the tracked sources. Building the prepared MMC5 target does not require downloading original ROMs or reference archives. Asset regeneration and some research/verification tools have additional dependencies; see the [architecture notes](docs/architecture.md).

### Other cartridge targets

| Target | Roster | Cartridge layout | Status |
| --- | --- | --- | --- |
| Expanded MMC5 | All 37 identities | 1 MiB PRG + 1 MiB CHR | Recommended development build. |
| Standard MMC3 / MMC5 | 14 identities in 12 slots | 512 KiB PRG + 256 KiB CHR | Smaller original roster; expanded alternates are excluded. |
| Oversized MMC3 | Expanded roster | 2 MiB PRG + 256 KiB CHR RAM | Experimental; qualification and feature parity remain in progress. |

For a standard build, run the audio preparation step above, then:

```sh
python tools/build_mmc5_expanded.py --flag-off mmc3 --output build/smb-crossover-mmc3.nes
python tools/build_mmc5_expanded.py --flag-off mmc5 --output build/smb-crossover-mmc5.nes
```

The experimental oversized builder is `tools/build_mmc3_oversized.py`; it requires a freshly built expanded MMC5 ROM as its graphics reference. Its mapper implementation must support eight-bit PRG banking and 256 KiB CHR RAM. Physical cartridge compatibility is still unverified, and Parodius currently uses a text bar on this target.

## Controls

| Screen / action | Controls |
| --- | --- |
| Main menu | Up/Down chooses START or OPTIONS; A or Start confirms. |
| Character selection | D-pad moves; Select cycles alternates; A or Start begins; B returns. |
| Audio test (expanded MMC5) | Up/Down character; Left/Right cue; Select music/SFX; A plays; Start stops; B returns. |
| Movement | D-pad moves or aims. |
| Jump / primary attack | A jumps; B attacks or runs, depending on the character. |
| Pause | Start pauses and resumes. |
| Weapon inventory | For supported characters, paused Left/Right selects equipment; paused Select returns to the primary weapon. |
| Mega Man / Bass weapon cycling | Select also cycles acquired weapons during play. |

Special moves use character-specific combinations. Zelda II Link has his own paused spell/stat interface. **Vic Viper and the Parodius ships use A to fire and B to buy the highlighted upgrade.** See the [player's guide](<Player Guide/SMB-Crossover-Players-Guide-NU.pdf>) for individual moves and tips. The guide is updated separately and can lag behind development changes.

### Easy and Hard

**Easy is the default.** It allows ordinary enemy stomps for ground characters and uses the earlier Crossover power progression for the original guest roster.

**Hard** uses the migrated Crossover 2.02 equipment systems and character-specific enemy contact rules. Many guests must attack rather than land on enemies. Mario, Luigi and the SMB3 pair retain stomping in both modes. Ships keep their own contact/shield rules, and hazards and special body attacks have separate rules.

New additions also have adaptations for SMB's levels and NES controls. The project does not claim that every character is identical to its original game or to Crossover 2.02.

### Options and cheats

- **PLAYER OUTLINES:** off by default. Turning this on adds black outline sprites; crowded scenes can flicker more.
- **MODE:** Easy or Hard.
- **CHEATS:** invincibility, starting level (1-1 through 8-4), mid-air jumps, screen wrap, freeze timer and full power. A selected starting level applies when confirming a character. Invincibility does not prevent pit or time-out deaths. Full power restores health/ammo and grants compatible character upgrades; existing suit and weapon choices are retained where possible.
- **AUDIO TEST** (expanded MMC5): choose a character and its music or SFX. Track labels describe the scene or event that uses the cue; some cues share the same underlying music.

Settings last until reset. Use B to return from a submenu.

## Known limitations

- Lag, sprite flicker, scrolling and collision regressions are still under review. NES sprite limits remain relevant.
- Moving-platform behavior, the full campaign and every powerup on the latest build have not yet completed verification across the entire roster.
- Some characters still share music or sound effects. Dedicated audio routing and additional effects remain unfinished.
- TMNT secondary weapons and other newer abilities still need broader gameplay verification. Some HUDs and animations need refinement.
- Oversized MMC3 is experimental and does not yet match every MMC5 feature.

The [current development record](docs/qa/current-work-pr-2026-10-24.md) and [source comparison notes](docs/reference/parity.md) contain detailed findings. QA reports describe specific ROM hashes and checkpoints; a passing older test does not certify the latest build. Generated ROMs and large test recordings are excluded from Git.

## Reporting bugs

Please include the character and alternate, Easy/Hard mode, level, mapper target and emulator or hardware used. Describe the steps that caused the problem and, when possible, attach a short video or screenshot. The ROM hash from the build receipt helps match a report to the correct version.

## Repository layout

| Folder | Contents |
| --- | --- |
| `src/`, `inc/` | Game code and assembly includes. |
| `chr/`, `audio/` | Prepared graphics and audio assets. |
| `tools/` | Build, conversion and verification tools. |
| `tests/` | Emulator fixtures and focused regression checks. |
| `docs/` | Architecture, source research and checkpoint-specific QA. |
| `Player Guide/` | Illustrated guide, preview and editable source pack. |

## Credits

Built on [SMB1Base](https://github.com/smbstudio/smb1base), with the original project's information preserved in [its README](docs/SMB1BASE.md). The concept and browser-game reference are [Super Mario Bros. Crossover](https://www.smbgames.be/smb-crossover.php).

This is an unofficial fan project. Original games, characters, artwork and music belong to their respective creators. Source and asset provenance are documented in the repository's research and architecture notes.
