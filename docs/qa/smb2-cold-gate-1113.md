# Prepared cheat-option cold-gate diagnostic

This is a **cheat-option diagnostic**, not standard stage qualification and
not a confirmed runtime exposure of E037. Root's native run calibrates the
real menu but finds an earlier invincibility movement regression. This
helper makes no Mesen run or game-byte change. Exact ROM is delivered12397:
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

## Root-only invocation and passive-read provenance

New runner `tools/audit/run_smb2_cold_gate_native_1113.py` is metadata-only
by default; an explicit `--run` is root's native action after freeing its
single queue. It authenticates exact12397, frozen factory6e1a9501 and
unmodified Luaeb9ae28a. Runner source SHA256 is
`c443a4c7cb7655c18d70b22e8d4382455cf61b2abc18a874c6471046c3b9de31`.
It introduces no derived Lua or changes to the frozen31f6b265 controller.

Root invocation, not executed by this helper:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_smb2_cold_gate_native_1113.py --run
```

The authorized existing component must contain only candidate.nes and
controller.lua, with its retained ROM already exact12397. The runner checks
the workspace queue **before** overwriting controller.lua, performs shared
storage preflight, and then uses the existing stdout runner's queue,
capture lease and watchdog. It never writes a ROM or capture/receipt file.
An additional8MiB component bound is below the existing task hard cap.
Installed bytes and same-name sidecar guards run before/after, including
the native run's error path; the retained component ROM also stays exact.
The native timeout remains240 seconds inside the300-second producer bound.
Other-project/user emulator processes are left untouched by shared policy.

Its stdout aggregate is always labeled a cheat-option diagnostic, never a
standard stage pass. It retains the actual failure reason/terminal state,
menu checkpoints and compact DMC/target/return evidence, capped at the
controller's64 observations. A last menu checkpoint is explicitly **not**
presented as a fresh failure-time UI snapshot. A failed calibration/route
still prints this aggregate before exiting nonzero. A shared-runner or
receipt error is bounded in `runner_error`, without inventing UI state.
Prelaunch authentication/queue failures fail closed before script overwrite.

Metadata/compile/sidecar/installed-byte checks pass with zero outputs.
Separate pure projection fixtures preserve an early UI-calibration negative
and retain a positive old-target witness even if the route itself fails.
These are data-format checks, not emulator or UI qualification. No helper
Mesen run is performed; root's actual diagnostic remains separate.

The inherited helper is exactly
`emu.read(at, emu.memType.nesDebug)`, including4015. Mesen's
[official Lua API documentation](https://github.com/SourMesen/Mesen2/blob/master/UI/Debugger/Documentation/LuaDocumentation.json)
defines this debug memory view without CPU read/write side effects.
The implementation path through
[LuaApi](https://github.com/SourMesen/Mesen2/blob/master/Core/Debugger/LuaApi.cpp),
[MemoryDumper](https://github.com/SourMesen/Mesen2/blob/master/Core/Debugger/MemoryDumper.cpp)
and NesConsole reaches
[NesMemoryManager::DebugRead](https://github.com/SourMesen/Mesen2/blob/master/Core/NES/NesMemoryManager.cpp),
which calls the handler's PeekRam. In
[NesApu](https://github.com/SourMesen/Mesen2/blob/master/Core/NES/APU/NesApu.cpp),
PeekRam returns status without clearing FrameCounter IRQ; ordinary
ReadRam4015 explicitly clears that IRQ. PeekRam may synchronize lazy APU
work to the already elapsed CPU cycle on the emulation thread, but does not
issue the side-effecting CPU read/acknowledgement or advance CPU time.
This confirms the documented passive API contract, rather than claiming
a new disassembly/differential test of the installed emulator binary.

## Native menu calibrated; distinct earlier movement negative

Root's actual Downloads test uses exact frozen eb9ae28a/6e1a9501 and
receipt `86e0977aefd42f0233e3fecee4c2177fefdde315ac51b95f97c2dbe6516fa0e1`.
The real input menu sequence passes: Options frame124, Cheats160,
Invincible172 (flag1/start-level0), Options184, rebuilt title215, then
ordinary Luigi selection/Start. The previously source-limited opening is
therefore **native-calibrated**, without a flag grant or changed script.

The diagnostic itself is negative at727 physical frames/290 Main:
X40/Y176 never moves, HP31/lives2/timer388, and the original
`No240-update active horizontal softlock` assertion stops it. All290 gate
entries reach canonical79:BDF5 and have290 FRC plus290 resident returns,
using resident127. Matched obsolete targets are0. No DMC-start witness
exists; only an after-stop record at438. Thus this is an actual
UI-enabled-invincibility movement regression **before** old-alias exposure,
not evidence that BDDE executed or that the prefix debt is harmless.

Next source work compares the actual canonical cold-dispatch owner calls
with ordinary fast-path source updates and input counters. No movement or
literal patch is granted from this result. If a private motion repair later
reaches real DMC119/120, the unresolved old E037 targets must remain in
its qualification: do not deliver a motion-only change that exposes them.
An actual full cheat-route witness and separate literal authorization are
required. Ordinary no-cheat12397 routes for all8 remain a separate closed
positive; this diagnostic does not supersede them.
