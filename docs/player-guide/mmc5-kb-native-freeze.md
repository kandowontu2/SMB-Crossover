# KB-based MMC5 expansion: frozen integration packet

The expansion hardware baseline is ready for incremental integration. This
packet is private and **has not been adopted into main**. Main remains the Rygar
walk repair checkpoint KB. The original HR experiment and its 243-file frozen
receipt remain unchanged.

## Files to merge

The six-file overlay is
`build/player-guide-agent/mmc5-native-kb-private/merge-staging/`.
`incremental-merge.patch` beside it contains only these changes; the adjacent
`incremental-merge-manifest.json` records each baseline and staged SHA256.
Apply the patch against the expected baseline or merge the small edits into
any newer work, rather than replacing complete newer source files.

| File | Change |
|---|---|
| `src/entrypoint.s` | Flagged expanded header and new core include |
| `src/mmc5.s` | Flagged boot/NMI bridges with old published spans preserved |
| `src/options.s` | Boolean `ENABLE_MMC5_EXPANDED`, default zero |
| `src/mmc5_expanded.s` | New cold bank62 initialization/publisher/API; no proof probes or diagnostic art |
| `smb1base-mmc5-expanded.cfg` | Separate 1 MiB PRG / 1 MiB CHR layout |
| `tools/build_mmc5_expanded.py` | Separate target; consumes prepared art without running asset generators |

The ordinary builder/config remain unchanged. The new builder defaults to
`build/smb-crossover-mmc5-expanded.nes` and refuses to overwrite either ordinary
mapper ROM with an expanded build. `--chr-extra` accepts up to 768 KiB of real
prepared upper graphics; absent artwork stays zero-filled. The source-overlay
option permits review without installing the packet:

```powershell
python build/player-guide-agent/mmc5-native-kb-private/merge-staging/tools/build_mmc5_expanded.py --workspace . --source-overlay build/player-guide-agent/mmc5-native-kb-private/merge-staging --output build/player-guide-agent/mmc5-native-kb-private/merge-staged-expanded.nes
```

## Exact cartridge identities

Both ordinary targets were compiled through the staged sources **without
defining the new flag**, exercising its actual default zero. Both reproduce KB
byte for byte:

| Target | SHA256 |
|---|---|
| Flag-off MMC3, 786,448 bytes | `4720972962f8faf6c8e45536f95001e79ae66c7141dcbfa09c768440fa039c00` |
| Flag-off MMC5, 786,448 bytes | `0ab6ac031ae9c80a6e516ce29130e041cfe2e34da5bfb447d78a514fbd2739e6` |
| Native-proved diagnostic MMC5, 2,097,168 bytes | `4b769549c5a114e30d264574667054602cf6b6d8c096c1cf67f42bd5eeb42226` |
| Diagnostic-free staged MMC5, 2,097,168 bytes | `757c2f0ac7bc53993bdcb597f9cec77d6fd1130bc21024e141a5659202f223cd` |

The last two differ only in test-only PRG banks64/125 and the 768 KiB high
diagnostic CHR region. All other PRG bytes, publisher CPU addresses, resident
bridge bytes, and original 256 KiB artwork are identical. The staged cartridge
also passed a fresh native 1,925-frame title/selection/gameplay flow; every
complete native PNG hash matches the ordinary KB control.

All four builds expose the existing fourteen identities across twelve portraits:
Mario/Luigi, Mega Man, Samus, Bill/Lance, Link, Simon, Pit, Rygar, Bass, Ryu,
Sophia III and Scrooge. This hardware packet enables **no empty third-row
portraits and no new profiles**. Those remain separate implementation work.

## Native proof

`native-proof-summary.json` consolidates sixteen accepted native runs, their
source/output hashes, observed counts and explicit scope. It distinguishes the
two retained unsuccessful exploratory runs. The installed emulator was Mesen
2.2.1, commit `4f18f37e8c462fcf7093422a6925d2bf535707a0`, executable SHA256
`8b92daa209ee5052845e02a663aeb1afd6194eca55d86e6628c51114c61da0a9`.

* Native title, all twelve portrait previews, held-Start gate, navigation,
  Select navigation, back/confirmation and real gameplay pass. All 1,925
  complete native screenshot hashes match KB control, both with and without
  diagnostic data in unused high banks. Sixteen retained snapshot pairs also
  match directly.
* Real Options/Cheats flow passes defaults, all 32 level entries and wrap,
  invincibility edges, parent/back navigation, unchanged parent options and
  Samus's selected 1-2 native pipe intro.
* Authored high-bank setup selects 255/256/511/512/767/768/1023 in each of twelve
  windows: 84 native CPU publications. The observer validates actual mapper
  ten-bit values, plus 896 real PPU pattern fetch bytes against ROM signatures.
  It writes ordinary CHR shadow fields to set up each case; it does not replace
  PPU output, OAM or ROM. These are diagnostic patterns, not character artwork.
* Controller-only Mario clears the 1-1 surface route and reaches 1-2 with 25
  rightward polls. Both expanded and KB control take 4,674 frames, zero deaths.
  The identical fixed controller stream produces identical recorded gameplay
  state on every row, including camera, velocity, modes, lives and skipped-NMI
  state. Raw CPU-cycle count is excluded. This is an all-small route, with no
  mushroom/flower or weapon coverage.
* Mega Man, Bill and Bass guest stress fixtures retain the HUD split through
  31/274/253 active gameplay lag frames and 650 active IRQs each. Bass's KB
  control also has 253 lag frames. Setup explicitly seeds power/star state;
  these are stress fixtures, not ordinary no-write playthroughs.
* Across accepted observed runs, 23,786 IRQ instances produce 47,572 final
  scroll writes with **zero timing faults**. Each final write remains on line31
  in horizontal blank, dot257..320.
* NMI/IRQ observers assert A/C window ownership and preservation of the actual
  shared farcall SMC. Complete menu runs encounter two real transient TITLE
  A-window owners; no CPU read from A000..BFFF occurs between CHR restoration
  and AudioUpdate. Native Reset after publishing physical CHR1023 clears the
  fifteen-byte ABI, restores ordinary CHR mapping and accepts Start again.

The earlier independent linked-code CPU/mapper receipt remains valid: 22,849
common named labels unchanged; 16 boot cases; 2,048 legacy publication
differentials; 12,288 ten-bit register cases; 64 special/HUD combinations; 124
real SMC high-PRG farcalls; 12,288 generic setters; 1,024 special setters; five
clear-mode cases. Legacy reload adds 52..53 CPU cycles; wide publication is
435 cycles. No hardware-core repair was needed after the HR receipt.

The unbounded PPU-fetch exploration was explicitly terminated for excessive
callback cost, then replaced by the bounded passing test. A generic adaptive
Mario controller fell at X2579/frame1868; the same known fixed input replay
subsequently passes on both cartridges. Neither exploratory result is counted
as a successful run.

## Integration ABI and reservations

Physical old PRG0..61 and old CHR0..255 remain unchanged. Old resident PRG62/63
move to126/127, keeping CPU8000/E000 and vector addresses. Bank62/A000 owns the
new publisher. `X5_NEW_3E` through `X5_NEW_7D` name physical62..125; future code
must be assigned a proper CPU window, not only a ROM bank number.

Proto ownership coordinated with the other agent is64/A000 audio,65/C000
presentation/audio wrapper,66/A000 cold presentation. Proof probes are absent
from the merge overlay, so they cannot occupy those allocations.

The fifteen-byte reservation is73E0..73EE, within the existing alignment gap:
`X5ChrMode[12]`, `X5SpecialChrUpper`, `X5HudChrUpper`, `X5WideChrActive`. It must
be coordinated with root's separate optional helper/profile SRAM; nothing
moves the published `XgLzHistory` at7400.

`X5ChrMode` bit7 clear retains the old logical map; bit7 set uses a physical
Lo8 in `CurrentCHRBank` and Hi2 in the mode byte. Special/HUD direct overrides
retain precedence. High bank tables therefore need real Lo8/Hi2 arrays.
`$5130` is written immediately before each `$512x` write and cleared after
publication, as required by its write-time latch. Ordinary attributes and the
existing manual scroll IRQ remain in use. See the earlier
[hardware contract](mmc5-expansion-contract.md) for the primary source audit.

Bank62 entrypoints: `X5ColdInit=A000`, `X5PublishChr=A02E`,
`X5SetPhysicalChr=A266`, `X5SetSpecialChr=A27A`, `X5ClearChrModes=A28F`.
SetPhysical takes A=Lo8, X=Hi2, Y=window0..11; SetSpecial takes the actual
1 KiB page Lo8 in A and Hi2 in X. A/X/P are volatile; Y is preserved. Word
writes belong inside the existing `NmiDisable` private-frame barrier. Clear
modes and rebuild legacy logical window bytes in that same frame before NMI.

This proves the native expansion baseline and guarded compatibility. Future
profile/portrait/art/music integration still needs its own tests. Physical
console/flashcart behavior, full-campaign coverage and all-weapons coverage
are outside this receipt.
