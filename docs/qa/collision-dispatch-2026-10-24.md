# Collision query routing: private OJ checkpoint

The private MMC5 candidate is SHA-256
`88906bd9b21a65c2a09128730599a4683ff6123a655386c1b55d3e0ec1ef3b8a`.
It replaces two long, read-only character-dispatch chains with a short route to
the same native collision leaves. The working-source adoption receipt is
`build/verification/collision-dispatch-oj/proof.json`; its presence and passing
source rebuild are required before treating this as adopted. This is partial
performance work, not a final release or completion of the active goal.

Only four game-source files change. Exactly444ROM bytes differ: the operands
within two existing18-byte fixed-bank query calls and a438-byte segment appended
to bank66. Header, CHR, RAM layout and all pre-existing qualified symbols remain
exact, except the compile-time farcall count. The original full dispatcher stays
available for mismatched or unsupported raw inputs. Roll's override retains its
original precedence. No movement, bounding box or collision response is changed.

Actual linked CPU comparisons pass31112cases with exact A/X/Y/fullP/SP,
application RAM and final bank mappings. Interrupt comparisons inject56498real
IRQs across624paths through actual query/leaf/return instructions. Supported
queries need at most6stack bytes rather than24. Together the two queries save
973cycles for Sophia and810for Chip; the4turtles save142cycles per update.

Matched600-update native component arenas retain identical recorded gameplay
fields, including decoded input, for Sophia and Chip. Five120-update scenes give:

| Scene | Sophia old/new lag NMIs | Chip old/new lag NMIs |
|---|---:|---:|
| Idle |60 /30|0 /0|
| Walking |44 /17|0 /0|
| Enemies |108 /73|6 /3|
| Primary attack |120 /120|10 /4|
| Jumping |111 /102|28 /7|

These are component arrangements, with per-completed-update input stimuli, not
controller-latency or whole-campaign comparisons. The first video-poll-indexed
fixture allowed input timing to diverge on the faster build; its failed report
is retained and its timing is not credited. Whole-loop mean CPU can increase
when the engine draws more often; the isolated query savings do not imply that
every entire-loop sample improves. Sophia's attack scene still lags every update.
The existing turtle fixtures retain identical gameplay and unchanged heavy
weapon lag counts27/25. No fixture is a claim of constant60Hz.

Fresh cold-menu discoveries and independent byte-exact input/trace replays
reach movable1-2 with zero deaths for Sophia Easy5151frames, Sophia Hard5543,
and Chip Easy4204. All14298replay PNGs are retained. The existing complete PNG,
body CHR, visible scanline31, world<=8 and camera<=4 bounds pass. All37cold menu
entries and7audio regression fixtures also pass; entry is not a level clear.
Samus's4096native audio rows remain byte-exact.

Both Sophia replays additionally pass read-only immutable SMC/invalid-execution
and stack guards. At Hard frame2086, a video-frame RAM read catches the existing
projectile block probe at1248,144 while its saved player origin is1180,176 and
last drawn origin1179,176. A positive native observer proves this exact temporary
borrow and its restoration before completed updates/drawing. Only that observed
sample is projected for the strict movement review. Original traces and full
PNGs are unchanged. Root viewed2085–2087 and three24-frame route overviews;
this is sampled inspection, not exhaustive human pixel review.

Chip Hard's generic controller still dies; the original four-case discovery
and replay aggregates remain failed. The three-case review explicitly lists
that failure and does not relabel the four-case set a pass. The older OG68case
sweep produced39clean discoveries and29failures, with no independent replays
for those39yet. Earlier-hash evidence remains historical, not current-build
roster certification. Darkwing's actual first Arrow stamp/emergence is observed,
but the controller has not physically collected it; no desired equipment byte
was injected to get past that gap.

External evidence is retained under
`C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-collision-dispatch-oj/probe-v3`.
The OI sweep and OK Darkwing diagnostics are in sibling dated archive folders.
The OJ finalizer is one-shot and must not be rerun after adoption. Closed OD/OE
checkpoints were moved, with all bytes verified, to the existing cleanup archive;
`workspace_storage.py --locate` resolves their old paths. Published ROMs remain
unchanged and workspace size must remain below30,000,000,000bytes.

The complete37identity/both-mode/every-item matrix, remaining deaths and gameplay
gaps, graphics overload and lag, source music/fidelity and oversized MMC3 port
remain required. The final gate in `final-verification-plan-2026-10-23.md` still
applies in full.
