from pathlib import Path
import hashlib,json,os,shutil
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';V=D/'mmc3-ship-lives-v25';O=P/'legacy-physical-summary-v1';O.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for folder,names in [('legacy-native-items-pilot-v2',['megaman']),('legacy-native-items-batch-v2',['proto','bass','samus','bill','lance','link','ryu']),('legacy-native-items-corrections-v3',['simon','sophia'])]:
 q=json.loads((P/folder/'proof.json').read_text());assert q['complete']and q['ROM_sha256']==sha(P/'candidate.nes')
 for n in names:
  z=next(x for x in q['runs']if x['name']==n);assert z['passed']and z['exit']==0;f=P/folder/n/'build/verification/native-legacy-items.json';j=json.loads(f.read_text());assert j['passed']and j['native_entry_staging'];assert all(x['collected']>x['staged']for x in j['items']);assert all(not x['attackRequired']or x['attackObserved']for x in j['items'])
  records.append(dict(identity=n,physical_mature_item_actors=len(j['items']),declared_attacks=sum(x['attackRequired']for x in j['items']),source_result=str(f),source_result_sha256=sha(f),fixture=str(P/folder/'fixture.lua'),fixture_sha256=sha(P/folder/'fixture.lua'),run=str(P/folder/n/'run.lua'),run_sha256=sha(P/folder/n/'run.lua')))
proof=dict(passed=True,goal_complete=False,ROM_sha256=sha(P/'candidate.nes'),identities=len(records),physical_mature_item_actors=sum(z['physical_mature_item_actors']for z in records),declared_attacks=sum(z['declared_attacks']for z in records),runs=records,scope='Ten actual cold Hard identities. Guarded native GameLoop-entry staging only, mature actors placed ahead of the player, real input/collision grants and exact ownership/exclusivity, complete native mushroom animation and explicitly declared source attacks. Simon additionally collects native large hearts; Sophia homing has a live native target. Pilotv1 transformation-readiness failure and v2 missing ammo/target fixtures remain retained. No random block emergence, all-item ability/audio fidelity, Easy progression, all-frame video, hardware or final campaign certification.')
(O/'proof.json').write_text(json.dumps(proof,indent=2))
doc=R/'docs/qa/current-work-pr-2026-10-24.md';backup=D/'current-work-pr-before-mmc3-v25.md';assert backup.exists()and sha(backup)==sha(doc);old=doc.read_text(encoding='utf-8');start=old.split('## Oversized MMC3')[0]
start=start.replace('Its actual source rebuild reproduces expanded MMC5 and both unchanged','Its actual source rebuild reproduces expanded MMC5 and both unchanged')
tail=f'''## Oversized MMC3 — qualified ship fixes adopted in root preparation

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
{proof['physical_mature_item_actors']} mature item actors were physically collected with exact ownership/exclusivity,
and {proof['declared_attacks']} explicitly declared source attacks were observed under controller input.
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

Only exec15527 is live: D/`run_mmc3_remaining_routes_v25.py`, writing
D/`mmc3-ship-lives-v25/remaining-routes-v1`. It runs the remaining34 exact
selected roster/mode cases from current MMC5's38-case aggregate against the
current MMC3 candidate with native mapper guards. New failures need actual
witnesses; no final all-roster mapper pass is claimed. Four ship cases are
already independently verified above.

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
'''
doc.write_text(start+tail,encoding='utf-8')
occupied=sum(os.stat(Path(dp)/n,follow_symlinks=False).st_size for dp,dn,nn in os.walk(R,followlinks=False)for n in nn);assert occupied<30_000_000_000
(O/'recording-integrity.json').write_text(json.dumps(dict(passed=True,workspace_bytes=occupied,goal_complete=False,summary_sha256=sha(O/'proof.json'),note_sha256=sha(doc),current_mmc3_receipt_sha256=sha(R/'build/verification/mmc3-ships-current-v25/proof.json')),indent=2));print(json.dumps(dict(passed=True,identities=len(records),items=proof['physical_mature_item_actors'],attacks=proof['declared_attacks'],workspace_bytes=occupied)),flush=True)
