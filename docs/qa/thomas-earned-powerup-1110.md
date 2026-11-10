# Thomas earned powerup progression — November 10

This helper produced a source-qualified in-memory repair and standalone
controller source. Root owns the single Mesen queue, candidate ROM and delivery.
No ROM, capture, generated receipt or build directory was written here.

| Binding | Value |
|---|---|
| Explicit installed parent | `a76d7610eed8493806200c52b96065af0369b926c55d033e17841f818756e2e0` |
| In-memory Thomas proposal | `6d83dea872b42cd39c14d756334a801c8f7da7dfa63ecea16d9f13835c63638d` |
| Original live six-page kernel | `69a1e4d318c29b86eb8ec1485dfc2c5933d39769f3f22427cf9fb826fdeb2a21` |
| New live six-page kernel | `ef6f43c25359401ba280bb5480b93a5a5a663683aa04137ce2de67c062ad04cc` |
| New complete cookie | `a70a4002a5d85501bf9e69d0625ddc43` |

## Two rejected native policies

The authored first mushroom is produced correctly by the current controller
path. It occupies slot 4 because Thomas's existing first-pipe lift uses slot 5.
`PowerUpObjHandler` calls `NrPickupCollision` before its normal collision test;
the Thomas private maturity vector, row 23, was an explicit `ThReject`.
That carry-clear result skips `RemainingNormalPlayerCollision`. The mature
item therefore passes Thomas without entering `HandlePowerUpCollision`.

Separately, a directed prepared mature item reaches the unchanged
`ThomasHostPickup -> MarioSourcePowerupCollision -> GuestBeginPowerup` path,
but its resulting freeze never advances. Eighty-five distinct actual
normal-NMI/Main updates leave Age 0/Active 1/engine 9. Row 33 was also an explicit
`ThReject`, labelled “generic powerup completion later” in the source.

The repair changes those two private vector targets only: row 23 uses the
ordinary native maturity rule, allowing Star/1UP or fully emerged
mushroom/flower; row 33 calls existing `GuestPowerupUpdate`. The resident
Thomas dispatcher, complete dual-cookie check and player/life/area context
check remain unchanged. Original movement, jump, damage, terrain, rendering,
art, metadata, all other vectors and helper actors are unchanged.

## Source funding and cookie

The 32 bytes of new policies occupy the start of the retired 91-byte
`ThomasHostQueries` component lab helper. Its exact current span is
RAM3 `$B5B2..$B60C`, before the live render anchor at `$B60D`.
The checker derives the current entry from the live side-vector address and
verifies the entire exact source body. Retained symbol aliases for these later
functions are three bytes stale and are not used as current bytes.

The helper is absent from all 36 actual service roots, has no incoming kernel
JSR/JMP operand, and its source only exports/defines it; no production caller
or address table names it. Native feet/head/side routines stay intact.
The remaining unused bytes are not borrowed by another component. The apparent
resident `$B8E0` tail contains live loader tables and is not treated as padding.

The existing fingerprint recipe is preserved exactly: the full 8,192-byte
kernel template, including its two unloaded pages, plus the complete
8,192-byte state template. The live six-page original plus retained template
tail reproduces the original cookie before mutation. The new revision-2
cookie fingerprints the new policies and unchanged complete state.

`tools/audit/check_thomas_powerup_progression_1110.py::proposal(a76_bytes)`
returns `(image, kernel, cookie, record)` in memory. Neither this proposal nor
the fixed-parent natural diagnostic silently follows advancing Downloads;
their exact inputs reconstruct from retained c10 and the frozen a5/Ex recipes.

## Actual naturally earned source route

The actual menu starts at RYU HAYABUSA, Select twice to THOMAS. After the real
parser/constructor and 60 ordinary opening inputs, the controller holds
Right+B to X325, Up+Right+B for eight updates, then Right+B until X400 and
coasts. This uses Thomas's original 27-pixel jump and existing helpers.
There are no actor, floor, position, health, gear or immunity grants.

The fixed image naturally enters `HandlePowerUpCollision` at route update 392:
Thomas X401/Y176, the mature slot-4 mushroom X411/Y158, state `$C0`.
The native return has carry set, actor erased, floaty 6 and SFX `$20`.
There are exactly 60 actual `GuestPowerupUpdate` calls. Ordinary Right then
resumes to X418/Y176 at route update 469, Status 1, engine 8, Active 0,
timer 0 and lives 2.

The narrow additional source proof passes 32 maturity cases (slots 4/5, four
kinds, four emergence states), eight ordinary/terminal native update ABI and
application comparisons, one fault in each complete header, foreign owner and
life-context rejection, and a real paused Main followed by resume. Four reached
instruction contexts execute four real NMIs, four real IRQs and one nested
scanline IRQ during the actual lag-NMI CLI window: 18 paired native ISR
executions, with exact hardware effects and resumed foreground.

These are finite CPU-model results. Natural flower/Star/1UP benefits, full-stage
routes and physical qualification of this proposal remain separate.

## Controller handoff and preserved negatives

The standalone stdout controller follows the same ordinary input policy,
captures slot 4, requires an actual native SFX `$20` write during that exact
collection call, and permits the sound engine to consume the queue before
return. It checks all 60 native tick returns, 16 pixels of resumed movement,
lives 2, original OAM/CHR, palette and THOMAS HUD before/after recovery.
No output files or images are requested.

Root's physical v1 baseline stopped before pickup because its observer assumed
latches 4..7 were the Thomas body. Receipt
`0558c021e74e8b4a70305cb6ceb7764eb7d57472f7b4ac0e4b7ebe81860566cf`:
frame 335/Main 299/X41/Y176, alignment/palette/HUD true, banks false.
V2 inspected each consumed sprite pattern but read the live descriptor at DMA.
Its baseline receipt
`1556c1f1ad96dee7b8a84bddc04b3ea9d83b678de2e0d65e160595cc3de3fbe6`
again stops before pickup: descriptor `$D04B`, first record cell missing.
Neither is a native pickup failure or a reason to change gameplay.

Frozen v3 snapshots the immutable ROM pose record at the actual
`ThNaturalDrawDone=$A375`, following the existing native helper's contract.
At DMA it matches that drawn record to actual OAM cells with one common anchor,
derives each consumed pattern slot/page and requires original pages 434..441.
Failures include the expected cell, all visible OAM, all eight CHR latches,
upper/mode and shadow publication fields. The API-only proof retains wrong-art
and missing-SFX negatives and proves a later live-descriptor change cannot
retag already drawn OAM. Root's v3 physical result is pending here.

## Frozen source pins

| Source | SHA-256 |
|---|---|
| `tools/reference/thomas_powerup_progression_1110.s` | `57611f69a9d0d7e146edf0ff4b21e49ed80d1e0ac0f7e2cc63b32a94955b59e2` |
| `tools/audit/check_thomas_powerup_progression_1110.py` | `5b085b8aeba5a2068c10487a975414b75bc9ca7a3e67eb656614603d2d342ea6` |
| `tools/audit/check_thomas_earned_powerup_1110.py` | `4f28d05e145c085f269b383b62a60b095d0a03d801fd84d183f298a57a38931b` |
| `tools/audit/check_thomas_powerup_policy_1110.py` | `279b5123ab4188b8c676a58fb2c2ef6d4c76d2b567cc3e8b0ea3b769f38bfe82` |
| `tools/playthroughs/thomas_earned_powerup_stdout_1110.lua` | `c0beb4856e173d0426001d6babbd593837120fe062fa2fcaeecd29f7d0d586c3` |
| `tools/playthroughs/thomas_earned_powerup_stdout_1110_v2.lua` | `fd52b4d6c9153f62013d746fd94f93d69f2f4d7ec5f55650a4827fbe57144960` |
| `tools/playthroughs/thomas_earned_powerup_stdout_1110_v3.lua` | `7b0c6c7e9962a4edb867210853da5d5c78b7052778c041904d9c8d60e4a96320` |

Tests use Python `-B`, the shared bounded wrapper and `--max-files 1`, with
zero generated files. Output reservations stay absent:
`build/thomas-earned-powerup-cpu-1110`,
`build/thomas-powerup-progression-cpu-1110`,
`build/thomas-powerup-policy-cpu-1110`, and
`build/thomas-stdout-source-1110`.

Thomas's existing 1-1 helpers retain initial left edges X400,560,688,864,2560,
2816; centers X416,576,704,880,2576,2832; initial top Y192 and width 32.
No helper was added or moved. Their broader crossing scope remains in the
[helper inventory](helper-platform-inventory-1101.md).
