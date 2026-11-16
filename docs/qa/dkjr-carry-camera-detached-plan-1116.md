# Reconcile the source camera before importing an accepted platform position

This is a detached source/funding proposal. No proposed bytes are mounted in
a CPU, combined into a ROM, staged, replayed or installed. Root must review
and lease the exact span before those steps. Current input here is strictbc5;
a later Bowser6a3 successor requires a separate typed binding and preserves
all Bowser bytes. Existingbc5 factories and probes remain frozen.

## First native cause is established

Root31697 actualbc5 private-X diagnostic completed, original ed3e route still
negative. Receipt:
`1779dfc276a184fe5b45f3db2c16133ceeff37a180b42b6d813ab7467f660e64`.
At Main3654/frame8890, the first original X72→71 store is RAM3:BB27,
`STA C203,X`, X16. Emulator post-store PC isBB2A; exact nearby bytes fromBB24
are `ed38c49d03c2cacacacae0`. The CPU targetC213 maps to RAM2/physical16915.

Before this store, worldX928, current camera848, saved camera847, delta1 and
WorldReady215. Native relativeX80 equals worldX−camera80. Original X72 already
expresses the native anchor in the current camera:72+8+848=928. Subtracting1
therefore moves the player a second time. This rules out a stale native
relative-X cache as this first cause.

The next support window[78,95,140,141] misses helper-left96 horizontally;
its actual141 plane remains vertically valid. Original source4 and the fresh
origin124 follow. The later B2C8 `STA75`/observedB2CA exports that already
changed original X as native927. The full earlier calibration is retained in
[private-X plan](dkjr-fourth-private-x-native-plan-1115.md).

Source12082's separate initial139-plane acceptance followed by a140 vertical
miss is not hardware evidence of this horizontal cause. That vertical case
must be rerun after the corrected ordering; it remains a required component
gate and is not waived by this proposal.

## Chosen ordering and lifecycle

The actual native platform position wrapper calls public row37 only after a
real platform position. It saves AXYP, R0..7, five RgTemps and its mapper/SMC
context, calls owner dispatch, then restores them. Current row37 atA06F is
the sole external current private control entry to `DkjrNativeCarryEvent`
atB6A5. Owner dispatch validates the two headers before private execution.

Current accepted ground carry jumps directly to `DkjrNativeImportAnchor`;
safe air/fall landing calls the same import after the original pending
transition and pre-snap fall-distance decision. Import translates the eight
player body cellsC210..C22F to the **current** native anchor. It does not
update saved cameraC435/436. A later successful NativePhase calls
`DkjrNativeShiftCamera`, which still sees the old camera and shifts all64
source cells again. This is the observed ordering defect.

The proposed accepted-import helper first calls the existing camera shift,
requires its Cset result, then tails into the unchanged anchor import:

```asm
CarryGround:
 jsr DkjrNativeShiftCamera
 bcc CarryReject
 jmp DkjrNativeImportAnchor
```

Safe air/fall import calls this same helper. Camera shift transports all live
source cells and updates the cache once. Import then anchors the eight player
cells to current native coordinates; the other56 cells retain their one
camera translation. The next Phase sees zero camera delta. There is no fresh
flag, new RAM, permanent player exclusion or global body/fall change.

The three existing import callers are currentB767 (safe carry), B776 (ground
carry) and BFD2 (initial anchor readiness). Only the first two are rerouted.
Initial readiness still imports and then calls CameraSync atBFD7. Fruit reset
still calls CameraSync atB9F4. Normal Phase's sole shift call remainsB8C3.
Its engine8/timer0/profile1/source1..5 admission remains unchanged.

Reset/fresh/cold rebuild source/profile and camera readiness before ordinary
active platform processing. Engine9/powerup, death/source5, unsupported source
states, invalid platform slots and foreign owners retain their earlier carry
rejections. Fatal original air/fall landings remain before the new helper:
they still execute the delivered pending transition and original fall-distance
comparison, then source5 without importing/snapping the body. The origin,
threshold, jump/fractional state and original landing routine are unchanged.

The detached plan explicitly retains the deliveredB7BB correction
`2010a24ce1a8` (pending transition then original fall-distance). The older
retainedv89 listing calledA8E1 directly; measurement initially rejected those
two stale operand bytes. The proposal reassembles the actual current call,
not that older listing's behavior.

## Exact funding, preimages and anchors

Planner `tools/audit/plan_dkjr_carry_camera_bc5_1116.py`, SHA256:
`2d7020ed4a3b6cf5529b554a03f9c872ea79298ec5a8e015dd3009f7252657c7`.
APIs `descriptor(rawbc5)` and `measured(rawbc5)` return the detached source,
exact old/new bytes, symbols and static census in memory. No composition API
is provided. Owning image:
`bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040`.

| Proposed logical span | Existing physical span | Old SHA256 | New SHA256 |
|---|---|---|---|
| RAM3:B6A5..B77A,214B |CHR881, file1951413..1951626|`8046df1b93344e4f083fb45e4eb7d4a4fa3599d6bb6c76e25a0bd744e8386673`|`867530bdf8aa623f51ebc9ea1f25c182a3ba5545ac7dd02ec3479bb3279ade53`|

Exactly130 bytes differ in this detached block. Funding is3 bytes from a
short guard and3 from the dead CarryReason store. The helper grows5 bytes;
one explicit unreachableEA atB778 balances the unchanged214-byte extent.
It is not a lease on other tail/padding bytes. No new carrier or RAM is used.

The B6F6 long `JNE CarryReject` becomes a short `BNE B6EF`, reusing the
existing unconditional `JMP CarryReject` in the preceding guard. Both reject
paths preserve the tested flags; only branch timing differs. This retains
CarryEventB6A5, the exported rejectB779 (`1860`), and LifeResetB77B. It avoids
moving the reject anchor to fund the short branch. SafeLanding movesB767→B761;
Ground movesB776→B770;13 internal labels move and are listed by the API.

The only current external word that resembles a moved label isB488's bytes
`4cb7`: opcode4C plus operand-lowB7 of the real `JMP B3B7`. It is not a
pointer to oldB74C. The complete actual private call/jump census has only
row37 enteringB6A5 from outside the span. Original donor control tables point
into the original translated program; the public owner computesA000+3×row
and enters row37, rather than manufacturing carry-interior addresses. No
split-immediate bank3 publisher targets this span. Raw B6xx control candidates
in other physical PRG banks are recorded as bank-local candidates, not
misclassified as executable DK ingress merely because their16-bit PCs match.

A future source lease must additionally cover the required existing16-byte
cookie encoding at file534485. Current preimage is
`a7280130b1118ac41a70e81c2eda030f`. No cookie, capsule or ROM has been
re-encoded here. All neighboring lifecycle/code/public/native bytes stay
outside the proposed change.

## CarryReason reader and alias closure

Removing `STA C8F6` leaves that private diagnostic scratch byte at its prior
value; it does not replace it with zero. This is an explicit data-write
difference requiring closure, not a blanket private-RAM exception.

The complete current11264-byte DK packet has exactly one little-endianC8F6
word: the operand of `STA C8F6` atB75B. Retained authenticated source names
CarryReason only at its definition and that store. Full source instruction
metadata has no direct load, compare, arithmetic or RMW reader of it. The
source packet/context is owner-specific; native stock data live below8000,
and owner header checks readCFE0..CFEF rather thanC8F6. Foreign owner code is
not admitted against the active DK packet.

The planner also authenticates all21 indexed instruction preimages whose
unconstrained8-bit index could mathematically reachC8F6. Legal bounds close
each family:

- C8C0/1, C8C8/9 and C8D0/1 tables use X0/2/4/6; maximumC8D7. Current Phase
  additionally admits profile1 only. Table initialization uses the same bound.
- Native lists beginC800/C840/C880, each with at most60 bytes plus sentinel.
  Validation stops byC8BC. Even a conservative shared Y≤188 with the
  unmodified C800..C803 bases stays no higher thanC8BF. Append's actual
  selected low-byte bases and WCount≤60 also stop atC8BC.
- CopyRect reads WL,X only for X0..3, maximumC8E7.
- FullBox uses `(X&1)<<1` as Y, hence WLeft+0/2, maximumC8EA.

Zero native indirect addressing opcodes does **not** imply zero indirect
readers. The translated original uses23 self-modified absolute,Y templates,
all authenticated in current packet initial bytes. Their complete families:

| Original pointer | Templates | Legal target domain |
|---|---:|---|
| 91 |4|Current fruit pointer0400; even full8-bit Y stays throughC4FF; actual count≤4|
| 04 |13|Original OAM pointer high02; even lowFF plus full8-bit Y stays throughC3FE|
| 02 |6|Bounded native lists above, or original fixed rectangle tables/records; no producer points atC8F6|

The 02 list producers choose the validated C800/840/880 pointers. Their
record walker stops at the FF sentinel; original fixed-shape tables resolve
to the retained ROM data, or bounded original RAM records. OAM emit/transform
sets high02 and restores the caller's saved high byte; fruit reset publishes
0400. Thus these legal producers cannot turn the removed scratch write into
an indirect semantic input. Poisoned manual pointers and arbitrary out-of-
contract indices are excluded explicitly; no synthetic all-RAM equivalence
claim is made. Normal list/pointer logic is unchanged by this proposal.

## Semantics and required qualification after a lease

| Context | Proposed behavior |
|---|---|
| ReadyD7, delta0, including camera0 |Existing shift succeeds/syncs; accepted import proceeds|
| ReadyD7, signed delta−8..+8 |All live cells shift once, cache syncs, then accepted player import|
| Low/page wrap, including modular16-bit wrap |Existing subtraction/borrow rules decide the same signed delta|
| ReadyD7, +9/−9 or larger/unrepresentable delta |Shift rejects; helper returnsCclear before import|
| Cache not readyD7 |Shift rejects before translating cells; helper returnsCclear|
| Existing platform/phase/scene rejection |Unchanged rejection before helper|
| Unsafe original pre-snap fall distance |Unchanged source5 decision before helper; no snap or fall-limit bypass|

The two bad-cache/delta rows tighten a standalone carry call that previously
could import without reconciling a valid camera context. This is deliberate
and must be tested rather than hidden by a mask. Shift may update its existing
delta scratch before rejecting a large delta; it does not translate cells or
sync the cache on rejection. Safe-air pending-transition effects already
occur before this helper, exactly where the old carry path evaluated them.

Private ImportAnchor's incidental V/AX values need not remain identical after
different arithmetic inputs. Its actual carry consumers branch on C; safe
landing then runs the unchanged original Land. The native post-position
wrapper restores full incoming AXYP and scratch/mapper context. Qualification
must prove that actual public contract, not silently mask private flags.
The short branch preserves P; the new helper adds a real JSR and up to2 bytes
of live stack depth. Shift uses its existing camera/cell scratch, not R0..7
or native SMC. Cost is not free: accepted carries add reconciliation calls;
the following normal Phase generally sees delta0. Actual per-carry and Main
cost, all rejected paths, IRQ/SMC saved-P and busy-NMI cuts remain to measure.

After root leases the exact source spans, required gates include strict
composition/inverse/current-byte preservation, initial/cold/retire/foreign,
header failures, all ground/air carry and camera edge cases, all actual
public ABI/IRQ boundaries, ordinary fourth support, and the retained source
vertical-loss component. Only afterward can root qualify native crossings
and the25 grounded D65E motor-return endpoint. No complete host-Main claim
or full1-1 success is made here.

## Detached verification

Final descriptor receipt SHA256:
`1ad9e4c5dbf00431f8db4cdbebba78bd2f87e05016e855ebabae6065721e9988`.
The actual214-byte preimage reassembles exactly; new block measures214;
public anchors and the delivered pending-transition stub are retained.
This executes only deterministic in-memory source assembly and static scans.
No proposed instruction executes in a CPU fixture.

Exact absent bounded root `build/dkjr-carry-camera-plan-bc5-1116`, max-files1,
600 seconds, zero outputs. No live source handles, emulator, capture, ROM
copy, candidate or game/control edit. Root alone owns any subsequent source
lease, native queue and nightly delivery.
