# Detached Battletoads resolver funding, November 15

This is source research only. No new ROM image or physical PRG read overlay has
been created, staged, installed, or run in Mesen. Official Downloads remains the
separate Prince `40a11ffb...` image. The explicit new input boundary recovers
exact `7a80f0f3...` through the frozen Prince inverse and derives the existing
private `a90cf06b...` reference through its unchanged strict composer. These
tests execute that versioned reference, not a combined current40a image.

The native a90 observer has already established that its previous optimization
executes: guards fall from 994/992 cycles to 21/24, approximately 1,965 cycles are
saved per Main, and full Rash/Zitz routes pass. The isolated controller-read
cadence remains negative. Root's complete native aggregates are in
`battletoads-native-profile-root-1115.md`; no fresh native result is inferred
from the following CPU-model costs.

The new read-only cost attribution (`research_battletoads_remaining_costs_1115.py`,
terminal source session 12490, receipt
`752f0453fcb1e1ec628467ffb0324db72dbd644b0eb460ac803f7ee1943d8464`)
observed three ordinary validated services per Main: offsets 0, 6, and 102
(slots 0 Movement, 2 Draw, and 34 Graphics). Per Main, WfResolve costs 1,950
inclusive cycles, BwBtResolve 1,656, CfOrBtCheck 1,263, and the three full
BtCheck calls 975. The wrapper layers therefore account for 975 cycles above
the full checks. The four normal source idle Main average 25,481.25 cycles;
Right averages 25,791.5. Scheduled NMI costs 4,254/4,233.75, including unchanged
AudioUpdate at 3,057/2,994.75. Source normal Main is not the native mix of
normal and cheaper catch-up iterations.

## Exact detached fit

`plan_battletoads_flat_resolver_1115.py` owns only independent CPU arrays at
virtual addresses 4020 and 5000 for testing. Its proposed physical envelopes
are not mounted:

| Physical envelope | Bytes | Old SHA-256 | Proposed SHA-256 |
| --- | ---: | --- | --- |
| PRG87 B020..B100, file 716848..717072 | 224 | `2b8557c5951bb6d53642b34f6a79678ef57dbbbccaa4698d56029cff0d3b113d` | `f1a73fbcf21d20b8297d087e17a33aa40e2ead56039d57193b408258f4c946c7` |
| PRG96 B799..B848, file 792489..792664 | 175 | `460c175d316220c95edefb02f7a5ddd7a80e46577e05d191b703a8dfa2ca6634` | `62e67fe24085db0de12c17e2117bc69ee4d302d4ee59cec3f133f06830826faa` |

The Router uses 223 code bytes and one NOP inside its existing 224-byte owner.
The 175-byte query envelope comprises a 7-byte dispatcher, 15-byte foreign
thunk, 43-byte owner29 sparse query, 26-byte raw33 query, and 84 table bytes.
Exactly 264 physical bytes would differ inside these 399 bytes. No new RAM,
CHR, cookie, validator, audio, timer, input, or drawing code is proposed.

The legal Router owner gate admits only raw27/29/31/33. It passes
Y=(SelectedCharacter-27)/2, giving 0/1/2/3, and publishes SafeA=3*slot before
reusing X. Only raw33 changes the **X register value to hexadecimal AD**,
the high byte of the existing BtCheck address ADC0. This is not an address
or scratch-RAM allocation. Owner29 keeps X=3*slot. The saved caller A/X/Y/P
frame and original tail transport remain in place.

Raw33 calls the original full BtCheck through its real FarCall. On rejection
it tail-delegates to the original Bw resolver, preserving original cold and
retired admission. Raw27/31 also use the unchanged Bw resolver. Owner29 keeps
all 21 real target descriptors, including the existing death worker, and
replaces the 15 NoOp descriptors with query rejection. The original Visible
SEC/RTS leaf has an explicit proposed alias. Public equivalence is tested
through the outer FarCall, rather than inferred from the private query carry.

## Terminal detached public transport

Bounded source session **52636 PASS**, 13,284 cases, minimum SP205, zero files.
Receipt:
`60dcc1f8f2201888275f0e5af6012dd1e6800f6a2fec32c796dd52701c055cf8`.

The actual old Router bytes match their independent frozen assembler. Cases
cover all 256 SelectedCharacter values and all 36 services; the four legal
owners also cover eight group classes and three additional status/register
corners. Raw33 covers retirement plus each of the 16 fingerprint-byte
corruptions. Selector/group/cookie/register perturbations are explicit
component fixtures. Only the initial source arena is a genuine compiled Rash
cold constructor; these permutations are not natural gameplay routes.

Every NoOp and Visible case executes its original leaf and full public return.
Other private services stop at the original Router tail transport before
executing gameplay or constructors. A/X/Y/P/SP, complete live application RAM,
physical RAM, mapper state, VRAM, and PPUCTRL match. The only published SMC
differences are 016C/016D in 520 cases. SafeA, returned A, and every other SMC
byte match. This is a narrow publication difference, not a blanket RAM mask.

Valid raw33 ordinary services save **230 cycles per call**, or 690 across the
three observed normal services, with exactly one full BtCheck per service on
both sides. The detached arrays have different branch/table page positions;
actual proposed-address cycle qualification remains required before an image
claim. No physical cadence or FPS improvement is claimed.

Tradeoffs are explicit. Non-cohort rejection has exact cycle parity. Raw27/31
save 22 cycles per query. Owner29 sparse lookup can add up to 220 cycles per
query; some high NoOps save 86 cycles. Corrupt or retired raw33 now performs
two full checks before the unchanged fallback result, adding 144..369 cycles
depending on the failed fingerprint byte. Cold/NoOp bypasses add 2..7 cycles.
These costs must be reviewed rather than described as universal savings.

Two earlier harness negatives are retained: session71600 used the proposed
B799 helper address while reconstructing the old B79D Router binding;
session38811 compared dead stack residue from a previous, deeper case as live
RAM. Both were fixture errors, corrected before terminal52636. Neither was
classified as a game defect.

## Rejected sparse lookup: all six reached frequencies

Session **17606 PASS** measured original, unmodified a90 source execution;
receipt `5c8989b8a88d84cfe12dc11d39b54b31ee1a56dc4cb7c5e0ef541173e0aa8f2d`.
Each character was selected by its actual compiled Select/Start path, with
roles 0..5 verified independently, followed by four warm Main, eight idle,
and eight Right Main. Every sample had zero active native enemies and no
gameplay seeds. All measured frames had exactly one GameLoop entry/return.

All six have the same 13 queries per Main: services 29, 0, 13, 12, 10, 34,
9, 1, and 2 once each, and service14 four times. After correcting the
detached arrays to preserve actual proposed low-byte addresses and page
crossings, the sparse plan adds **1,618 cycles/Main** to every wrestler,
both idle and Right. Per-query additions are 154 for 29/12/13, 13 for 0,
174 for 10, 160 for 14, -86 for 34, 185 for 9, 229 for 1, and 1 for 2.
The four side queries alone add 640 cycles. This rejects the sparse plan as
a usable shared optimization; its BT savings do not justify that regression.

`plan_battletoads_dense_resolver_1115.py` is a separate detached successor.
It keeps the dense 108-byte table and replaces the dispatcher with four
entry-low bytes indexed by the proven cohort Y. Router's LDA immediate
becomes LDA absolute,Y, using its existing one-byte NOP. The helper has a
15-byte foreign thunk, 22-byte dense query, 25-byte raw33 full-check path,
one NOP, four entry lows, and the original 108-byte table: exactly175 bytes.
Its query reuses the unchanged group-only suffix B639 of WfColdIdentity.
NoOp/Visible aliases use the existing unchanged B2CD/B2CB CLC/SEC leaves.
The source is not mounted. Its terminal detached results follow; ingress,
SMC reader classification, and reached ISR remain separate gates.

## Dense successor terminal components

Session **90945 PASS**, 13,284 public transport cases, minimum SP205,
receipt `444de8dd7ae977a66f9edd6a5dab22b2b52d9c3ff3b0d5f97494890da069137e`.
The same complete return/application-memory checks pass, with only 016C/016D
differences in the same 520 cases. The dense successor proposes 181 changed
bytes inside the same 399-byte envelopes. Its new Router SHA is
`da9b79944fb1cd43e1eb73a185c052d12bbd14a4ce2f2d97f06bed3d18389be1`;
the helper SHA is
`b4b2a93877921df0c916c2c571b1a6d5a328aeed5f8a2cf42d9b4c4e30d791ab`.
All 21 real descriptors except the equivalent Visible leaf stay byte exact.
The table remains at B7DC; the four new entry-low bytes are B7D8..B7DC.

The unchanged B639 suffix is exactly `ade85f2907c906b00238601860`.
Session69733 retained an incorrect B0 03 preimage assertion and stopped
before executing the new arrays. The actual source branch is B0 02; the
correction is authenticated by both the current ROM and retained listing.

Session **30126 PASS**, receipt
`9c7ed10a897a93578ed6af532847f6df539ca42dea584fa16cda63769fd98809`,
exhausts 65,536 direct suffix cases: all256 group bytes, all128 valid status
values, and two X/Y corners. X/Y/SP and D/I/V are exact; A is group&7,
C/N are set for roles0..5, Z is set only for6, and invalid6/7 return C0.
All high group bits are ignored by the actual AND7. Another4,096 full public
NoOp/Visible cases cover all128 valid status values and two A/X/Y corners.
These are component fixtures, not natural gameplay permutations.

The same terminal job repeats actual compiled Select/Start for Hogan,
DiBiase, Bigelow, Honky, Savage, and Andre, four warm Main then eight idle
and eight Right Main per character. All six retain the measured13 queries
per Main and zero enemies. Every valid query now saves6 cycles, so the
actual-frequency weighted gain is **78 cycles/Main for every wrestler** in
both phases. No existing wrestler lag regression is hidden.

Valid raw33 ordinary services save233 cycles each while retaining one full
BtCheck per service. Raw27/31 save28 per query, non-cohort rejection is exact,
and invalid role6/7 owner29 rejection adds1 cycle. Raw33 fixed cold/no-op
bypasses add3..8 cycles. Raw33 corrupt/retired service rejection still takes
the original fallback, with two full checks and the explicit extra latency.
Whole-Main and native cadence gains remain unqualified.

## Consumers, publication, and reached vectors

Session **53438 PASS**, receipt
`38a7c8c2efade4d425d88d31941ae3522ddf5b79e052eaf9ad2627fee6abd1ef`.
The current structured domains cover Hu144, Wf36, Bw8, and thirteen Nr split
tables. The bank-E0 farcall into the changed query domain is solely Router's
old B79D publication. Authenticated common code rows, decoded Prince streams,
and the retained executable containers introduce no additional standard
bank-E0 query entry. The retained WWF runtime source/listing classifies old
NoOp/Visible references as exports, definitions, or descriptor rows, and the
three old table readers belong to the replaced query. The preceding
WfOneLifeStatus ends in RTS, so there is no fallthrough into the old leaves.

Three near-JMP aliases numerically name B799/B79B/B79D in PRG78/79/95.
Their actual opcodes were executed separately: each remains in its own mapped
page and does not enter PRG96. Session1035 initially stopped at these leads
for classification; they were not ignored as padding or treated as Wf calls.
There are no fixed-bank direct control leads into the old Wf entries.

Read-only observation of the six actual family cold/menu/idle/Right paths
records1,500 NoOp and132 Visible entries. Neither016C nor016D is read before
its next write. The six pairs of first writers are canonical target
publications (raw tags/PCs):129:A315/A31A,131:B42B/B430,
252:AD7A/AD7F,254:8315/831A,255:ED6A/ED6F,255:F118/F11D.
This closes the observed publication difference without a private-RAM or
invalid-state mask. The already qualified public FarCall protocol publishes
its typed target before invoking it; unchanged opaque snapshots preserve the
transport value rather than making the old leaf address a result contract.

Corrected terminal ISR session **24581 PASS**, receipt
`41907750166130224f5f0ddbe9410632a3f1b83d1e659cb9fa08be0c975c62fd`.
It retains28 actual compiled Rash/Hogan cold and Main caller frames, plus
three separately labeled foreign/corrupt-header query components. The deepest
representative of each reached PC/status pair yields277 cuts. Each passes
the unchanged actual IRQ handler and busy NMI handler:277+277 entries,
minimum SP159. AXYP/SP, live stack, every SMC byte, mapper state, and public
continuation endpoints restore exactly. The native handlers neither execute
nor read the detached arrays. No regular NMI arm is forced, and this is not
a nested-interrupt scheduling claim. Audio still executes in the actual NMI.
Session34790 had the same terminal vector results but mislabeled all31 frames
as actual callers;24581 corrects the receipt metadata to28 actual+3 components.

## Frozen source packet and entrypoints

| Source | SHA-256 |
| --- | --- |
| `current_battletoads_resolver_research_1115.py` | `746a65785f8fde172af70252ae0cc9eedb4e59324cfc9c306a2a5114b274580f` |
| `plan_battletoads_flat_resolver_1115.py` (rejected sparse plan and shared fixtures) | `d27a42a2a61401c738f8ec97101cdd411d3ac34627a65dc9d6604aba40cb542e` |
| `plan_battletoads_dense_resolver_1115.py` | `04d2397ee37917ee62ecf4f8ac8b8181ddcb88bb5ca26196ec5353d45f86b7c0` |
| `audit_battletoads_dense_consumers_1115.py` | `2c19d90a9f09cc273c84c4d123554969b6102ba3d4a8bde70055aabdeda94995` |
| `check_battletoads_dense_isr_1115.py` | `dc1397c685e88f7e691831c21939b9d1cd4b36997d828e30e5e34ab996b25f21` |
| `research_battletoads_remaining_costs_1115.py` (versioned prior cost inputs) | `1687f4754529c625f730f95b7235cb41410b9de2fc9efd96e8e7cf20807aff46` |

`Dense.shapes(parent7a80, referencea90)` returns both full old/new arrays,
hashes, typed half-open file spans, counts and labels. `Dense.router()` and
`Dense.helper(referencea90)` construct the two arrays independently. The dense
plan's physical spans are716848..717072 (224 bytes) and792489..792664 (175).
Their old hashes remain2b8557c5... and460c175d...; new hashes are recorded above.
They are disjoint from every one of a90's nine existing funded envelopes.

Every CLI below runs only through the bounded wrapper, with exact output
root `build/battletoads-remaining-idle-1114`, max-files1, timeout600, and zero
generated files:

```
python -B tools/audit/run_bounded_build_v1.py --output build/battletoads-remaining-idle-1114 --max-files 1 --timeout 600 -- python -B tools/audit/plan_battletoads_dense_resolver_1115.py public
python -B tools/audit/run_bounded_build_v1.py --output build/battletoads-remaining-idle-1114 --max-files 1 --timeout 600 -- python -B tools/audit/plan_battletoads_dense_resolver_1115.py components
python -B tools/audit/run_bounded_build_v1.py --output build/battletoads-remaining-idle-1114 --max-files 1 --timeout 600 -- python -B tools/audit/audit_battletoads_dense_consumers_1115.py all
python -B tools/audit/run_bounded_build_v1.py --output build/battletoads-remaining-idle-1114 --max-files 1 --timeout 600 -- python -B tools/audit/check_battletoads_dense_isr_1115.py
```

The current40a loader deliberately uses its portable inverse only to recover
the strict versioned7a80/a90 reference. A future whole image must retain the
actual official40a bytes and join only a90's nine qualified spans plus these
two disjoint query spans. Its inverse must restore exact40a, including Prince;
none of the frozen7a80/a90 factory or composer APIs may be widened.

No source-overlay or ROM composition lease exists for this proposal yet.
Actual mounted cold/lifecycle, both full BT routes, and a mounted source
profile remain required after root grants the exact source lease. Physical
native cadence and delivery remain root-only, separately unqualified work.
All frozen C/F/benchmark/profiler files and prior leases are unchanged.
