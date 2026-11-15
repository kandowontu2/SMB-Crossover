# Failed current40a dense generation 5b28

This generation is **unqualified and frozen**. It was never written to a ROM
file, staged, installed, or run in Mesen. Source grant368b5651 authorized only
the in-memory composition and source CPU execution.

`compose_battletoads_dense_current_1115.py` composes exact40a plus the prior
nine a90 spans and the first dense224+175 spans. Candidate:
`5b28a14cc135517a58a4dff840b4e3c6896e79547577b3c0ce083a1bc85b878d`.
It has955 inline preimage bytes,716 changed bytes confined to those955,
and a portable inverse reconstructing exact40a, preserving Prince and all
other unowned bytes. Strict source23735 passed receipt
`e3c6af7c0a4df835a661451ac92bab6519900bce87753bb6ef279eb5dd4608c0`.
Unknown/dirty inputs are rejected, Lua bodies are unchanged, and no mutable
Nightly read occurs after initial input. Those are packaging results only.

Mounted source15672 failed during the third compiled Rash navigation input,
before its public query matrix. `CrossoverMenuInput` reached BRK6DD0 with
maps[254,224,225,255]. The failure was retained, not waived by detached units.

Actual trace82751, receipt
`5d4698d8ab76b143cd38daa9a15506339d2691d30befdcb076c75d9ee2997ba0`,
establishes the first wrong read. Selected33/group64, PRG87:B0C2, SP180,
Y3 executes `LDA B7D8,Y`. That CPU window still maps PRG87, so it reads
file718827/CPU B7DB byte02. The intended entry table is physically PRG96,
file792555, byteBE. The subsequent actual SFC at016B/SP177 maps rawE0
and calls B702, rather than the intended B7BE. B702 enters an unrelated WWF
restore tail without its expected saved frame. RTS at PRG96:B96E/SP186
consumes CF6D and lands6DD0. This is a real mapped-opcode/data binding fault.
There is no observer skip or PC retarget. Model's rewritten symbols are not
installed until after cold returns, which it never did on this path.

Exact40a and referencea90 pass that navigation and Start. The diagnostic's
128-query recording ceiling later stopped both baseline cold traces; that is
an observer limitation, not a baseline game failure or full cold-pass receipt.
The earlier verbose62785 output was truncated;82751 is the retained compact
trace. The normal strict frozen baseline factories remain unchanged.

The detached dense units made virtual helper/table data globally readable,
so they did not test whether Router could read a table in a different PRG
page. Their public ABI results remain scoped to that harness. Corrected
detached units now assert PRG87 for every Router read and PRG96 for every
helper/table read, with a sensitivity case that rejects this exact old read.

Frozen failed-generation source hashes:

| File | SHA-256 |
| --- | --- |
| `compose_battletoads_dense_current_1115.py` | `3305bedce666e7ce2aead2d58e962659c1d10e650d378698ef6f13a790f2656c` |
| `replay_battletoads_dense_current_1115.py` | `cc398818213798006d817bab66d5b0c72a19926d05b6bb6fbfd01ec609a46a0d` |
| `diagnose_battletoads_dense_cold_1115.py` | `ca318aa6b4fa9186530417ce4bb601244d7d05ee357614b4671580f1b5a8ffb7` |

Failed generation Lua pins are Rash9edee8c1..., Zitz8c724351..., candidate
cadence2fabddfd..., and versioned40a cadence8d6c655b.... They are not qualified
native candidate controls. The corrected plan is separately named in
`battletoads-dense-carry-1115.md`; the old lease/hashes/APIs are not widened.
