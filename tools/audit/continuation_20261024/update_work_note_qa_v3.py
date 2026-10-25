from pathlib import Path
import shutil
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
p=R/'docs/qa/current-work-pr-2026-10-24.md';backup=D/'current-work-pr-before-qa-v3.md';assert not backup.exists();shutil.copy2(p,backup)
p.write_text('''# Current QA source, integrated MMC3 tools and native qualification

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

P/`background-v1` is the current live diagnostic scan over all38 verified
streams (exec8908). Inspect its progress/proof; early cases have zero candidates.
It only tests same-before/after middle-frame background clusters with original
sprite/border masks. Persistent/longer defects, sprite omissions and source
fidelity remain outside its scope. Any candidate requires investigation.

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

## Oversized MMC3 — canonical preparation integrated, campaigns open

The actual private MMC3 ROM is2,097,168bytes:2MiB PRG and256KiB CHR-RAM.
SHA256 `43134c243d752fcaeab93d348ef56849df810f069788de9af1d76ed498359867`.

Current canonical tools are installed:

- `tools/prepare_mmc3_oversized.py` accepts `--source-root` and `--output`.
- `tools/build_mmc3_oversized.py` accepts `--output-dir`; use external output.
- `tools/mmc3_current_repairs.py` applies83 guarded unique source contexts
  from `tools/mmc3_oversized/repairs.json` plus the native74KiB menu atlas.
- Root receipts `build/verification/mmc3-tools-current-v16/proof.json` and
  `mmc3-tools-current-v18/proof.json`. V18 narrows the inert padding repair to
  its stable directives so both PZ and QA sources produce the SAME MMC3 ROM.
  Root recipe SHA256 is `1ed109ed1c934bd45d2b28a024577f70de17cbed43bb57e2e7218a99af4c5539`.

Canonical fresh preparation reproduces all629 qualified prepared files;
actual canonical build output is D/`mmc3-tools-v16/canonical-build/`.
D/`mmc3-tools-v18/qa-candidate.nes` independently compiles current QA source
to the same431... ROM. The old external extensionv5..v12 chain is historical,
not needed for current builds. V14/v17 consolidation/context failures remain
retained; v15 and v18 fix tooling only, preserving compiled mapper bytes.

Previous scoped native evidence at D/`ryu-head-oversized-mmc3-v12` remains
valid for these identical ROM bytes:

- `entry-all-v2`: all37 cold identities, variants,140 ordinary gameplay
  frames, actual NMI/SMC/bank restoration, full boot CHR-RAM, VBlank-only
  cache writes and protected native terrain/actor bytes.
- Menu native source pixels/OAM/CHR/palettes/nametables for37 identities with
  outlines off/on:74 exact poses,5,856 browsing frames, zero mixed/blank poses.
- Zelda II full native pause navigation, locks, purchase/defer, four exact
  world/OAM/font restores, no MMC5/ExRAM writes and native NMI/bank guard.
- Assembled10bit cache-key differential18,432 writes/hits,55,296 misses,
  all18slots and packed-neighbour/native24byte-prefix preservation.
- `roundtrip-v1`:629-file prepared ZIP SHA256
  `8dac71a8a18b83ae12fb8c461e7b773dd30ab84a11459d95cd421ef2b9f27d10`.

Critical mapper repairs retained in the recipe: omitted Roll/Z2/Parodius
raw art; true MMC3 renderer fallbacks; direct resident native-audio dispatch;
proper C windows F7/F8/FC and A-window menu F9; source auxiliary windows6/7
literal sprite translation; all37 menu choices; source-page10bit cache keys;
18-entry metadata outside native sound's first24bytes; complete Z2/CV3 state
in inactive XgLzHistory; real MMC3 HpRamEnd=$73c5, modes at ProtoVariant+3;
pause font restoration and stack preservation; non-emitting logical CHR.
V4's shared-farcall-in-NMI approach was rejected as unsafe. V10 overlapped
ProtoVariant; v11 had wrong new-bank CPU windows and corrupt Roll/TwinBee.
Do not reintroduce those historical implementations.

Full native route pilots now run in D/`mmc3-full-route-v22` (exec2095), for
RollEasy,TwinBeeEasy,RyuHard. They use mapper-specific read-only cache/bank/
SMC/boot/body/composite witnesses. Do NOT reuse MMC5-only CHR or Roll observers
or quietly mark those inapplicable observers passed.

Retained pilot findings:

- V19 stopped before emulation on a missing helper-exported linker symbol;
  v20 resolves the actual $0155 SMC start from the linked labels.
- V20 incorrectly asserted CHR mode1; the native mapper's PRG_FIXED_8=64
  uses CHR mode0. V21 corrects the observer without changing game bytes.
- V21 Roll reaches1939 before an invalid observer assumption rejects an
  UNUSED free cached pair. Cache victims intentionally keep unreferenced
  pairs. V22 checks every assigned pair, all protected terrain/actor bytes
  and actual visible uses against the displayed key, retaining the failure.
- V21 TwinBee reaches the flag, then remains at3151/176 in engine4 until
  frame16000. NmiSkipped increments continuously and DMA stops. This is an
  unresolved MMC3 exit/execution problem; inspect actual interrupted PCs and
  cache pending/cursor state in v22's `mmc3-interrupted.csv`, then locate the
  first incorrect write/loop. Do not call MMC3 fully playable yet.
- V20/V21 RyuHard never leaves the title: first option pulses were sent at60
  during the longer boot CHR transfer. V22's controller waits180 (boot verified
  at145), preserving actual user input and source mode settings. Its result
  is pending, not evidence of a character failure.

## Live work and remaining requirements

Only two jobs should remain live: exec8908 background scan (host-only), and
exec2095 MMC3 pilots (one Mesen worker). Confirm v20/v21 terminal states before
starting more native work; max TWO project Mesen workers total. All MMC5 route,
correction, benchmark, packet, source-adoption and tool-integration jobs have
completed. No need to restart their fresh-output folders.

Resolve the MMC3 exit issue and finish current-hash native campaign/item/music/
overload/fidelity qualification. Continue legacy weapon use/refill/damage/
expiry/SFX and source-specific ability checks beyond item acquisition. Both
mode/shortcut campaign coverage and physical hardware remain separate. Keep
source movement, original palettes/tracks and guide obligations intact.

Kirby's already-delivered1:40 video is
`C:/Users/kando/Videos/SMB-Crossover-Kirby-Abilities.mp4`, SHA256
`0529a886ea6f4222921560d43f50d3a270890a994cfdcf36eaced5494c07d213`.
It uses native PY pixels/audio,14copies, six base scenes and recovery/pickups;
staged scenes and one labelled half-speed recovery are declared. Preserve
D/`kirby-showcase-v1` lossless pixels/PCM. Do not relabel it QA or redo it.
''',encoding='utf-8')
