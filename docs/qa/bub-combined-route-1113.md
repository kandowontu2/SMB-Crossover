# Bub/Bob combined performance follow-up, November 13

This is the explicitly composed private candidate
`f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7`,
from unchanged `bub_native_noops_1113.combined_proposal(7ef)`.
Its strict `combined_reverse` reconstructs public
`7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`.
The UI-only e76 and empty-loop-only a77 APIs remain unchanged and separate.
No additional ROM, RAM, CHR storage or helper platform is used.

Root measured both identities in actual Mesen: 48 original source/Main
updates in 76 physical idle frames, versus public7ef's96; 36 walking updates
in64 frames, versus72. Every physical frame polled input; all138 entered,
returned and source updates matched, including71 normal and67 catch-up
returns. This is a material improvement in these windows, not a60Hz or
whole-roster performance claim. The UI-only run retained96/72 frames.
Full native hashes and receipts belong to
[`bub-noops-native-1113.md`](bub-noops-native-1113.md).

`replay_bub_combined_route_1113.controller(raw, identity, mode)` is a pure,
read-only standalone Lua factory; `identity` is0 for Bub and1 for Bob, and
`mode` is `mushroom` or `full11`. It authenticates the complete f88 ROM,
strict inverse7ef, both complete runtime cookies, every a77 hook/body and the
new native UI bytes/getters. It uses the current real title/menu sequence:
Start, Down three times, Right, Select once/twice, Start. It writes only the
controller peripheral and emits a stdout receipt, with no capture files.

Control decisions come from the individually hashed retained November3
actual Downloads controllers. Their compact checkpoint99 receipt SHA256 is
`feb66cc4ec1dbe7929a6c3cff93c054f9b3b1efb5d07b05502a1753aee2a3a7d`.
Only those four existing controller files are read (or their exact members
from the authenticated checkpoint ZIP, in memory, if absent); no
packet/dependency tree is rebuilt or extracted. Current labels, hook mappings and the exact
256-byte native collision-attribute table replace historical bindings.
Diagnostic CSVs/screenshots are removed. The controller retains actual
source cooldown, facing, bubble growth, trap recovery, floor support and
normal-jump tests. It observes both actual GameLoop return contexts.

The source adapter first executes genuine current cold/menu/Start/parser,
then executes the identical Lua gameplay decisions against real6502
Main/NMI. Its scheduler passes and `physical_frames` field are model event
counts, not hardware cadence. No actor, terrain, position, health, source
upgrade, bubble-pool or native item state is supplied.

Source results:

| Identity/run | Matched Main/source | Result |
| --- | ---: | --- |
| Bub natural mushroom |460|One real Goomba trap/pop; one ordinary bump of question block336; immature then mature native actor; native transformation completes with status1/source flags1; X411/Y176, lives2.|
| Bob natural mushroom |460|Same actual item/combat progression, X411/Y176, lives2.|
| Bub full1-1 |5261|Four pipes and three pits,17 natural pops,18 captures,6 earned original bubble rides, flag/castle then25 consecutive living grounded1-2 updates; X40/Y176, lives2.|
| Bob full1-1 |5261|Same full seven-obstacle route,17 pops/18 captures/6 rides, then25 living grounded1-2 updates; X40/Y176, lives2.|

The initial Lua field declaration iterated a Python set. Root's strict
metadata guard caught its process-dependent hash before any route Mesen run.
The field names are now sorted; separate child processes using
`PYTHONHASHSEED=0` and101 produce byte-identical metadata and scripts for all
four cases. Parsed Lua fields equal current native addresses. Reversing this
literal declaration retains exactly the same key/value map and every other
control byte; no controller uses `pairs`, `ipairs` or `next` on that map.
Full-route CPU runs above preceded this declaration-order correction; their
gameplay decisions, addresses and control bodies are unchanged. Both corrected
mushroom scripts additionally pass real CPU Main/NMI:460 matched entered,
returned and source updates, one genuine trap/pop and question-block bump,
completed native transformation/status1/source flags1, X411/Y176 and lives2.

Frozen deterministic standalone Lua SHA256:

| Identity | Mushroom | Full1-1 |
| --- | --- | --- |
| Bub |`f848ad7065ecf9a026eeb98b4cc9d12c88231afcadf53bbe6a6d4fc55194c3eb`|`1c764ce0e76923816e6d0d1a079ab6b8549ebfefd41cda00764fc9fa5c2f059b`|
| Bob |`e631b0e6c42825f4ba608a3fb6f166213ed3680f8a592e4f975c7ed65163b2a5`|`1d60813d2910cd143ea73e2783c578c428fdbcd0354420d03b2ce3b236daac86`|

The mushroom and full-stage routes are separate runs. The full-stage run
uses the unpowered retained route; it does not imply a mushroom-powered
full-stage or natural flower/Star/1UP pass. The last pit uses two genuine
supported original jumps, with actual left/right native foot support
observed at the source jump entry. No helper is added, so the helper-platform
inventory has no new affected name or location.

Separate declared forced-blank cold fixtures pass full code readback and
both complete-cookie publication; warm calls neither copy nor read CHR.
Code/helper readback faults and WRAM protection reject, all32 individual
header corruptions reject,22 genuine busy-NMI cuts preserve the cold frame,
and retirement is repeatable. Minimum foreground SP187 (protected189).
The current compact retire entry is AE0A, explicitly bound by its compiled
PHP/PHA entry window. Reusing the old v97 harness's AE0B skipped PHP and
produced a fixture failure; this was a stale test address, not a game defect.
Fault/header tests are explicit fixtures and are not called natural gameplay.

Combined foreign comparisons pass for Mini Mario, Getsu Fuma, Sonic,
Super Sonic, Donkey Kong Jr, Excitebike, Prince, Jay McCray and Steve Hermann.
Each uses genuine menu/Start/cold construction and60 opening updates, then32
additional ordinary controller Main/NMI updates. Complete AXYP/SP, native
and source RAM, live stack, SMC and maps equal actual public7ef. DK Jr saves
1,175 cycles per sampled Main and Prince1,264; the other seven save0 in
these samples. This is nine specific opening/regression contexts, not all
foreign gameplay or full-stage qualification. Jay/Steve rows are discovered
through the actual current menu inventory, with no guessed historical slot.

The previous frozen UI/source-loop ABI, mixed-slot, caller-liveness
and IRQ gates retain their exact scope in `bub-native-noops-1113.md` and
`bub-empty-loop-probe-1113.md`. Neither native cadence nor the source route
results replace the required root-owned current physical routes and regressions.

All producers run through `run_bounded_build_v1.py --output
build/prince-pickup-reach-1112 --max-files 1`, with zero generated output files.
This helper launches no Mesen and writes no ROM, root controller, Downloads
file, release or patch asset. Root owns any later local nightly delivery;
GitHub releases remain empty under the user's current policy.

Reproduce bindings with `--bindings`, current cold fixtures with `--cold`,
and combined foreign Main comparisons with `--foreign`. Use
`--cpu --identity 0|1 --mode mushroom|full11` for the real controller routes.
No output directory or receipt file is created by any mode.
