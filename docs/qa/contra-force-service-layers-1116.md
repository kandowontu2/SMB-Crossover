# CF service and transport costs on versioned ffbb

Read-only source attribution, not a game change, candidate composition, native
run or lag acceptance. Current input91dc
`91dc4ac58ae749bc81f1ef91953c7c3e5aba73dd07e4b6ea2cd3059d1cdb41cc`
is explicitly inverted by frozen `compose_battletoads_mature8_1116.py`
SHA256`6db3aa513aac81d022efdc881b01bdcb93a639ccd4f99e8671fed3f8986bb27c`
to exact6a3 for this **versioned6a3→RAMffbb** measurement. It is not a
current91dc+CF composition or execution claim. Frozen6a3/ffbb APIs stay strict.

Tool `profile_contra_force_service_layers_1116.py` SHA256
`67d7fe0eb1098fa7cd822103a8385f702413810e2fd2690090d926b7ce637153`.
Bounded source67910 terminal0/PASS, receipt
`b6b250321cc34cdca4ba583aa4321cb77293d326ad75b6740e4c920c791d0811`.
All scopes match real mapped PC, return PC and SP. Nested ISR cycles are
excluded from Main. Exclusive scopes partition all observed Main cycles
exactly. Actors, shots, health, position, terrain and abilities are unseeded;
real compiled BURNS menu/start and warm opening provide the state.
All three used output roots remained absent, zero generated files.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/contra-force-service-layers-1116 --max-files 1 --timeout 600 -- python -B tools/audit/profile_contra_force_service_layers_1116.py
```

## Budget and overlap

| Scope, cycles per actual Main | Idle | Right |
|---|---:|---:|
| Normal Main,4 measured each |52237.75|52581.25|
| Union of14 R87 service queries |30232|30499.5|
| Real private leaf bodies, inclusive union |7355|7622.5|
| Within-query routing/validation/transport |22877|22877|
| Main outside those queries |22005.75|22081.75|
| All actual lowRAM instructions inside SFC scopes |8819|8819|
| Busy-NMI component,8 actual Main each |46287.75|46453.75|
| Busy component query union,104 total/13 per Main |26774.5|26937.125|
| Busy component private leaf-body union |5446|5608.625|
| Busy component all lowRAM SFC instructions |7892.5|7892.5|

The query and leaf rows are nested: do not add them. The complete elimination
of all22877 normal query overhead would still leave29360.75 idle/29704.25
Right before NMI. This is a theoretical ceiling, not a feasible proposal or
physical cadence prediction. Repeated headers alone cannot close that budget.

The busy component injects one real busy NMI at actual CfHostMovement per
scheduler pass. Four passes yield8 actual Main, not four; draw and late-paint
services occur only four times, all other active services eight times except
side32. This is a source ISR/catch-up component, not hardware FPS. Actual
NMI totals are17428/17347 normal idle/Right and31533 each busy phase;
AudioUpdate is unchanged and is not proposed for removal.

## Nonoverlapping exclusive layers

The following idle totals partition Main. The SFC-scope row includes
unlabelled callee bodies: it is **not** synonymous with transport. The
8819/7892.5 lowRAM rows above are measured instruction addresses inside those
scopes and are a subset, not another additive row.

| Innermost scope | Normal idle/Main | Busy component idle/Main |
|---|---:|---:|
|SFC|18611.75|16085.625|
|generic_resolver|1512|1404|
|generic_router|1512|1404|
|generic_wrapper|3960|3755|
|leaf|2278|1729|
|main|2388|2415.625|
|outer_header|5586|5187|
|private_internal|4648|3394.5|
|private_router|9759|9147.5|
|private_transport|1941|1726.5|
|query|42|39|

## All36 current handler slots

Normal idle4 Main service counts below are expressed per Main; Right has the
same counts. All unused slots are zero observed frequency, not an authorization
to skip their service or infer NoOp semantics. Leaf-inclusive and query-inclusive
columns overlap. Internal Graphics/Visible calls inside Draw remain in the
leaf-body scope rather than being miscounted as separate public queries.

| Slot | Actual RAM3 handler | Calls/Main | Leaf cycles/call | R87 query cycles/call |
|---|---|---:|---:|---:|
|0|CfHostMovement $A91B|1|2313|3811|
|1|CfHostGraphics $B361|1|123|1632|
|2|CfHostDraw $B371|1|3148|4668|
|3|CfHostGraphics $B361|0|0|0|
|4|CfHostShots $B694|0|0|0|
|5|CfHostInjury $AB71|0|0|0|
|6|CfP1LateEntry $BE53|1|670|2247|
|7|CfHostUnimplemented $B8FE|0|0|0|
|8|CfHostUnimplemented $B8FE|0|0|0|
|9|CfHostVisible $B34C|1|21|1618|
|10|CfHostHead $AAD6|1|142|1750|
|11|CfHostBody $AA7F|0|0|0|
|12|CfHostAdder $AA8B|1|10|1640|
|13|CfHostBoxProfile $AA8F|1|8|1649|
|14|CfHostSide $AAE3|4|129|1781|
|15|CfHostSceneEnsure $A808|0|0|0|
|16|CfHostBox $AA92|0|0|0|
|17|CfHostPortrait $B37F|0|0|0|
|18|CfHostMenuName $BD01|0|0|0|
|19|CfHostReset $A873|0|0|0|
|20|CfHostUnimplemented $B8FE|0|0|0|
|21|CfHostUnimplemented $B8FE|0|0|0|
|22|CfHostUnimplemented $B8FE|0|0|0|
|23|CfHostUnimplemented $B8FE|0|0|0|
|24|CfHostCollect $B822|0|0|0|
|25|CfHostFullPower $AB56|0|0|0|
|26|CfHostForcePalette $BC86|0|0|0|
|27|CfHostUnimplemented $B8FE|0|0|0|
|28|CfHostHeadWithin $AABF|0|0|0|
|29|CfHostPaletteTick $BC8E|1|52|1869|
|30|CfHostStatusName $BD54|0|0|0|
|31|CfHostUnimplemented $B8FE|0|0|0|
|32|CfHostWorldPalette $BCF3|0|0|0|
|33|CfHostUnimplemented $B8FE|0|0|0|
|34|CfHostShots $B694|1|352|2224|
|35|CfHostUnimplemented $B8FE|0|0|0|

## Full guard and transport evidence

Every observed public CF query has all16 outer header bytes read before its
first private A2 veneer, measured per invocation rather than cumulatively.
Each then reads the same16 header bytes again inside the private A2 router
(15 fixed cookie bytes plus separately derived class). Normal56 queries per
phase each have matching56 outer and56 inner complete checks. Busy104 queries
per phase have104 outer and104 inner complete checks. Each byte count equals
the corresponding service-call count. Header read points are actual
PRG69:BF79/BF8C and RAM2:BE99/BEAC. No check is bypassed by this profiler.

Normal per Main:14 calls each to R87 Router B08E, Wf PRG96:B799,
Bw/Cf PRG67:B22B, CfOrBtCheck PRG69:BF47, and private RAM2:BE6E.
Private CfCallA has17 calls per normal idle Main because input/body/packet
also use it; Right averages17.5. The observed lowRAM SFC instruction union
is8819/Main. SFC scopes also contain unlabelled actual code in PRG4/126/2/79
and other owners; their full aggregate is retained only in compact stdout,
not called bank-switch cost.

The private router alone takes9759 exclusive cycles/Main; outer complete
checks5586; generic resolvers1512; R87 Router1512; measured Nr/Hu wrapper
instructions3960. These categories partition opcode work and retain all14
real service executions. A future guarded direct path may eliminate repeated
transport or redundant validation only after proving the sole full check
precedes *every* private opcode and the complete caller/foreign/fault/retire
contract. No such new descriptor or source lease is claimed here.

## Retained observer negatives and scope

Initial98005 failed before CPU at a cached metadata raw-object identity
assertion; the corrected observer reuses the exact cached authenticated
reference object while executing owning ffbb. A following restart correctly
rejected mutable Nightly91dc at the frozen6a3 loader. The new explicit91dc
inverse boundary fixes that reference extraction without widening it.

The first successful service run produced verbose per-byte output beyond the
retrieval cap (receiptc2c1800f82a08224176657e022d20ee319248abdc93b63f9816739498fa8bbb5).
Its per-invocation header evidence was then tightened and stdout compacted.
The compact b78e3485 receipt established the same cycles; final b6b25032 adds
physical opcode ownership within SFC scopes so unlabelled bodies cannot be
misreported as transport. No game bytes or control policy changed between
these observer revisions.

Root4846 native work-marker timing remains **unimproved**:48idle Main96physical,
71/95 missed-read frames;16Right Main32physical,23/31 missed-read frames.
See the scoped native negative and Burns source pass in
[work-marker QA](contra-force-p1-work-marker-producers-1116.md).
Other three source full routes remain deferred by root; no new CF native or
delivery was performed by this helper.
