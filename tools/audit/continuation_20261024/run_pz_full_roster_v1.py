"""Fresh whole-roster discoveries and independent direct replay on adopted PZ."""
from pathlib import Path
import json,hashlib,subprocess,sys,time
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
O=D.parent/'2026-10-24-native-head-pz';O.mkdir(exist_ok=False)
ROM=D/'ryu-head-candidate-v5/candidate.nes'
driver=D.parent/'2026-10-24-roster-pe/matrix-v1/bound-runner.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
digest='675c57f4abd94d51d0f48a54f0a1d661ed75ef18b153de32a29d94145ba1d47d'
assert sha(ROM)==digest and sha(driver)=='d6ab9cc1e938923797525704cf6d0e99e16fda6f007b98da1024cb167f00f167'
parent=D/'current-discovery-37-v1.json';selected=json.loads(parent.read_text())['runs'];assert len(selected)==37
report=dict(passed=False,complete=False,goal_complete=False,phase='discover',ROM_sha256=digest,source_index_sha256=sha(parent),driver_sha256=sha(driver),wrapper_sha256=sha(Path(__file__)),native_workers=1,runs=[],existing_same_hash_Ryu=[],scope='Fresh actual cold-menu full1-1 controller discoveries for the adopted successor. Parent runs select policies only. Full same-hash physical replay follows. Every-item/shortcut/source-fidelity/performance obligations remain open.')
def save():(O/'progress.json').write_text(json.dumps(report,indent=2)+'\n')
save()
for old in selected:
 name,mode=old['identity'],old['mode']
 if name=='ryu':
  for m in ['easy','hard']:
   p=D/'ryu-head-review-v5'/m/'proof.json';q=json.loads(p.read_text());assert q['passed']and q['ROM_sha256']==digest
   report['existing_same_hash_Ryu'].append(dict(mode=m,path=str(p),sha256=sha(p)))
  save();continue
 before=Path(old['folder']);manifest=json.loads((before/'manifest.json').read_text())
 assert sha(before/'manifest.json')==old['manifest_sha256']and sha(before/'policy.lua')==old['policy_sha256']
 out=O/('discover-'+name+'-'+mode)
 cmd=[sys.executable,str(driver),name,'--rom',str(ROM),'--output',str(out),'--behavior',mode,'--frames',str(manifest['config']['limit']),'--capture','12','--chr-commit','--policy',str(before/'policy.lua'),'--timeout','180']
 start=time.monotonic()
 with(O/(name+'-'+mode+'.log')).open('w')as log:p=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 f=out/'manifest.json';m=json.loads(f.read_text())if f.exists()else{};result=m.get('result')or{}
 row=dict(identity=name,mode=mode,exit=p.returncode,folder=str(out),manifest_sha256=sha(f)if f.exists()else None,policy_sha256=sha(before/'policy.lua'),frames=result.get('frames'),deaths=result.get('deaths'),failure=result.get('failure'),seconds=round(time.monotonic()-start,2),passed=p.returncode==0 and result.get('cleared')is True and result.get('deaths')==0 and m.get('chr_commit',{}).get('passed')is True)
 if f.exists():assert m['ROM_sha256']==digest and not m['fixed_replay']
 row['parent_inputs_exact']=(out/'inputs.csv').exists()and(out/'inputs.csv').read_bytes()==(before/'inputs.csv').read_bytes()
 row['parent_full_trace_exact']=(out/'trace.csv').exists()and(out/'trace.csv').read_bytes()==(before/'trace.csv').read_bytes()
 report['runs'].append(row);save();print(json.dumps(dict(completed=len(report['runs']),total=36,**row)),flush=True)
report['complete']=True;report['passed']=all(x['passed']for x in report['runs'])and len(report['runs'])==36;save()
(O/'discover-results.json').write_text(json.dumps(report,indent=2)+'\n')
index=O/'replay-index.json';index.write_text(json.dumps(dict(ROM_sha256=digest,phase='discover',runs=[x for x in report['runs']if x['passed']],existing_same_hash_qualified=report['existing_same_hash_Ryu']),indent=2))
with(O/'replay-host.log').open('w')as log:
 p=subprocess.run([sys.executable,str(D/'streaming-replay-v1/replay.py'),'--rom',str(ROM),'--discoveries',str(index),'--output',str(O/'direct-v1')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
final=dict(discoveries_passed=report['passed'],replay_exit=p.returncode,goal_complete=False,ROM_sha256=digest,existing_same_hash_Ryu=report['existing_same_hash_Ryu'])
(O/'pipeline-result.json').write_text(json.dumps(final,indent=2));print(json.dumps(final),flush=True)
raise SystemExit(0 if report['passed']and p.returncode==0 else 1)
