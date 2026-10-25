# Options: Cheats submenu

Options now has a third row, CHEATS. Up/Down selects a row; A/Start opens it. Inside Cheats, Up/Down selects INVINCIBLE or START LEVEL. A/Start/Select/Left/Right toggles invincibility; Left/Right cycles the starting level (A/Start/Select also advances). B returns to Options, then the title.

Defaults are invincibility OFF and displayed level1-1. Until the level value is changed, native start/continue behavior remains intact. After a change, the selected1-1 through8-4 applies on the next character confirmation. Deaths and ordinary area transitions do not apply it again. Settings last until reset. Invincibility prevents enemy and hazard damage, retains the current power and avoids flashing/star effects. Pits and timer expiration retain their normal behavior.

## Validation

Both mapper builds pass the real controller menu test over all32 values and both wrap directions, held-button edge toggles, back navigation, existing option preservation, and a Samus1-2 launch through the actual native pipe intro. Screenshots were inspected. A menu-enabled invincibility test passes84 actual enemy-contact arenas per mapper: all14 identities, both modes, and all3 power forms. Native contact with cheats OFF, character selection, outlines, firebars, score anchors, terrain publication and Bill's full flagpole/castle transition also pass. The final scoped matrix has18 native checks.

Compiled CPU tests compare the relocated rare enemy cleanup against the previous ROM, including registers, flags, scratch, six slots, stack, windows and foreign MMC3 selectors. The damage predicate covers every InjuryTimer byte with cheats ON/OFF. Starting-level mapping covers all32 levels, explicit/default state and continue handling. This is not an interrupt-injection claim.

Two SRAM bytes are appended; header, CHR and rebuilt baseline ROMs remain identical. The menu uses an existing unused PRG tail. Only attempted injury gains16 cycles; normal non-contact gameplay gains no instructions. A rare enemy cleanup now incurs a bank round trip. The original menu's static third row is drawn with rendering disabled, keeping dynamic menu packets within the native queue capacity.

The first level implementation overwrote authored native starting stages even when untouched; the final version uses an explicit changed-value bit. The original failed flagpole checks are retained, and the final checks pass. An initial queue assertion incorrectly included gameplay HUD work; the corrected assertion checks the menu it claims to check. Earlier build/command/parser failures remain in the audit directory.

Checkpoint: `build/checkpoints/cheats-options-bt/manifest.json`. Final native receipts: `build/verification/cheats-final-bt/summary.json`. Compiled CPU receipt: `build/verification/cheats-abi-br/summary.json`.

Current-build recheck: `build/verification/cheats-current-cl/summary.json`. Both mappers again pass controller-only navigation across all32 levels and84 invincibility contact arenas each. The actual submenu screenshot was inspected. These checks confirm Cheats remains functional alongside subsequent fixes; they do not admit the unrelated pending Water Shield performance candidate.

The broader all-character source-fidelity, lag optimization, remaining bugs and final video goal remains active. Original recordings and lossless captures are retained under the user-approved100GB cap.

Latest request recheck: `build/verification/cheats-request-1792713124153/summary.json`. All four current-ROM checks pass, including all32 menu values and84 contact arenas per mapper. The submenu screenshot was inspected; README now documents access and controls. ROMs are unchanged from the Rygar world-palette GA checkpoint. The broader roster goal remains active.
