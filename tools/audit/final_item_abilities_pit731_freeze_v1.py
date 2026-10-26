"""Freeze PitEasy731 preparation and host-only result-parser rejection models."""
from pathlib import Path
import argparse,copy,csv,hashlib,json,shutil
from final_item_abilities_pit731_run_v1 import collect,verify_manifest
from final_item_abilities_static_prepare_v2 import CURRENT,D,ROOT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['prepared'] and not ready['native_run']and not ready['native_granted']and ready['ROM_sha256']==CURRENT
 assert sha(a.ready/'manifest.json')==ready['manifest_sha256'];count=verify_manifest(a.ready/'manifest.json');out=Path(ready['output'])
 assert not(out/'launch.json').exists()and not(out/'proof.json').exists()
 cfg=json.loads((out/'config.json').read_text());model=a.output/'HOST-MODEL-ONLY-not-native';model.mkdir()
 put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n')
 # These files are explicitly synthetic parser inputs, NEVER native receipts.
 native=dict(passed=True,family='pit',hard=False,actual_mode_readback=0,abilities=[dict(q=q)for q in cfg['abilities']],physical_collections=[dict(transformCalls=60,ownerCalls=1)]*2,nmis=101,irq_scroll_stores=101,complete_dma_checks=101,hardware_chr_checks=1201,minSP=128)
 put(model/'native-abilities.json',native)
 with(model/'actual-ppu.argb').open('wb')as f:f.truncate(101*256*240*4)
 with(model/'case-example.argb').open('wb')as f:f.truncate(256*240*4)
 with(model/'actual-ppu-index.csv').open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=['ordinal','ppu_frame']);w.writeheader();w.writerows(dict(ordinal=i,ppu_frame=i)for i in range(1,102))
 put(model/'ppu-capture-native-result.json',dict(passed=True,frames=101,bytes=101*256*240*4,actual_mode_readback=0,original_done_seen=True))
 base=dict(kind='completed-DMA-before-render-enable',id=0,page=2,start=dict(pc=0xe005,oamaddr=0,mask=0),complete=dict(oamaddr=0,mask=0),source=list(range(256)),hardware=list(range(256)),differences=[],writes=[dict(value=i,stamp=dict(oamaddr=i,mask=0))for i in range(256)])
 dma=model/'ability-dma-epochs.jsonl'
 def dma_model(bad=None):
  with dma.open('w')as f:
   for i in range(1,102):
    q=copy.deepcopy(base);q['id']=i
    if bad=='hardware'and i==1:q['hardware'][7]=99
    if bad=='255writes'and i==1:q['writes'].pop()
    if bad=='destination'and i==1:q['writes'][7]['stamp']['oamaddr']=11
    if bad=='mask'and i==1:q['writes'][7]['stamp']['mask']=30
    f.write(json.dumps(q)+'\n')
    f.write(json.dumps(dict(kind='startFrame-hardware',completed_dma_id=i,hardware=list(range(256))))+'\n')
    f.write(json.dumps(dict(kind='actual-PPUMASK-write',scoped=True,enabling=True,safe=bad!='late',stamp=dict(scanline=-1,cycle=275 if bad=='late'else 274)))+'\n')
 dma_model();tests=[]
 def expect(name,passed):
  z=collect(model,cfg);assert z['passed']==passed,(name,z['errors']);tests.append(dict(name=name,passed=True,expected_parser_accept=passed,actual_parser_accept=z['passed'],errors=z['errors']))
 expect('synthetic_complete_parser_input',True)
 for field,value,name in [('actual_mode_readback',1,'wrong_numeric_mode'),('hard',True,'wrong_boolean_mode')]:
  n=copy.deepcopy(native);n[field]=value;put(model/'native-abilities.json',n);expect(name,False)
 put(model/'native-abilities.json',dict(native,abilities=native['abilities'][:-1]));expect('only9ability_cases',False)
 n=copy.deepcopy(native);n['physical_collections'][0]['transformCalls']=59;put(model/'native-abilities.json',n);expect('only59transform_updates',False)
 put(model/'native-abilities.json',native)
 for bad in ['hardware','255writes','destination','mask','late']:dma_model(bad);expect(bad,False)
 dma_model();(model/'first-failure.json').write_text('{"host_model_only":true}');expect('first_failure_never_backfilled',False)
 # Preserve the rejection fixture. It is labelled HOST-MODEL-ONLY everywhere.
 result=dict(passed=True,native_run=False,host_model_only=True,tests=tests,models_are_not_PPU_or_gameplay_evidence=True,ready_sha256=sha(a.ready/'proof.json'),original_ability_mechanics_untouched=True)
 put(a.output/'host-parser-models.json',result)
 report=ROOT/'docs/qa/final-item-abilities-pit731-ready-2026-10-26.txt'
 assert not report.exists()
 report.write_text(f'''Pit Easy current731 single-pilot readiness,2026-10-26

PREPARED ONLY. No native grant/run/worker, retries or production/settings edits.
ROM {CURRENT}
Ready {a.ready}
Ready proof SHA256 {sha(a.ready/'proof.json')}
Manifest SHA256 {sha(a.ready/'manifest.json')}
Script SHA256 {ready['script_sha256']}
{count} fresh source/tool/profile/runtime bindings independently verified.

ONE-SHOT COMMAND, ONLY AFTER ROOT REVIEW AND EXPLICIT NATIVE GRANT:
{ready['stable_command']}

Scope: ONE PitEasy0 cold-selected profile, character6/slot6. All10 original
plans retained: six hammer hits/defeats/cleanup (tier0/1/2,bothfacings), tier0/1
flight refusal, tier2 full60fuel/exhaust/landingrecharge/nextjump and partial
release/recharge. Two real mushroom/flower collections have actual head/block
reveal/fullrise/no-premature-grant and60committed updates each. The mature item
is aligned for contact only after native full rise, as in the historical
qualified component. It is not an unassisted physical route or seeded tier.

Complete seed policy: {a.ready/'seed-policy.json'}
World/floor/question-block/nametable, playerposition/motion/fractions/facing,
scroll readiness, prior empty attack pools and protection timers are staged at
GameLoop entry. Hammer target is actual valid GoombaID6/highpage1/defaultHP0,
with native terrain support and facing-relative placement. No PlayerStatus,
PitFuel/PitFlight/PitBlocked or ability outcome writes. Thus A physical prefix
is real with disclosed setup/contact placement; B controlled world/target use
has actual input/dispatch/collision/cleanup, not genuine earned depletion.

The whole qualified731 source/static observer script normalizes EXACT after
removing only the added READ-ONLY fullPPU recorder. All original mechanics,
input policy, caps,10outcome assertions, numeric mode0 readback, IRQ31/CHR/five
SMC/bank/stack/publication guards and E008complete256protocol remain. All32
memory callbacks are installed at startup; return dispatcher stays LAST.
Full generated Lua5.4 loads/records3inactive mock PPU epochs. Two endFrame
callbacks: capture first, original guard/report/stop second. No runtime callback
registration/removal. The original case screenshots/events/APU logs stay on.

Every actual endFrame PPU is retained raw in actual-ppu.argb and its actual
frame/scanline/dot/CPU/update/phase/mode/tier index. Every actual DMA logs full
256source+256hardware and per-write actual destinations/masks/stamps before
strict assertions. E005 is NOT completed; E008 afterLDA/beforeSTA is genuine.
Pending startFrame is explicitly distinguished from completed publication.
All real render-enable stamps use scoped pre-render<=274/vblank241..260 guard.
Native runner additionally reaggregates all recorded256epochs and PPU sizes/
index/currentmode/10case membership/two60-update transforms before its result.
All missing native outputs/host failures remain FALSE with a permanent launch
marker; no retry is possible. Actual image/interaction review remains separate.

Host-only result-parser controls pass{len(tests)}positive/negative models, including
wrong mode/boolean,9cases,59updates,wrong hardware,255writes,destination,
render-mask/late-enable and existing first-failure. Their generated files are
explicitly HOST-MODEL-ONLY, not native receipts or emulated frames.

Runtime: NEW isolated copy of actual qualified portable worker, bound before
launch. Exe {ready['environment']['emulator_sha256']}
Core {ready['environment']['core_sha256']}
Worker settings {ready['environment']['worker_settings_sha256']}
User context {ready['environment']['user_context_sha256']}
Persisted worker RAMRandom is overridden by actual AllZeros command; nonrandom
CPU/PPU/mapper,doNotSave,hardware8sprites/adaptiveoff,0extraPPUlines,runahead0,
normal100%clock retained. Other existing emulator accuracy flags are recorded;
this is not physical-console fidelity. No user/source worker config writes.

No inference for other five profiles, Hard, other items/identities or campaign.
No global visual/no-flicker/sourceaudio/waveform pass. Retain all prior mode
withdrawals and historical ROM hashes. Current ledger stays unchanged pending
separate fresh Luigi freeze; Mario731 narrow Easy evidence remains linked.
''',encoding='utf-8')
 files=[Path(__file__),report,a.ready/'proof.json',a.ready/'manifest.json',a.output/'host-parser-models.json']
 for f in list(files):
  if f.suffix=='.py':
   snap=a.output/'source-freeze'/f.name;snap.parent.mkdir(exist_ok=True);shutil.copy2(f,snap);files.append(snap)
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size)for f in files]))
 proof=dict(passed=True,prepared=True,native_run=False,native_granted=False,ROM_sha256=CURRENT,profile='pit-easy',ready_proof_sha256=sha(a.ready/'proof.json'),ready_manifest_sha256=sha(a.ready/'manifest.json'),verified_ready_bindings=count,host_model_tests=len(tests),host_model_proof_sha256=sha(a.output/'host-parser-models.json'),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),stable_command=ready['stable_command'],maximum_launches=1,native_worker_held=False)
 put(a.output/'proof.json',proof);print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),**proof),indent=2))

if __name__=='__main__':main()
