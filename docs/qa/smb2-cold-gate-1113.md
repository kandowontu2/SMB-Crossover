# Prepared cheat-option cold-gate diagnostic

This is a source-prepared **cheat-option diagnostic**, not standard stage
qualification and not a confirmed runtime exposure of E037. No Mesen run
or game-byte change is made. Exact current ROM is delivered12397:
`12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52`.

New pure API:
`replay_smb2_cold_gate_native_1113.controller(raw)` returns standalone Lua.
Factory SHA256 is
`6e1a95017100d08193b5c7298d89125066eaa6e6832bd55cde7bbd0fe4c042d1`;
Lua SHA256 is
`eb9ae28a623d58d75b5795e3620643c7e2b945a047e75df46ae3fbd9bec6102b`.
CLI prints metadata only; `--reset-probe` prints the bounded source-model
limitation below. Neither mode writes files or launches an emulator.

## Actual-input opening and unchanged ordinary route

The prefix uses only ordinary controller presses, reusing the established
real frontend flow from `sound_cheats_menu_native_v1.lua` without that old
script's files/screenshots/audio tests:

1. Wait for a real visible title. Down then Start opens Options state4.
2. Two fresh Down presses choose row2; A opens Cheats state6/focus0.
3. Assert fresh flags/start-level0, then A enables only Invincible bit0.
4. B returns to Options/focus2; B rebuilds the title. Assert the enabled
   bit survives, every other cheat remains off and start-level stays0.
5. Execute the frozen Luigi roster selection/Start and ordinary1-1 route.

The ordinary route text before adding this prefix is SHA256
`5804ddb027a6b2956dae8fd155184a4a521a59e7fd784689d95db240fd8bfe4f`.
All its input decisions and full flag/castle/pipe plus25 living grounded1-2
assertions remain. Exact removal of the menu/observer/label additions
reconstructs that text. No asserted endpoint is weakened or replaced with
an early pass upon seeing an old target. A live assertion also requires
CheatInvincible to remain exactly1. The receipt and success reason state
`cheat_option_diagnostic=true` and `standard_stage_qualification=false`.

Invincibility is enabled by the actual menu's game instructions, never an
emulated memory write or seeded ability. No air jump, wrap, timer hold,
full-power or starting-level option is enabled. No input/position/item,
health, actor, source header, audio status or mapper seed is introduced.

## Bound observations and exact current guards

The factory authenticates the complete45-byte E02B bridge in119/120/125/127,
the actual low-bank126:83A1 `JSR E02B`, native79:BDDE UI-tail bytes and
79:BDF5 `HuGameColdDispatch` entry. All four ordinary E045 paths currently
target BF:AD21; an initial guard using an older81:A021 literal was rejected
and corrected to actual installed bytes, without relaxing the45-byte guard.
Current CrossoverMenuInput, CheatsMenuInput and CheatsSixInput entry windows
are also authenticated against their retained compiled entries.

One64-record budget covers menu states, DMC/bank/target and caller-return
observations. Low pulse/noise changes do not define DMC interest. At most12
audio-interest records, one detailed canonical context and four119/120
contexts are retained; global call counters remain uncapped. All reads use
`nesDebug`/read-only state access; there are no images, dumps or emulated
state writes.

An attributed old/canonical target needs the real83A4 caller return and a
fresh same-Main chain through E02B, the cold E033 branch, E042 tail,
FarCallCommon015A and SMC JSR016B. The token checks actual produced target,
rawCF mapping and SP at each gateway. Native target entry additionally
requires expected SP and stack return016E. It then observes FRC return,
original caller return and next Main outcome. Tokens expire at next Main
and are bounded to120,000 cycles/four frames. The diagnostic preserves
missing returns as evidence; it does not repair a stack, target or state.

## Exact source limitation

Metadata generation passes strict12397 inverse/source binding, all current
instruction windows, Lua compilation, read-only guards and original-route
text reconstruction. This is **not** a passing source execution of the new
title/options opening or cheat-enabled stage.

The existing gameplay replay driver begins in its established native-menu
arena and sets `CPU_CONTROLLER_OPENING`, so it skips the Lua title opening.
Using it with an injected CheatInvincible value would falsely qualify this
test. That route is deliberately not used here.

Instead a50,000-instruction probe starts at the real RESET vector using the
existing controller/mapper bus. It remains at E29C `LDA $2002` / E29F
`BPL E29C`, maps254/215/216/255 and debugger status2002=0, before title or
input. This bus always returns PPUSTATUS0 and supplies no video/APU clock.
No vblank/status override, shortcut past RESET or cheat seed is applied.
Therefore the new opening is **source-unqualified**, and runtime exposure
of the obsolete target remains unestablished until a genuine timed run.
The reset probe documents a model limit, not a ROM failure.

All producers run through the existing bounded empty root
`build/prince-pickup-reach-1112 --max-files 1` with120/300-second limits.
Outputs0; no ROM/controller/capture files, extraction, grants, helper
platforms, Downloads replacement or release action. The verified12397
nightly and all frozen factories remain unchanged.
