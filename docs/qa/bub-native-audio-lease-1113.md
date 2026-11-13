# Bub/Bob native funding and scheduling study

This is a source-only study of exact public `7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`.
It grants no storage and emits no ROM, Lua, capture or build files. Root owns
the Mesen queue. Private a77 remains uninstalled; its unchanged 30Hz empty
cadence is recorded in [the probe report](bub-empty-loop-probe-1113.md).

`tools/audit/audit_bub_native_audio_lease_1113.py` runs under the existing
`build/prince-pickup-reach-1112 --max-files 1` bounded root, with zero files.
The user's dirty historical progress JSON is untouched.

## Actual scheduling budget

Eight ordinary cold-derived empty pairs use the unmodified native IdleLoop.
One actual busy NMI at the source clock increments NmiSkipped; the existing
TerrainCatchupPending then admits exactly one non-draw Main and clears its
draw skip before waiting again. No skipped-draw, counter, actor, position or
ability byte is supplied. Each pair reaches both real returns 82BE and 82D0,
with one source update per Main and no actors at X40/Y176.

| Cost, CPU cycles | Public 7ef | Private a77 |
| --- | ---: | ---: |
| Normal draw Main, excluding the injected busy NMI | 45,419–45,476 | 42,989–43,046 |
| Actual non-draw catch-up Main | 37,296–37,798 | 35,905–36,407 |
| Auth calls, normal/catch-up | 14 / 13 | 14 / 13 |
| Generic RAM transports, normal/catch-up | 8 / 7 | 8 / 7 |

Regular NMI takes 4,311–6,041 modeled CPU cycles; add the unmodeled 513-cycle
OAM DMA. Busy NMI takes 2,740 normally, with 3,257 initially; the measured
native IRQ takes 120. The CPU model does not reproduce video phase alignment.

NTSC provides about 29,780.5 CPU cycles per frame. A three-frame pair, or
**40 source updates/second**, has about 89,341 cycles for two Mains, one
regular NMI/DMA, two busy NMIs and three IRQs. The measured baseline needs
roughly 4.5–6.8k cycles removed per pair; a77's 3,821 misses that threshold.
True 60Hz would require roughly 20–22k removed from each normal Main, not a
6–8k reduction. These are budgeting estimates, not native cadence results.

An explicitly unfunded WRAM5800 **direct CPU fixture**, derived from genuine
Bub cold/menu state, measures a 227-byte unrolled complete-header checker.
It matches current returned AXYP/SP/maps and R5/R6 for all 256 valid P values
and 192 poisoned-header cases. It saves 249 cycles per valid check, or 6,723
per normal/catch-up pair before gateway costs. Combined with a77, this gives
about 3.7–6.0k pair margin for a gateway and video phase. No WRAM5800 runtime
allocation is proposed. Exact native placement and foreign costs remain open.

## Current Rogue page, not free zeros

Physical PRG87 BF00..BFFF is the complete original Rogue Dawn `RdaPage94`,
declared in `src/rogue_dawn_audio_pages_v3.s`. The page is five bytes
`ad ad 1e 20 20` followed by 251 zeros. Its SHA-256 is
`3574a5efbb8dd0c3b5708ef977aa329e487ccbf28f3630a2352aadedd8ed429c`;
the full current bank87 hash is
`5ad254f292f54fa7147dd7917170b9903933ef27fcd7e1a2fd863b389bacf76b`.
File range is half-open 720656..720912. All fifteen source depot symbols
RdaPage80..94 bind the actual B100..BFFF depot. The current bank prefix holds
live TMNT movement/render/lifecycle and the BT cold router; none is retired.

All **224 actual current** lower/upper Rogue map rows were inspected. Only
lower row126 maps this page, with tag D7/high BF at file byte515125. No literal
local JSR/JMP in the prefix targets BF00..BFFF. This is not an indirect-reader,
alternate-map or DMC exclusion proof.

The exact current reader C97:C409..C47F is authenticated. Its existing virtual
mux C469..C47F already maps a bit7-clear tag with bit7 restored, then enters
BF00 (DA retains its specific B705 view). Thus a hypothetical D7→57 map row
can preserve every logical byte through a 29-byte native synthesis leaf;
**227 bytes remain potentially recoverable**, not granted. The leaf uses AND
classification and no PHP/PLP, preserving arbitrary model P as well as the
real C/V/DI flags. An earlier 25-byte PHP version normalized model bit5 and
was rejected by the arbitrary-P boundary gate before any ROM file existed.

The in-memory reader fixture poisons all 227 residual bytes with AA. Actual
reader execution passes all **57,344 logical byte/AXYP/SP/map/touched-RAM
comparisons**, plus 1,536 arbitrary-P boundary comparisons. The affected
256-byte page costs **19–25 additional cycles/read**; all other 57,088 reads
have exactly zero added cycles. This establishes data and direct reader
behavior, not native-page ownership or full audio timing.

## Emitted gateway cost: rejected design

The in-memory `--gateway-cost` fixture fits an actual native layout without
new PRG/CHR/RAM: the existing native65 CoCheckHeaders40-byte interval remains
40 bytes, a duplicate five-byte CoSmc table is rebound through its two actual
getters AE1D/AEC8 to the existing identical AA61 table, and that exact five
bytes holds the mapper stub. A 199-byte C87 worker after the 29-byte audio
leaf leaves 28 bytes. Native65 AF27 is retained; the mapped worker is DF1D.

Cold-derived direct fixtures pass **1,792 valid-P and 1,344 poisoned-header
cases** across the seven actual table pointer entries. These include six
cookie paths and the table-boundary pointer; supplied headers are explicitly
ABI fixtures, not new foreign-owner cold claims. Returned AXYP/SP, complete
native RAM, SMC, live stack and final maps match. Minimum foreground SP is
217. No code is emitted to a file and no production candidate is exposed.

The actual gateway erases much of the theoretical saving: Bub saves only
**111 cycles/check**, or **2,997 per normal/catch-up pair**, after the bank
transfers. Other valid cookie checks cost **113 additional cycles/check**.
Together with a77 the pair saves 6,818, leaving almost no worst-case budget
margin and risking foreign cadence. Root rejected this design: **no grant,
installation or native test**. Its exact in-memory fixture is retained as a
measured negative. The physical87 indirect/alternate-map/DMC closure remains
unfinished; equality of the logical bytes does not authorize its reuse.

## Required for any future audio-page lease

- Close current physical87 indirect/native/graphics alternate mappings and
  DMC sample ownership, including retained native TMNT and BT consumers.
- Give an actual native gateway layout, exact code/preimages and its measured
  worst-case normal/catch-up cost. A generic gateway must also disclose any
  foreign-owner cost increase; source behavior equality alone is insufficient.
- Qualify genuine IRQ/rendered NMI cuts and actual ordered Rogue audio, then
  source warm/cold/foreign behavior for any integration. The current reader
  fixture claims none of these.
- Obtain root's explicit source-qualified allocation before a production
  gameplay proposal. Do not infer a lease from equality or a zero run.

The current next target is a typed native no-op/full-box or a measured
40Hz-capable structural transport reduction. A structural
bundle that checks complete headers at every external entry may remove more
redundant work than moving isolated primitives, but no unchecked auth cache,
persistent admission bit or source-physics substitute is authorized here.
