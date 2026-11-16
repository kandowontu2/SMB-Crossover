# GB Pit: native stock pickup checks

The tested Downloads ROM is
`98261effbc214d24a00b2f8bd2950eca8ea3bf3675b331956a2ad42a7ab819e6`.
The independent source Mushroom and Flower passes are recorded in the
helper's GB Pit stock notes; they do not close native Mesen qualification.

## Ground-route control negative, actual Downloads23405

Receipt `1e6ed2d705a6d471c2c2aa8a53622f76415d28c2c5f482348a7c5436c8188f43`
returns false after 1401 balanced Main calls, 1129 balanced PitMovement and
PitFlight calls and 1527 physical frames. Factory39fc5b09 / Lua5230e253
is the frozen source-qualified Mushroom controller. The ROM is unchanged.

The cap exit begins at Main651, world416/34. The attempted left descent
stops at world308/112 with camera307 and relative X1. The source run could
reach305 and fall to176; this native run remains supported by the block
row at320. The terminal condition is still308/112, alive with both lives.
There is no head hit, item birth or pickup. The assertion retained is
`One bounded grounded firstM route`.

This is an input-route negative, not evidence that the item or Pit's
collision code is broken. The successor must leave the row at its actual
right edge, reach genuine ground176, then return beneath it for a fresh
upward jump. Preserve this frozen result and all original item maturity,
physical pickup, score, sixty upgrade ticks and twenty-five returned-worker
requirements. No game state seeds, game patches, helper changes, images or
capture files were used. Native Mushroom/Flower remain open.
