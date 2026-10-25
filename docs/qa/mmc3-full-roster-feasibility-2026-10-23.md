# Full-roster MMC3 feasibility

The user clarified that an **oversized MMC3 with up to 2 MiB PRG-ROM** is an
acceptable target. Under that target, **all current program content and the
entire uncompressed graphics image fit the storage budget**. The earlier
512 KiB audit below applies specifically to ordinary MMC3; it was too
restrictive for the user's intended target.

This remains a feasibility result, not a working full-roster MMC3 build.
Identical MMC5 expansion-channel audio cannot be retained on MMC3 hardware.

The audit reads the frozen ND release:
`2b0a3b7ee1581bc011b8df1f7e1683020a7fa3f90f580e142c070f7f3e3d75ba`.
No ROM, cartridge header, prepared graphics or gameplay source was modified.

## Revised result: oversized MMC3

Oversized MMC3 extends R6/R7 to eight bank bits, providing 256 banks of
8 KiB / **2 MiB PRG-ROM**. This is documented as an extension with varying
emulator support. [Oversized MMC3 reference](https://www.nesdev.org/wiki/MMC3)

| Resource | Bytes |
| --- | ---: |
| Oversized PRG capacity | 2,097,152 |
| Current linked program/music/data | 621,913 |
| Entire current graphics image, including its unused space | 1,048,576 |
| Combined content | **1,670,489 / 1.593 MiB** |
| Aggregate storage margin | **426,663 / 416.66 KiB** |

A bank-layout capacity experiment keeps all original program banks 0–99,
places all raw graphics in banks 100–227, and moves the two fixed code banks
to 254/255. Banks 228–253 remain completely free: **208 KiB** of whole-bank
space, in addition to unused space within the preserved program layout.
Every preserved program byte and every graphics byte compares exactly with
the released MMC5 build. This container is a placement proof; its existing
MMC5 instructions have not been converted into executable MMC3 code.

A separate standalone diagnostic ROM executed real 6502 instructions on the
installed Mesen build. All **256 PRG banks** were selected/read through both
R6/R7 in both PRG modes: **1,024 banking cases passed**, including the last-two
fixed banks. Lua only observed the CPU's result; it did not write emulated
memory. This establishes local emulator support, not flash-cartridge support.
Mesen's upstream mapper implementation also retains the complete eight-bit
PRG bank values. [Mesen mapper source](https://github.com/SourMesen/Mesen2/blob/master/Core/NES/Mappers/Nintendo/MMC3.h)

The preferred oversized design is **2 MiB PRG plus banked CHR-RAM**, with
graphics stored in PRG. Oversized PRG does not extend MMC3's CHR register
width. A CHR-RAM loader/cache removes the need to force all art into a
256 KiB CHR-ROM layout. The capacity proof does not depend on compression or
discarding characters, tracks, animation frames or outlines.

Remaining implementation work is concrete:

- Cache/load active character, weapon, world and HUD graphics into CHR-RAM.
  Prove upload timing and residency, including live weapon/ability changes;
  extra PRG capacity does not remove the PPU transfer budget.
- Relocate the expanded profiles' 1 KiB ExRAM state using an explicit RAM
  overlay plan.
- Convert mapper publication, fixed-bank references and HUD IRQ behavior.
- Use the existing MMC3 sound fallback/priority rules for the missing MMC5
  pulse voices.
- Establish the supported emulator/flash-cartridge implementations. The
  standalone Mesen test does not certify a particular physical cartridge.

The diagnostic declares 32 KiB CHR-RAM as a proposed cache size. It tests PRG
banking only; no CHR cache or full-game performance claim is made. Evidence is
under `build/verification/mmc3-oversized-feasibility-nf/proof.json`, alongside
the diagnostic source, ROM and native result. The released game ROMs remain
unchanged.

## Original audit: standard MMC3 hardware budget

Ordinary MMC3 supports 512 KiB PRG-ROM, 256 KiB CHR, an 8 KiB PRG-RAM window,
and no expansion audio. PRG registers R6/R7 have six effective bank bits. A
larger NES header does not add the missing address lines. Oversized mapper-4
ROMs supported by some emulator implementations are a different compatibility
target. [MMC3 hardware reference](https://www.nesdev.org/wiki/MMC3)

| Resource | Current full-roster build | Standard MMC3 target |
| --- | ---: | ---: |
| Declared PRG-ROM image | 1,024 KiB | 512 KiB |
| Linked PRG segments, including internal reservations/imported binaries | 621,913 bytes / 607.34 KiB | 524,288 bytes / 512 KiB |
| Declared CHR image | 1,024 KiB | 256 KiB |
| Unique complete 1 KiB CHR pages | 392 KiB | 256 KiB |
| Offline co-resident tile-pair repacking experiment | 341 KiB | 256 KiB |
| Unique exact 8x16 tile-pair dictionary | 203,744 bytes / 198.97 KiB | Storage bound only |
| Declared PRG-RAM allocation | 8,189 of 8,192 bytes | 8,192 bytes |
| Extra character-state memory at $5C00–$5FFF | 1,024 bytes of MMC5 ExRAM | Must be relocated |

There are 426,663 bytes of unallocated PRG padding in the 1 MiB file. Removing
that padding still leaves the linked program 97,625 bytes over the MMC3
limit. This is a lower-level measurement than the ROM file size, but it still
includes internal reserved space and original imported binaries. It is not a
proof that every linked byte is necessary. A rewritten MMC3 bank dispatcher,
tables and loaders also need space.

## Graphics experiment

Exact 1 KiB-page deduplication reduces the 1 MiB CHR image to 392 KiB. The
current packer already performs much of this kind of sharing for the standard
roster, so simply rerunning it cannot add the complete roster.

A separate offline experiment permits tile indices to change inside each page.
Every pattern on each old page must remain available together in one new page;
the first 16 KiB stays byte-exact. Thirty-two deterministic greedy packing
trials reached **341 pages / 341 KiB**. Every one of the old 1,024 pages and
32,768 tile-pair slots reconstructs exactly. No pixels, animation frames or
outline graphics are removed. This remains 85 KiB over the target, and it has
not implemented all background/font/paired-window residency constraints.

The promising storage bound is that all exact 8x16 patterns together occupy
only **198.97 KiB**. Folding horizontal/vertical sprite reflections gives an
optimistic 175.56 KiB dictionary, but that treatment cannot be applied blindly
to background tiles. Neither dictionary is an executable layout. A real packer
must group the patterns required by each actual pose, simultaneous projectiles
and world actors into the mapper's available windows. It must rewrite every
tile reference and preserve sprite ordering, flips, outlines and the HUD split.

Static CHR-ROM with a new pose-aware allocator is the strongest first design
to investigate. It keeps animation changes as bank switches and avoids adding
large per-frame PPU uploads to an already busy game.

CHR-RAM is another hardware-supported design, but it moves graphics storage
into PRG-ROM and requires CPU uploads. The existing project's 2 KiB-history
LZSS codec compresses the exact tile-pair dictionary to **111,682 bytes**, with
an exact independent host decode check. Appending that data to the present
linked program would require **733,595 PRG bytes**, exceeding 512 KiB by
209,307 bytes before indices/loaders. This does not make CHR-RAM a shortcut.
The decoder history also needs a safe RAM allocation separate from concurrent
audio decoding. [CHR-ROM/CHR-RAM tradeoffs](https://www.nesdev.org/wiki/CHR-ROM_vs_CHR-RAM),
[MMC3 board configurations](https://www.nesdev.org/wiki/TxROM)

## Program storage opportunities

Segment-name classification gives the following current allocations; it is not
a live-code analysis and does not establish removable byte counts:

| Group | Linked bytes | Implication |
| --- | ---: | --- |
| Audio engines, playlists, wrappers and samples | 275,507 | Largest redesign target |
| Of those, existing compressed frame-based playlists | 161,905 | Already use command macros and LZSS |
| Graphics/pose record segments | 99,000 | Opportunity for record sharing, mirrored-pose encoding and compact pose data |
| Bill's extended orbit tables | 29,696 | Possible compact exact representation; preserving arithmetic and lag requires proof |

Potential work without intentionally dropping characters, moves, tracks or
frames:

1. Extract only reachable audio code/data from native imports and consolidate
   duplicated kernels where their data addressing permits it. For example,
   the five 8 KiB Metroid imports retain complete source-bank layouts, including
   data resembling original game graphics. No such bytes have been declared
   dead or removed here; sound/lookup reachability needs to establish that.
2. Investigate compact note/sequencer music data in place of stored per-frame
   register streams. Preserve track/event selection and verify the resulting
   timing and output. Existing playlists are already compressed, so further
   generic compression is not a demonstrated solution.
3. Re-encode pose records, sharing exact repeats and genuinely mirrored poses.
   Decompression needs a bounded buffer and a renderer cost budget. Original
   asymmetric poses and sprite priority cannot be discarded as duplicates.
4. Repack relocatable code/data across the 64 PRG banks. Existing native import
   addresses, fixed resident code and DPCM placement impose additional
   constraints; aggregate free bytes alone do not prove a legal link layout.

No savings estimate above is booked as achieved. The required reduction is at
least 95.34 KiB of current linked storage, plus the new MMC3 implementation's
overhead and normal bank-fragmentation reserve.

## RAM, mapper and sound changes

The 18 added identities use MMC5 ExRAM for shared transient state, persistent
records and alternate-selection bytes. Ordinary MMC3 cannot read that memory.
The current 8 KiB PRG-RAM segment leaves just three bytes outside its allocated
extent, although some allocations contain padding or inactive-family state.
An explicit union/overlay layout for inactive character and audio drivers is a
plausible way to recover the needed room. It needs reset, inventory, pause,
alternate-selection and interrupt-liveness tests.

MMC5 physical CHR pages above 255 and its separate sprite/background mappings
must be replaced. New characters currently publish those pages through
`X5SetPhysicalChr` / `X5SetSpecialChr`. MMC3 needs its own address translation,
bank-selection publication and IRQ-safe HUD/font handling. Existing standard
MMC3 support provides a foundation, but it does not implement the expanded
profiles automatically.

The full build really uses the two MMC5 pulse channels for shared world effects
(`src/mmc5_sfx.s`). MMC3 has no corresponding hardware voices. The existing
standard MMC3 mix path borrows NES music channels for effects; a full port would
need equivalent prioritization or rearrangement. Preserving the roster and
moves is a different feasibility question from preserving every simultaneous
MMC5 voice exactly.

## Decision

- **Oversized 2 MiB MMC3:** the full existing content fits the storage budget,
  including all raw graphics. The banked CHR-RAM port and runtime adaptations
  remain to be implemented and verified.
- **Current implementation on ordinary MMC3:** does not fit or run unchanged.
- **Full roster and moves after a redesign:** plausible; capacity remains
  unproved. Graphics patterns have a promising storage bound, while program
  data, bank residency and RAM allocation require concrete prototypes.
- **Every current MMC5 capability, including independent expansion voices:**
  cannot be reproduced identically on plain MMC3 hardware.
- **Larger MMC3-derived/custom board:** a separate cartridge design and mapper
  compatibility decision, not proof of fitting the existing MMC3 ROM.

For the oversized target, the next useful proof is a working CHR-RAM cache
and explicit RAM overlays, followed by mapper integration and regression
testing. The 256 KiB pose-aware graphics / 512 KiB PRG packing goal applies
only if strict ordinary-MMC3 compatibility is required. The public MMC3 and
MMC5 ROMs remain the frozen ND releases.

Measurements and offline reconstruction artifacts are in
`build/verification/mmc3-full-roster-feasibility-ne/`: `measurements.json`,
`co-resident-packing-proof.json`, `co-resident-pair-map.json`,
`budget-profile.json`, and the experimental CHR/dictionary data. The zlib
figures in the measurements are PC-only comparisons, not proposed NES decoders.
