# Read-only next-cost analysis

This records the pre33 design analysis. The subsequently authorized scoped
implementation and independent results are in `docs/qa/enemy-offscreen-v33.md`.

This is the historical v32 analysis. The later implementation and its
validation are documented in [the v33 report](crowd-performance-v33.md).

`GetEnemyOffscreenBits` is resident at `$8CB7` (MMC3) / `$8CE1` (MMC5) on immutable32. The native
six-Goomba crowd profile charges about1,950 cycles/update to this routine.
No replacement has been implemented. This note describes a conservative
interior predicate and its exact observable result, suitable for a later
independent differential implementation test if authorized.

For input enemy slot0..5, accept only Y-high1, Y32..223, the unsigned16-bit
distance `enemyWorld - ScreenLeft` in1..255, and the independently computed
distance `ScreenRight - enemyWorld` in24..255. All other cases must tail-call
the original helper. These conditions inspect the actual two camera edges;
they do not assume a255-pixel viewport. Page crossings and16-bit wrap therefore
remain conservative. A24-pixel right margin is sufficient: native horizontal
table values `$0F/$07/$03/$01` disappear in the caller's four right shifts.
Exactly at the left edge must fall back, because the native result is nonzero.

For that interior, the native result is A0, X=ObjectOffset, Y1, C0, V0,
and N/Z from the final X reload. It writes the **single shared**
Enemy_OffscreenBits byte0; R0=0, R4=inputSlot+1, R5=4, R6=32 and R7=255-enemyY.
R1/R2/R3 remain unchanged. A prospective gate can use only R0/R7 scratch until
it commits to the fast path, so a rejected actor still obtains the original
R5/R6 behavior. Restored SP is part of the contract; discarded stack bytes
below SP are not. Decimal mode remains disabled, as on the NES.

Read-only standalone6502 execution of the actual linked32 resident bytes
passes7,776 qualifying cases **per mapper**, including every native slot, differing
ObjectOffset, low-byte camera boundaries,16-bit page wrap, nonstandard camera
widths and vertical interior boundaries. It verifies A/X/Y/C/N/Z/V and every
R0..R7 value against the contract above. Actual MMC3 native cost is299..335
cycles, mean333, excluding the caller JSR; MMC5 is299..334, mean332.06.
Source and ROM hashes are bound in
`build/profiling/enemy-offscreen-v32-analysis.json` and
`build/profiling/enemy-offscreen-v32-mmc5-analysis.json`; the analyzer is
`tools/profiling/analyze_enemy_offscreen.py`. This analytical interpreter is
not a controller replay or NES hardware timing measurement.

A straightforward guard plus exact-result stores is approximately132 cycles,
including RTS, for a successful interior actor: about167..203 cycles saved
per actor. A right-edge reject could add roughly80 cycles, so savings need
actual crowd profiling. An OBJECT-local ordinary-enemy wrapper can replace
that call without growing the crowded resident/FIXED regions; general callers
would retain the original routine. No SRAM or physics/AI/contact changes are
needed. Future validation must include rejected edge/page/high-Y inputs and
all caller-visible flags/scratch, then the unchanged canonical crowd traces
and actual DMA/draw metrics. No runtime optimization is claimed by this note.
