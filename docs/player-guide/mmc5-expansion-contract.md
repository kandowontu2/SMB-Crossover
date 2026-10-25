# Private expanded MMC5 cartridge: hardware and integration contract

The user chose the full expanded roster for MMC5 and the current roster for
MMC3. This is an isolated hardware/build proof, not a finished expanded-roster
ROM. Main sources, main cartridges and the current player-guide edition remain
unchanged by this work.

## Retained proof

`build/player-guide-agent/mmc5-expanded-private/` contains the separate linker
configuration, copied source, build log, cartridge, symbols, and receipts.
Reproduce with `build/player-guide-agent/mmc5_expand_private.py`, then run
`build/player-guide-agent/check_mmc5_expand.py` with a Python containing py65.
Neither script runs the mutating main asset builders.

Cartridge: `smb-crossover-mmc5-expanded-proof.nes`, 2,097,168 bytes, NES2 mapper5,
1 MiB PRG +1 MiB CHR. Current SHA256:
`906c4c92ee92372d82afa34e1dd70867ed1ffcbfebddeec4073950f339e180f4`.
The high CHR pages deliberately contain diagnostic signatures, **not new hero
artwork**. Replace that test segment when authentic expanded art is integrated.

Passed linked-code CPU/mapper tests:

- 22,849 common named labels retain their original CPU/RAM values.
- Original physical PRG banks0..61 and CHR pages0..255 remain byte-identical.
- 16 mapper initialization cases, including every possible initial upper latch.
- 2,048 old-roster publication differentials: A/X/Y/allP/SP, ordinary RAM/SRAM,
  all twelve effective CHR windows, and coherent A-window restoration match HR.
- 12,288 exhaustive bank-register cases: every physical CHR page0..1023 in each
  of twelve hardware windows, including independent high-page signature reads.
- 64 special/HUD override combinations retain their precedence and high bits.
- 124 real existing SMC farcalls reach PRG64 and125 and restore every previous
  bank0..61. These calls use compiled `FarCallCommon`, not a bypass call.
- 12,288 generic word-setter cases, 1,024 special word-setter cases and five
  complete mode-clear cases preserve the documented memory ownership.

These are synthetic RP2A03 CPU arenas with an independent register/latch model.
They do not establish real PPU scanline timing, controller playthroughs, flashcart
support, or physical cartridge behavior.

## Hardware facts and source audit

In the installed mode3, PRG windows select8KB banks using seven address bits;
the ROM flag remains bit7. A full1 MiB therefore uses physical banks0..127.
CHR mode3 uses twelve1KB windows with ten-bit bank registers. `$5130` supplies
the upper two bits **when each `$5120..$512B` register is written**. Changing the
upper latch afterward leaves those loaded ten-bit values intact. Normal
attributes differ from ExRAM extended attributes, where upper bits affect live
background addressing. [NESdev MMC5 register reference](https://www.nesdev.org/wiki/MMC5)

Mesen's primary mapper implementation independently records each CHR register
as a16-bit value assembled from the low write and upper latch, masks ROM PRG
banks to seven bits, and keeps sprite/background register sets distinct in
8×16 mode. See `SwitchChrBank`, `GetCpuBankInfo`, `UpdatePrgBanks`, and mode3
`UpdateChrBanks`. [Mesen MMC5 implementation](https://github.com/SourMesen/Mesen2/blob/master/Core/NES/Mappers/Nintendo/MMC5.h)

Current game writers are `MapperInit` and the `SwitchAreaCHR` expansion inside
`BankSwitchCHR` (`src/mmc5.s`, `src/reset.s:215`). The manual scroll IRQ does not
write CHR registers. Legacy `BankSprCHR*` / `BankBgCHR*` macros have no live
callers; their generic immediate helper ORs the PRG ROM flag, so new wide CHR
code must use the new publisher rather than those macros.

## PRG layout and exact ownership

The separate `mmc5-expanded.cfg` inserts physical banks62..125 before the
resident areas. Original banks0..61 keep their physical positions and bytes.
Old resident banks62/63 become126/127, at the same CPU8000/E000 addresses;
vector CPUFFFA remains in the final bank. Mapper initialization explicitly
selects FE/FF for those resident windows. The default reset mapping therefore
still starts in the final ROM bank.

New linker areas are `X5_NEW_3E` through `X5_NEW_7D`. Bank62 holds the cold CHR
publisher, initialization and setter APIs. Bank64/A000 is available for Proto
Man audio; bank65/C000 is reserved for his presentation/tables as requested by
root. The other new areas currently default to A000 windows; change an area's
CPU origin to C000 when assigning a graphics bank, and use the corresponding
native PRG C-window publication. Physical bank numbers remain7-bit; compiled
MMC5 ROM selectors OR80. Root coordinates all future allocations.

The private experiment uses banks64 and125 for four-byte farcall probes; they
are test-only segments and must be removed when real assets occupy those banks.

There was insufficient free MMC5 fixed-tail space for a new resident stub.
Instead, the boot publication bridge retains/pads its original20-byte span;
the NMI bridge retains/pads the original136-byte publication span. It jumps
over the padding, so the padding does not become a runtime delay. Their helper
code lives in new bank62. No existing source contribution moves.

The NMI bridge uses direct PRG register writes and the already-saved main
`CurrentBank`; it never edits shared farcall SMC or `CurrentBank` itself. It
restores the main A-window owner after publishing. Full NMI routes still need
to qualify transient title-screen A-window ownership, where native code may
have temporarily mapped TITLE without changing `CurrentBank`.

## Fifteen-byte CHR ABI

The experiment reserves only the proven pre-existing gap at73E0..73EE; root may
relocate these aliases within its private helper gap. It allocates no new bytes
after the existing SRAM tail and does not move `XgLzHistory` at7400.

| Field | Bytes | Meaning |
|---|---:|---|
| `X5ChrMode` |12| One entry for each5120..512B hardware window |
| `X5SpecialChrUpper` |1| Upper two bits for existing active special-art override |
| `X5HudChrUpper` |1| Upper two bits for existing active HUD-art override |
| `X5WideChrActive` |1| 0=unchanged legacy fast path;1=ten-bit publisher |

For a `X5ChrMode` entry, bit7 clear selects the existing8-bit logical
`CurrentCHRBank` value through `ChrPhysicalMap`, with upper bits0. Bit7 set
selects a direct physical bank: low eight bits from the corresponding
`CurrentCHRBank` byte, high two bits from the mode byte. Bits2..6 are ignored.
New art tables therefore need explicit physical Lo8/Hi2 arrays; appending
8-bit logical IDs would wrap and is not the new ABI.

Active special art at sprite window4 and active HUD art at background window8
retain precedence over the generic window mode. Their existing low-byte fields
are combined with the new separate upper fields. On MMC5 these are actual1KB
window numbers; do not pass a2KB pair index or apply a second increment.

All writes must stay inside the existing private GameLoop frame. `GameLoop`
sets `NmiDisable=FF` before updating and releases it at `PauseSkip`
(`src/game.s:46`, `src/game.s:113`). Guest lag NMIs retain the old hardware CHR
along with old hardware OAM (`src/reset.s:259`). A16-bit bank selection can
therefore be prepared as two ordinary bytes before the completed frame is
published. Do not introduce new wide-word writers outside that barrier.

APIs in bank62 (A/X/P volatile; preserve Y unless it is the input window):

- `X5SetPhysicalChr`: A=physical low8, X=upper2, Y=window0..11. Stores its mode,
  enables wide publication, and sets `ReloadCHRBank=1` without counter wrap.
- `X5SetSpecialChr`: A=actual special1KB page low8, X=upper2. Activates the
  existing special override and requests wide publication.
- `X5ClearChrModes`: clears all fifteen bytes and requests a reload. Then rebuild
  the selected legacy profile's ordinary logical window bytes in the **same**
  private frame before releasing NMI.

The bootstrap clears all fifteen bytes and explicitly selects normal attributes
and disables the unused MMC5 vertical-split region. The game's native CPU scroll
IRQ remains responsible for the HUD split.

## Timing and remaining integration proof

The old-roster fast path is the original unrolled publication after clearing the
upper latch. Measured added CPU cost is52..53 cycles when a reload occurs.
Ten-bit publication measured435 cycles for a one-window wide test. The wide
path writes the proper latch immediately before every register write and clears
the latch to0 afterward, without disturbing the ten-bit values just latched.

Before shipping, integrate root's current helper/Rygar changes, use authentic
new art, remove probes/diagnostic CHR, and validate real reset/title selection,
legacy/new profile switching, lag-frame publication, special/HUD coexistence,
music bank restoration, scanline timing and controller routes. This packet does
not implement any new character by itself. The inherited MM3_AUDIO/ROSTER
alignment warnings do not reflect a new layout change: their original bank
bytes and CPU addresses are unchanged in this proof.
