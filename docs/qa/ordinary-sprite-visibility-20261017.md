# Ordinary sprite visibility: immutable29

The128 explicit flat arenas cover Mega Man, Samus, Bill and Bass, both mappers,
outlines on/off, idle/walking, and0/1/2/4 ordinary supported Goombas. After setup,
the only input is idle or Right. Every Goomba stays live and supported; there
are no attacks, injuries or outcome/timer patches. The eight diagnostic runs
pass and measure8192 physical frames. This is an isolated renderer audit,
not a controller stage-clear proof.

`tests/ordinary-oam-visibility.lua` attributes source parts at their real
renderer calls, verifies the completed hardware OAM copy, decodes mapped CHR
and actual palettes, then evaluates the NES first-eight sprite selection per
scanline. Selection counts a sprite's entire16-row rectangle, including
transparent rows. Per-actor composite comparisons distinguish lost pixels,
wrong colors, whole-actor loss and absent OAM submission. It separately records
completed DMA and game rendering across physical frames.

All8192 samples have every expected live actor submitted, no rejected OAM
allocation, and at most20 visible OAM entries. The64-entry total OAM limit is
not involved. No whole player body disappears, but portions of players and
whole Goombas lose scanline selection. Four Goombas also cause physical frames
without a fresh completed draw/DMA.

Walking, outlines off,64 physical frames per row:

| Mapper | Player | Goombas | DMA | Peak row sprites | Player partial frames | Whole-hidden enemy actor-frames |
| --- | --- | --- | --- | --- | --- | --- |
| MMC3 | Mega Man |1|64|7|0|0|
| MMC3 | Mega Man |4|32|13|48|41|
| MMC3 | Samus |1|64|5|0|0|
| MMC3 | Samus |4|43|11|0|64|
| MMC3 | Bill |1|64|7|0|0|
| MMC3 | Bill |4|34|13|33|24|
| MMC3 | Bass |1|64|9|33|0|
| MMC3 | Bass |4|33|15|58|58|
| MMC5 | Mega Man |4|32|13|52|40|
| MMC5 | Samus |4|43|11|0|64|
| MMC5 | Bill |4|33|13|34|21|
| MMC5 | Bass |1|64|9|30|0|
| MMC5 | Bass |4|32|15|56|64|

An enemy actor-frame denominator is Goombas×64; four enemies give256, not64.
The first complete pass without per-actor streaks is preserved separately;
the final summary includes each actor's visibility and longest hidden streak.
Samus keeps the player's fixed OAM priority while the other three rotate the
whole ring. With four Goombas, Samus outlines off yields64 aggregate hidden
enemy actor-frames and a longest per-enemy hidden streak of6 physical frames;
outlines on yields128 aggregate hidden actor-frames. Enemy shuffle changes
which Goomba loses. These counts do not assert permanent starvation.

Evidence: `build/verification/ordinary-oam-v29/summary.json`, eight logs and
compact per-character JSONL tables. The JSON records both immutable ROM hashes
and the exact fixture hash. No runtime or asset changed during the audit.

## Read-only opaque-pixel-preserving layout feasibility

`tools/audit/analyze_sprite_vertical_alignment.py` reads the actual ROM pose
records and decoded CHR. It checks every legal vertical shift and existing
pattern reuse under H/V flips, asserting identical opaque coordinates and
color indices. The coordinate-descent plans are feasible examples rather
than proofs of optimality. Both mapper reports agree.

- Bass WALK3 can reduce body plus one Goomba from9 to8 sprites per row. Its
  white part7 movesY16→22 using existing tile10 with V flip. The face part10
  movesY12→6 with one new32-byte pattern. BankE1 has zero pairs30/31 available;
  both directions need the same new pattern. No physical bank is needed.
- Bass WALK1 can move white part9Y16→4 by reusing tile2C with H flip. This
  removes phantom row pressure without consuming CHR, but seven original
  parts have genuine opaque pixels on one Goomba row, so independent vertical
  shifting alone cannot lower its peak9 demand.
- Bill WALK2 can move part5Y16→25 with one new32-byte pattern in bank1D's
  zero pair31, reducing body plus one Goomba from7 to6 sprites per row.
- Mega Man's relevant normal banks have no zero pairs. Lowering idle's peak
 7→6 would need two new patterns and a separate pool-allocation audit.

The stronger bounded WALK1 composite search in
`tools/audit/analyze_bass_composite_cover.py` discards only pixels already
occluded by another body part and retiles the final image. It preserves exact
palette/color-index symbols, not just the current RGB, retaining palette
cycling semantics. A2004-candidate integer cover proves a9-part layout with
maximum6 body sprites per row (8 with one Goomba) covers the same341 opaque
pixels. It needs eight patterns new toE0. A complete reference-closure audit
finds E0 pairs13..22 are exclusively used by WALK1/DASH pointer aliases across
all252 pose-bank entries and both directions. They can be reclaimed without
touching the other body patterns or common buster pair0. The bank's zero
pair31 can remain unused. This feasibility does not itself modify an asset.

Reports: `vertical-alignment-feasibility.json`, its MMC5 counterpart,
`bass-walk1-composite-feasibility-v30.json`, and
`bass-walk1-reference-closure.json` in the same evidence folder. Any future
implementation still requires independent pre/post composite and completed
DMA pressure checks; CPU optimization remains a separate shared pipeline task.

## Implemented31 layouts and independent acceptance

The internal viewport now uses the nine-part Bass WALK1/DASH composite and
the shifted Bass WALK3/Bill WALK2 records. Original records and their original
CHR remain the fallback whenever relativeX is outside16..224, Y outside16..207,
or Yhigh differs from1. This preserves the original renderer's whole-part
clipping at the top and side edges. Both directions retain their exact palette
and color-index symbols; the change does not alter pose timing or movement.

One private1KiB logical bank83 preserves Bass's original E0 bank, including
every old fallback pattern. It copies the ordinary buster pair0. The only
changed bytes in previous physical CHR are22 bytes in the proven zero pairs
E1:30 and1D:31. All192 original named body records and1,080 table references
retain identical semantics. The ROM uses255/256KiB CHR on MMC3 and247/256KiB
on MMC5. No FIXED or SRAM bytes were added.

`bass-ordinary-body-layout` and `bill-ordinary-body-layout` pass4,600 actual
completed-DMA composites across both mappers. The independent oracle decodes
immutable30 ROM records and patterns rather than generated31 assets. It
covers all three power levels, both directions, outline modes, star colors,
Bill fire/Lance exclusions, both guard boundaries, page-carry seams, side
clipping, and every above-top Y−25..−1. Bass's ordinary native-drawn buster is
also checked in all2,760 Bass images while83/E0/E1 mappings change. Six global
palette-symbol composites independently equal their original30 images.

The first reference export incorrectly passed the entire attribute byte as a
horizontal flip argument. That negative is preserved and excluded. The
corrected exporter reads H and V bits independently and regenerates solely
from30. A separate initial pointer assertion assumed that Bill always used
the outline RAM filter; Bill has no added-mask flag, so the final assertion
checks the actual per-character policy. Neither issue required a runtime fix.

The same128 ordinary arenas and8,192 physical samples pass31. Selected
walking results, outlines off,64 physical frames:

| Mapper | Player | Goombas | DMA | Peak row sprites | Player partial frames | Whole-hidden enemy actor-frames |
| --- | --- | --- | --- | --- | --- | --- |
| MMC3 | Bass |1|64|8|0|0|
| MMC5 | Bass |1|64|8|0|0|
| MMC3 | Bill |2|64|8|0|0|
| MMC5 | Bill |2|64|8|0|0|
| MMC3 | Bass |4|32|14|54|52|
| MMC5 | Bass |4|32|14|54|52|
| MMC3 | Bill |4|32|12|32|12|
| MMC5 | Bill |4|35|12|29|10|

Bass plus one Goomba improves from row9 and30/33 partial-body frames to row8
and zero. Bill plus two Goombas also stays within eight. Larger crowds still
overflow the physical row limit, and still skip some fresh DMA/render frames.
There are no rejected OAM allocations or missing actor submissions. The
64-sprite total remains unrelated to this flicker.

Evidence is consolidated in
`build/verification/ordinary-oam-v31/acceptance-packet.json`, with source and
fixture hashes, all four passing art logs, before29/after31 crowd tables,
original negative exclusions, and `packing-invariants.json`.32 differs from31
by exactly two menu palette bytes, with identical gameplay/CHR; the full32
suite independently reruns the registered art checks. This acceptance does
not establish controller playthrough clears or general zero-lag behavior.
