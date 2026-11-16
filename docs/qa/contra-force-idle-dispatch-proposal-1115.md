# Contra Force idle dispatch proposals — detached only

Owning input is exact delivered bc5
`bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040`.
No proposal below has a source-overlay, ROM, native or delivery lease. No new
game opcode is mounted, and no whole ROM/capture/output file is produced.
Root's actual Downloads77416 baseline, Lua8752, receipt
`c95fafe9a703dff44b018a845639d508c99eda40a2296b6f1b79b5070f3aaac7`,
confirms severe lag: idle48 Main takes96 physical frames, with71/95 complete
frames missing literal reads; Right16 takes32 frames,23/31 missing. All65
movement/input/body calls return, with naturally zero actors/shots. This is
the hardware baseline, not an optimization result.

## Frozen first proposal and footprint

`plan_contra_force_idle_dispatch_1115.py` SHA
`06a4efc814a0b81957f03026fe892b0e13a90fd4c9f9ca04264c08eae6c9f9b4`
provides `descriptor(rawbc5)`, `router(rawbc5)` and `late(rawbc5)`. It reuses
only the exact retained inputs bound by `profile_contra_force_current_costs_1115`
and the current compiler labels. The actual private router is291B; the124B
object discussed earlier is the separate RAM1 palette packet worker.

| Detached envelope | File | Bytes | Old SHA256 | New SHA256 |
| --- | ---: | ---: | --- | --- |
| RAM2:BE6E..BF90 router | 2022014 | 291 | `1e716c053fc9531abca8cbc4934ec610f8fb813ee19e917ed4278b6bb40bf07b` | `6c346a9d6331ed8d28af6c740c15cc247dd7b8760a67a4f67b0607a6e51ea906` |
| RAM3:BE53..BEFE P1 late | 2030179 | 172 | `a247fb3fd68b6b90218a96f4ec2183ddd361e9cdcebdb1ad7c4375f8745a01dc` | `2c6f0cec5bf1e13c9c2df96302a06d79b440446a3773bf81092f291ec9407bf4` |

Descriptor67671 passed, receipt
`2761474ee9c6328831727aa929f2ece8ba9022d7e35ff5ca9f69c57d07f2e8b9`.
Its exact old/new hex, labels, changed counts145/139 and digest requirements
are returned by the API. It does not produce an owning candidate image.

Changing these payload bytes requires normal integrity digest updates, not a
weaker guard:12 digest bytes at573377 and642970. The full16-byte views at
573373/642966 have old
`a71f00053a7d2d9a77d5accd30e79766`, proposed
`a71f00053a40fd2178c5dafce54ca4d0`. Prefix/class/version are unchanged and
still validated. The detached24KB payload SHA becomes
`3a40fd2178c5dafce54ca4d0e8b64b127a635746e73803d4ad7e13b6f1cf4245`.
The smallest corresponding four-span footprint is487 owned bytes and306
actual changes; no art, new RAM or claimed unowned padding is involved.

### Constant-time router arithmetic

Four RP2A03 `SEC; ADC SFC-low; ROR A; LSR A` stages from A0 calculate exact
floor(offset/3) for **all256 byte offsets**. Quotients36+ reject as before;
nonmultiple offsets are not silently excluded. The extra13 arithmetic bytes
are funded by sharing the existing duplicate success/failure stack rotation.
The full private15 fixed-cookie comparisons plus dynamic class comparison,
and all immutable outer checks, remain. All72 Lo/Hi table bytes stay at
BF49/BF6D. New code212B leaves seven bytes inside the proposed owned envelope;
this is not a claim to current free storage elsewhere.

`check_contra_force_idle_dispatch_1115.py` SHA
`ecd8663fdcc65ac9b534a090599dfb92a1ed3712635e130ac87ec99d7264768d`.
Router64654 passed36,067 detached cases, receipt
`8b47cb422a109bdec66ad558011675b2c8c247e68bc6f18df5d07ef50927eeda`:
32,768 all-offset/all128 hardware-status cases,1,536 header faults,1,536
FmGroups cases,216 register/stack/bank corners, and11 measured service offsets.
The worker is an explicit return fixture; actual CfCallA/FarCall is not run.
All final AXYP/SP, the **entire page1**, every written scratch/protocol byte
and full-header read signatures equal. Minimum SP123 in a synthetic corner.

Actual14-callback normal-Main weights save **1,332 cycles**. Offsets0/3/6
regress40/29/18 cycles; offset42 gains114 four times,87 gains279 and102 gains334.
Corrupt-cookie paths regress five cycles. No universal faster-path claim is
made. This alone cannot establish a physical cadence improvement.

The new arithmetic rereads shared SFC-low four times instead of once. Audit
14870 on **unmodified current code**, receipt
`8a909efaa27765afab46c0a4aadbcc7d5b68af2efe7abd5e03675842ef97fadd`,
captures actual CF offsets0/87/102 at old RAM2:BEB8, source SP211/228/224.
Each legal actual IRQ120 and busy NMI3257 preserves AXYP/SP, mappings/shadows,
all33 SMC bytes, live caller stack and all CF RAM1/2/3. Minimum interrupt SP190.
No regular NMI is invented inside busy Main. This closes the existing source
value's ISR stability; reached cuts on **new** opcodes remain post-lease work.

### P1 paint and complete entry

The public BE53 entry remains fixed. Four bytes are funded by keeping the
already-saved original P/A stack bytes instead of popping and immediately
pushing them again before saving X/Y. The private leaf moves BE80→BE7C and
its one internal JSR is rebound. This funds a48B paint loop replacing44B.
All hidden nonzero tag bits still clear, visible shot/native arbitration and
alternation remain, and the ordinary packet gate still runs. Untagged rows
skip only writes of identical RAM values. Final A and carry are restored to
the original leaf values before the unchanged gate.

Paint81704 passed65,536 all256-attribute × two legal Choice ×128-status cases,
receipt`c7ead2d338a05bb09f3f0b912fc4e77b3c117ef5731636311aaafe8efa14291c`.
Exact final AXYP/SP/data is compared. The isolated row fixture starts X252;
it is a component proof, not a naturally entered full-frame claim.

Full-entry checker `check_contra_force_p1_entry_1115.py` SHA
`0d24a222d0b2189a74866393572c302ec9a4d7ab531f5ec75d7f1f3918adbee5`
passed88006,6,144 cases, receipt
`b51c0301bc273fb0d6c0fbd59acd93708263358f23646f7b8506f186aff597df`.
All128 hardware statuses, six token values and eight visible/hidden/tagged
OAM scenes compare public AXYP/SP and all written private/OAM/attribute data.
Actual packet/CfCallA are represented by an explicit gate-RTS fixture; the
unchanged gate's consumed PHP byte, AXY and SP are exact. Legal SFC input P
already normalizes B, so its gate tuple is bit-exact. Synthetic B0 input can
differ only in the CPU B copy, normalized identically by the gate's first PHP;
all live C/V/I/D/N/Z and final public flags remain exact.

The sole discarded stack-data difference is the low leaf-JSR return byte at
01DB for **unit entry SP224**, exactly four lower after relocation. The word
has already been consumed by RTS before public return. Every other written
stack byte and the live caller bytes are compared; this is not a blanket
page1 mask. Minimum SP218. Early token0 paths have no difference.

The actual empty opening's64 tag-zero rows save **718 cycles** including the
entry change. Tradeoff: synthetic fully tagged scenes regress562–882 cycles;
mixed tagged fixtures also regress. Incoming Choice is overwritten to0/1 by
the full leaf before paint. The combined empty-Main estimate is2,050 cycles,
not a current hardware cadence gain.

Audit14870 SHA `40e2c89334f9403f82c9556f24ef6224cc6e17edcc46c95d9c6197beb7bafcd2`
binds the retained actual assembly sources and compiled DBG references. All
moved router internals refer only within a2-router; CfP1Late has only its own
export and one actual JSR in p1-runtime. All36 public JMP veneers and36
authoritative target words remain unchanged, including service6→BE53. The
sole BE80 word in all24KB is that own JSR. This is symbolic plus authoritative
vector closure, not a blanket global literal/indirect-code claim.

Two P1 checker harness errors are retained: the first invocation stopped at a
Python `else16` syntax typo;70106 stopped at a closure accumulator assignment.
Neither changes a proposed byte or establishes a game failure.88006 corrects
only the harness and completes the proof above.

## Separate shared-layer successor — pending

Root requested prioritizing the actual Router87→WfForeign96→Bw/Cf67→CfCheck69
layer. `plan_contra_force_shared_tail_1115.py` is a separately named proposal;
the frozen06a4 arrays above remain untouched. It retains the175B helper
envelope and all108 target bytes at B7DC, with67B of code and no Router edit.
Foreign/BT pointer setup shares the existing raw33 carry selector. Foreign
drops only its mandatory existing SFC return word and jumps to actual0163,
reusing the outer farcall frame instead of creating a nested one.

Descriptor71476 passed, receipt
`ed17a8b65171c62f6f4efca25d40b127add763098320a27946a9dd43f85bf357`.
Old175 SHA`1db29ae7f1b6ecc475f5282287b4e0aba1865fe4892bf8e54cd2a63abfbb8119`,
new SHA`1e2a39fb24a91467d578292b0a759402bd9319c2292157d552ae0f386f1d02a3`,
62 changed bytes, file792489..792663/PRG96:B799..B847. API returns exact hex.
The original33-byte SFC producer is actual file8208, SHA
`c22c9c8d9efbb1836af4549d0601292c8150da3b3609c83d8192e2b0bb51fd4c`.

This design needs explicit internal-contract review: Foreign X becomes B2;
Bw overwrites it on valid paths and the Router must discard it on faults.
NextBank_SMC0162 can differ before the next header/caller overwrite. The
helper must only have genuine SFC ingress (return word016D and an outer old
bank byte); arbitrary direct JSR is not admitted. These are **unqualified**
until actual caller/ingress/SMC liveness proof, not hidden masks. All real
services/checks/retirement behavior must remain. Savings may be only hundreds
per Main; no timing benefit is asserted from the descriptor.

Detached caller smoke13097 stopped on an immutable-write assertion in the
**old generation before helper entry**. Diagnostic17520 identified the
fixture's synthetic page1 fill overwriting the actual015A..017A SFC producer.
Restoring that exact33-byte producer after dead-stack initialization corrected
the harness; no proposal byte changed. Corrected66127 passed576 smoke cases,
receipt`a4f76953bfba30e729225d4180c4e910920cff11439b5f6ea4afca8a14a7bfa7`.

Full31745 passed23,616 detached caller cases, receipt
`4eb9b5c20f679d52128f84d4d920471d8e2161a41c6817174a0419a1c5d503bd`:
18,432 all36 commands × four admitted cohorts ×128 hardware statuses, plus
cold modes, group roles and16-byte header faults. All final caller AXYP/SP,
callback input/registers/live stack, raw maps, all33 SMC bytes, nonstack writes
and complete physical RAM compare exactly. The actual unchanged SFC33, Bw213,
CF outer/private header and BT full-header instructions run. Unchanged other
handlers and Bowser header are explicit return fixtures, so this is not a
gameplay/whole-handler proof. New arrays execute only at detached unit PCs
5020/4099; no new opcode is placed at a game PC and no NesBus image is mounted.

The two helper-return bytes are consumed by the tail. Other discarded getter
frames can leave differences at unit addresses01C6..01D4; these are all below
the **exactly compared** matched callback or returned-native-caller live stack.
Every final nonstack/protocol byte and every physical RAM bank is compared.
There is no blanket private-RAM mask. Minimum SP197. An ordinary unmodified
Main separately authenticates every actual helper's return word016D and outer
old-bankD7 at source SP201..227. Arbitrary direct-JSR ingress remains a
**required contract/consumer review**, not a silently supported API.

Per callback this saves23 cycles on CF/Bowser, costs two on valid BT, and costs
zero on WWF or bypassed BT cold/NoOp. BT fault paths save21. **All14** actual CF
services traverse this helper (42 four times); the earlier residual-only
estimate of12 omitted two calls inside already-named scopes. Therefore the
proper weighted gain is **322 cycles/Main**, not276 or thousands.
Unchanged-one-Main48307/frequency receipt
`398d68b8c3a9dc3913989bb5349f17c63294380f49d4a517bf1dfe45fa8d67dc`
binds exact offsets and real SFC frames. No physical gain follows from this.

| Shared proposal source | SHA256 |
| --- | --- |
| plan_contra_force_shared_tail_1115.py | `729b4565ed4e852ebf14e63e81c06d9ba3ca341b5863d276b2d16d0668193bcd` |
| check_contra_force_shared_tail_1115.py | `1bd54a1662e9bc10c080766178899c7bb769d7f33ea9a0d850816631197c597c` |
| inspect_contra_force_shared_frequency_1115.py | `224ac95540d0ce04cd3d083c7eb1702b7cc2580957f91fabc86a7aaee4e4273d` |

Remaining before any lease: complete actual helper ingress/NextBank reader
transfer, precise new-frame ISR obligations, and root review of the explicit
internal contract. Source allocation/native/delivery remain false. Root's
larger work-marker lead is recorded separately in
`contra-force-p1-work-marker-design-1115.md`; it has no arrays or implementation.

The retained current runtime.cfg, SHA
`87cde222a35c4dede2a11d0202b16c3b87be9c1acd327ac79d4f4343616bc55d`,
explicitly assigns C2TAIL/A2ALIAS DE00/BE00 size1E0 solely to CF_A2_ROUTER.
That is a resource lead for a separately reviewed partial loop unroll,
**not** permission to use79 trailing FF bytes or change the frozen291B plan.
Every fixed-cookie comparison and the dynamic class check must remain.

All producers use absent `build/contra-force-idle-dispatch-1115`, max1 file,
600s under the shared bounded runner, `python -B`, with zero output files.
Only exact retained inputs are read. No historical graph is restored. Root
owns all allocation, source mount approval, native queue and delivery.
