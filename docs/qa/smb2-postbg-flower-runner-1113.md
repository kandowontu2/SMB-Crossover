# Root-only current SMB2 Flower/vegetable runner — November13

Prepared CLI: `tools/audit/run_smb2_postbg_flower_native_1113.py`.
It accepts `--variant 0..7/all`, or a comma-list such as
`--variants 1,2,3,4,5,6,7`, plus `--scope collect/throw/hit`, `--metadata` and
the optional `--followup` or `--ack-followup` control corrections. The control
selectors are mutually exclusive. The two variant selectors are
mutually exclusive; lists preserve order and reject duplicates or values
outside0..7. Omitting both selectors still selects Imajin4.
Only exact installed Downloads12397 is accepted:
`12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52`.
It never constructs or installs a candidate ROM.

The frozen `replay_smb2_postbg_flower_native_1113.py` adapter is authenticated
against SHA256
`04577796b7789175fbf8178ee780f116b82888cfec804d1de16d7a295abce01d`.
That adapter authenticates the unchanged Flower source SHA256
`52f1d6f743b0df158f71123e58a39faa195236d45add1b5b515c34d33c4c4890`.
All eight parent-controller hashes are checked for every scope. The runner
independently reverses only the expected-ROM literal in the resulting text and
checks that same parent hash. By default, original inputs, observers,
assertions, bounds and endpoints remain byte-exact; no failed assertion is
waived.

`--followup` explicitly selects the separate ordinary Flower-left
neutral/predictive horizontal settling correction in
`replay_smb2_flower_control_followup_1113.py`, authenticated against SHA256
`f78b68e72ea531df1e0adae1f6e749e31c7fbe2db6d77fbe7434d2a872654153`.
The runner first applies all default parent guards, then verifies that removing
the helper and reversing its one call change recovers the exact frozen text.
Its result labels the changed controls, records the frozen current-controller
hash, and asserts exact original observers, bounds and other inputs. It does
not describe the changed horizontal controls as original input parity.

## Metadata qualification performed

All24 variant/scope combinations compiled and passed exact parent/adapter hash
guards on actual Downloads12397. Metadata mode wrote zero files and did not
import/call the native execution branch. An additional metadata isolation check
passed with Path text/byte writes, mkdir, subprocess.Popen and the native-case
entry patched to fail immediately if called. No Mesen was launched.

Representative current Imajin4 controller hashes:

- collect: `e5ff3210c06614f2e59bb850f8ae412de6776119fd81458a89ac1a18c1bf01c4`
- throw: `a5d357a820373ea6abf03741c9e60f94f6ee5d3480b9110582bc644d9ede9e4b`
- hit: `5c9e0b7005b1bafc73f660b65de5b675d3966260b8b978b63ec7102f6933e663`

The metadata aggregate prints every requested variant's full current and parent
Lua hashes. These are compilation/source checks, not physical Flower/throw/hit
qualification. No native pass or receipt is claimed by this preparatory task.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --resume --max-files 1 --timeout 180 -- python -B tools/audit/run_smb2_postbg_flower_native_1113.py --variant all --scope hit --metadata
```

The same command was checked for `collect` and `throw`. The helper's existing
unfinished output root retains zero files. No additional output root was made.

The optional correction's eight collect hashes and source qualification are
recorded in `smb2-flower-control-followup-1113.md`. All eight corrected collect
metadata cases passed through this runner, including the explicit1..7 list.
The default Mario controller remains exact b6; corrected Mario remains exact
a463. Isolation passed with Path text/byte writers, mkdir, subprocess.Popen
and `native_case` blocked. The comma-list parser also passed valid ordering and
whitespace cases and rejected empty, duplicate, out-of-range and invalid lists.
This bounded check emitted only stdout: zero files, controller overwrites or
Mesen calls. It did not qualify additional physical variants or throw/hit scopes.

## Native mode: root's single queue only

Root may later run, for example:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/run_smb2_postbg_flower_native_1113.py --variant all --scope collect
```

This native command was **not executed** by the helper. The root-owned existing
component must contain its existing `controller.lua`, with at most the retained
`candidate.nes`. The CLI overwrites only that one existing controller slot.
It hashes and preserves every other retained file and the exact directory
inventory. It never writes a ROM, capture, screenshot, receipt, log or sidecar.
The aggregate distinguishes controller overwrites from new files.

The launch ROM is always the actual
`C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes`, with exact SHA and
nightly sidecar guard before/after each run and the batch. The shared storage
preflight runs before the controller overwrite. Native execution uses only the
existing `run_stdout_mesen_1110.run`: same single queue, capture lease/watchdog,
25GB free-space floor,128MB in-memory stdout bound and existing storage caps.
Its `capture` argument is a monitored path, not a created capture directory.
Timeout is180 seconds per case by default, optionally1..240, preserving the
shared runner's maximum. The outer bounded invocation also caps total duration.

Each completed native case emits a short progress record with variant, pass,
receipt SHA and endpoint. The final compact aggregate includes those receipt
hashes, physical/returned-Main counts, endpoint, mature Flower collection and
native erasure/SFX/popup, earned pull/carry/throw records, projectile contact and
native enemy defeat when requested. No per-frame trace is emitted. The shared
stdout helper hashes the unmodified complete receipt in memory.

An actual failed controller receipt is printed in the aggregate and then fails
the CLI; missing required successful-scope evidence also fails closed. No
capture files, runtime state writes or helpers are admitted. `collect` retains
its60 resumed-update assertion; `throw`/`hit` retain original earned-reserve,
carry/launch or native-defeat and resumed-play assertions.

Only this new CLI and this QA file are owned. Frozen Flower APIs, ROMs, grants,
controllers, root continuation/inventory and user progress remain untouched.
GitHub releases remain empty; no patch or release asset is created.

After Mario's corrected collect pass, root can qualify the other seven without
repeating it:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/run_smb2_postbg_flower_native_1113.py --followup --variants 1,2,3,4,5,6,7 --scope collect
```

The helper never executes this native command. Add `--metadata` and use the
helper's zero-output bounded root for compilation/authentication only. Scope
assertions, strict failure behavior, the actual Downloads SHA/sidecar guards,
queue and file-inventory guards remain unchanged in either control mode.

## Frozen Mario native negative and receipt-only diagnostics

Root's first actual Downloads12397 Flower run81010 is a strict negative before
collection: Mario collect Lua
`b6b10f5db8387b6673efb78749b4dc093ae79b02f82f2129750f70c4c09579ce`,
receipt
`db83087aa20a8b9a0d6de8abf00f9ca5252f827a1a5900956100ce2c4107e5cd`.
It reaches2938 physical/2600 returnedMain, X293/Y176, HP31/both lives, timer292,
then the existing finite-route assertion fails. No pickup/hit/helper/state
write is observed. Other variants were not run because the runner correctly
stopped. This is not a demonstrated ROM or source-physics defect.

The runner now exposes negative-only diagnostics from the existing full receipt:
phase/since/hold, opening, birth/launch, last4 recorded heads/prepares, last8
recent source/state/pad records and last8 phase events. Source VX/VY/Held/Fresh
and all other already-recorded fields are retained. `latest_recorded_source`
is explicitly the latest retained sample, not an invented terminal RAM read.
The Lua, its observers, assertions, frozen52f source and045 adapter are unchanged.
Root can repeat the exact Mario negative to display those previously omitted
fields; no new runtime observer, input, ROM write or diagnostic file is added.

## Optional source-acknowledged throw and hit

`--ack-followup` authenticates the separate factory SHA256
`8846c50a316355f4198471b2cf3d3e62db4b7086c251d88761864d1520f0abc4`.
It supports only `--scope throw` or `hit`; collect is rejected. Its underlying
f78 retreat and f6a enemy-aim factories remain separately hash-pinned and
unchanged. The default and `--followup` preparation functions remain exact.
All original parent hash guards still run before the new text is admitted.

The result labels ordinary B hold/release acknowledgement and, for hit, neutral
aiming with the qualified close-range wait. It retains every original pickup,
reserve, health, collision, defeat and resumed-play assertion, adds a12-update
input acknowledgement bound and a read-only current-ROM-bound original BIT
Fresh observer. On every successful Ack native case, the CLI additionally
requires that observer's actual Fresh64 while Holding is nonzero. A default or
`--followup` pass gains no such new requirement.

Compact evidence now preserves already-recorded target/aim/aim_target and
throw_fresh/throw_input_ack records, including source velocity and input fields.
This parser change adds no observer or input to any frozen controller. Source
qualification and preserved native negatives are in
`smb2-flower-hit-followup-1113.md` and `smb2-flower-ack-followup-1113.md`.
Root owns the actual three Ack positives and remaining native qualification.

Root's next guarded command can skip the already-passed Mario/Luigi cases:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 600 -- python -B tools/audit/run_smb2_postbg_flower_native_1113.py --ack-followup --variants 2,3,4,5,6,7 --scope hit
```

The helper never executes this native command. New selector metadata,
dispatch/isolation and exact frozen/current hash checks passed under the same
zero-output helper root: b6/a463 and priority3824/2bb3 remain exact, selector
order and conflicts are checked, unknown ROMs reject, and existing receipt
fields survive unchanged. Path writers/mkdir, Popen and native entry were
blocked throughout. No controller, ROM, capture or receipt file was written.
