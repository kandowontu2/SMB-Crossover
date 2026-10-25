PRIVATE MMC3 PARSER ARCHITECTURE PROPOSAL

Candidate: C:\Users\kando\Videos\SMB Crossover Archive\2026-10-24-native-rest-py\mmc3-parser-v42\candidate.nes
SHA256 bc89a756e24b354bfe1455d1c0dd942c9ef97392a721f2dc2e56da17e8e4183a

This architecture packet is not adopted. Later bounded native qualification
is recorded at docs/qa/checkpoints/2026-10-25/mmc3-native-v42; its limits
and unchanged matched frame cadence remain explicit.
The final proposed recipe rebuilds the exact tested CPU candidate from current
root source/current MMC5 reference; only metadata differs from V42 recipe.

Native92-byte MegaManResetBlockHealth is restored at its original PC. The
49-byte immutable FarCallCommon moves into the original51-byte public warp
read slot. The optional2-byte pad is deliberately omitted: V39 has only16
LOWCODE tail bytes, so the new18-byte public warp trampoline consumes those16
plus the recovered2 bytes. V40 retained pad and correctly failed by2 bytes.
Later LOWCODE code and COLLISION move16 bytes; call operands are relinked.
PRGLow is now full through$9fff. Native parser code/PC/cycles are exact V25.
The rare warp leaf and full256-byte original indexed source window append
strictly after the exact5925-byte native Gradius audio segment in bankFD.
E7..F6 remain byte-exact packed music. No whole bank is treated as free.

The six-byte tiny region remains$0155..$015a. Five actual operand bytes remain
NextBank$013f, SafecallA$0156, FarcallJmpTarget$0158/$0159, SafereturnA$015a.
Native guards must protect the actual six bytes, all five payloads and SP>=5b;
old guards with FarCallCommon's PC frozen at$9041 must bind current labels
(FarCallCommon=$9435, BillNativeReadWarp=$9466, M3ReadWarpCold=$b725/bankFD).
ZeldaII$73fa..$73ff and all1164 linked RAM labels remain unchanged.

Actual CPU checks:1752 inventory/support,4032 cell resets,47360 crossed warp
cases and3072 actual13-row column commits. Parser saves230 cycles/cell and2990
cycles/column against V39 while retaining native V25 timing. Support delta0.
Exceptional warp reads add141..142 cycles; output selector71/A/X/Y/P/SP, banks
and application RAM match, including all256 raw indexed source bytes.
The column kernel is ChkMTLow through its actual RTS, excluding earlier
ProcessAreaData/layout creation, interrupts and frame cadence. No60Hz claim.

Run native exact-hash boot/menu/fullroster and stack/NMI/IRQ guards next, plus
audio/warp/PPU/timing cases. Integrate with independent Parodius font or Zelda
platform changes only through a fresh build and exact-hash checks.
