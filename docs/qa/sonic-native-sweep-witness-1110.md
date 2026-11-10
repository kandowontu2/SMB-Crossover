# Sonic native sweep witness/preflight, 2026-11-10

PASS in memory only. This component captures the original24-bit position and
checks the exact old-to-new span before a future native16px terrain sweep. It
does not query terrain, perform contacts, replace the source motor, install a
frame hook, allocate host RAM/code, admit raw43 or produce a ROM/Mesen proof.
Frozen core, PointRead and shape sources remain byte-exact.

Source `tools/reference/sonic_sms_native_sweep_witness_1110.py`, SHA256
`03b737cd008af3996860a2a0d34b99db02df1de85f846e003640e201e104f5ce`,
assembles to394 bytes, image SHA256
`7bcc530cef9e8cbe98614654a10d11ac4c6f44799132b7661756a1be483257a2`.
Proposed test code `[B940,BACA)` and25 context bytes `[C0BC,C0D5)` are capacity
and explicit API signatures only, not native allocations/lifetime grants.

## Source ordering and contract

`SonicSweepCapture` copies all six bytes of original X/Y position, including
both fractions. Its required future call site is immediately before unchanged
`PositionStep`, after the genuine motor, pose, animation and hard-cap/top work.
No earlier frame coordinate or reconstructed integer position substitutes for
this witness. Body dimensions must stay unchanged across this seam.

Horizontal/vertical preflight verifies native mode1, a captured marker, actual
source body24x24/32, canonical signed24-bit velocity in the source hard-cap
domain, and exact equality of `old24 + velocity24` with current position.
It then computes old/new leading integer points, inclusive16px start/end cell
origins, direction and cell count. Positive uses width/height as edge; negative
uses edge0, matching the frozen shape adapter. Failures preserve the original
actor/core state and old witness and return C0/nonzero Status/CellCount0.

Statuses8..11 retain mode/velocity/coordinate/body meanings.12 is missing
witness,13 is inconsistent integrated position,14 is a nonrepresentable or
oversized cell span. The marker is not a native frame epoch: a stale zero-speed
witness can coincidentally match. A real typed lifecycle/caller must capture on
every update and prove the epoch; this isolated component grants neither.

The genuine source cap can retain fraction255 at integer speed16, yielding a
17-integer-pixel move. Its inclusive leading-cell path can contain three cells:
the start cell plus two entered cells. The starting cell matters when an old
contact sits on a solid boundary with preserved source fraction. Endpoint-only
or one-intermediate-cell handling is therefore insufficient.

## Actual6502 qualification

The bounded stdout checker executes capture, the frozen original `PositionStep`,
and preflight for262144 cases: both axes/directions and every256-by256 pair of
old position fraction/velocity fraction at the original positive/negative cap.
The phase/page selection covers32px and256px seams and both body heights.
Some arithmetic coordinates are outside the native viewport/queryable interval;
this matrix deliberately establishes no PointRead availability for those cells.

| Axis/direction | One cell | Two cells | Three cells |
|---|---:|---:|---:|
| Horizontal positive |0|63520|2016|
| Horizontal negative |2016|63520|0|
| Vertical positive |0|63520|2016|
| Vertical negative |2016|63520|0|

All4032 three-cell cases agree with independent full-integer arithmetic.
Preflight costs338..3496502 cycles, minimumSP222. All capture/preflight writes
stay in the proposed25-byte context plus the normal return stack; only actual
original PositionStep writes the six original position bytes. No host ZP,
native buffer, retired fixture map, SMC, header or mailbox access is introduced.
Whole-memory canaries survive outside the explicit test source state/code and
normal return stack.

Twenty-six negative cases cover both axes with invalid mode, missing/stale
witness, malformed body, positive/negative oversized or noncanonical velocity,
fraction/integer mismatch, world wrap and leading-edge overflow. An initial
unqualified run caught a16-bit subtraction wrap alias in the new preflight.
The new source now checks subtraction carry as well as high byte; the complete
262144-case matrix and all26 negatives pass after that correction.

The inherited actual state census is634 operand sites/99 distinct bytes,
maximumC0B3, with all ten indexed sites restricted to the already-proved0/3
or0/64 domains. Frozen shape context isC0B4..BB; the new context startsC0BC.
PointRead scratch remainsC100..C115. This establishes source disjointness,
not ownership against a live native caller or an exclusive host RAM lease.

Reproduction (zero files; output root remains absent):

```text
python -B tools/audit/run_bounded_build_v1.py --output build/sonic-sweep-witness-1110 --max-files 1 --timeout 600 -- python -B tools/audit/check_sonic_native_sweep_witness_1110.py --output build/sonic-sweep-witness-1110
```

## Next collision seam and budget

The source-funded core5526 + PointRead365 + shape441 + this witness394 totals
6726 bytes. Current proposed layout includes132 gap bytes and endsBACA,
leaving310 loaded bytes before the existing seven-rowBC00 limit; contiguous
packing would leave442. Neither figure proves the remaining sweep/frame/
constructor/renderer glue fits. The additional992 bytes beforeBFE0 would need
an explicitly source-funded eighth carrier row and revised cold-loader proof.

The next separate selector must read each inclusive cell in travel order via
the qualified PointRead and actual native classifier, stopping at the first
solid boundary. Horizontal retains the source's post-integration Y-midpoint;
vertical uses oldY but recomputes X-midpoint after horizontal clipping. No
diagonal interpolation or swapped contact order is substituted.

Pure boundary algebra would encode earliest boundaryD against final leading
pointP as signed offset `D - (P & FFE0)`, sometimes negative16 or32. This is
**not sufficient for the original contact API**: a negative shape offset jumps
straight to ContactClip and bypasses ContactGround's ground-bit80 write. A
future selector must preserve that branch as well as the clipped coordinate.
One candidate method is to stage only the selected axis's integer probe at the
chosen cell after all required terrain reads succeed, retaining the original
fraction, then invoke unchanged contact with its normal cell-phase0/16 offset
(plus16 for negative travel) and neutral class0. This still needs CPU/corner/
flag qualification and is not implemented by this witness. Unsupported cells
or any required point outside `[actual screen-left column, committed parser end)`
must remain unavailable, never empty traversable floor. World/top/viewport
policy and failure after the genuine motor has integrated need a real frame
transaction; this preflight does not roll back that motor or solve OOB handling.

Original constructor, once-per-game-update epochs, dedicated native service
bridge, full24px rendering/abilities/effects and fourth Mr. Gimmick alternate
remain future work. No public in-game Sonic improvement is claimed here.
