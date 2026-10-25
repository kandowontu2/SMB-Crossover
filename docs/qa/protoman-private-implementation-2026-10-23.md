# Proto Man private candidate — 23 October 2026

This candidate is complete for private integration review and is **not installed in main**. Its base is the Rygar-KB checkpoint. Expansion is enabled only for MMC5; disabling it reproduces both existing KB release ROMs exactly.

## Implemented behavior

Select on Mega Man cycles Mega Man / Proto Man in the same menu position. Proto Man has an authentic colored preview, selected name, hint and HUD/lives name. Moving to another character clears the direct high-CHR mapping. The grid remains the shared existing menu; this adds no raw family ID or extra portrait position.

Proto Man remains `SelectedCharacter=1`. Movement, collision, jump, slide, swimming, damage, pickups, weapons, ammunition, inventory ownership and Easy/Hard dispatch share Mega Man's existing code. The source shield-bearing jump artwork is cosmetic; no separate shield ability or damage multiplier is invented.

Twenty-seven authentic source poses cover standing, four walking phases, standing/walking/air shooting, jump, slide, climb, recoil, startup step, carry, throw and Hard Knuckle. Actual source black pixels remain in the body; no added outline-mask sprites are introduced. Original common bullet tiles and injury-effect tiles are retained in the corresponding body banks.

Original MM3 whistle, ending and staff-roll score data run through a copied original MM3 native kernel. The whistle ends naturally and transitions into the area playlist. Existing weapon and land/hurt sound effects retain Mega Man's shared buffers. This is a related original-game music selection, not a claim that every Flash skin music choice is reproduced.

## Authentic source

`reference/crossover2/source.json` pins SWF SHA-256 `6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af`, Git blob `7ffefb108c55a0a10403403988d60c68432254c9`. `BmdInfo.as:369` binds skin `MegaMan003` to `MegaManBase.PROTO_MAN_NAME`. Body symbol 103, arm symbol 101 and bitmap ID 24 supply the actual helmet, scarf, body, arms, masks and placement matrices. This is not red Mega Man artwork.

`build/verification/protoman-candidate-agent/art-manifest.json` records the sheet/timeline hashes, every selected source frame, tile allocation, and independent exact source-pixel/palette-role round trip for all 27 poses. The contact sheet and native screenshots are retained beside it.

The native audio comes from retained primary [lsmmega/mm3](https://github.com/lsmmega/mm3), commit `8ecd0a9247ed17709e8cd9cc692c38288daa2bc5`, and `.upstream/mm3/audio/music/{protoman_whistle,ending,staff_roll}.asm`. Score macros/data are compiled unchanged into a namespaced copy of the existing imported engine.

## Memory and integration

| Allocation | Used | Purpose |
|---|---:|---|
| Bank 64 / A000 | 8,157 B | Native MM3 kernel plus three original scores |
| Bank 65 / C000 | 6,982 B | Body records, exact original projectile records, native wrapper and Rush-land leaves |
| Bank 66 / A000 | 4,067 B | Cold presentation/audio core, local bullet-pointer tables and expanded-only menu |
| CHR pages 256–275 | 20,480 B | Authentic body/composite tiles |
| Fixed SRAM aliases | 2 B | `ProtoVariant=$73DD`, `ProtoAudioState=$73DE` |

The guide agent's unchanged 15-byte ABI occupies `$73E0..$73EE`; its publisher is in bank 62. No bank64/125 diagnostic probe routines or diagnostic CHR survive in this candidate. No `.res` is appended to the old SRAM layout.

Seven existing files have narrow patches: `entrypoint.s`, `characters.s`, `character_select.s`, `screen_render.s`, `megaman_weapons.s`, `metasprite_engine.s`, `megaman_audio.s`. `implementation.patch` is against saved original hook text. **Do not replace whole main files**: root's newer Bass/level changes need a normal context merge.

The resident audio entry retains its 16-byte span, status wrapper 66 bytes, projectile wrapper 139 bytes and preview replacement 32 bytes. Bank12 remains byte-identical, including original audio/Rush leaves. All old global CPU addresses match KB except the explicitly relocated menu globals; the menu's former span is reserved so the following Rush-reset leaf retains its public address. Two pre-existing alignment warnings remain for MM3_AUDIO and ROSTER; the new segment has an explicit correct alignment.

NMI routing saves/restores actual A/C windows and shadows. The new path writes no shared farcall SMC. The original projectile record addresses D108..D367 are preserved. The outlined projectile routine uses local pointer tables, since the original global tables belong to bank4 and cannot be read while executing in bank66.

## Verification

* `flag-off-proof.json`: disabled builds match KB exactly: MMC3 `4720972962f8faf6c8e45536f95001e79ae66c7141dcbfa09c768440fa039c00`, MMC5 `0ab6ac031ae9c80a6e516ce29130e041cfe2e34da5bfb447d78a514fbd2739e6`.
* `cpu-proof.json`: 96 base pose/facing/power selectors; **756 complete DrawAll pose/facing/buster/outline cases** compare actual OAM with immutable-record expectations; 256 palette streams and 24 special/star gates; 490 interrupted-bank hardware/shadow/SMC checks; 2,400 native audio updates. Whistle completion occurs at update 796.
* `extra-proof.json`: 56 carry/special selector cases and scoped global-address comparison. A negative control restores only the four unsafe old pointer-load operands: it draws 40 sprites instead of 11 and fails the oracle. Native screenshot inspection caught that same lower-body disappearance before the fix.
* Native Mesen power-on/controller proof covers Select, preview, entry into 1-1, walking, jumping and firing. Over 1,000 frames it observes 992 NMIs, 923 scroll IRQs, 839 Proto audio updates and 141 explicit high-CHR body checks. Complete NMI returns preserve interrupted C and consistent A ownership.
* A separate controller test covers seven Mega Man / Proto Man / Samus menu transitions, variant persistence and legacy-CHR restoration.
* `native/movement-differential.json` compares 701 controller-frame samples across 26 gameplay/inventory fields. 698 rows match exactly. Three rows at 1087–1089 straddle death/respawn loading one frame apart; they are explicitly **not** claimed identical. Before that reload and after loading, the sampled motion, shots, damage and scroll state agree. Gameplay dispatch itself is shared.

This is not a full-campaign traversal, audio listening review, or proof of every weapon against every enemy/terrain combination. Combined-build replays remain necessary after root merges other work. No main source or level data was changed by this candidate.

## Reproduce and adopt

`assemble_candidate.py` rebuilds only the private tree; `build_art.py` rebuilds authentic assets from retained local source. `check_proto.py`, `check_proto_extra.py` and the four native Lua scripts reproduce the checks. The compressed debug file is supported directly by both CPU checks and the existing native runner.

Adopt the shared MMC5 expansion packet first, merge the seven hook diffs, add the new `protoman*.s/inc` files and two binary assets, and assign the four optional segments as in the private config. Preserve ongoing root edits. The manifest records source and artifact hashes. Legacy release ROMs remain unchanged.
