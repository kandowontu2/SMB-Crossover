# Koopa sword admission and Bill Flare terrain

Accepted component45 passes all761 corrected-observer regression slots in one complete run and the linked compatibility review. Its ROM bytes are identical in provisional-a and provisional-b. The roster playthrough, weapon and recording goal remains incomplete.

Ryu's normal sword (shared profile32) previously used the generic enemy proxy, which missed Koopa's source secondary head rectangle. Four mirrored head-only cases per mapper fail on accepted44. The repair admits the source main and facing-dependent secondary rectangles separately, then calls the existing damage path once. It is restricted to green/red Koopa, supported walking/shell states, valid facings and Ryu's normal sword. Other attacks and enemy kinds retain the fallback. The integer-position component does not establish source subpixel/cache timing or walking-to-shell lifecycle parity.

All56 frozen native cases pass. An independent compiled CPU proof covers888,594 cases per mapper,1,777,188 total: the full source rectangle grid, signed world/page/Y-high guard classes and all six slots crossed with all256 incoming status bytes. It executes the actual JSR,267-byte helper and RTS. Carry matches the independent source geometry; X/SP and I/D/B/U are preserved. Ordered scratch and return-address writes are exact, without ignoring stack or RAM ranges. This is isolated CPU evidence, not a traversal or frame-rate claim.

Bill Flare's source filter requests bricks and enemies, excluding other ground. The native collision bridge uses inventory type43/shared profile70. The7-byte terrain filter keeps brick/question dispatch before the filter and continues corner probing after non-brick ground. All52 frozen terrain cases pass:32 ground survivors and20 unchanged controls. Independent review checks718 cached pointers and1,542 event records. The14 isolated ground cases per mapper cover eight active updates; the two real-B cases per mapper cover three active projectile updates within eight fixture updates. Angle, prone anchor, mixed projectile count and visibility remain separate issues.

The frozen historical AV observer preserves all2,400 original result rows byte identically on each mapper. That fixture has no actual Flare/non-brick contacts, so no golden revision is required or made. The separate terrain component supplies that coverage. Observer timing is not claimed to be neutral for performance measurements.

The initial full run passes760/761 slots. Its MMC3 Link sword assertion fails because an unqualified CPU-address hook also observes music bank61 at the relocated GUEST address. Fresh additive read-only diagnostics reproduce44 MMC3 pass,45 MMC3 failure and45 MMC5 pass. Actual bank8 calls occur once at ages0..8; the spurious age9 callback is bank61 with unrelated bytes. The test correction tracks the actual mapper bank and checks the linked entry bytes before observing the sword. Inputs, arena writes, timing/health assertions and all expected values remain unchanged. The original fixture, failure, diagnostics and full raw logs are preserved.

An initial static byte-budget guard also failed: it predicted8,009 GUEST bytes instead of the actual8,017. Independent opcode review accounts for all eight bytes as absolute addressing selected by ca65 for scoped low-page references. The actual267-byte helper is fully guarded in the CPU proof. The original model, guard failure and partial preparation remain intact. GUEST retains175 free bytes; no SRAM, CHR or mapper-header change is introduced.

The prior40 lifecycle and68 admission cases pass unchanged on45. Shadows remain off by default with a gold option row. The44 performance optimization remains included;45's weapon repairs do not by themselves establish a further lag reduction. Dense scenes still flicker and can exceed the CPU budget.

The paired MMC5 crowd check covers3,600 completed updates across Samus, Mega Man and Bass, retaining all204 captured gameplay fields. All60 scenes keep exactly the same physical frames, redraw/DMA counts and measured enemy visibility as44. Mega Man's foreground work adds one cycle per update in this set; Samus and Bass are unchanged. With outlines off, Samus draws60/60 four-Goomba updates and30/60 six-Goomba updates. This confirms retention of44's performance and the remaining dense-scene redraw limitation, rather than a new speedup in45.

Evidence:

- `build/checkpoints/roster-audit-v45-provisional-a/validation/bound-summary.json`
- `build/verification/link-sword-timing45-bank-diagnostic-a/report.json`
- `build/verification/ryu-koopa-primary45-cpu-proof/summary.json`
- `build/verification/koopa-head-v45a-positive-b/report.json`
- `build/verification/bill-flare45a-terrain-actual-positive/source-positive-summary.json`
- `build/verification/bill-flare-v1-observer-candidate45a-first-a/report.json`
- `build/verification/ryu-koopa-primary45-budget-triage/report.json`
- `build/verification/ryu-lifecycle45a-positive-a/report.json`
- `build/verification/ryu-gates45a-positive-a/report.json`
- `build/verification/plain-walking-v44-v45b-crowd-retention-comparison.json`

All14 final-hash routes through2-2, every alternate/special/upgrade, final lossless audiovisual capture and frame review remain required. An ordinary45 Ryu discovery clears1-1 but dies in1-2; an old Bill prefix also fails on44. These partial routes do not certify the current ROM.
