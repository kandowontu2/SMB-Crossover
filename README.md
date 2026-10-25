# SMB Crossover for NES

Play Super Mario Bros. with characters from across the NES library, each bringing their own movement, weapons and upgrades.

This is a native NES adaptation of [Super Mario Bros. Crossover](https://www.smbgames.be/smb-crossover.php), built on [SMB1Base](https://github.com/smbstudio/smb1base). The expanded MMC5 version currently includes **37 playable characters and alternates across 19 selection slots**.

**Status: playable, actively developed, and unfinished.** Character behavior, graphics, sound and performance are still being tested and corrected. MMC5 is the recommended target for the full roster.

## Features

- A three-row character select screen, with alternate characters chosen using Select.
- Character-specific movement, attacks, equipment, health and resource systems.
- Easy and Hard behavior settings, plus optional player outlines, invincibility and starting-level selection.
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
| TMNT | Leonardo / Raphael / Michelangelo / Donatello | Distinct primary weapons and directional attacks. |

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
- **CHEATS:** invincibility and a starting level from 1-1 through 8-4. A selected starting level applies when confirming a character. Invincibility does not prevent pit or time-out deaths.

Settings last until reset. Use B to return from a submenu.

## Known limitations

- Lag, sprite flicker, scrolling and collision regressions are still under review. NES sprite limits remain relevant.
- Moving-platform behavior, the full campaign and every powerup on the latest build have not yet completed verification across the entire roster.
- Some characters still share music or sound effects. Dedicated audio routing and additional effects remain unfinished.
- TMNT secondary equipment is incomplete. Some newer abilities, HUDs and animations still need refinement.
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
