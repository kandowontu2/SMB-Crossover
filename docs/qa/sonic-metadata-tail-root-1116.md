# Sonic: independent metadata-tail capacity review

This is a read-only review of owning1327, not a code allocation or a repair.
It supports the separate ordinary upward-hidden-block rejection investigation.
The existing private code ends atBFE0 and has no available private tail.

Root `audit_sonic_metadata_tail_root_1116.py`, SHA256
`4db00b7eb423439bd331c1cbc6f975e877e3e970a5dfba6d52bbd3d9b9cdfe1b`,
passes receipt
`b5a1b55da03f22874490617cc0339e80fd9a631cc92072a0ff76043cca9575e0`.
The exact metadata328 hash remains
`367881d827a2cb80aafe71ea45dcdf4c8791ac3a129eaea781be4e579c9067f4`.

Retained ring_feedback producer7d79ea99 explicitly declares COLD_TAIL
D31F..D400 and asserts37 produced bytes. Actual bytes agree:17 bytes of
dispatch, then ten16-bit page IDs321..327/330/333/334 atD330..D344. The
remaining188 bytes D344..D400 are FF. This is a declared producer extent,
not a claim that any run of FF bytes is free storage.

The two cold-table indexed reads use a source-bound page index0..9 and
ASL/TAX0..18, ending atD343. The three other conservative indexed-read
leads are the original draw tables atD24E/D252/D256: DrawIndex resets0,
loops until4, and DrawFlip is exactly0/1; XOR keeps the tile index0..3.
Exact current opcode/table bytes and original effects source5dfe2161 agree.
Those reads stop byD259. All38 published service targets and the conservative
JSR/JMP literal census exclude the188-byte tail.

This closes the declared producer extent and the enumerated literal/indexed
reader leads. It does not prove arbitrary-pointer exclusion, all writer/ISR
lifetimes, or authorize mounting new opcodes. A separate exact repair plan
must preserve native67/68 rejection, distinguish upward hidden5F/60 contact
from lateral/downward pass-through, retain original contact/rollback/native
head effects, and recompute the existing complete cookie domain. Actual
source/native replay remains required before any nightly change.

Initial producer-only receipt0dd9129f retained the same capacity and reported
five indexed leads. The final audit classifies those five using actual
bounded loops; no game bytes changed. All invocations use absent bounded
`build/sonic-metadata-tail-root-1116`, max1/600s, zero generated files. No old
builder/dependency tree, emulator, ROM, screenshot or patch asset is produced.
