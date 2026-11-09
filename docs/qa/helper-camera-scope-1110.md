# Helper platform camera admission audit

This audit binds the delivered build
`f2050c1964b53b4bd3dc2e5f24c2ed688d47ad79a8aef6bb2cfd55e28b3e7e42`.
The four literal calls to native `InitEnemyObject` at `$82:$A74F` lead from the
four enabled authored helper managers below. The placement inventory and route
receipts provide the character and crossing scope.
[Placement inventory](helper-platform-inventory-1101.md) ·
[Composition receipt](../../build/helper-camera-render-composite-1110/proof.json)

| Manager | Constructor farcall begins | Camera admission and behavior if full |
|---|---|---|
| Shared generic, including all six WWF identities | PRG 26 `$AD92` | The stored center is eligible at camera-relative X−55 through +295 in Easy and −48 through +288 in Hard. It tries for a free slot throughout that interval, including after the left edge enters view. |
| Thomas | CHR 430 file offset 1489733, loaded at `$B335` | Tries while the native left edge is 256–287 pixels from camera-left. Passing the entry edge marks the record seen even if allocation never succeeded. |
| Goku and Karnov | PRG 26 `$B2DA` | Uses the same 256–287-pixel window with separate placement records. Passing the edge without allocation marks that record seen. |
| Mini Mario | PRG 78 `$BCE0` | Starts when camera-right is 32 pixels before the helper left edge and can retry until camera-right is 47 pixels beyond it. |

The generic GameCore call at `$83C4` reaches `$837B`, bank 26 dispatch `$B134`,
and `HpSpawnAndTrack` at `$AD0B`. Its margin call at `$AD43` reads
`ScreenLeft_X_Pos` and `ScreenLeft_PageLoc` at `$071F/$071D`. All 34 original
records match the repository source and the historical native WWF candidate.
Its added record 34 still applies to all six raw-29 WWF variants in Easy and
Hard. In 1-1, area `$25`, it places a 48-pixel horizontal `$28` at initial
left X1376, center X1400, and Y208. The first eligible native left edge is
at camera-relative +271 in Easy and +264 in Hard. The current Celeste weapon
tail still calls `CmWeapons` and has no ingress to the private Celeste helper
experiment.
[Shared manager](../../src/crossover_helpers.s) ·
[Original table](../../src/crossover_helper_data.inc) ·
[WWF record source](../../tools/audit/propose_wwf_generic_helper_1102_v1.py)

The exact f205 Mini replay constructed all three helpers offscreen at +287,
+286, and +286 in slots 5, 4, and 3, then boarded and crossed each one.
The earlier exact `6bd5e4b1` replay reached six live slots at camera X582
after constructing all three helpers. The actors were those helpers and
three Goombas. The initial f205 Goku attempt constructed the first helper at
+286 in slot 5 and died before reaching it. Earlier native `5444f3e3` runs
establish the Thomas, Goku, and Karnov crossings and their offscreen
construction. Each result applies to its recorded cartridge and controller.
[f205 Mini constructors](../../build/helper-camera-render-composite-1110/mini/capture/camera-lifts.json) ·
[6bd5 six-actor sample](../../build/mini-platform-actor-profile-1110/capture/instruction-sample.json) ·
[Initial f205 Goku attempt](../../build/helper-camera-render-composite-1110/goku/capture/helper-camera.json)

The exact f205 1-1 enemy stream at file offset 19023 has ordinary Goombas
at X352 and X640, a two-actor group command at X864, and two singles at
X1280 and X1312 near the WWF entry. For the 34 original records, the static
census used the wider Easy margin for both modes and counted enemy stream
origins from 72 pixels behind first eligibility through the parser's right
look-ahead at entry. The largest counts were four
authored actors near the 3-3 and 6-3 helpers. This census includes group
multiplicity and does not model moving survivors, native items, or guest
actors. For example, the exact f205 Darkwing Arrow allocator at PRG 67
`$AB03` can add two real `$26` actors using the same six slots. The retained
native captures contain no helper whose entire offscreen window was blocked
by six occupied slots.
[Enemy streams](../../src/level_tiles.s) ·
[Darkwing Arrow allocation](../../src/darkwing_weapons.s)

Native `ProcessEnemyData` normally keeps regular stream actors out of slot 5
and allows the `$2E` exception. Frenzy handling precedes that limit. The
power-up allocator tries all six slots and starts at slot 5. Ordinary actors
use the authored stream cursor and the right edge plus 48 pixels as a parse
window. Groups fill slots 0–4 and advance the stream even if some members
could not be placed. The native exit allocator can reclaim an actor when
full. Mandatory helpers cannot borrow that policy without affecting gameplay.
[Native enemy parser and item allocation](../../src/level_tiles.s) ·
[Native actor processing and bounds](../../src/object.s)

A capacity fix needs a native witness that records the pending helper, camera,
and all six flags, IDs, and positions from first eligibility through entry.
If native culling frees a slot before entry, the smallest candidate is to
let the pending helper claim that already-erased slot before another parser
pass. If all six actors remain valid until entry, an earlier reservation
would need to use a genuine offscreen actor within native culling bounds,
hold its original motion until the existing activation point, and preserve
any enemy, group, or item admission delayed by the reservation. The capacity
fallback remains open.
