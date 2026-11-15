# Battletoads ae66 remaining idle/input-read overrun

This is source research on exact
`ae669c7ec7536f1c912b3000597be7b3416c20f312638b2589f52fab55f0bc01`.
Root delivered this image in72436. Its native literal-read observation13017
still has23 missed reads across47 complete idle frames, with Main histogram
0:24/2:23; Right32 has16 missed reads and histogram0:16/2:16. Average48Main
in48 physical frames is not constant per-frame input polling. The delivered
347B optimization and every frozen source/composer remain unchanged here.

All work uses the separate `research_battletoads_remaining_idle_1114.py` and
absent output root `build/battletoads-remaining-idle-1114`, bounded600s/max1.
No outputs, ROM files, new opcode/data placement, Mesen or gameplay seeds.
The explicit input loader accepts only exact571→the existing granted ae66
composer, or exactae66→its portable strict inverse. It retains ae66 as the
executed owning image; no frozen input API is relaxed.

## Genuine source attribution

Terminal24494 is current actual Downloads ae66: compiled Rash cold/Start,
4 ordinary neutral warmup updates,8 idle, then8 Right. Every iteration has
one actual GameLoop entry and return. There are no native actors; HP47,
two lives, power0/Star0 are retained. Idle mean Main is27483.75 cycles and
scheduled normal NMI4243.875; Right27738.25/4411.125. MinimumSP192. This is
not a physical cadence prediction. It is a shorter sample than the frozen
48/32 source profile and legitimately has different phase means.

Terminal72188 adds actual JSR/return cost accounting on4 idle/4 Right:
27447.25/4254 and27757.5/4233.75 Main/NMI. AudioUpdate is3057/2994.75
inclusive scheduled NMI cycles. Its presence is not evidence it can be
skipped. Five WfResolve calls total3280 inclusive cycles/Main; their nested
BwBtResolve calls total2790. The wrapper difference is98 cycles/call,
490/Main. Full BtCheck remains1625 cycles across5 calls, with no weakened
header check, memo or validity epoch. Native adder/box public slots12/13
cost894/892 inclusive cycles/Main. Existing private BtSave/Restore cost560
total, across4 calls each.

Inclusive costs overlap; they must not be summed across parent/child calls.
The profiler keeps genuine nonlocal JSR unwinds separate from returned-call
costs. Terminal46427 rejected an overstrict assumption that every JSR returns
to its immediate continuation. Actual Nr A1CC/A554 deliberately removes that
frame. The corrected72188 accounts for these transfers and reaches both
phase boundaries. This harness correction changes no game code.

The first99693 profile used an unverified historicalED5B label for a side
tail. It did not affect total CPU cycles but that label's attributed cost is
discarded.24494/72188 use the actual current fixed side-tail symbol90FF.

## Exact executed geometry route and rejected shortcut

Terminal67831 binds both ordinary raw33 calls:

`NrAdder/NrBox → A1CC → A554 → HuNrRarePrefix → PRG79:B6C0/B6D0 →
HuGenericIndex B840 → HuCommonAfterSelected B85C → HuExtendedBT B8B8 →
PRG87:B044/B047`.

The five-entry Nr low/high/bank planes are for IDs20..26. They do not own
raw33. Inspection96676/79575 rejected incomplete standalone index fixtures;
the actual nonlocal source route explains those failures. The proposed
six-byte plane redirect was withdrawn before any metadata placement. All
those planes remain unchanged.

Terminal32721 binds HuExtendedBT as32B `[B8B8,B8D8)` at file653512, not the
initial incomplete24B estimate. It computes the public B020+3Y target and
clamps invalid Y to unavailable36. Owners27/29/31/33 share this path;28/30
take other branches. A global table/row rewrite would affect other families.

The private actual leaves are RAM3:B2FD `LDY0/SEC/RTS` andB301 `LDY0/RTS`.
Existing immutable equivalent code is PRG96:A7A6 andA7C3, the owned native
tails of JnAdderDispatch/JnBoxDispatch. Their opcode equality alone is not
complete caller, SMC or interrupt qualification.

The fixed side entry is PRG126:90E4. Its current owner41 branch goes via913D
to PRG124:AD9B, not directly to958B. Adding33 to that owner mask would not
prove a native-query shortcut. Its two NOPs alone do not fund a new complete
owner33 guard/native jump while retaining foreign status/transport behavior.

## Unallocated next proposal

The tool's `--proposal` is a detached selector at test address4000, not a
resource address or mounted ROM. It measures a straightforward38B addition
to the current32B HuExtendedBT path. Only selected33 with service12/13 sets
the existing common-restoration target to immutable PRG96:A7A6/A7C3; all
other owners/Y continue through the exact original32 bytes. Invalid-Y clamp
is retained. No new RAM, private cache or cookie changes are needed.

Terminal51869 passes262,136 exact foreign/other-Y terminal cases plus8
intentional native target cases across all256 owners, all256 Y values and
four incoming statuses20/31/69/E5. It compares the detached terminal before
the existing common restore, not a complete gameplay callback. The original
32B span hash is `edbe58bcfddb346392b666ec2e0aeea2279063201201e0d6b4a349d5d59ef7b5`;
the70B detached test code is
`77cf033dabeb43b9c16dbbd9fea966e39ead084e30f161b8e8609436fe91e232`.
Receipt `41323e189d665d4c9a6f518c74d8d5de070db21355b0673043346329929e69ed`.

This intentionally changes ordinary host geometry admission with a corrupt,
absent or retired private BT cache: the native profile defaults remain
available. Public BtRouter/BtCheck APIs and private callbacks remain fully
validated and unchanged. This is not invalid-cache fault parity.

Funding, all exact ingress/source argument domains, actual callback ABI,
SMC consumers, reached ISR and full source/native gameplay remain open.
No allocation or placement is inferred from detached tests or byte-pattern
leads. The next candidate must preserve the entire cache/cookie/public check,
score table and all delivered fixes. Further native testing belongs to root.
