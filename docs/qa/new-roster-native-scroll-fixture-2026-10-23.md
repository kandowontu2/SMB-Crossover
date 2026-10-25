# Sustained native scrolling check

Fixture: `build/verification/new-roster-scroll-native-agent/scroll.lua`. Runner: `run.py` in that directory. No game source, ROM, level geometry or movement constants are changed.

The retained negative control is frozen MZ expanded ROM SHA-256 `043b1368b7ff41ca7d61d830c5d19b29bea69f37be657a594878711cbcc39764`. Each of 18 identities runs its actual installed character engine with Right held for 650 video frames, starting at world X32/camera0. This reaches well beyond the earlier short entry checks.

The scene is explicitly arranged in RAM: empty collision air, two solid ground rows, no enemies, no spring or powerup actors. Collision buffers are refreshed before native game updates while the native parser, rendering, scrolling, input, movement, NMI and IRQ routines continue to run. Enemy parsing points at an existing ROM end-of-stream byte. Player/camera coordinates and the scroll cache are initialized once per scene and never corrected by the fixture afterward. These are focused component scenes, not ordinary campaign routes or graphical reviews of the visible level artwork.

Every ground profile must advance world X≥512 and camera≥128 and provide at least100 grounded post-scroll samples. Its relative X must stay around80..112, allowing at most one observed update's horizontal movement beyond the band. The trace records individual violations and consecutive violations to catch a march toward the right edge. Gradius has its authentic independent screen-space flight/autoscroll policy, so it must advance world/camera but is exempt from the ground-position band.

## Retained MZ results

The checker matches exactly five expected broken profiles. It does **not** label MZ's whole roster as passing.

| Identity | Result | Maximum world X | Maximum camera | Observed ground-relative band |
|---|---|---:|---:|---|
| Proto Man | Pass | 834 | 722 | 80..112 |
| Darkwing | Pass | 999 | 887 | 81..112 |
| Zelda II Link | **Fail** | 239 | 0 | No scrolling samples |
| Kirby | Pass | 867 | 755 | 80..112 |
| Chip | Pass | 1198 | 1086 | 81..112 |
| Dale | Pass | 1198 | 1086 | 81..112 |
| Grant | **Fail** | 239 | 0 | No scrolling samples |
| Sypha | **Fail** | 239 | 0 | No scrolling samples |
| Alucard | **Fail** | 239 | 0 | No scrolling samples |
| Little Mac | **Fail** | 239 | 0 | No scrolling samples |
| Mike | Pass | 774 | 662 | 80..112 |
| SMB3 Mario | Pass | 984 | 872 | 80..112 |
| SMB3 Luigi | Pass | 984 | 872 | 80..112 |
| Vic Viper | Pass | 881 | 649 | Flight/autoscroll exception |
| Leonardo | Pass | 758 | 646 | 82..112 |
| Raphael | Pass | 758 | 646 | 82..112 |
| Michelangelo | Pass | 758 | 646 | 82..112 |
| Donatello | Pass | 758 | 646 | 82..112 |

The passing grounded profiles have 602–622 post-scroll samples each and **zero band violations**. The five failures retain cache0 and camera0 and stall against the native screen edge. The entire run completes12,300 frames, with12,292 NMIs and12,237 IRQs checking complete A/C-bank restoration.

The read-only frozen-source inventory `mz-cache-source-audit.json` finds the expected explicit stores: Mega Man/Proto in `characters.s`; Darkwing in its core; Kirby in its core; Chip/Dale in render; Mike in its core; SMB3 in movement and render; TMNT in draw. Vic also publishes the cache in render but uses its own scroll gate. MZ's Zelda II movement and CV3/Mac core/draw paths lack the corresponding store. Those source observations explain the native negative witnesses; source text alone was not accepted as a scrolling pass.

## Reuse after integration

Run the same runner with the exact final ROM and a fresh evidence directory, omitting `--negative-mz`:

```text
python build/verification/new-roster-scroll-native-agent/run.py FINAL_ROM --output FRESH_OUTPUT
```

It binds the fixture to that ROM's own debug symbols and enemy-stream terminator, records ROM/template/bound-script hashes, and requires **all18** profiles to pass. `--negative-mz` is only for the retained old-ROM control and checks the exact five-name failure set. It must not be used to approve a final ROM.

Scope is ordinary grounded walking in the normal character state, plus the ship's normal flight. Jumps, pipes, attacks, all power forms, special transformations, enemy pressure, performance and campaign completion are outside this bounded fixture.
