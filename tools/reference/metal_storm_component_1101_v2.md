# Metal Storm source component — November 1

This component is ready for host-adapter work. It is **not an unlocked character**
and has not been installed in the nightly.

Donor: `C:/NES/Metal Storm (USA).nes`, SHA-256
`22e7576958e842c564153bf799293cedf90c6a0aaee302b73ec8af88a7481d87`.

## Concrete results

- Recovered 1,988 original instructions in `AB53..BCAC`, `E324..E32A` and
  `EA4E..EB21` (4,661 bytes). The semantic assembly plus untouched gaps reproduces
  the selected donor banks 0/1/14/15 (32 KiB) exactly.
- Private assembly occupies 6,323 bytes at laboratory `9000`, with a relocated
  two KiB source-state image at laboratory `6000`. It exports `MsFrame`,
  `MsHorizontal`, `MsGravity`, `MsJumpClock`, `MsIntegrateY`, `MsWalls`, `MsSupport`.
- 480 legal donor actor entries, produced by real donor reset/Start/NMI code,
  agree in 960 original/private unit executions. Walking, held/released jumping,
  both gravity directions, floor/ceiling contacts and both projectile slots run.
  The original external API effects are recorded in memory and replayed at
  explicit boundaries; those API implementations have **not** been ported.
- The original `F282` renderer exports 208 valid state/frame/facing/gravity
  contexts, 144 distinct original 8x16 patterns (4,608 bytes), and original
  OAM attributes/palette indices. The archived original native idle image
  (581 opaque pixels) reconstructs exactly. The other poses are CPU evidence.

The output is `build/metal-storm-component-1101-v2`. Its receipts are
`assembly.json`, `CPU-controls.json`, and `art.json`; `body.chr` and the latter's
packets are the graphics inputs. `body-preview.png` shows original state/frame
poses. A `FF` frame-map sentinel is not rendered. State 6 has no valid player
frame-map entries and must not be used as an invented animation.

Run the source recipe only through the storage wrapper:

```powershell
python tools/audit/run_bounded_build_v1.py --output build/metal-storm-component-1101-v2 --resume --timeout 180 -- python tools/audit/prepare_metal_storm_source_1101_v2.py
```

This command applies only before this output is frozen by `source-stage.json`.
The finished packet retains exact sources and aggregate results rather than
per-frame fixtures, videos or PPU dumps.

## Required host adaptation

1. Allocate real selected-owner code/state resources. The `9000/6000` addresses
   are laboratory arenas and no host grant exists. The pending menu alternate
   is slot 11, `FmAlts & 2`; do not admit it to raw-ID tables until the typed
   route, cold scene constructor and cold menu metadata are complete.
2. **Replace laboratory `MsPointer=$00` with native foreground R0/R1=$03/$04.**
   `$00..$02` belongs to SMB NMI scratch. Return restoration of `$00/$01` in
   these unit tests is not interrupt safety. Test real IRQ/NMI cuts, all SMC
   operands, bank shadows, private pointers and stack depth after the change.
   Save slots `State+7FE/7FF` also require closure against any added audio APIs.
3. Reverse the native held-input byte into source `$31`: A=01, B=02,
   Select=04, Start=08, Up=10, Down=20, Left=40, Right=80. The source updates
   its own `$0735` A/gravity edge latch. Up+A reverses upward; Down+A reverses
   downward. Do not force a flip on every held frame or replace jump physics
   with Sophia/Mario constants.
4. Source world X is `$0480/$0498`; top-left Y is `$04B0/$04C8`. Fractional
   walking is `$0730`, the original jump clock `$05B8` runs 0..49, vertical
   displacement is `$0570`, and gravity is bit 7 of `$0734`. Collision samples
   use X offsets 4..27 and Y 0..31 (the active feet/head edge swaps with gravity).
   Native contacts must preserve this ordering and update source support state.
   Initialize source right bound `$0732/$0733` to the actual host extent;
   the source level-one fixture's 228 is not an SMB world limit.
5. The source actor calls 10 external interfaces, listed with exact call sites
   in `assembly.json`. Replace them with explicitly typed host adapters:

   | Entry | Source responsibility / boundary |
   | --- | --- |
   | `FF1E` (`EB22`) | Tile lookup into source RAM; returns `$6E/$6F` pointer. Convert to private/host pointer safely. Do not interpret SMB metatile bytes as original tile flags. |
   | `FF33`, `FF36` | Side/contact and slope/support response. Original contact masks include gravity-dependent sides. |
   | `FF3F` (`DA71`) | Source 240-line Y normalization. Preserve its carry contract if retained. |
   | `8BCF` | Moving-platform/object displacement and aggregate velocity. The original helper can enter `AB53`; it is an isolated external boundary in the frame test. |
   | `FF27` (`DCAE`) | Source object updates/animation clock. It updates unrelated source objects too; do not import it wholesale over SMB enemies. |
   | `8874` | Source scrolling/CHR machinery via original scene dispatcher. Replace with committed host camera handling. |
   | `FF39` (`D75B`) | Banked source service dispatch; final frame tail call also runs source scene logic. Preserve needed animation effects with a host-owned leaf, not the whole source scene. |
   | `9ED7` | Optional scripted actor control; not a normal player movement hook. |
   | `FF18` | Source scene/VRAM completion; never call an original forced-blank spin loop in live SMB gameplay. |

6. Original B-spawn code creates independent slots 2/3 in source object arrays;
   both slots activate in the donor run. Their update, native enemy/brick hits,
   score/effects and original projectile graphics still need separate recovery.
   Source weapon/armor/Gravity Fire upgrade fields are present in this actor,
   but earned pickups and all upgrade branches are not qualified by 480 frames.
7. `art.json` stores original pattern byte offsets, not host-allocated tile IDs.
   Allocate CHR per pose, preserve original flip/priority/palette behavior and
   camera commit order, keep world CHR windows unchanged and draw through the
   native OAM capacity/rotation path. The original first6-cell idle geometry is
   verified; a generic palette or extra generated outline is not necessary.
8. Music/SFX are not ported by this actor component. Source queues `$07E3/$07E7`
   remain original actor writes; no acoustic or timing claim is made.

The CPU oracle supplies vblank/sprite-zero readiness without raster timing.
No native Mesen instance was launched for this component. Complete cold
Select/Start/continue, injury/death, pipe/world transitions, Easy/Hard rules,
controller-earned upgrades, real interrupts and native 1-1 routes before
declaring the character playable or publishing a nightly with it enabled.
