# Karnov cold-loader funding, v6

This is a source component, not an installed or native-qualified ROM. The
ownership of proposed CHR pages1019/1020 remains a separate admission gate.
The CPU model never executes the copied combat payload.

Apply `prepare_karnov_loader_funding_1101_v6.transform_sources` to the resident
returned by the existing pickup v5 transformer. Pass the exact text of
`karnov_combat_carrier_loader_1101_v3.inc` as `helper_source`. Write the returned
`resident` and each `fragments` entry in the owning builder's existing output
root, then perform its complete source/object link. `carrier=False` tests only
the funding optimizations; `carrier=True` includes the ten-row loader proposal.

The existing CHAR_SELECT segment and `.res` remain the sole lease owners.
There is no overlapping linker segment, additional ROM lease, persistent
scratch, new SMC, or borrowed NMI zero page. Native R0..R7 remain3..10.

The funding changes only cold code: indexed R0..R7 and five-operand save/restore
loops, one shared cookie-invalidation routine, compact public checker bank
iteration, and removal of the redundant R0 clear inside each copy row. The
entire hot KrDispatch source is asserted identical to the input. Its Y and
stack frame require no adaptation.

The funding's shared invalidation calls add a two-byte return address. The
previously proposed carrier row/setup and mapper JSRs also add a two-byte
return address at their respective cold call sites. The actual cold Main
interrupt test covers these paths; it reaches minimumSP138, fifteen bytes
above the SMC floor123. Both619-Main gameplay routes reach minimumISRSP135,
preserving the required twelve-byte reserve.

Exact extended layout against base0162287ebf5b8fcb8a84dcf108a0d0930c4dc9d6e68928c4804bd774712e1a6c:

| Region | Start | End, exclusive |
| --- | --- | --- |
| Five original SMC operand offsets | BAD6 | BADB |
| Shared cold invalidation helper | BADB | BAEE |
| Original70-byte carrier helpers | BAEE | BB34 |
| Immutable dispatch authentication head | BB34 | BB49 |
| Original pickup SuperFireball leaf | BB49 | BB8B |
| Alignment fill | BB8B | BB8E |
| Exact original water table | BB8E | BC8E |
| Existing pickup/authentication tail | BC8E | BFAE |
| Unused lease tail | BFAE | BFB0 |

The resident remains2430/2432bytes and the kernel remains untouched. The
full original isolated assembly reproduces every resident byte of the base
ROM. The source-model link updates precisely three declared native farcall
targets and37 authentic veneer JMP targets in memory; it writes no candidate
ROM or shared source. Root must perform the real owning-object link, bind a
new cache cookie, recheck all imports/leases and qualify the resulting native
candidate before delivery.

Tests cover12 complete cold/warm loader differentials,12 failure routes,
66 public checker cases including each of32 cookie bytes,288 genuine child
ABI seams,48 full pickup consumers, both new carrier readback failures,
49 actual cold Main interrupt cuts, and two619-Main pickup routes with18
interrupt cuts each. The unextended cold loader costs192 additional CPU
cycles in these fixtures; hot dispatch gains no indexed-loop overhead.

The10-row proposal copies the existing8KB image first, then CHR1019 into
C2:C900..CCFF and the first256bytes of CHR1020 intoC2:CD00..CDFF. Copy and
readback both complete before either paired validity publication. Real buffered
PPU reads total18964. Whole-source ownership and native audio/combat/campaign
qualification remain outside this component.
