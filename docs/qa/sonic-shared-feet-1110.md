# Sonic shared feet transport

This source-only component adds raw43 to the current native foot filter and
routes its real native getter call to typed common service35 at PRG65 B0F5.
The getter still requires root's separate raw43 public/common admission and
the authenticated D100 service envelope. Those are not supplied or claimed
by this component. No ROM, build file, emulator capture, or nightly file was
written. No platform actor or placement changes occur.

API: `tools/audit/check_sonic_shared_feet_1110.py` exposes
`proposal(raw) -> (image, record)` and asserts all current preimages.
The qualified input is the Sonic owner's aligned source packet
`679b3e479fedd7628b5edd782283cae9eb59e2183c984a82776672ba6d7ac083`;
with only this transport applied in RAM:
`45432808bc209199f2c1b585964a00805a6f04e2f3762dd523a5758538336e59`.

## Source funding and exact layout

The fixed Sophia head packet's incoming-A store is dead: its actual PRG5
B9E3 callee begins LDA0. Removing three bytes and consuming the single
unexecuted NOP before the legacy side veneer funds the four-byte raw43 test.
The native foot entry moves E46D to E46A. Its two genuine JSR operands at
file offsets1039387/1039396 are rebound. The unused source side symbol moves
E496 to E497; its JMP90E4 and all following PCs stay intact. The two whole-word
E496 matches at358452/693168 are unrelated data and remain exact. They are
not treated as callers.

In the PRG65 default router, incoming A already equals SelectedCharacter;
the duplicate load is removed. The cold Z2 getter overwrites incoming A, so
its dead publication is removed. The JMP to the next instruction is removed.
The compact original router occupies BC93..<BCB6, leaving nine known bytes.

The union router's duplicate incoming-A publication is removed. The Gimmick
getter at actual PRG24 B877 starts INY/LDA0/JMPB87F and never consumes incoming
A. Its old 23-byte custom NextBank forwarding packet becomes a 13-byte
pointer/JMP prefix plus the ordinary five-byte LDA98/JMPFarCallCommon tail.
The tail occupies exactly Sh's explicitly qualified AC10..<AC15 source lease.
The authenticated 59-byte Sh body, both real import targets, and following
table bytes AC15 onward remain exact. Sh ends in RTS before this tail.

| Region | Contents |
| --- | --- |
| BFB0..<BFC2 | Original family tests plus raw43 branch |
| BFC2..<BFCF | Gimmick target pointer and jump to Sh tail |
| BFCF..<BFD7 | Sonic target-low F5 and jump to BCB6 |
| BCB6..<BCBE | Sonic target-high B0 and direct jump B0F5 |
| AC10..<AC15 | Gimmick ordinary native FarCall tail |

The two remaining one-byte slots are explicit NOPs. BFD8..<C000, including
the native DK helper and exported FF getter, remain exact. The Sonic route
publishes the complete F5/B0 target while retaining its genuine bank65 caller
frame; B0F5 creates the existing common saved-state/authentication context.
No private opcode is executed before that authentication.

## Source CPU qualification

110 paired directed getters start from actual menu, cold load, parser, and
60 ordinary opening updates. They cover MARIO, LINK, ZELDA II LINK, SOPHIA III,
all four FF classes, MR GIMMICK, DONKEY KONG, and ARTHUR; Y0/1/30/31/32 and
flags31/F5. Four additional Sophia head-tail pairs pass. Returned AXYP/SP,
native/private state, and mapper state match the unchanged parent exactly.
This includes the Gimmick replacement's additional balanced native FarCall
frame; its minimum foreground SP is211.

Five representative changed contexts include the deepest reached Gimmick
frame. Each passes real NMI and IRQ against the unchanged native ISR, then
exact resumed foreground execution: 20 paired ISR executions. The original
Gimmick NMI clock intentionally changes declared fields5C37..5C39; those
values are compared exactly against the unchanged-parent interrupt. Only
those three fields are excluded from the separate no-clock-tick live-body
assertion. Registers, live stack, R0..7, SMC, remaining native/private state,
and hardware/mapping behavior stay strict.

These are source CPU callback and interrupt results. Natural Sonic movement,
the complete public raw43 getter/header-fault path, and physical Mesen remain
separate requirements. Current aligned source still deliberately rejects
raw43 at the public common selector until root composes its admission patch.

Frozen source SHA256:
`106c68d674b24c52ce683339c0e95b9386b921eb774171970feeff13040d5dd3`
for `tools/reference/sonic_shared_feet_1110.s`.
Frozen checker SHA256:
`edcfa3236f7f6b1ec91ad6c9b378ee939428a542dfc2ebaba233d70cb4eb096e`.
Tests ran with Python `-B`, bounded `--max-files 1`, and zero written outputs.
