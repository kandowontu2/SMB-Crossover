# Private Parodius drawing performance pass (NS)

This pass remains a private 37-identity MMC5 build. It does not close the final
all-character/all-powerup, dedicated audio, sprite visibility or oversized-MMC3 gates.
The published 33-identity builds remain unchanged.

## Repair

`PnDrawRecord` avoids repeated subtraction for power-of-two record rotations.
Complete records stream directly from their immutable source into OAM, preserving
the old rotated reverse-part order. Interior records use a bounded renderer;
edge records keep signed X clipping and the original status-bar/bottom Y filter.
Truncated large effects keep the original buffered selection/capacity path.
No new WRAM is allocated. The helper shares unused space in `ROLL_CORE` and its
bank is restored by the existing farcall ABI.

The old temporary pose buffer and R0/R1 are dead after this local call: the next
actor reloads its record, and the common player reservation reloads SmPosePtr.
The direct path therefore leaves the source pointer intact and skips temporary
buffer writes. Registers/flags, stack, A/C-bank restoration, OAM cursor, every
actual OAM byte and the exact OAM store order are compared to NR. The generated
art contract is also checked independently for all662 pooled records.

## Measured performance

The before/after gear arenas use real cold menus followed by declared native-
update-boundary staging. Controller pulses use completed update counts, and
actual native input traces are retained. Full-fleet input traces match exactly
for all three pilots. Each row covers120 native updates with two live Goombas.
These are seeded performance arenas, not physical gear-acquisition or campaign tests.

| Pilot | Full-fleet video frames, before -> after | Lag NMIs, before -> after | Mean draw CPU cycles, before -> after |
|---|---:|---:|---:|
| Octopus | 241 ->225 | 181 ->165 | 22,642 ->18,008 |
| TwinBee | 231 ->196 | 171 ->136 | 22,446 ->14,957 |
| Pentarou | 205 ->190 | 145 ->130 | 21,475 ->12,992 |

ISR-excluded draw work falls about20.5%,33.4% and39.5%; inclusive whole-game-loop
cost falls about4.8%,8.3% and10.7%. Nested spans overlap and must not be summed.
The ships still lag substantially under full gear. Idle and two-Goomba phases
retain120 updates in120 video frames; the ordinary-fire improvement is small.
Octopus ordinary-fire traces differ at one input edge by one update, so that
phase is not an exact-input performance comparison. Every phase's equality flag
is recorded, including any other such difference.

## Evidence boundary

The instruction comparison includes16,128 rotation cases and44,560 whole-emitter
cases, including all662 native pooled records, viewport/page boundaries,
rotated OAM, empty records and capacity rejection. It is not campaign evidence.
Physical pickup checks still compare45 actual uploaded pickup/score poses to the
original cartridge art. Real terrain death checks retain native animation calls,
committed pixels and movable respawn. Cold-entry checks cover all37 identities.
Six fresh Easy/Hard1-1 discoveries and independent exact controller replays are
required in the NS proof, together with actual CHR/DMA/HUD observations.

A Bell assertion exposed an invalid late palette comparison: SMB independently
animates question-block color$3F0D. The failed TwinBee sample expected$27 while
both the captured incoming palette and correct restoration contained$17; NR
happened to match the later animation phase. The original failure and diagnostic
bytes remain preserved. The repaired fixture checks all32 actual PPU restoration
writes against the captured incoming palette, before normal cycling can change
it. Both NR and NS pass this stricter packet assertion; no game palette code was
changed to satisfy the fixture.

The shared Roll bank has a fresh Roll component regression. Ordinary14-identity
MMC3/MMC5 builds reproduce their unchanged hashes. Exact checkpoint source ZIP
rebuilding and public-ROM hashes are recorded separately. This pass does not
claim60Hz, physical-console proof, all-item coverage or completion of the goal.
