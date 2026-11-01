# Karnov equipment HUD v9 — isolated implementation

This component implements the selected Boots0, Boomerang3 and Wings7 display.
It is not integrated or installed. It grants no code, CHR, cache RAM or native
timing lease. The Bomb/Ladder v8 source packet and existing v7 options remain
unchanged.

## Display and original source

The selected item has a full name, two source BCD stock digits and its original
16x16 icon. With no supported owned selection, the display reads FIRE and leaves
stock/icon blank. Zero stock is blank, matching original Karnov's NMI publisher.
The smaller hint alternates SELECT and DOWN+B every128 accepted source updates.
SELECT cycles owned supported equipment and normal fire. Hold Down and press B
to use the selected equipment. Choosing FIRE does not cancel original effects
already active; the actual v7 sequence test verifies that Wings continues.

The donor is `C:/NES/Karnov (USA).nes`, SHA256
`0d49c1120fc13ead1efe4429f7cbb4f01b90e2486c66661c46e922dda6dc830a`.
Original C534..C59F builds icon quads82/83/92/93 (Boots),88/89/98/99
(Boomerang),8C/8D/9C/9D (Wings). The original E099 mapper publisher writes
raw MMC3 selectors5..0 and shadow13+X with CHR inversion clear. BG pattern base
is0000; source shadow14=38 therefore maps those0800-window tiles to physical
CHR page38. The original indexed icon patterns are retained separately.

The native atlas uses tiles30..3B for all twelve icon cells and3C for a simple
plus sign. Source icon indices1 and2 are swapped so original index2 uses native
white HUD ink, while0 and3 remain0/3. This is an explicit palette-index
adaptation: every pixel, transparent pixel and color distinction is preserved,
but the donor's RGB palette is not ported. Existing native HUD palette2 remains
owner, with no palette/attribute/OAM/direct PPU writes.

All51 other font cells remain byte-identical, including every digit/letter
(00..23), blank24, dash28, x29, coin2E, copyright2F, and all KARNOV/WORLD/TIME/
equipment/control text. The native top-status template and numeric/coin/world
producers use these retained glyphs. Cells30..3C are not ordinary Karnov HUD
glyphs; the native IRQ restores font0 before world fetches. This lease is only
for ordinary gameplay: title/menu/lives/time-up/game-over text must never retain
the equipment font.

The source font was inspected in0ffb1d79, then checked identical in delivered
1c073196 and `chr/mmc5/bg_ground.chr` (first1KB SHA256
`275ff7fb837629ec43321dcc4167453e0a176fb62a86ae55733b826a601e67cb`).
The1024-byte source font is preserved; no old ROM or debug tree is copied.

The preparation recipe reconstructs519 exact original HUD/ownership/cursor/
stock-publisher bytes. The tests compare all100 valid BCD values per supported
item against actual donor NMI output and compare the original and relocated
C534 quad builders. The native cursor sprite blinking is intentionally replaced
by a persistent selected icon/name, without adding any hardware sprites.

## Code and data split

The assembled component is440 bytes. The pure `split_source(text)` function in
`prepare_karnov_equipment_hud_1101_v9.py` returns an owning-source proposal:

| Source part | Bytes | Proposed segment |
| --- | ---: | --- |
| KrHudTick through small index tables | 361 | KR_OPTIONS_ROM |
| KrHudDataStart / names36 +hint7 +packet36 | 79 | KR_COMBAT_ROM |

No branch or callback crosses the split. All remote references are absolute
indexed LDA operands. The isolated split link at9000/CD40 and contiguous link
both execute the same behavior. CD40 is a test address, not a resource grant;
root must choose/assert the real existing combat tail. Shared original
dispatcher bytes are not included in the440-byte total.

The one1KB atlas is `equipment-font.chr`. Physical page1023 (lowFF/high3) is an
explicit proposal only. `KrHudPhysicalLow/High` are owning-link constants.
The include never directly writes mapper registers. It publishes the existing
InvHudPhysical/X5HudChrUpper/X5WideChrActive/ReloadCHRBank fields, with dedicated
InvHudActive tagE9. Selection changes update queued tile IDs and do not reload
CHR when the owner is unchanged.

`KrHudCache` needs six authenticated private C2 bytes. Proposed C87A..C87F hold
committed derived selection, displayed BCD stock, hint phase, and three candidate
bytes. Unselected inventory changes need no redraw. The cache changes only
after accepting a whole empty native queue. The cache address is an import,
not an implicit ownership grant.

## Native queue and scheduling boundary

`KrHudTick` is intended for the authenticated gameplay UI service29. It consumes
A/X/Y/P and returns A0/C1 for an owned gameplay call, C0 otherwise. It preserves
all ZP/R0..R7, source state, maps and SMC. No stack bytes are pushed in the
ordinary gameplay worker. The non-gameplay hide branch calls KrHudCancel, adding
one two-byte JSR frame; its actual host stack reserve still needs qualification.

The worker requires raw34, OperMode1, task3, engine8, visible screen and negative
NmiDisable. The latter is the actual foreground GameLoop publication barrier;
the worker must not be called as NMI work. An occupied queue, nonempty header or
nonzero VRAM_Buffer_AddrCtrl defers the complete update without changing cache,
font state or the existing queue. Clean cached state does not publish anything.

The packet has four ordinary literal commands,35 command bytes plus terminator:
2023 length12 (name/stock),204A length7 (hint),2037 length2 and2057 length2
(icon rows). This is one more name cell than the existing34-byte inventory HUD;
it does not overlap KARNOV, WORLD, TIME, score, coins or world/time digits. A
native whole Main/NMI deadline check must account for that one added literal
cell and for later native queue producers. The standalone producer range is
15..1095 CPU cycles; those numbers are not whole-frame lag measurements.

The exact delivered1c073196 ROM consumer proof captures only its68-byte IRQ31
and11-byte publisher tail. Across1024 CPU cases, the publisher resets5130=0,
then the unchanged IRQ restores5128=0 before world fetches, in113 cycles. This
requires no added IRQ or NMI instruction. It is not a full owning HUD NMI replay.

## Required retirement cleanup

`KrHudCancel` clears only ownerE9 and requests the normal CHR reload. Ordinary
non-gameplay guards use it; foreign identities intentionally leave unrelated
HUD owners untouched. Root must add an equivalent conditional cleanup to the
ROM-owned KrRetire/scene path before invalidating the private cache. No C2
opcode may run after its authentication is retired. The current1c resident has
no such cleanup. An inline conditional leaf needs17 bytes using `LDA #1 /
STA ReloadCHRBank`, without assuming the reload flag can safely be incremented.
Actual newlife/scene/menu transitions must be tested after that hook is funded.

## Cache ownership evidence

The audit is bound to frozen1c source packet SHA256
`dedeb87c123ce5b575bcf16f0eb84bd52bffd6a1808174cfd4f25fe5856514ea`.
It resolves587 store operands across25 selected source/kernel/options/pickup/
combat files. The original private RAM writes and conservative255-byte indexed
bounds avoid C87A..C87F. The only three indirect writers have explicit owners:
cold loader zeroC000..DFFF (before publication), newlife stateC000..C7FF,
metadataD000..D540. Subsequent C2 carrier rows are C900..CDFF andD600..DDFF.
Combat's source-bounded17-byte parked frame beginsC869 and endsC87A exclusive;
its exact loop and other indexed scratch bounds are asserted. No postcold
selected-source writer overlaps the proposed cache.

This source audit does not independently grant native callback/global aliases
or prove every future host write. Root's independent whole-owner review and
actual owning link remain required.

## Proof and reproduction

The aggregate CPU receipt records600 original-stock/native display comparisons,
six original/ported icon builders,120 selection/ownership/hint cases,120 clean
cache cases,46 occupied-queue deferrals,84 mode/identity guards, seven actual
assembled v7 Select/Down+B steps,768 source-icon pixel comparisons and1024 exact
current consumer cases. Both contiguous and split implementations execute in
the fixture. Minimum standalone SP is220 from entry224, including hide calls;
it does not qualify actual host Main/ISR reserve.

Use the shared bounded runner with this one owned output root:

```
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-hud-1101-v9 --timeout 120 -- python -B tools/audit/prepare_karnov_equipment_hud_1101_v9.py
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-hud-1101-v9 --resume --timeout 180 -- python -B tools/audit/check_karnov_equipment_hud_1101_v9.py
```

The single PNG is generated from actual assembled packets/font and the existing
native HUD palette. It is a layout/pixel preview, not an emulator screenshot.
There are no Mesen runs, videos, frame forests, owning source edits or installs.
