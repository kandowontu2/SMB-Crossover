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

## Source cause: cold owner routing, all supported cheat masks

New zero-output checker `check_smb2_invincible_dispatch_1113.py` binds exact
installed12397 and its inverse, actual compiled menu/caller/restore/owner
windows, and the normal S2BoundaryGame foreign path. Normal E045 dispatch
reaches BF:AD21 S2BoundaryGame, then F6:B86F S2MainGame, B897 S2MainPlayer
and A640 S2NativeStart. The canonical cold path instead reaches CF:BDF5
HuGameColdDispatch, BF:A252 CheatsGameRoutinesGate, then its A2D0 Native
tail calls81:A021 GameRoutines directly. This skips the source owner that
imports controls and updates the SMB2 actor. Native PlayerCtrlRoutine alone
does not replace that update. Source clock advancement is not evidence of
an actor update.

The matrix uses all eight genuine cold/menu/Start constructor variants.
For each it clones the constructor and tests all32 supported flag masks.
The nonzero masks are produced by actual compiled CheatsMenuInput calls
with explicit focus/pressed UI mailboxes: rows0/2/3/4/5 toggle bits1/2/4/8/16.
This is a **direct menu-call source unit**, not a title/options replay; the
real opening's authority remains root's86e0977a native receipt. No direct
cheat-flag, actor, position, source health or ability seed is used.

All256 cases pass the diagnosis assertions, eight ordinary Right Main/NMI
updates each. Every one of248 nonzero-mask cases makes eight CheatsGate,
Native, GameRoutines and PlayerCtrl calls, with zero calls to the four S2
owner entries above. X remains40, Held/VX remain0, despite actual saved
Right input1 and eight source-clock increments. All eight zero-mask controls
make eight calls to each S2 owner entry, set Held1 and move right from40.
The source trace SHA256 is
`6fbf5f5d323ffa9e04771f2e0fa315eeb73b99fc1261a1523511daeee9893f3f`.
This is a whole-byte CheatsGate routing defect, rather than an Invincible1
input-poll defect. Ordinary no-cheat routes remain the closed positives.

The actual Native entry is reached1984 times with GuestHurtKind0 and
A0/Z1/N0, established by its immediately preceding `LDA GuestHurtKind/BEQ`.
Other incoming flags and X/Y are not assumed zero. A blanket retarget to
S2BoundaryGame would be unsafe: that routine's foreign leg targets81:A14D
HuGameRoutinesDirect, whose raw24/DragonPower and raw2/RdVariant1 special
paths return to E033. The repair must select only raw25 and retain the
original foreign81:A021 fallback, without introducing that recursion.

## Isolated minimal routing proposal before the grant

The checker also contains an isolated instruction-memory unit proposal;
it does **not** return or modify a ROM. Existing57-byte owned restore/tail
A2A9..A2E1 has preimage SHA256
`f0b7b295e1117561595767b6105c2b6a7a203d3044118e020af663c6e55e24b5`.
Changing its ten-byte pop loop to eight bytes (`LDX #F8; PLA; STA R0+8,X;
INX; BNE`) retains the same eight R0..R7 pop/write addresses and order via
zero-page wrap. The restored X/Y/A/P and original injury tail remain.
The two bytes allow a20-byte selector in the existing Native footprint:
raw25 reuses existing AD40's genuine F6:B86F tail, while all other raw
owners retain the exact81:A021 target setup through a15-byte local tail.
The selector uses LDA/EOR and restores the proven A0/NZ precondition,
preserving Carry/Overflow and introducing no extra pushes or RAM writes.

Requested storage is only BF:AAF0..AAFE, file half-open518912..518927,
with AAFF retainedFF. All16 current padding bytes areFF, SHA256
`5ac6a5945f16500911219129984ba8b387a06f24fe383ce4e81a73294065461b`.
The exact Ready85 member
`build/doki-current-component-1101-v1/src/smb2_roster_host_v5.s` in retained
source.zip has SHA256
`ec181a33ecc6a7bd74d5f0856ec6cf40f76b00946a71e603cdf8a446f10e3220`.
Its line84 explicitly emits this padding after the14-byte
S2TypedWorldPalette arithmetic/RTS and before the36 veneers at AB00.
No local literal JSR/JMP targets the padding; all224 actual current Rogue
page-reader rows exclude physical63. The apparent old B001..B800 gap is
**not** used: current bytes there are populated code/data, irrespective
of the historical segment-end label. Root must review and grant the
exact15-byte padding before any composer or runtime placement.

The isolated source unit passes65,280 foreign-owner/all-P pairs,
256 raw25/all-P owner pairs and65,280 nonzero-hurt/all-P pairs. Each R0..R7
slot spans all256 data values for every P; fixed loop control is independent
of those data. All foreign/injury AXYP/SP, live stack and ordered RAM/SMC
writes match the original exactly. Raw25 differs only in its intended
F6:B86F target/terminal bank A, using authenticated existing AD40 code.
This is a proposed restore/selector ABI, **not** a Main/IRQ/native pass.

Commands use the same empty bounded root, max-files1, timeout120/600;
bindings,256-case matrix, exact-source funding and isolated ABI modes
all exit0 with outputs0. There is no resource grant, ROM patch, new
RAM/CHR/helper, renderer change or native invocation from this work.
The unresolved119/120 E037 old cold literals remain untouched and must
be qualified if a later private movement repair reaches DMC aliases.

## Granted private candidate and closed source gates

Root subsequently granted precisely the57-byte restore/tail and15-byte
padding request in `allocations/smb2-cheat-owner-1113.json`, SHA256
`b13857fde91a588fc992acaf86da2a9c2da9ec171e0a055091fc896663d01d33`.
The earlier no-grant paragraphs above describe the isolated design stage.
No neighboring byte, E037 operand, audio, RAM, stack allocation or physics
change is granted. AAFF and all36 service veneers remain exact.

New strict composer `compose_smb2_cheat_owner_1113.proposal(exact12397)`
returns private image
`e8cd1e48bdc48412c30e31b2d0f5decf3a86c49aed85890e8452989e34cc1e17`
and an in-memory layout. `inverse`/`reverse` reconstructs exact12397 and
requires a forward round-trip. Exactly64 bytes differ within the72 granted
bytes. Every unowned byte and the complete119/120/125/127 resident/sample
banks remain exact, including the unresolved E037 operands. Header, CHR,
source actors and geometry are unchanged. No ROM file is produced.

`tools/reference/smb2_cheat_owner_1113.s`, SHA256
`fdc5aad5a90308a7ad752e165b7c30d7bf2f9b358b68aa949e42175ff2b72084`,
assembles entirely in memory to the exact grant-pinned DRAFT_RESTORE and
DRAFT_TAIL. Public A252 and Restore A2A9 remain fixed; the internal Native
entry becomes A2CE, owner tail AD40 is reused and AAF0 holds the foreign
setup. The grant-pinned original diagnosis checker remains SHA2da19919.
Composer source SHA256 is
`17d915df6bd6d28e7608d8f644e32294f76cefee38cf3e272994da2422c45fa8`.

New `check_smb2_cheat_owner_1113.py`, SHA256
`a9ac31386b875bcdc03df4bde6e4c5d4fd3aa9cbc2b3f4c18882718bf8c9124e`,
closes these source gates on exacte8cd:

- All eight candidate genuine cold/menu/Start constructors pass, with full
  state matching the all-off parent constructor. Another128 paired actual
  Main/NMI updates with ordinary inputs retain exact full state, cycles and
  ordered writes on the no-cheat path.
- All256 eight-update option/identity cases pass: all248 nonzero masks now
  execute S2MainGame/MainPlayer/NativeStart eight times, receive actual Right
  input and move from40; the eight zero masks retain S2BoundaryGame. Menu
  flags still come only from the explicitly labeled compiled-menu units.
  Trace SHA256 is
  `b21e9915d4f1b3d8123c92bf72c0104baa0754db33a881c77982b2d0da74a183`.
- All93 foreign named identities use genuine parent menu/Start/parser/cold
  constructors, then authenticated candidate ROM views.104 cheat profiles
  make832 complete Main/NMI pairs with exact RAM/WRAM/maps/peripherals and
  ordered writes. This includes800 actual foreign Native/AAF0 calls. Inv1
  covers every identity; raw0/2/24 families additionally use mask31, including
  DragonPower/Rogue dispatch exclusions. Digest:
  `2741a73bd9522e5b7ae9ae19380adedf3ff45445e070e08fbd2c7d3f54bc121b`.
- 178 IRQ and178 genuine busy-NMI cuts cover every one of34 granted
  instruction PCs and all pop-loop stack depths. Contexts are actual Mario
  foreign Main, actual SMB2 Luigi owner Main, and an explicitly directed
  compiled GuestInjuryStart service after genuine MegaMan cold. That service
  creates the real legacy frozen swap: kind1/Legacy1/engine9/ticks0. The
  first draft's modern-ticks assertion was an invalid fixture assumption;
  no game state was edited to correct it.
- The actual original parent ISR is the ROM oracle at each same candidate
  cut, followed by the intended complete candidate Main. AXYP/SP, full
  RAM/WRAM/peripherals, live stack, SMC, maps and ordered writes match;
  minimum SP182.61 real source-music advances match without audio masks.
  Three existing FarCallCommon pending-STA map completions pass only the
  exact0166/0175 opcode/A/shadow/map exception; no broad mapper relaxation.
  Only instruction ROM is rebound after RTI for the new foreground;
  there is no live RAM, audio, SMC or stack repair.
- 12 corrupted/truncated/mislabelled parent/candidate cases fail closed,
  including an E037 mutation, sample mutation and retained-AAFF mutation.
  Exact inverse and all unowned-byte equality pass.

These31-mask cases qualify **movement-owner routing**, not every cheat's
trigger semantics. A separate observation-only mask16 unit on all8 gives
source HP31/max0/vegetables0 initially, then HP63/max2/vegetables9 after
eight genuine NrFullPower and S2FullPower calls. Native Status becomes1
and Size0; source S2Size stays0. These are actual grant-routine results,
without source-stat seeds. Wrap and mid-air jump trigger cases remain open.
The IRQ injury context is a service unit, not a naturally earned injury.

## Frozen private native adapter; root invocation still required

`replay_smb2_cheat_owner_native_1113.controller(exacte8cd)` is a pure
adapter. It strictly reverses to12397, authenticates frozen6e1a source and
eb9 Lua, and changes **only** the exact ROM pin. Replacing that pin back
reconstructs the entire original Lua byte-for-byte, including calibrated
real title/options/Invincible controls, Luigi route, No240-update softlock,
all original terrain/25-grounded assertions and64-record causal observer.
No emulated write, input change, screenshot or file operation is introduced.
Lua compilation and readonly checks pass.

Adapter source SHA256:
`2f0a5f42434d161fe5250aa41862e1c37f36d1a809099f15f72d836178bf0ae6`.
Private Lua SHA256:
`53055897759c775a4f27c7a27d1b9af437bf4c566b3e1a6058bf8d34a98f4755`.
It remains explicitly a **cheat-option diagnostic**, not standard stage
qualification. Root owns any private Mesen execution in the existing
two-file component; no helper Mesen run occurred.

All source runs use the same empty bounded root/max-files1 with outputs0;
the root remains absent. There are no ROM copies, captures, expanded trees,
Downloads changes or release assets. The movement-only candidate remains
**private and blocked from delivery** pending actual UI-enabled gameplay,
enemy-contact/protection checks and newly reachable DMC/E037 evidence.
Any E037 repair still requires a separate source-backed grant.

## Root-only private diagnostic CLI

New `run_smb2_cheat_owner_native_1113.py`, SHA256
`3c9c4f4218e954fd8697fa76772cc524a53ae8a96542e40af806fded1ed0c040`,
defaults to readonly metadata/compile checks. It pins composer17d915df,
factory2f0a5f42, exacte8cd and frozen Lua53055897. Metadata passes with
actual Downloads12397/sidecar guards unchanged and both existing Bub slot
files still exactf88/79c3859f. Prospective bytes are2120526 across the same
two files, below the8MiB component bound. No private image was staged by
this helper.

Only explicit `--run` may overwrite existing
`build/bub-empty-native-1113/candidate.nes` and `controller.lua`, without
backups or additional files. It accepts only the exact known f88/79c385
preimages or e8cd/530558 restaging identities; known partial staging is
labeled. An existing empty capture directory is permitted, while all extra
files and unrelated directories are rejected. The queue guard precedes
**either** overwrite, then shared storage preflight reserves only actual
byte growth and zero new files. The generic stdout runner repeats queue
admission and retains the existing capture lease/preflight/watchdog.

Root invocation, not executed by this helper:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/bub-empty-native-1113 --resume --max-files 2 --timeout 360 -- python -B tools/audit/run_smb2_cheat_owner_native_1113.py --run
```

The native timeout remains240 seconds. Source preparation and post-run
guards stay within the360-second outer bound; no cap is raised. It launches
the private slot, never Downloads. The installed ROM's exact full bytes
and same-name sidecar guards are checked before and after, including
staging/emulator/receipt/route error paths. Private staged ROM/Lua hashes
are also checked afterward. Neither installed bytes nor old literals are
rewritten; no delivery or release capability exists.

The compact stdout result retains the original route reason, terminal
fields, menu checkpoints and up to64 exact target/return/audio observations,
plus uncapped causal counters. A matched obsolete E037 target explicitly
forces `real_causal_obsolete_E037_private_negative`, even if the original
route receipt reports pass. The original pass/reason remain separately
visible. Absence of an old-target witness never clears the delivery block.
A last menu checkpoint is not presented as failure-time UI state.

Pure source contract units pass: queue rejection prevents both writes and
storage preflight; success order is queue, storage, existing-ROM overwrite,
existing-Lua overwrite; a negative receipt still runs installed byte/sidecar
guards; an old-target witness and original reason survive route failure;
an old target also forces a private negative when a mocked route passes;
and a menu-only negative retains checkpoint scope. These use mocked queue,
file-write and native functions with memory-only data, not Mesen or runtime
state. Real component and Downloads hashes remain unchanged. Metadata and
units use the existing empty bounded helper root/max-files1, outputs0.
