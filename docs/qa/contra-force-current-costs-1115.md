# Current Contra Force idle/walk costs — November 15

This is read-only source attribution on exact delivered **bc5**
`bc5e275d1dd4dabab4b5b2def66f7643ae46aee17a31ab37887528b791594040`.
It creates no image, patch, allocation, native run or timing acceptance.
The earlier four individual full-stage native passes and the actual 421
idle120 = 60 Main/CF-return observations remain versioned in
`contra-force-full11-source-1114.md`; they are not new bc5 hardware results.

## Inputs and actual owning code

`profile_contra_force_current_costs_1115.py` SHA256
`721d91c5220c20f71d31cb61683b05cfb3612244b4f86aff1d3c6c692d8f1a94`
accepts only exact bc5. `compose_hot_draw_bt_67e_1115.inverse` recovers exact
67 for bindings only. The bus retains **all actual bc5 CPU bytes**.

Only five existing CF inputs are read from
`build/contra-force-projectile-contact-1031-v3/kernel`:

| Input | SHA256 |
| --- | --- |
| runtime.dbg | `d98abb1cc9701fb2b4674c99cbeef7fe03411a8d00cefd0752522af06aad4f82` |
| runtime.lbl | `8944961064964d2bac2d7b2ebca31fbb4ac4c2d9b555af032f7477ee16414ab2` |
| ram1.bin | `aee82a91f7f4396105f66286aab9630cb65f7cdbb365a0da07fd0cf7f16c8624` |
| ram2.bin | `8d37a18c459df07976adab3f1f815272a342f3a482c4c0894293762a33b38d50` |
| ram3.bin | `0ad7bb16f75acc550db46f63e9466a370b6370d247b7e3d3ad3be6db86901795` |

The actual 24,576-byte carrier935..958 SHA is
`3a7d2d9a77d5accd30e7976645856118f8734fca5a84f7df7bff8946ec989f84`.
It equals the retained three images with declared padding/cookie tails.
No archive or historical dependency tree was restored.

The compiled menu really selects **BURNS**, slot30, raw31, variant0, no Select
cycles. Actual Start/parser/constructor reaches X40/Y176, life2, power0/Star0,
no cheats, naturally zero native actors and all12 source shot slots zero.
The complete current C2 cookie and zero32-byte C3 tail are verified.
Inspect16569 passed, receipt
`636f9e8af30712158c941a59461bdb9ea2dbc9ffbe3f2129d6d4d9a157e1cee1`.
The prior inspect57016 stopped at a malformed *local source pin* before CPU
execution; fixing that typo did not change an input or game byte.

DBG segment/oname ownership, checked against actual carrier bytes, resolves
the original **CfNativeInput RAM1:B03C** and **CfNativeBody RAM1:B308**.
The old 421 profile's assumed RAM3 aliases were not hits and must not be used
to claim original-core cost. Current movement is RAM3:A91B, private router
RAM2:BE6E, transport RAM2:CA0B; every point authenticates its mapped tag and
eight actual bytes. Dynamic return PC, map and SP acknowledge each call.

## Normal Main, exclusive accounting

Normal35824 passed eight idle and eight Right Main calls after four ordinary
warm updates. Receipt
`130ea2e8174504d5554313ea504b1f04758f12ca5ff07989c8d298052a13f5b6`.
All named entries/returns balance, no nonlocal unwind or pending scope/ISR.
Minimum SP189. Controls are only idle and Right, with empty actor/shot checks
after each actual Main. Final positions are40/176 and49/176.

These are instruction cycles per Main. Each row is **innermost exclusive**;
the final residual includes every instruction not assigned to a deeper named
scope. The entire column sums exactly to the separately acknowledged actual
GameLoop scope. Nested inclusive values must not be added to these rows.

| Exclusive scope | Idle | Right |
| --- | ---: | ---: |
| Unassigned inside GameLoop | 22,336.125 | 22,341.125 |
| CfA2Router | 9,759 | 9,759 |
| CfOrBtCheck | 5,586 | 5,586 |
| CfP1LateEntry | 4,237 | 4,237 |
| CfCallA | 2,638 | 2,715.25 |
| CfHostRenderAll | 2,571.125 | 2,579 |
| DrawAllMetasprites own work | 2,362.375 | 2,362.25 |
| CfNativeBody | 1,192 | 1,239.875 |
| JnSpecialDrawDispatch | 864.75 | 864.75 |
| CfNativeInput | 313 | 346 |
| All other named Main scopes | 4,381 | 4,381 |
| **Actual GameLoop total** | **56,240.375** | **56,411.25** |

Each phase has8 render calls,112 external checks and112 private-router calls
(14/Main),8 P1Late calls, and8 AudioUpdate calls outside Main. CfCallA is136
idle/138 Right, including nested original-worker calls. The14 service rows are
0,1,2,6,9,10,12,13,14 four times,29,34. The outer-check SMC operand itself
contains the check address at ingress; service offsets are taken from the
actual private-router entry, not inferred from that outer operand.

Regular NMI totals are34,775 idle and36,113 Right over8 calls each. AudioUpdate
inclusive is24,159/25,497 (3,019.875/3,187.125 per NMI), including its expanded
audio dispatch. These are separate overlapping ISR scopes and are **not**
part of the GameLoop column. Hardware-entry wall accounting includes the
seven entry cycles; the instruction-only ISR counter does not. No claim of
physical frame cadence follows from this scheduled source driver.

## Actual source catch-up component

Busy6643 passed, receipt
`2a2e3756bf9173910d917beab730797d96cef0a809c3d7e8c836c7e5b1277d4e`.
One actual hardware NMI is injected at the first real CF movement ingress per
source scheduler iteration, while Main's existing busy flag is set. No game
RAM flag or draw-skip flag is seeded. The unchanged resident IdleLoop and
TerrainCatchupPending produce8 render plus8 no-render calls in each phase.
Render calls have14 checks; no-render calls still have12. All named calls,
returns and actual regular/busy NMI spans close; minimum SP189.

Combined16-Main costs are772,355 idle and775,256 Right. An observed Right
render costs57,147 excluding its2,740-cycle injected NMI; the following
no-render call costs40,296. Other sparse no-render examples cost41,150 and
40,593. This is a reached **source interrupt component**, not a claim that
hardware runs at this input/render ratio. In particular, skipping draw alone
does not remove most CF update cost. The terminal receipt was retained, but
the tool display truncated part of its detailed stdout; no omitted sparse
row is asserted here.

## One-Main residual and palette witness

`inspect_contra_force_idle_residual_1115.py` SHA256
`f92dec8c96fddf619713ea3b518fd1beeb90f72e535331b2abc9de32c67982dd`
passed95377, receipt
`28757815f44ea6c2de8ede44550c7d39cebf5e4965dee34aaa89182ed6d8adbd`.
One actual ordinary idle Main costs56,226; its22,299-cycle residual is
aggregated by actual physical tag/page. No per-instruction trace is saved.

| Residual location | Cycles |
| --- | ---: |
| Low RAM0100..01FF, actual farcall transport015A..017A | 7,363 |
| PRG87:B000..B0FF | 1,332 |
| PRG79:B800..B8FF | 1,073 |
| PRG67:B200..B2FF | 1,020 |
| Fixed PRG126:8300..83FF | 742 |
| PRG2:A600..A6FF | 730 |
| PRG124:A500..A5FF | 704 |
| All other residual pages | 9,335 |

The top14 residual instruction counters are actual low-RAM transport
015A..017A. The reported low-RAM byte samples are its **final SMC publication**,
not a claim that every execution used that final target. Physical-ROM samples
are exact immutable current bytes. This localizes substantial shared host
transport/foreign dispatch work beyond the CF-specific workers; it does not
prove that any of those calls can be removed.

The exact actual late owner is RAM3:BE53..BEFE,172B,
SHA`a247fb3fd68b6b90218a96f4ec2183ddd361e9cdcebdb1ad7c4375f8745a01dc`.
Its22B RAM3:BF55 gate SHA is
`84c2741a56496029b0304ea58f5bc98e28d88cad662173f2024c9efafacdb5cf`;
the124B packet worker is **RAM1:BF10**, SHA
`43b2f24320c1248a381f58b7342824cb23558e72fcd6ea94e6f94d2ec8e0c591`.
The late entry consumes its one-shot bit7 token, restores24 native attributes,
then scans all64 OAM rows for visible palette participants. It chooses native
or shot colors (alternating when both are visible), scans/paints64 rows again,
clears tag bits18 from **all rows including hidden ones**, and publishes the
ordinary complete palette packet through CfCallA. This work is not all hashing
or unused graphics. The current exact bytes are in the compact source receipt.

At actual RAM3:BE80/SP209 this empty opening has8 visible/56 hidden rows,
**all64 attribute tag masks are zero**. The whole256B OAM is identical before
and after paint, SHA
`832ff3a0bcf3a66d187cbbf967569e0f1f4e859558022b997e07b5c792c34cf7`.
Visible0/choice0 and every row matches the original hide/clear contract.
This supports researching a no-change fast path. It does **not** authorize
skipping paint merely because Visible==0: hidden tagged attributes must still
be cleared, and native actors or earned shots require the existing arbitration.
No replacement bytes, spare-space claim, integrity skip or source overlay
has been made. Audio/input/timers and all complete cookie checks remain intact.

## Current hardware benchmark packaging

New `replay_contra_force_current_idle_1115.py` and checker provide a strict
bc5-only Burns idle48/Right16 **completed Main** observer, based on the frozen
ordinary-menu CF clock. They add literal4016/4017 physical-frame read counts
and Main histograms, while acknowledging actual movement and RAM1 input/body
return PC/SP/mapping. Zero native actors and all12 source shot slots remain
required; no A/B, gameplay write or full-route repetition is added.

Callback55087 caught a missing indirect RAM-name binding for the pos() helper;
no pin is qualified from that generation. Explicit pos-name extraction fixes
only configuration. Callback93972 then passed six actual Main entries/returns,
five movement/Input/Body entries/returns each and96 actual CPU port reads,
with every dynamic mapped return acknowledged. Receipt
`6da96a9f0ab8d22223de55af4b6ff4c1f833d148ba53de852a91ac958beffcf2`.

Complete88082 also passed the entire64-update observer, receipt
`4b8d11e81072ecc2e35879619d64e17373221b41fa7f316d571588efa26af211`:
66 total Main entries/returns,65 movement/Input/Body entries/returns each,
1,056 actual CPU port reads and130 cookie/empty checks. The phases each have
exactly48/16 Main and CF movement returns, ending X40 then59/Y176, grounded,
life2, power0/Star0, source contact1/age0, correct original variant. Actual
movement caller is C2:CA2B, Work RAM offset18987, return SP212. This model
schedules one Main per frame iteration: its47/15 complete-frame read bins and
zero skips are **not hardware cadence evidence**. Native launch/interpretation
belongs to root; no cadence success is presumed.

Frozen packaging:

| Artifact | SHA256 |
| --- | --- |
| Factory `replay_contra_force_current_idle_1115.py` | `f8d7dc9a9c3a85cee4c3d142f590fb460f35d68c972c5d7c80003eb9c99be875` |
| Checker `check_contra_force_current_idle_1115.py` | `4a7f3ae84d1506bababb715c5b7c47e5cdb1922326bfb3971319328ab03e2dac` |
| Exact LF controller | `8752e93299f3ae10e11da02b975bb5bdc067fa1e4e3d02fb42c84ec9e4e7ebe0` |
| Observer body | `6e1bababb077ad935556b7b2202f001c76c40a1119e8add52d2a9b41086e1a31` |

APIs: `controller(rawbc5, 'burns')`, `metadata(rawbc5, 'burns')`. Whole-image
rejection checks cover parent67, unknown/truncated input, changed118/live108,
CF carrier/cookie, Prince/unowned bytes, and an unqualified Smith identity.
The frozen old CF421 factory/default remains untouched. Current Main hooks
authenticate actual bank126 SHA
`5bd9cd2fce2eaa0b6bd14b403a3ea0fb4c979499087d3df5c2c330bdffa5a331`.
Current input/body hooks use physical RAM1 offsets12348/13064, not a numerical
PC alias in RAM3. `NmiSkipped` is actual RAM314. Port reads and full-Main/
worker/native-service returns have distinct counters. Phase-boundary partial
physical frames are excluded from the literal-read histogram rather than
inventing a full-frame sample. No new whole-stage result is asserted.

All producers used `run_bounded_build_v1.py --output
build/contra-force-current-costs-1115 --max-files 1 --timeout 600`, with `python
-B`; this root remains absent/zero files. No ROM, capture, dependency tree,
emulator or Downloads write was created. Root owns all native work and cleanup.
