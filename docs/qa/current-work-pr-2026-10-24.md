# Current QA source, integrated MMC3 tools and native qualification

The goal remains ACTIVE and incomplete. The latest user message is “ty”; the
Kirby ability video is already delivered. Continue the authorized final repair,
all-character1-1 and every-powerup/use/graphics/performance work. Do not create
another goal or claim completion. No subagents were started in this continuation.

## Authoritative working source — QA adopted

Current expanded MMC5 ROM SHA256:
`054d9e33a84f628947b0dea15914ba2aae7796ca610a25548eab96407064384a`.

- Adoption: `build/verification/native-probes-qa/proof.json`.
- Checkpoint: `build/checkpoints/native-probes-qa/checkpoint.json`, which points
  to the external ROM/debug/source packet to preserve the30GB workspace cap.
- NEVER rerun D/`adopt_native_probes_qa_v3_once.py`: it already succeeded.
- P/`packet-current-v3/source.zip` contains1220 current source files, SHA256
  `b7a21ffcf8bae37d05644892d2202ed5e2e17f91d3b875cf9ba24b1ff4fec58f`.
  Its actual source rebuild reproduces expanded MMC5 and both unchanged
  ordinary flag-off binaries. Root files exactly matched that catalog at adoption.

External evidence roots:

- D = `C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py`
- P = D/`native-probes-qa-v2`
- Q = `C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-head-pz`

Only `src/characters.s` and `src/megaman_weapons.s` changed in this game-code
adoption:54 ROM bytes, existing fixed spans in resident banks126/127, no RAM,
CHR or OAM added and existing exported PCs retained. Head selectors0/1 and
side selectors0..10 reach the SAME ordinary native query more directly.
Other source-family gates remain complete. This is a CPU reduction, not a
new geometry/movement/music rule or a claim that all lag is solved.

The parent PZ ROM is still retained at
`build/checkpoints/native-head-pz/candidate.nes`, SHA256
`675c57f4abd94d51d0f48a54f0a1d661ed75ef18b153de32a29d94145ba1d47d`.
NEVER rerun its successful `adopt_ryu_head_pz_once.py` either.

Public ROMs and the NU guide remain unchanged. No final release was installed.
Working source and separately qualified private builds are current; do not
accidentally test an older public ROM. Adoption checked29,995,665,929 occupied
bytes before1064 source bytes and small receipts. Large captures/builds stay
external. Preserve lossless evidence and do not reset the dirty tree.

## Current exact-ROM native verification

P/`full-roster-aggregate-v1/proof.json` PASSES:38 independently replayed,
zero-death1-1 cases cover all37 identities, with Ryu in both modes. Other
identities use their stated selected modes. Every actual PPU frame is retained
losslessly, indexed and checked against RGB/PNG hashes; saved inputs and CPU
traces replay exactly. Original world-motion<=8, camera0..4, CHR and visible
scanline31 bounds are unchanged. Source-owned temporary query origins require
their separate read-only native guards, never a blanket waiver.

Its five exact-hash parent batches are all complete and passed:

- `direct-v1/proof.json`: Mega,Proto,Samus,Bill (4).
- `remaining-direct-v1/proof.json`:27 other selected cases, including Ryu both modes.
- `corrected-direct-v1/proof.json`: Donatello,Scrooge,Link,Dale (4).
- `gap-direct-v1/proof.json`: BassHard (1).
- `landing-direct-v1/proof.json`: Simon,Chip (2).

Use each row's `guarded_review` when present; raw rejected reviews remain
retained. All27 earlier successful discoveries now have physical replays.
Seven initial failed discoveries remain in `remaining-roster-v1`; nothing was
relabeled. Subsequent controller-only corrections addressed actual witnesses:
Scrooge waited on the last brick while the mushroom escaped; Link's old
limit ended shortly before movable1-2; Dale/Donatello/Bass missed native
landings; Simon needed an earlier genuine air jump to descend onto the last
step; Chip needed to jump from the actual pipe edge. The game supplied all
motion, health, item actors and supports. Failed retries remain in correctionsv1..v4.

P/`items-v1/proof.json` PASSES all26 scoped native cases:144 actual item
actors,44 health/star/life actors and28 Kirby copy/mode lifecycles. This is
not complete legacy weapon-use/refill/damage/expiry/SFX/source fidelity.
P/`entry-v1/results.json` passes all37 actual cold controller entries.
P/`guards-v1/proof.json` passes the four complete legacy native NMI/bank/SMC/
stack routes. CPU tests pass33,696 Mega/Proto and4,104 other-selector actual
query differentials, preserving registers/flags/application writes/final banks
with declared stack/farcall-bookkeeping exclusions.

Human sampled overviews inspected in this continuation: Simon,Bass,Chip,
Donatello,Scrooge,Link,Dale. Chip's suspicious white streak at2087 was checked
against neighbouring actual PPU frames2080/2083/2089/2094 and actual OAM:
it is the narrow edge phase of the ordinary spinning block coin, not a new
artifact. This does NOT claim exhaustive human inspection of every frame.

P/`background-v1/proof.json` is COMPLETE: all38 verified streams,
188,756 actual PPU PNGs,132,670 eligible adjacent triples, zero candidates.
It only tests same-before/after middle-frame background clusters with original
sprite/border masks. Persistent/longer defects, sprite omissions and source
fidelity remain outside its scope. Any candidate requires investigation.

P/`legacy-inventory-cpu-v1/proof.json` passes118,272 actual public ownership
queries and22,528 spending cases on the current exact ROM, both modes and
linked item/ammo pool oracles. These are explicitly seeded CPU component
tests; they do not substitute for physical legacy pickup/use/refill scenes.
P/`post-adoption-integrity-v1.json` rechecks all1220 current source files and
all four unchanged public ROMs, with29,995,670,936 workspace bytes.

## Performance evidence and limits

P/`profile-v1/proof.json` is an exact read-only full Mega replay with matching
input/CPU/render/OAM/CHR/scroll/actual hardware audio. Source baseline is
Q/`profile-megaman-v5/proof.json`. Function medians in those DIFFERENT adaptive
routes: head616→137cycles,side314→146, BGcollision2729→1578,
player5486→4335, GameLoop23426.5→22175. Do not turn these into a controlled
FPS claim. Adaptive Samus skipped-NMI count increased1661→1721 while physical
route length fell4226→4162; the candidate is not universally faster.

P/`matched-benchmark-v2/proof.json` and
`full-roster-aggregate-v1/matched-comparison.json` pass eight STAGED native
fixtures: stationary Mega/Samus/Bill/Raphael in the same three-initialized-
Goomba setup, original audio enabled,1200 physical frames per version.
Actors are explicitly reset at native GameLoop boundaries; never call this
a controller-only campaign. Mean GameLoop cycles PZ→QA:

- Mega21584.84→20433.84, logical1199→1199, skipped NMI600→600.
- Samus22930.09→22270.09, logical1200→1200, skipped0→0.
- Bill22942.77→22292.44, logical1200→1200, skipped600→599.
- Raphael22643.45→22759.45, logical1198→1198, skipped3→3.

Raphael's116-cycle overhead is the preserved owning-family fallback. Separate
native draw-skip classes are recorded because mixed normal/catch-up work can
shift medians. These scenes show CPU savings for legacy families but no material
throughput gain. Do not claim constant60Hz, universal lag removal or measured
display-FPS gains. Earlier benchmarkv1 failed Lua string generation before
gameplay; v2 fixed the harness. No game-code failure was waived.

Native Mega/MM2 audio ZP swapping was already unrolled before this change.
Do not disable original music or reimplement that old optimization. Never
introduce foreground shared-farcall SMC into NMI.

## Oversized MMC3 — qualified ship fixes adopted in root preparation

Canonical current candidate SHA256:
`09c5ced7680c303f07ff9ad4655e56300d63c99eab90b4dafcf61938d75fd45c`.
Actual ROM is2,097,168bytes,2MiB PRG/256KiB CHR-RAM. It is externally at
D/`mmc3-ship-lives-v25/canonical-build/smb-crossover-mmc3-oversized.nes`.
Root receipt `build/verification/mmc3-ships-current-v25/proof.json` and
checkpoint `build/checkpoints/mmc3-ships-v25/checkpoint.json` are authoritative.
NEVER rerun successful D/`adopt_mmc3_ship_v25_once.py`.

Only `tools/mmc3_oversized/repairs.json` changed in this adoption; all game
source/MMC5 bytes and the four public ROMs remain unchanged. Root recipe SHA256
`29815141274a2a2e2c39108c7cde0c3568cf0c02840fafbfde00b6517eb071c9`.
Root preparation/build tools retain `--source-root`, `--output` and external
`--output-dir` support. Fresh canonical root build exactly reproduced the
physically tested09c5... candidate.

Current complete1220-file source/build catalog is now frozen in
D/`mmc3-ship-lives-v25/source-packet-v1/source.zip`, SHA256
`8939f66994a80d1ee1002da6471e6468d8a55b118181935d114215332310f016`.
P/`packet-current-v3` remains the historical pre-MMC3-recipe QA catalog; the
game source still matches it, but its old recipe is no longer root-current.
Do not mistake an old431... build or receipt for current mapper qualification.

The three mapper-specific repairs are:

- Scripted ship pole contact retains its anchored X. The parent right-edge
  clamp rewrote3161→3151 and lost climbing state, freezing at the flag.
- Ship5c and5d state occupy distinct existing inactive Contra/Zelda audio
  pages. The old map aliased native PnType/VvObjY and PnX/VvObjX, causing a
  first-update201-pixel displacement. Actual linked RgAudioRam=$6f3d,
  PnType=$6f3d,PnX=$6f75,VvObjY=$703d,VvObjX=$707d,VvHeld=$7120.
  Gradius native audio owns separate XgLzHistory=$7400; it is untouched.
- Lives portraits run the existing tagged auxiliary OAM resolver after
  drawing, as ordinary gameplay does. This restores complete Octopus,
  TwinBee and Pentarou portraits. No new RAM/CHR or movement constants.

Exact current D/`mmc3-ship-lives-v25` proofs all PASS:

- `cold-entries-v1`:37 actual cold selections/alternates,140 native frames,
  full262144-byte boot CHR, VBlank/protected-byte cache and NMI/bank/SMC checks.
  All37 additional completed-loop motion JSONs pass>30 actual committed
  updates with world<=8/camera0..4, including first gameplay update.
- `native-routes-v1`:four fresh ship1-1 discoveries with zero deaths and
  native mapper guards; every max world step2, camera0..1.
- `direct-v1`:four independent exact-input/CPU-trace replays into movable1-2,
  every actual PPU frame/RGB/PNG/index/gzip verified, strict motion and visible
  scanline31/actualIRQbank254 guards. Human overview/start/pole review is
  sampled. Octopus's early five-frame screenshot can still be loading black;
  stable lives frames408/432/456 and independent physical replay show it whole.

Retain V23 flag-fix and V24 state-fix failures/proofs. V24's four native routes
and replays plus37entries passed, but its broken lives portraits were caught
visually; V25 is the accepted current recipe. Native observer-v1/v2 failed on
missing helper alias/flat emulator-state keys, then read-only v3 exposed the
correct direct body bank and missing tagged-OAM resolution. These were harness
errors, never rewritten as gameplay passes.

Heavy read-only observers use the identical-binary private Mesen at
D/`mmc3-flag-fix-v23/script-budget-probe-v2/emulator/Mesen.exe`, with only
portable ScriptTimeout=5. The1.3second pure-host probe proves its actual
watchdog difference; CLI budget overrides did not work. No emulated clocks,
ROM/controller/frame bounds or global emulator settings changed. Two native
Mesen workers maximum.

## Additional current MMC5 native inventory work

P/`legacy-physical-summary-v1/proof.json` PASSES ten Hard identities:
MegaMan,ProtoMan,Bass,Samus,Bill,Lance,Link,Simon,Ryu,Sophia.
86 mature item actors were physically collected with exact ownership/exclusivity,
and 51 explicitly declared source attacks were observed under controller input.
Each arena is fully staged only at a guarded actual GameLoop entry; no hot
mid-actor activation or injected inventory flags. Native mushroom animations
must finish before asserting powered state. Passive upgrades have acquisition
coverage; their complete behaviors are separate.

Successful frozen scenes: `legacy-native-items-pilot-v2` Mega;
`legacy-native-items-batch-v2` Proto/Bass/Samus/Bill/Lance/Link/Ryu;
`legacy-native-items-corrections-v3` Simon/Sophia. The original batch's two
failures are retained: Simon lacked hearts before the stopwatch; Sophia had
no live homing target. V3 adds actual private large-heart pickup/refill and
a fully initialized native live target, preserving the attack assertions.
Pilotv1 asserted PlayerStatus before the native transformation finished;
v2 waits for that actual readiness without weakening final powered state.

This is not random question-block emergence, full natural reward delivery,
all-ability/SFX/audio fidelity or every-frame graphics review. It complements
the retained CPU inventory matrix and existing26 current native item scenes.

## Live work and remaining requirements

Exec15527 is live: D/`run_mmc3_remaining_routes_v25.py`, writing
D/`mmc3-ship-lives-v25/remaining-routes-v1`. It runs the remaining34 exact
selected roster/mode cases from current MMC5's38-case aggregate against the
current MMC3 candidate with native mapper guards. New failures need actual
witnesses; no final all-roster mapper pass is claimed. Four ship cases are
already independently verified above. At17cases, Luigi and Mac died and Sophia
hit the16000-frame bound at1616/144. Do not convert these to passes. Sophia's
state/NMI activity appears frozen after brick combat; exec28132 runs the
read-only exact-input D/`observe_mmc3_sophia_stall_v25.py`, output
D/`mmc3-ship-lives-v25/sophia-stall-v1`. It deliberately stops on a bounded
debug witness and cannot produce a campaign pass. Two Mesen workers maximum.

Sophia's read-only stall witness is now terminal and confirms90physical frames
without a completed loop at2621, PC$0194. The separate
`sophia-stack-writer-v1/proof.json` observes the FIRST immutable bank-return
PLA at$017c overwritten104→49 at2533, native SP$7c, latest InventorySupported
entry SP$A0 at2532. This is real stack/code overlap, not just slow progression.
The runtime RAM dump shows return-stack words replacing the SMC bank-return
tail. InventorySupported's unrelated family gate chain is the immediate path.

Private D/`mmc3-sophia-stack-v26/candidate.nes` SHA256
`467c3fac231f6628b90fe791a787a8aa2861f861190552708ebf7cf19a3f50a0`
compiled a14-byte Sophia-only direct support result but FAILED the isolated
predicate differential: the old outer farcall reloads ID11, clearing Z, while
the attempted final CPX set Z. Retain it as rejected; no root adoption.
Exec49212 builds D/`mmc3-sophia-stack-v27`, replacing that CPX with SEC/NOP
to preserve the actual native N/Z/C return. It remains unqualified and private.
The complete raw-ID/mode/alternate/flag/register/application/bank differential
must pass before replaying the unchanged failing Sophia input. Root recipe
and its current accepted candidate remain09c5...; public builds are unchanged.

V27 CPU differential PASSES1752cases/64Sophia cases, saving576..588cycles and
12stack bytes for Sophia, adding4cycles to other IDs. SHA256
`ad90ce9a0754ee92418374ef6f553255fd32e6ea5ff8f81384e82dfe1898ce92`.
All37 cold entries and committed-motion checks pass with the NEW complete
49-byte opcode guard. BUT V27 native qualification FAILS: the retained physical
input prefix dies at2469 before its intended regression point, and a fresh
adaptive run reaches1474/x699 then the stronger guard catches immutable RTS
$0185 overwritten at native SP$85, PC$C85A during Sophia audio. Twelve freed
bytes are insufficient. No V27 adoption or freeze-fix claim. Those failures,
including full49-byte guards, remain under `native-sophia-v1`.

All jobs above are now terminal, including15527,28132,46360,49212,55385,84668.
The remaining34-route V25 sweep completed with25clears and9failures: Luigi,
Mac,Grant,Rygar,Link,Simon,Chip Easy and DaleHard died; SophiaEasy froze.
Its aggregate remains failed; ship4 independently pass on the same V25 hash.
The three raw borrowed-origin traces have specific positive observations above.

Private next direction: remove executable bank-switch code from the hardware
stack area. D/`build_mmc3_static_call_v29.py` is currently compiling (see its
tool session, not a native emulator job). It stages a resident LOWCODE bank
dispatcher plus a five-byte LDA/JMP trampoline and one return byte in the actual
six-byte SRAM alignment gap$73fa..73ff, after Z2UiState$73f9 and before
XgLzHistory$7400. NextBank reuses its existing reserved$013f cell; all five named
operand aliases are retained. No physics or extra board RAM/CHR. The original
49-byte A-bank load span is padded; only6bytes are copied at boot. Candidate
must still prove gap ownership, including history lookbehind/native audio,
bank/flag/register/NMI/IRQ/rare-call ABI, stack margin and full native gameplay.
Existing33-byte shared-SMC observers MUST be adapted to the five explicit
payload aliases and actual new code extent, since blindly reading past tiny
code would include the audio history. Preserve all original behavior bounds.

V28 compilation failed because its source replacement accidentally removed
three appended resident helper definitions from prepared mmc3.s. V29 narrows
the replacement through FarCallCommon's first final RTS and preserves the
appended helpers. V28 is retained as a tool failure, never a ROM/behavior pass.
No architectural candidate has been adopted; root remains qualified09c5... .

V29 also failed compilation: adding the49-byte dispatcher to LOWCODE would
overflow PRGLow by24bytes (only25free). V30 now compiles via exec70309,
D/`build_mmc3_static_call_v30.py`, output D/`mmc3-static-call-v30`. It reuses
the unreachable48-byte CrossoverPatchStatusName tail for a49-byte static
dispatcher; one unreachable side-query NOP is removed and that wrapper grows
66→67, keeping subsequent FIXED/DPCM/tail layout balanced. The original
status name still tail-jumps to RlNameDispatch. This is staged, not qualified.

Inspection of actual generated V29 confirms SIX copied bytes already:
LDA#param/JMP target(5) plus private return byte$73ff,
SafereturnA_SMC=M3FarReturn-1. It does NOT alias `safecall_a`; that earlier
possibility was considered and rejected. NextBank reuses reserved$013f.
Root's explicit NextBank source users are only the old SMC operand macros.
Audit raw native audio/history accesses before accepting the alignment gap.

For a six-byte copy, use43 ROM padding bytes to preserve the old49-byte A-bank
load span (five-byte version used44). All named aliases must be compatible with
SMC_Store/LoadValue/LowByte/HighByte and source firebar backup/restore wrappers.
The LDA/JMP trampoline enters the target with the same A/X/Y/P/SP and return
stack depth as the old LDA/JSR, at a different return PC; don't introduce a
second nested JSR. Resident code and the tiny executable bytes need guards;
the five payload fields need explicit NMI preservation checks. No expansion
of physical board RAM or use of $5000..$5fff is authorized by this proposal.

Next CPU check can adapt `check_mmc3_sophia_support_v27.py` to the new static
candidate. Its Memory model implements actual MMC3 bank selector6/7 and copies
the actual SMCCODE segment. Exclude only the newly owned tiny code/payload
region in application RAM comparison, retaining A/X/Y/flags/SP/nonbank I/O/
final physical bank checks and other application RAM. Also check the actual
farcall ABI itself, nested calls and native IRQ/NMI before full playthroughs.
Do not weaken raw motion/PPU/guard assertions or mark any failed run passed.

V30 failed compilation in PRGA03, and the placement was architecturally wrong:
CrossoverPatchStatusName is BANKED bank3, NOT resident. Never use that padding
for a routine that changes the A-window bank. V28/V29/V30 have no passing ROM.
The actual resident catalogue is D/`mmc3-resident-scopes-v25.json`, produced
from actual linked bank/size metadata. Always verify physical banks first.

The useful resident slot is MegaManResetBlockHealth atFE:$9031,92bytes. Its
leaf body uses RAM buffers only; it ends by PLA/restoring A and its N/Z. A
BillRareCall trampoline can preserve the original selector/flags, with both
cold leaf returns routed through BillNativeCaptureP. Keep the old92-byte slot:
18-byte trampoline +49-byte static FarCallCommon +25unreachable padding.
This frees hardware stack code while preserving every later LOWCODE PC.
Moving this parser cell-reset body adds bank-call work during column parsing;
its complete RAM/A/X/Y/flags/bank and IRQ ABI must be compared, and measure
performance honestly. Do not just assume those flags from the returned A.

V31/V32 stopped before preparation: there are no completely unused8KiB ROM
banks in228..253. E7..F6 contain packed music; FD contains native Gradius audio.
Do not overwrite those banks. V33 instead appends the96-byte cold reset body
in the actual FF tail after the unchanged VIC_NATIVE_AUDIO segment in FD. The
builder asserts tail room/FF bytes and appends its segment after the existing
definitions, preserving the original driver's bytes/addresses. Original
Gradius/audio read bounds and native audio equivalence still require checks.

Only compiler exec43121 is currently live: D/`build_mmc3_static_call_v33.py`
→ D/`mmc3-static-call-v33`. All Mesen workers and prior compiler jobs are
terminal. No architectural candidate has yet passed compilation/native
qualification or been adopted. Root recipe remains298151.../ROM09c5...;
MMC5 remains054d... and all public ROMs/guide remain unchanged.

D/`mmc3-ship-lives-v25/borrowed-motion-v2/proof.json` PASSES Proto/Bill/Lance
with byte-identical original inputs/trace, actual completed-loop and body-draw
guards. Raw endFrame samples at2197,2841,2865/4880 are positively identified
as the actual tagged block probe, with saved body origin near the previous
draw. Every adjacent completed native update remains world<=2, camera0..3,
and drawing never consumes a borrowed origin. This is specific read-only
state evidence, not a general waiver or independent pixel replay. V1 failed
before gameplay because its screenshot output subfolder was missing; retained.

Exec96989 and27126 are terminal. P/`legacy-physical-direct-v1/proof.json`
PASSES all ten independent frozen inventory scenes:11410 actual PPU frames,
2,804,395,440 raw bytes retained losslessly as verified gzip, every RGB/PNG and
frame index checked. Original pickup timing, exact ownership and declared
attack results reproduce exactly. Native NMI/SMC/bank guards pass. Human
overview review sampled all ten; no obvious corruption found in those samples.
This does not establish every-frame subjective review, precise SFX/source-art
fidelity or all passive behaviors.

All V23/V24 jobs, V25 entries/discoveries/replays/tool adoption, inventory
pilot/batch/correction jobs are terminal. Do not rerun fresh-output folders
or successful one-shot adopters. Public ROMs/guide remain unchanged.

Next: independently retain/review physical inventory frames and exercise
remaining passive/special/refill/damage/expiry/audio paths; finish current-hash
MMC3 full roster/campaign/item/music/overload/source-fidelity qualification.
Both-mode/shortcut campaigns and physical hardware remain separate. Keep the
workspace under30GB; all large new builds/captures/source packets stay external.
Preserve lossless captures and rejected candidates. Do not disable native music,
replace source physics or introduce shared foreground farcall SMC into NMI.

Kirby's already-delivered1:40 video remains
`C:/Users/kando/Videos/SMB-Crossover-Kirby-Abilities.mp4`, SHA256
`0529a886ea6f4222921560d43f50d3a270890a994cfdcf36eaced5494c07d213`.
Native PY pixels/PCM,14copies,six base scenes and recovery/pickups, declared
staging and one labelled half-speed scene. Do not redo or relabel it QA.

## Current build handoff and static dispatcher follow-up

The user's current-build request was fulfilled with a byte-verified copy at
`C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes`, SHA256
`054d9e33a84f628947b0dea15914ba2aae7796ca610a25548eab96407064384a`.
This is P/candidate.nes, not an unqualified MMC3 architectural experiment.

V33 failed its assembly-time variable padding expression. V34 compiles as
`d55f376e1e5f9100276b5257457edf2eeb6413cc6f11d6360f016f07f24b72d1`,
but the relocated cell-reset leaf failed CPU ABI: BillRareCallCommon requires
each cold target to publish its output selector. V35 checker output retains
the failure in V34/abi-cpu-v2.log: input shadow64 wrongly returned0.
V36 adds the original cold-call selector/flags capture protocol and passes
5,784 isolated CPU comparisons (1,752 inventory predicates,4,032 cell resets),
ROM46459fed3e742573fab2e56615113ebb5bd22fd8bbc683a7a48adee33a8eab32.

CRITICAL: V34/V36 SRAM allocation is REJECTED despite CPU ABI success.
The six bytes73fa..73ff are explicit fixed aliases Z2AttackStage/Timer,
Z2PreviousButtons/CachedPose/Scratch/Scratch2 in zelda2_link_state.inc.
Only Z2UiState/Variant were exported; checking just exported labels wrongly
suggested a gap. No native test or adoption of that overlapping allocation.
These are never user builds. Root source/recipe/public ROMs remain unchanged.

V37 now compiles via D/build_mmc3_static_call_v37.py (exec7378): resident
49-byte common dispatcher, six-byte tiny LDA/JMP/private-return region at
the ORIGINAL stack-page base0155..015a, leaving42 more bytes of downward
stack headroom than the original49-byte code. NextBank still uses reserved
013f, all five source operand aliases are retained. This is not complete
removal of stack-page code. Guard the actual six bytes and require native
stack SP>=5b; preserve all five payloads across native NMI/IRQ. All character
state addresses, notably Zelda II73fa..73ff, must stay unchanged. Native
Sophiа stress, cold roster, full campaigns/audio/timing remain unqualified.
No successful one-shot adopter should be rerun. MMC5 stays054d... .

V37 compiles as20b9f314443db1b05a205517d27e23abb4219774f2fa255dd972b2d275e2f55d.
Its abi-cpu-v1 passes all5,784 exact comparisons, and cold-entries-v1 passes
all37 actual controller selections, native140-frame movement, complete boot
CHR, NMI/banks/cache and completed-loop displacement guards. Tiny code now
uses the original stack-page base0155..015a, never Zelda II state.
V39 removes the unused misleading M3_CALL_RAM memory declaration left in the
private V37 cfg; complete ROM bytes are IDENTICAL to V37. Future recipe/source
adoption should use the clean V39 packet, not the dead declaration.

V37/native-sophia-v2 passes a fresh zero-death1-1 clear in5,667 physical frames.
Read-only guards observe374,276 resident calls and3,703,152 native stack writes,
minimum SP131 vs protected floor91. Complete six-byte code and explicit five
SMC payloads survive native NMI; no source audio/physics/gameplay writes.
V1's host observer was aborted: emu.getState on every stack write was too slow.
Its retained aborted-host-observer.json explains V2: record actual stack-write
addresses directly and enforce the same bounds, with no emulated timing change.

V37/direct-sophia-v1/direct-sophia-easy/proof.json independently reproduces
the complete original input/CPU trace and5,467 actual PPU frames, every RGB/PNG,
frame index and1,343,701,128 raw bytes retained as verified lossless gzip.
Its native tiny/stack/cache guards pass and all15,368 visible scroll writes
are scanline31/actual bank254. HOWEVER the enclosing generic raw-X motion
review rejected five temporary origins at1904,2196,2519,3793,3853; retain that
failure, never turn it into a generic raw-origin waiver. A new exact read-only
query/body-draw/completed-loop witness is running before positive admission.
Independent capture success alone is not a full graphics/campaign pass.

Current live work: exec58976 D/run_mmc3_roster_v37.py writes V37/full-roster-v1
(all38 selected cases, strict completed-loop plus native tiny/stack/cache/NMI
guards; raw physical origins retained separately). Early Mega/Proto/Bill/
Mario/Luigi clear; Samus falls into the gap aroundX2477, retained for diagnosis.
Exec from D/observe_mmc3_borrowed_sophia_v37.py writes V37/borrowed-sophia-v1.
All earlier compiler/CPU/cold-entry/Sophia discovery/capture jobs are terminal.
Root recipe remains298151.../accepted MMC3 ROM09c5...; architectural20b9...
is private and not adopted. MMC5 user download remains054d... .

V37/borrowed-sophia-v1 PASSES the specific five query frames1904,2196,2519,
3793,3853 with byte-identical original inputs/trace. Actual MmBlockAttack=1,
rawX/Y equals actual probeX/Y, saved body stays within8px of preceding draw,
and drawing never consumes a borrowed origin. All2,306 completed updates have
maxworld2 and camera0..3. V37/sophia-review-v1/proof.json binds that positive
evidence to the existing independent direct pixels, identifies EVERY one of
the ten outgoing/incoming raw spikes, and retains the generic review failure.
Human reviewed overview, all five three-frame probe sheets, stable lives/
startup/pole sheets; no obvious terrain or whole-screen displacement in these
samples. Some crowded sprite rows drop individual tiles; this is not complete
OAM/source-art/SFX certification. sophia-background-v1 scans all5,467 indexed
PNGs,3,861 eligible triples,zero transient candidates, with its narrow limits.

V39/layout-v2/proof.json PASSES1,163 original RAM labels unchanged outside the
explicit moved SMC code/operands; all Zelda II alias source bytes unchanged,
complete5,925-byte original native Gradius driver segment unchanged, original
CHR exact, resident/common and cold parser banks checked. V1 incorrectly
included intentionally relocated SMC operand labels in its unchanged-data
list; failure retained. V2 excludes only the original SMCCODE segment and
checks all five relocated operand aliases explicitly. Isolated cycle costs:
inventory predicate+0..28 cycles, EVERY relocated parser cell-reset+230cycles.
This is a real performance cost: benchmark native parsing before adopting;
do not present stack repair as a general lag improvement.

Possible follow-up for that cost, NOT IMPLEMENTED: the resident51-byte
BillNativeReadWarp slot could hold49-byte static common+2pad. Its existing
public warp-read entry could move to the25-byte free LOWCODE tail as18-byte
BillRareCall, with a cold read body in the verified FD tail. That would keep
hot MegaManResetBlockHealth92-byte body unchanged and move the exceptional
warp read instead. Preserve exact selector71/A/X/Y/P, and table semantics;
copy/verify the full original256-byte indexed source window if rawX parity
is required (actual native warp indices0..10). Check tail room and native
Gradius read bounds; no whole ROM bank is unused. This would change ROM hash
and require fresh native qualification, not relabel existing20b9 evidence.

Samus controller-corrections-v1 PASSES native1-1 in7,268frames,zero deaths,
unchanged20b9ROM and all guards. Original bot spent its jump before the stair
gap; the first samus-gap-v1 correction then blocked itself at the next riser
and timed out at2401. Both failures retained. Successful correction lands
on the existing higher stair around2400 and launches with normal controller
input; no physics or map writes. Independent replay remains outstanding.

Darkwing's long-A correction FAILED and is retained. Source explicitly has a
50px original jump and uses its Arrow/hanging toolkit for tall64px pipes;
holding A cannot replace that traversal. Original failed recovery-controls
shows a real Arrow adaptor2/gas10/mode1, but no ammo consumption. The original
Arrow controller pulses B for ONE physical poll at the apex, which may miss a
lagging logical update. Exec76931 D/run_mmc3_darkwing_arrow_v37.py now preserves
the original controller/toolkit and holds that trigger8physical polls, writing
V37/darkwing-arrow-v1. This is still a hypothesis/test, not a proven cause/fix.

Exec58976 full-roster-v1 remains live (24cases completed at last snapshot;
Samus/Darkwing/Mac failures retained; corrected Samus separately passes).
All other V37/V39 compile/CPU/layout/cold-entry/Sophia capture/review/scan and
the two-case controller-corrections-v1 jobs are terminal. Two project Mesen
workers max. User's separately opened Downloads MMC5 Mesen is NOT ours to stop.
Workspace measured29,995,704,213bytes before these small notes; all large
evidence stays external and lossless captures are preserved. Current source/
recipe/public builds remain unchanged; download054d... verified in Downloads.

The Darkwing8-poll Arrow test PASSES native zero-death1-1 in7,000frames,
V37/darkwing-arrow-v1/proof.json. Original Arrow recovery/pickup, normal50px
jump and hanging toolkit remain intact; actual gas decreases and the player
passes both tall pipes. All native tiny/stack/NMI/cache and committed-motion
guards pass. This supports the controller pulse timing explanation; it is
not a ROM physics change. Mac also PASSES after holding each requested A
press for at least8polls (preserving longer holds): V37/mac-jump-v1/proof.json,
5,047frames,zero deaths, all guards. Independent physical replays of these
new input streams and corrected Samus are still outstanding.

At last snapshot full-roster-v1 has33/38 attempts finished, retaining four
original failures Samus/Darkwing/Mac/Grant. The first three now have separate
current-hash native clears above; do not overwrite their failed original rows.
Grant died at the second gapX1394. Exec6158 D/run_mmc3_grant_jump_v37.py tests
the same minimum8-poll A hold on Grant, output V37/grant-jump-v1. Only this
and exec58976 full-roster-v1 are project Mesen jobs still live; earlier
Mac/Darkwing/correction/capture/scan/CPU/compiler jobs are terminal. No public
or Downloads ROM was replaced with20b9. MMC5 download remains054d... .

Grant's minimum8-poll A controller also PASSES: V37/grant-jump-v1/proof.json,
5,990physicalframes,zero deaths and all native code/stack/NMI/cache/motion
guards. That job is now terminal. Full-roster-v1 is the sole remaining
project Mesen job,35/38 attempts finished at the latest snapshot. All four
initial failures now have separate native corrected-input clears, which
still need independent replay/visual admission. Next assemble exact current-
hash roster evidence without dropping failed originals; continue remaining
all-item/passive/audio/performance checks. Do not adopt or release20b9 merely
because discovery coverage finishes; retain the parser+230cycle concern.

GitHub checkpoint3720c8f was pushed to master with current source/guide/tests,
a coherent CLAUDE-HANDOFF-2026-10-24.txt and frozen external tools/proofs. The
user explicitly requests all subsequent coherent changes committed/pushed.
V37 full-roster-v1 is TERMINAL:38 attempts,32 clears,six original failures.
Samus/Darkwing/Mac/Grant have separate corrected-input native clears. ChipEasy
and DaleHard retain real13px committed displacements; no bound was relaxed.

Chip exact failed-input observer chip-collision-v2 reproduces identical trace
and input bytes. First wrong horizontal write is bank10/$A2FD/frame924,
Player_X_Position82->95 (world338->351), SamusStopAtWallBanked left clamp.
Earlier actual head/side callbacks show Chip's private rising velocity ignores
SMB's positive1 ceiling response and keeps rising into a used block. Its
feedback gate accepts only zero. Private chip-ceiling-feedback-v1 changes one
BNE opcode to BMI on each mapper, preserving all other ROM bytes/symbol PCs;
no shared wall or jump kernel changes. CPU feedback6,720 cases per mapper pass.
New native Easy/Hard Chip/Dale routes are pending; no adoption/release claim.
Original failures and read-only causal evidence remain retained.

Newest user requests: Zelda II Link's TERRAIN collision box is wrong against
blocks/pipes/platforms (explicit clarification); Parodius alternates need the
full graphical upgrade bar like Gradius, replacing abbreviated text. These
remain outstanding and must receive separate reviewable GitHub checkpoints.

Chip/Dale ceiling feedback is now adopted, MMC5 ROM274fff8613d98a281d7549d13
e59430c4d6b4553eb16bd9d2c651e0b409c8b3b; fresh ROOT compile matches the tested
private candidate byte-for-byte. Downloads/SMB-Crossover-Current-MMC5.nes was
updated and the old054d... file hash-backed up externally. Root source changes
only BNE->BMI in CdMovement's native stop feedback, one ROM byte; original
shared wall geometry, Rescue Rangers jump kernels, RAM/CHR/music and PCs stay
exact. Receipt build/verification/chip-ceiling-feedback/proof.json.

Native-routes-v2 all eight cases (Chip/Dale Easy/Hard, both mappers) clear
zero-death1-1 with original committed motion and code/stack/NMI/cache/CHR
checks. Retained v1 failures were controller observations reading fixed MMC5
aliases on MMC3; v2 binds policy symbols to actual linked labels, recording
each old/new binding. It changes no emulated state/ownership. Independent
direct-v1 ChipEasy/DaleHard on each mapper retain17,448 actual PPU frames,
RGB/index/lossless archives and exact input/trace, raw world<=3/camera0..3 and
actual visible scanline31 writer banks254/126. All four overview sheets were
human inspected, no obvious terrain/screen displacement in these samples.
No exhaustive animation/SFX/all-item claim; private MMC3 architecture still
unadopted due its parser+230cycles. Old full37-identity MMC5 evidence belongs
to054d... parent, not relabeled as full current274f... qualification.

Zelda II Link terrain diagnosis: its current ordinary Link row9 head+17 and
feet+32 covers a short15px body, while Zelda II native artwork spans32px.
Standing/crouch/Fairy need their own terrain integration; no source fix yet.
Original Parodius full seven-cell HUD captures now exist for all three ships
under D/parodius-hud-source-v1, with PPU maps, direct pixels and matching
variant bytes; no power bar graphics have been installed yet.

Parodius graphical bar private work: actual original HUD uses a raster-swapped
font, so the first endFrame-pattern export was rejected. Source-v2 captures
PPU during real scanline216, original second nametable row2; art-v3 verifies
all5,376 native frame/letter-mask pixels across three ships, with original CHR
provenance and all required current HUD glyphs retained. Private candidate-v2
ee0b6bc5e253e6de7476ef9b781e748c1fced896a28cadd13d74561119172a44
uses three free1KiB font pages396..398 and full32px cursor halves across eight
attribute bytes. CPU queue-proof passes16,128actual cases, max terminator81
within84B, deferral/clean/screen flags and font acquisition. Native PPU/entry/
exit qualification pending; ROOT source/download unchanged. MMC3 keeps its
prior text fallback until its font upload ownership is handled. Rejected
candidate-v1 accidentally compiled parent nested includes; exact CHR assertion
caught it and v2 stages the unchanged parent include correctly. No source
adoption or current-build graphical-HUD completion claim.

Parodius bar now ADOPTED for MMC5, exact current download/root buildee0b6bc5
e253e6de7476ef9b781e748c1fced896a28cadd13d74561119172a44. Fresh ROOT compile
matches tested private candidate; previous274fff... download hash-backed up.
Native UI all three actual-menu ships passes192directPPUframes/344,064pixels,
all seven full32px cursor positions, empty cursor/font reacquisition, font
timing, full five-field NMI and A/C bank ownership. Human inspected actual
PPU images. Three ordinary-controller zero-death1-1 clears (4974/4958/4970
frames) continue through1-2 entry with strict motion/body-CHR checks. Native
route PPU/SFX/full-campaign review remains distinct from UI pixel components.
No other character graphics/RAM/global palette changes. Active oversized
MMC3 asset preparation now packs the three fonts and passes complete raw-CHR
equality against this MMC5 reference; MMC3 graphical font loading remains a
text fallback. Receipt build/verification/parodius-graphical-hud/proof.json.
Zelda II Link TERRAIN profile is next, still unresolved.

2026-10-25 Zelda II terrain diagnosis: all 24 linked original/alternate Link selector combinations still return short profile 9. Authenticated original USA ROM queries show normal/crouched head Y+0, feet Y+32, sides Y+6/+26; Fairy head Y+8 and feet Y+26. Crouching does not halve the native body. Source ROM query and prepared sprite bounds are preserved in checkpoints/2026-10-25/zelda2-terrain-observation/proof.json. No collision repair or native gameplay claim yet.

2026-10-25 UPDATE: adopted Zelda II terrain candidate v4, SHA256 f00c2a7ad0459a3cd0b369bb4fbc9f374dc27d9335b2cc1fe1867f3f98d73d23. Current Downloads MMC5 ROM and a fresh root compile match the tested candidate exactly. Prior ee0b6bc5 build is backed up externally. Dedicated full-height normal/crouched queries override the old shared row only for the Zelda II alternate during gameplay. Fairy uses its authenticated smaller head/foot span; its lower side points are deliberately centered for SMB, avoiding the original face-dependent off-body lower query. Reads retain the player's actual position and native block-cell receipt. Actual upward crossings separate before side checks; corrected floor alignment and wall page carries remain bounded. Existing RAM and CHR bytes are exact.

The component oracle executes 35,260 assembled cases across head, feet, sides, wall clamp, post-response and admission. Eleven native staged original1-1 geometry scenes, 88 direct PPU frames and 176 guarded NMIs pass; the actual question-block actor retains worldX352. Both modes independently replay zero-death1-1 runs through moving1-2 entry: 9,326 physical frames, exact inputs/trace, all PNG RGB/raw roundtrips and visible scanline31 splits. Human inspected both overview sheets and native geometry samples. Existing Link Easy, Samus Easy, Sophia Hard and Mac Easy controls clear with their motion/CHR guards. The initial Samus Hard control incorrectly used an Easy policy and died on contact; matching Easy passes, and the failure remains preserved. The initial Zelda II controllers turned too late on the last small stair gap; corrected inputs land on the top step and build forward speed before jumping, with no game-state or physics writes.

Receipt: build/verification/zelda2-terrain/proof.json. Small proof copies: checkpoints/2026-10-25/zelda2-terrain-candidate-v4. Full lossless evidence remains in external D/zelda2-terrain-candidate-v4. Do not rerun adopt_zelda2_terrain_once.py. Moving-platform-specific Fairy attachment and source enemy/body hitbox projection remain follow-up work; these terrain checks do not certify either. Current oversized MMC3 source preparation/CHR parity passes, but its new native build, full graphical Parodius font upload and architecture performance remain unqualified. The overall goal is still incomplete. User has renewed the allowance and explicitly requested continued work.

2026-10-25 adopted robot no-op weapon-selection repair. Current source/download SHA859b51acb503dde2b9f57ef45a6a6d2bc22a98aa726a331897ef0af6cc4ff587, fresh compile exact. Only30 ROM bytes in PRG59; all old exported PCs/RAM/CHR remain exact.548 assembled components,125 transitions and27 native UI cases/332 guarded NMIs. No-op Select preserves shots/charge; real transitions retain cleanup. Actual baseline failure and fixture revisions remain preserved. Receipt build/verification/robot-selection/proof.json; small copies in checkpoints/2026-10-25/robot-selection. No new full-level, attack-lifetime, PPU or audio admission.

2026-10-25 adopted Zelda II platform/body and shared native small-lift drawing fix, current SHA49d980e564abfb8bfc71bf0c69d5f25c91afed0968d231f959252fa53552b174. Original SMB platform actors, movement and carry are retained. Normal/crouched source body rectangles, private platform collision shapes, Fairy26px feet and actual paired balance flags now align with native platform origins; no static floor rounding while supported on a nongrid lift. Guest OAM rotation no longer erases native small girders: authentic masked three-sprite rows draw late through the existing bounded allocator after firebars. All RAM and CHR bytes remain exact.

Exact-hash evidence:58 staged native arenas, verified hardware/DMA/body publications and interrupts; position/body/BIT/native-jump/balance/renderer CPU oracles. Controller-only Easy4751/Hard4840 both clear1-1 with zero deaths and actual committed motion/CHR guards. Root inspected three native contact sheets. V12 conditional legacy names preserve both standard cartridge outputs byte-for-byte while producing the exact qualified expanded49 hash. Receipt build/verification/zelda2-platform/proof.json; light copies checkpoints/2026-10-25/zelda2-platform-final49. These new routes are discoveries, not independently replayed full-route PPU/audio acceptance. All-character/every-item/campaign and constant60Hz objectives remain open.

2026-10-25 adopted combined weapon admission fixes, current SHA55bcfb8209b628062ce1f833a2ed386bd6f08426d34fed9fa8b5ba1f90694be7. Current Downloads and default expanded ROM/debugger files match fresh ROOT compile. Ryu refuses primary during live Jump Slash after an actual auto-equipped pickup; Sophia reserves a complete three-missile volley before spending; SMB3 fire/hammer hit Bowser and hammers hit Buzzy Beetles. Only85 PRG bytes in banks6/37/90; all prior exported PCs/RAM/CHR unchanged. Complete repaired banks match independently qualified donors, and all89 native component cases pass again on combined55, with1248 CPU components and byte-identical ordinary target controls. Actual original hammer lifetime was tested over consecutive full source updates; original35-hit balance is explicitly adapted to host5HP. Component/graphics/NMI proofs do not certify natural earning, all AI phases, a new full-level route, full audio review or the complete every-character/every-powerup goal. Receipt build/verification/native-weapon-fixes/proof.json; light copies checkpoints/2026-10-25/native-weapon-fixes-55.

2026-10-25 adopted native pickup/contact composition220be8247baf877785c91244876038354442e68502b3f837920f39a674a1fa3e. Mac preserves HP/stars/stamina/live move on actual coin/score/1-Up gains, records modular counter wrap, resets after actual death/new-game. TMNT Kiai pickup uses current screen-relative box and native edge clipping after its full48-call rise. Chip/Dale crate vertical contact rejects240px wrapped gaps from actual native falling enemies; valid local overlaps retain exact original application state. No Kirby patch was needed for the reproduced native fall/inhale controls. Only124bytes in banks79/87/93; every other ROM byte equals55, all old qualified PC/RAM/CHR unchanged. All76 native component cases rerun on combined220 plus full-byte life, original DEC/BPL and crate-window CPU boundaries. MacEasy4657/ChipEasy4287/DaleHard4414 controller clears independently replay with12758 exact physicalPPU frames, zero deaths and moving1-2. Standard outputs remain byte-identical. Current Downloads/default artifacts freshly rebuilt and exact; backups external. Receipt build/verification/pickup-contact-fixes/proof.json; small copies checkpoints/2026-10-25/pickup-contact-fixes-220. Do not rerun adopt_pickup_contact_fixes_once.py.

Ongoing follow-ups: Samus/Contra source audit found upward Wave Beam X-page wrap and is preparing a native-qualified private repair; CV3 Alucard source-noise proposal8357 is HELD because matched native cadence regressed; optimized dedicated overlay under investigation. Every-item matrix preparation deduplicates historical12identity/24mode item profiles plus Kirby copy modes and10 legacyHard identities; these are not all37 identities on current220. The whole goal, remaining audio/performance/oversizedMMC3 and final every-identity/every-item qualification remain incomplete. Max2 Mesen workers; Samus/Contra and CV3 each own1, root has none during their runs.

Source text normalization restored chip_dale_boxes.s original LF line endings before Git commit. Split lines are identical to the native-qualified proposal and another fresh ROOT build remains exactly220; default ROM/debugger/build receipt now use that canonical build. Proof source-eol-v1/proof.json copied with the checkpoint. Root inspected48 actual independently replayed route PPU samples plus native component images; this is selected visual inspection, not exhaustive manual review.

2026-10-25 adopted Samus upward Wave repair, current84e55b6d60da4be5550d823f88ee40a9b220dbef5a1e8dd21de3d69aa28cb328. Downloads/default ROM and debugger artifacts match a fresh canonical ROOT compile. Upward Wave retains world-page carry/borrow; its terrain gate uses the actual bridged Wave type instead of unrelated projectile slot0 after a bridge call. Only34 bytes in banks10/127; old qualified PC/RAM/CHR and other complete banks exact. Both ordinary target outputs remain byte-identical. Original source line endings restored, followed by another exact build.

Exact84 qualification:70,656 assembled upward updates,2,688 unchanged horizontal/nonwave controls,150 viewport checks,18 production terrain cases and16 staged native Easy/Hard cases. Hard collection is an actual Wave inventory collision after seeded base/Long state; Easy tier is seeded. Independent controller-only SamusEasy1-1 replay covers5,733 physical PPU frames with zero deaths and moving1-2; selected actual route/component frames inspected, not exhaustive manual review. Small receipts in checkpoints/2026-10-25/samus-wave-84; full lossless evidence external D/samus-wave-combined220-v1. Do not rerun the one-shot Samus adopter.

Separate current-source MMC3 build417e254d on parent220 and compact Sophia capacity helper are private proposals only (ec06418). Active MMC3 recipe unchanged; no current full-roster MMC3 qualification. Alucard authentic noise cue386 privately passes22 native cases and cadence/ordinary controls, but is not adopted. Mac authentic music is in private source/CPU work. The current84 every-item matrix and six progressive-family native reruns remain bounded component evidence, not all37 current full-level/every-item completion. Whole goal remains incomplete.

2026-10-25 adopted original Alucard primary noise cue, currentae97d45e5a33b20a399c0b55f241ea933a72eaea6f88e7fc69eae93af85c96e4. Current Downloads/default expanded artifacts and fresh canonical ROOT compile match. Only643 bytes in banks27/28/82/84, all other complete ROM banks and CHR exact84. All retained qualified symbols remain exact; the one intentionally removed private CV1 restore-loop back-edge Load at DCE9 is disclosed because that address now lies inside the replacement JSR operand. No fake callable alias was added. No new RAM allocation; eight formerly unused roster-private bytes hold the noise owner/cache. Durable audio producer regeneration reproduces every frozen generated output, ordinary mapper outputs remain byte-identical.

Current exact-hash tests:22 native cases (12 real B releases, source/legacy/pressure,5 ownership/pause/retrigger/scene/DMC controls,2 Bill controls),4,160 full ordinary AudioUpdate CPU cases and256 restore differentials. Original28-update noise register schedule passes; source bus flush order/frame quantization is an explicit adaptation, not an identical-waveform claim. Matched1,233 wallframes: zero-update97 to92, draws1099 to1103. Six-Goomba pressure boundary-inclusive draws158 to161. All1,069 non-noise source-register writes and legacy145 full writes match; Bill cadence/APU/cycles exact. Root inspected22 actual endpoint PPU frames; seeded invulnerability deliberately hides Alucard in some endpoint phases. This is not exhaustive animation/level/audio review. LF restored from actual Git originals in roster_audio.s and prepare_guest_audio.py, followed by another exact compile. Source-final donor EOL claim was insufficient and the canonical proof records the correction.

Small receipts: checkpoints/2026-10-25/cv3-alucard-ae97. Full native/CPU/lossless evidence external D/cv3-audio-combined84-v2. Do not rerun adopt_cv3_alucard_audio_once.py. Grant/Sypha primary DMC storage and other CV3 cue/music routes remain incomplete. Mac authentic one-bank native music and CV3 actual injury-rate follow-ups are private source/CPU work; progressive acquired Pit/Rygar/Scrooge abilities have one sequential native grant. Mac's old character-name pad reservation was released: verified new resident gate reservation is LOWCODE bank126,99FE..9A0F, the18-byte prefix of the branch-skipped SmallPlatformCollision tail. ROOT worker released; max2 project Mesen processes. Workspace measured29,737,482,935bytes before this small checkpoint; lossless material remains external. Full37/every-item/performance/MMC3 goal remains open.

2026-10-25 private current-ae97 MMC3 rebase compiles2334dca4; generated Alucard audio guard and reset context ported explicitly,677 bounded changed bytes vs417,54,732 retained qualified symbols/LOWCODE/tiny/rawCHR exact,2048 local capacity CPU cases pass. No native/cadence/release claim and active recipe/user build unchanged. See mmc3-current-source-2026-10-25.txt. User explicitly confirmed existing roster finishes before new characters; curiosity about an extra menu row is not an implementation request.

2026-10-25 acquired progressive abilities frozen on exact84:62 native cases/12 real physical collections/720 committed transformation calls across Pit/Rygar/Scrooge in both modes;12,514updates,12,508NMIs,150,096CHR checks,11,986DMA checks,minSP193. Pit hammer/flight gate/exhaust/recharge, Rygar40/64/88 reach/hit/4px return/catch, Scrooge ground/enemy pogo pass. Agent reviewed157 unique PPU images representing344 captures. One Scrooge original failure was wrong staged enemy standing Y, retained with source/native-CPU geometry proof. No game patch/new identity/full-every-item claim. Source-only next: turtles8profile actual gear/food/caps/volley/catch lifecycle. See final-item-abilities-2026-10-25.txt and checkpoints/2026-10-25/acquired-abilities-84.

2026-10-25 adopted Grant/Alucard injury repair52918588bab0eec3f3a1f857bf084d2d799e88a5c781c75233c098ccc5f54f3f. Real enemy-contact owners now request the existing authentic193-byte Simon-shared DMC at original Grant14/Alucard13 rates; Sypha remains unchanged pending its distinct sample. Same-width hooks and28-byte bank7 helper/four FE11..FE14 padding bytes preserve all old qualified PC/RAM/CHR/sample bytes/starts/lengths. Only68 ROM bytes in banks7/82/127; no new RAM. Last bank7 byte BFFF remains free, previous29-byte pad is now occupied. Current Downloads/default artifacts and fresh canonical ROOT compile exact; old source/build backed up externally. Git-original source EOLs retained, no full-file churn.

Independent ROOT rerun on exact529:14 real cold-menu enemy-contact native cases; Grant/Alucard attack-before-contact, pressure/retrigger, actual Start pause/resume and natural DMC hardware completion; Sypha/Simon/Link controls.1,728 public DMC ABI,144 actual injury-owner,2 original-source payload/rate/DAC chains and5,024 ordinary full AudioUpdate CPU cases. Ordinary targets unchanged. All guarded native banks/5SMC/stack/CHR/OAM/visible IRQ pass. Cost is explicit: public DMC starts add34..49 CPU cycles; Alucard180-update pressure takes270 rather than269 wallframes,90 rather than89 zero-update frames, same91draws. Grant and control cadence unchanged. No identical-waveform/full-CV3/full-roster claim.

Receipts build/verification/cv3-injury/proof.json; small copies checkpoints/2026-10-25/cv3-injury-529; full native/CPU/lossless external D/cv3-dmc-root529-v1 and D/cv3-dmc-followup-v1. Do not rerun adopt_cv3_injury_once.py. Authentic primary72 and distinct Sypha75/general priority remain open; source-only installed-asset/shared bank-capacity audit is underway before a safe MMC5 fixed-bank mirror. MMC3 fixed E-window cannot use that mirror architecture. Private current-ae97 MMC32334 build was pushed2774ab2, not installed; it is now an older hash after529.

Acquired62-case Pit/Rygar/Scrooge ability packet on84 pushed aa30a34. Full37/every-item fields remain false. Next turtle8profile lifecycle fixture is source-only, preferring actual25 native defeats for gear drops and original-ROM verification before calling uncapped boomerang catches a defect. Mac authentic native v5 d7e585(parent220) is HELD: exact600 gameplay rows/1021wallframes but draw595 to591 and lag5 to9. Agent is optimizing only inactive original SFX scans, requiring all original golden state/stores before native rerun. A owns1 native worker; ROOT released its worker after529; B/C source-only. Max2 project Mesen processes. User reconfirmed existing characters first, then new roster; no menu-row implementation.

2026-10-25 CONFIGURATION COVERAGE CORRECTION: Shared Python-to-Lua boolean
serialization emitted bare True/False (nil). Nine final Hard labels across
18 Pit/Rygar/Scrooge receipts are withdrawn; actual mode was Easy0. Old raw
receipts/captures remain unchanged. Fresh exact529 Hard numeric-mode and
actual RAM-readback tests pass six profiles:9 progression+31 ability cases,
15 physical collections/3 caps/720 transformations. See final-item-mode-
correction-2026-10-25.txt, final-item-mode-native-2026-10-25.txt and
lua-configuration-correction-2026-10-25.txt. Root inventoried1056 frozen Lua
scripts across17 selected roots;40 hits classified, including three failed
unadopted Zelda Fairy attempts. Accepted Zelda v4 has integer flags; Mac/CV3
mode configurations were numeric. No whole-roster completion claim.
Existing roster first; no new characters/menu row. Installed529 unchanged.
A Mac v7 direct source-ZP relocation passed original golden CPU state/stores
and is granted one native worker on donor220, pending current composition.
B genuine529 Hard packet passed; one worker for turtle lifecycle follow-up.
C full CV3 shared fixed-bank mirror implementation remains source-only.
Max2 project Mesen workers; user emulator untouched. ROOT native grant idle.
2026-10-25 authentic Mac nine-track music ADOPTED8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277.
Current Downloads/default artifacts and fresh canonical compile exact; backups
external D/mac-native-current529-v1/adoption-v1. Only7959bytes/PRG38,123,126;
all54193 oldqualified symbols/CHR/fixed DPCM and ordinary mapper outputs exact.
Root reran162009 sourceCPU calls,48570 actual dispatcher source calls,
5856 ordinaryAudioUpdate controls plus9216 fullAudioUpdates/all36 other IDs.
Other36 APU/RAM/register/mapper outcomes exact; later fallback paths add12CPU
cycles, explicitly retained. Root native14music selections/source/hardware/
NMI/5SMC/CHR/DMA pass. Exact600gamework/1021physicalframes,598draws2lag vs
parent595/5; every work phase equal/better. Three real stationary PPU samples
inspected, not exhaustive visual or source-waveform/campaign qualification.
See mac-native-music-adopted-2026-10-25.txt and mac-native-music-8ff checkpoint.
Do NOT rerun one-shot Mac adopter. Native worker released to A for natural
Mac item lifecycle; B retainsone529turtleworker. C source-only full CV3 DMC
rebase; remaining26B SmallPlatformCollision pad9A10..9A29 reserved privately
for <=25B authentic completion gate, Mac18B99FE..9A0F stays exact. No adoption
of C's private source yet. Max2 task Mesen processes; user's emulator untouched.
Full roster/every-item/audio/performance/MMC3 goal remains ACTIVE/incomplete.
2026-10-25 natural-resource Mac item component passed on adopted8ff, both
actual numeric Easy0/Hard1, unchanged frozen fixture.9stages/5physical pickups/
15realGoomba contacts per mode, earned super spends realstar/stamina, real
injury/star loss/death/life decrement/96HP20stamina0stars movable respawn.
No resource/status/attack/protection/timer writes or pickup actor/collection
teleports. Original73whitepixel star/committedOAM and reused hardware guards
pass. No new production patch. Report final-mac-items-native-2026-10-25.txt;
small receipts mac-items-8ff; full external D/final-mac-items-v3. Nativeworker
RELEASED. Full-health/cap, empty-stamina/refill, genericStar/1Up/water/final
current1-1 remain separate; no all-item/fullcharacter completion claim.
B529turtles6/8profiles passed, Donatello2pending under1worker. C source-only
8ff full CV3 samples/priority/trueDAC completion and no-source idle overhead
qualification underway; A now source-only Mike/Parodius music feasibility.
Current8ff music/source pushed4656a7c. GoalACTIVE/incomplete; current roster
first, no newcharacters/menu row. Max2 project Mesen; user emulator untouched.
2026-10-25 Mac Easy current8ff1-1 controller clear independently replayed,
zero deaths,4658nativeframes/4657polls, moving1-2.4458 actual physicalPPU
frames fully lossless/RGB matched,2739committed viewport checks maxWorld6/
maxCamera3,2794bodyCHR frames0bad. Four PPU samples reviewed, not exhaustive.
Small receipt mac-route-8ff; full D/mac-native-current529-v1/mac-route-v1.
Root nativeworker EXITED/RELEASED. Workspace measured29,739,111,758bytes/
389667files (<30,000,000,000cap); no retained captures deleted.
All8turtleprofiles on529 passed:240physical items/3800eligibledefeats/
152actualnative drops/64injuries,205270gameupdates; actualmodes0/1.464selected
PPUframes reviewed. Original100..102boomerang refunds/HUD matchsource; no
newgamepatch. Frozen529evidence notrelabeled8ff, broadmissinglifecycle/scenes/
performance remainopen. B's nativegrant RELEASED; nowRollsource-only.
C full current8ff sample e6b private source/CPU/IRQ/layout/flagoff/producer
passes, ONE sequential native grant after review. Rootadoption stillpending:
real72/75owners,125/127actualDMC reads/naturalheldDACtail/lifecycle/ordinary
negativecontrols andmatchedno-sourcepressure. C currentlysoleMesenworker.
A source-only Mike11trackdriver mayfit verifiedfreebank115tail, preserving
allreachablemusicbytes; ParodiusDMC/perf unresolved. Allcurrent rosterfirst.
GoalACTIVE/unachieved; no newcharacterrow. Current8ff/pushedf84a400 unchanged.
2026-10-25 fullCV3 source-only readiness e6b on current8ff checkpoint saved:
cv3-dmc-source-e6b +eight immutable source/CPU/IRQ/storage tools and readiness
JSON. Original72/74/75/76 queue/priority/heldDAC design,4056assembledIRQ/RTI,
6048priority/72realCPUowner/1152tail/5024ordinaryAudioUpdate pass; producer/
ordinarymapper hashes/EOLs/Macbank123+18gate exact. Onlysource-classidle adds13
cycles; listedunrelated idle0, ordinaryworst85. No native/releaseadoption claim.
C grantedone nativeworker, actual initialGrant/Sypha/Alucard ownercases pass;
fullordinary/matchedcontrols inprogress. Source-report.txt preservesreadiness
beforethose results. Newnativefixture/tools andevolvingmainreport uncommitted
untilboundedreturn. RootDownload/source remains8ff. Rootnativeworkerfree.
A Mike source-only no-pad gate feasibility; B Roll source-only lifecycle audit.
2026-10-25 PRIVATE full-CV3 e6b remains HELD after independent native repeat.
Agent32candidate/24baseline hardware-owner cases pass,400manifest files checked;
root4fresh Alucard paired runs pass hardware guards but REPRODUCE Hard97vs98
combined fireball/injury draw and pressureHard230->231 deferred draw. Strict
cadence false; NO adoption. Root source6048/72/5024 +4056IRQ/layout/54475retained
symbol bindings pass; these do not waive actual cadence. See checkpoint
cv3-dmc-native-e6b-held and cv3-dmc-independent-hold-2026-10-25.txt. Source and
Downloads remain8ff. Native tools/report frozen/pushed for review. C source-only
optimization in a new packet; C worker released. B owns1Roll native worker;
root currentlyfree. A Mike source/CPU private; first classifier-carry error was
caught before adoption and is being corrected in a new retained proposal.
No new roster/row; goalACTIVE/incomplete.

2026-10-25 ADOPTED fullCV3+Save4c70fe485f73fb8d437fae2e79ae8ddad83908dc26d4008f21e0a2abeccee2da.
Source/default/Downloads/canonicalROOT exact20-file deployment. Neverrerun
adopt_cv3_dmc_optimized_once_v2.py. Checkpointcv3-dmc-4c70; root report
cv3-dmc-adopted-2026-10-25.txt. Root633catalog/2048Save+1224IRQ/6048priority/
72owners/5024ordinary/4056IRQ/layout/9472all37ordinaryAudioUpdate passed.
Agent32candidate+24baseline actualnative; root6freshpairedAlucard pass.
Olde6bHard97vs98draw loss fixed. Offset88Hardpressure prefixdrawdefers1frame,
recoversnext; wholecase358vs360frames/same120draws240updates/sameworststall.
Explicitrootacceptanceofboundedfasterphase, noallprefix/universallagclaim.
Incomplete19filev2catalog preserved; correctedv3independentlyenumerates20.
Oldsamples/Macbank123gate18/RAM/CHR/symbolsexact; copyloop saves314CPU.
ROOTone sequentialMesen continuesfull37identity/38route1-1+PPU on FROZEN8ff,
notnew4c70. Scans7profiles34447PNG,0transientcandidates; root56sampledframes
viewed, noobviouscorruption there, notexhaustive. B provedRolldoubleupdate;
proposedone18-byteRollfarcallremoval only, now granted1composed4c70worker
forbothmode36-steplifecycle aftersource/CPU. A Mikev7donor8ffgoldens/CPU pass,
rebase4c70required; no nativegrant. C remainingCV3effects sourceonly on4c70.
OtherownedWIPuntrackedpreserve. GoalACTIVE/incomplete; no newcharacters/row.


2026-10-25 Roll drop owner accepted
Current MMC5 is9bac46e934d3301e378139783febf2d54c4fd5753a62e082f2d7e6580946d58c.
ROOT canonical compile and Downloads/default bytes agree. Only18 redundant local
drop-update bytes inbank119 changed from4c70; shared object dispatcher owns the
single update. Both native modes72steps/624defeats/139natural drops pass;
ROOT independently reran412owner+8140resource CPU cases and reaggregated all427
raw event captures. Checkpoint:docs/qa/checkpoints/2026-10-25/roll-owner-9bac.
Missing Roll fade remains open. Existing full-roster1-1 run is8ff-only:37/38
profiles passed across36identities; BassHard controller contact failure retained
and retry running. SMB3 P-bar transient font withdrawal is independently found,
private fix under CPU/native qualification; no current P-bar fix claim yet.
No new characters/menu row. Continue existing37 identities and every powerup.
