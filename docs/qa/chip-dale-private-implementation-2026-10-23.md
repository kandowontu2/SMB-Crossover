# Chip / Dale private implementation

Status: playable private MMC5 candidate, ready for contextual integration. Main source was not edited. Based on the immutable `build/checkpoints/kirby-roster-mg/source.zip`, whose expanded ROM SHA-256 is `b86695b7323e2f655b8d032e00938826648fd32a7af4a31a03d7d59cd66c8074`.

Candidate: `build/verification/chip-dale-candidate-agent/chip-dale-private.nes`.
SHA-256: `1596dd8813ea51828756b51f206b5c86f15bf96e0292b286808f674a387a7306`.

## Playable behavior

- Third-row slot13 selects Chip, raw character ID14. Select toggles Dale, retaining family14. The original game's sprites, an authentic Chip silhouette, highlighted names, lives-screen and status names are present. Dale selection survives Start and death.
- Left/right use Rescue Rangers' horizontal kernel at `$01CC` pixels/update, with instant direction changes. A launches at native upward velocity `$0687`; native gravity is `$55/256`, short-jump release `$FFAB`, and downward cap `$F800`. The retargeted original integrators preserve the native fractional steps. Terrain and camera integration are explicitly SMB adapters.
- B picks up a nearby visible crate. B while carrying starts the original two-frame, four-tick horizontal throwing sequence; release occurs on its fourth update, at four pixels/update. Up+B throws immediately with native upward velocity4. Down while carrying hides the player inside the crate. Hiding from an eligible ordinary enemy defeats that enemy and consumes the wooden crate.
- Three health units. Mushroom contact heals one; flower contact restores all three. Both remain visible native SMB actors, emerge normally and grant health only on actual contact. Native pickup SFX queues are used. Three harmful contacts cause death; a new life restores three health units.
- A visible wooden crate is placed32 pixels ahead of each entrance. B can lift a nearby eligible brick into a carried crate, using the exact queried block-buffer cell and normal metatile destruction transaction. Ground, terrain-marked bricks, question blocks, used blocks and pipes are rejected. Original level geometry is unchanged except the specific breakable cell the player actually lifts.
- Six private box slots avoid stealing native enemy/firebar/platform actors. Thrown crates can defeat eligible ordinary SMB enemies and break on terrain. Inactive character wrappers never touch the shared Kirby transient overlay.
- Easy/Hard uses the existing project stomp policy; this is an SMB adaptation, not a Rescue Rangers difficulty-system claim.

## Authentication

Original local cartridge image: `C:/NES/Chip 'n Dale - Rescue Rangers (USA).nes`.
SHA-256: `8d5e3d9ce20fa0a61b23e93dbc975606803f2d5e7a264514b02b96f832a63181`.
PRG SHA-256: `ebfdcf589eccee78b740c5ff71e0f21a5c9e52bada1d732a15ce491bb35d6919`.
CHR SHA-256: `ab619f858a954910df3478e96453a41ed07258d641281e43679e9aaff659581c`.

The primary [Capcom instruction manual scan](https://www.digitpress.com/library/manuals/nes/Disney%20Chip%20%27n%20Dale%20Rescue%20Rangers.pdf) supplies the jump, pickup, throw, upward throw and hide controls. Original ROM execution supplies the artwork, animation sequences, timing, palette and numeric kernels. Existing local original-address research was read from the separate `mario in kid icarus/rangers` project; its Mario hack physics were not copied.

Art extraction executes the original bank5 renderer, resolves its OAM/CHR pixels, and repacks those pixels losslessly into the project's 8×16 sprite format. Fifty native player frames and ten object frames, in both directions, are retained. Native palette0 is `$0F,$0F,$37,$16`; only its three opaque colors are the player colors. The universal background follows the SMB area's native palette, including black on the lives screen. No generated or recolored Mega Man placeholder is used.

Numeric kernels: original `$F21E..F25A`, `$F2A2..F2EA`, `$F2FB..F328`; gravity initialization `$C6FC`, jump setup `$C9A9`, short-jump release `$CBC2..CBC9`. Original virtual carried-object index `$82` aliases actor2: `$CD95` writes actual upward velocity high byte `$0562=4`; `$CDF5` writes actual horizontal velocity high byte `$0542=4`. These are not object-type constants.

## Resources and integration

| Resource | Allocation / actual usage |
|---|---|
| PRG79 A-window | Core, rendering, boxes, health and dispatch:2393 bytes (`$A000..A958`) |
| PRG80 C-window | Authentic native frame records/tables:3350 bytes (`$C000..CD15`) |
| PRG81 A-window | Native kernels and SMB movement adapter:748 bytes (`$A000..A2EB`) |
| CHR412..459 reserved |412..424 body poses;425 stable wooden-crate page;426..459 unused |
| ExRAM persistent | `$5F10..5F1F`, health at0, initializer marker at15; other bytes reserved |
| Variant | `$5FE1`, covered by root's menu-variant preservation |
| Active transient | `$5C00..5CFF`, mutually exclusive with Kirby13; active14 gates before all mutations |
| Resident drawing | Existing31-byte `KbDrawDispatch` changes only its admission condition and cold target; no added bank4 guard |
| Resident C banking | Append80 to `DwResidentGraphicsBanks`; entirely resident, no NMI farcall/SMC exposure |

No old SRAM addresses move. All old global labels outside the cold `PROTO_MENU` and `X5_PROFILES` segments retain addresses. The palette and menu cold implementation labels relocate inside their existing banks. Original SMC, NMI/IRQ, drawing-admission and collision leaf entry addresses remain fixed. Both standard, expansion-disabled builds reproduce the exact MG/KB MMC3 and MMC5 hashes.

`merge-staging/` contains own files and contextual shared snapshots; `incremental-merge.patch` is the narrow review boundary. Compose the hooks into current source. Do not overwrite newer shared files wholesale. Root can replace the private `Cd*Dispatch` chain with its shared profile registry. Menu layout/CHR were generated using the existing root menu generator with the authentic Chip portrait; compose new slots through that generator.

Two general shared fixes are included: names16..31 now use a full pointer rather than wrapping an eight-bit `index*16`; Chip's GetPlayerColors emits the correct SMB background entry at `$3F10`, preserving sky/lives colors. Per-frame player palette updates touch `$3F11..13` only.

## Verification and scope

- 9,008 linked RP2A03 comparisons against original ROM execution cover the retargeted horizontal, vertical and gravity/release primitives.
- 120 original pixel reconstructions and 300 linked renderer/10-bit CHR cases cover 50 body poses ×2 directions ×3 prior power tiers, plus original object pixels.
- 1,004 linked core calls include 180 lift cases across both variants, both directions, five world-X boundaries and nine tile/terrain conditions. The queried cell alone changes, its adjacent question block remains intact, player X/page/Y are preserved, and all 192 old inventory ammo bytes remain unchanged.
- 30 menu name/variant cases, 1,344 old palette cases identical to MG, 96 Chip/Dale area/background/power palette cases.
- Native1,000-frame ordinary-controller checks for Chip and Dale separately: front-end navigation, variant selection, entry, visible entrance crate, B pickup, carry, Down hide, B throw, movement/jump and high CHR. Full NMI A/C restoration and IRQ paths were exercised.
- Native2,050-frame check: ordinary Dale selection/entry followed by explicitly authored bounded arenas. Actual hide/Goomba contact consumes the crate without losing health. An actual B throw travels and kills a Goomba. Native SMB mushroom/flower emergence is visible and does not grant health while distant; actual contact heals. Three actual harmful contacts produce death and actual new-life re-entry, preserving Dale. All192 old ammo bytes remain unchanged during the interactions.
- The first pickup test incorrectly expected Zelda II's48-update custom emergence. Chip intentionally uses SMB's ordinary17 one-pixel steps at `FrameCounter%4=0`; the test was corrected. SMB may set additional enemy-state bits after emergence, so readiness checks bit7 rather than equality with `$80`. Earlier failed evidence is retained.

These are bounded kernel, renderer, controller and interaction proofs, not a full campaign, complete obstacle-route or hardware cartridge certification.

## Remaining differences / limitations

This is not yet a claim of complete Rescue Rangers engine parity. The original game's music has not been ported: the private audio-family adapter uses the existing Pit music, with existing SMB action SFX. Original recoil trajectory/death duration are not fully migrated; the port uses a60-update hurt animation interval with SMB invulnerability/death lifecycle. The visible HP display is text, not original heart art. The collision hull is the existing standing/crouched SMB guest adapter, not a proved byte-for-byte original Rescue Rangers hit-test port. Thrown-box terrain/enemy classification, lifetime and six-slot storage are documented SMB policies rather than original enemy-system exactness.

Down+A dropping through source one-way ledges is not implemented; it never permits dropping through solid SMB ground. Swimming, vines, spring/flag/castle and long campaign routes remain unproved. Original metal boxes/apples are extracted but not exposed as selectable fake features. Flowers/stars/bonus-game/co-op progression from Rescue Rangers are not implemented. These limitations are explicit so the selectable core is reviewable without presenting future work as complete.
