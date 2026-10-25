"""Continue the terminal34-case batch without rerunning/overwriting its work."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent
BASE=D.parent/'2026-10-24-native-head-pz';O=BASE/'finish-v2';O.mkdir(exist_ok=False)
ROM=D/'ryu-head-candidate-v5/candidate.nes';digest='675c57f4abd94d51d0f48a54f0a1d661ed75ef18b153de32a29d94145ba1d47d'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
driver=D.parent/'2026-10-24-roster-pe/matrix-v1/bound-runner.py';replay=D/'streaming-replay-v1/replay.py'
assert sha(ROM)==digest
prior=json.loads((BASE/'progress.json').read_text());assert len(prior['runs'])==34 and prior['ROM_sha256']==digest and all(x['passed']for x in prior['runs'])
for row in prior['runs']:
 p=Path(row['folder']);m=json.loads((p/'manifest.json').read_text());assert sha(p/'manifest.json')==row['manifest_sha256']and m['ROM_sha256']==digest and m['result']['cleared']and m['result']['deaths']==0
index=O/'existing34-index.json';index.write_text(json.dumps(dict(ROM_sha256=digest,phase='discover',runs=prior['runs']),indent=2))
(O/'v1-terminal.json').write_text(json.dumps(dict(exit=1,exception="KeyError: 'manifest_sha256'",completed=34,action='Versioned continuation; all original output/receipts retained. No game assertion changed.'),indent=2))
log=(O/'replay-existing34.log').open('w')
child=subprocess.Popen([sys.executable,str(replay),'--rom',str(ROM),'--discoveries',str(index),'--output',str(BASE/'direct-v2-34')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
report=dict(ROM_sha256=digest,goal_complete=False,complete=False,replay34_pid=child.pid,replay34_exit=None,new_runs=[],existing34_index_sha256=sha(index),existing_same_hash_Ryu=prior['existing_same_hash_Ryu'],native_workers_maximum=2)
def save():(O/'progress.json').write_text(json.dumps(report,indent=2)+'\n')
save()
bindings=json.loads((D/'current-37-bindings-v1.json').read_text())['runs']
for name,mode in [('megaman','easy'),('bass','hard')]:
 row=next(x for x in bindings if x['identity']==name and x['mode']==mode)
 before=Path(row['folder']);m=json.loads((before/'manifest.json').read_text());assert sha(before/'manifest.json')==row['files']['manifest.json'] and sha(before/'policy.lua')==row['files']['policy.lua']
 out=O/('discover-'+name+'-'+mode);t=time.monotonic()
 with(O/(name+'-'+mode+'.log')).open('w')as f:
  p=subprocess.run([sys.executable,str(driver),name,'--rom',str(ROM),'--output',str(out),'--behavior',mode,'--frames',str(m['config']['limit']),'--capture','12','--chr-commit','--policy',str(before/'policy.lua'),'--timeout','180'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 path=out/'manifest.json';new=json.loads(path.read_text())if path.exists()else{};result=new.get('result')or{}
 item=dict(identity=name,mode=mode,folder=str(out),manifest_sha256=sha(path)if path.exists()else None,passed=p.returncode==0 and result.get('cleared')is True and result.get('deaths')==0 and new.get('chr_commit',{}).get('passed')is True,exit=p.returncode,frames=result.get('frames'),seconds=round(time.monotonic()-t,2),parent_inputs_exact=(out/'inputs.csv').read_bytes()==(before/'inputs.csv').read_bytes(),parent_full_trace_exact=(out/'trace.csv').read_bytes()==(before/'trace.csv').read_bytes())
 if path.exists():assert new['ROM_sha256']==digest and not new['fixed_replay']
 report['new_runs'].append(item);save();print(json.dumps(item),flush=True)
all_rows=prior['runs']+report['new_runs']
assert len(all_rows)==36
(O/'discover-results.json').write_text(json.dumps(dict(ROM_sha256=digest,complete=True,passed=all(x['passed']for x in all_rows),phase='discover',runs=all_rows,existing_same_hash_qualified_Ryu=report['existing_same_hash_Ryu']),indent=2))
report['replay34_exit']=child.wait();log.close();save();print(json.dumps(dict(replay34_exit=child.returncode)),flush=True)
index2=O/'last-two-index.json';index2.write_text(json.dumps(dict(ROM_sha256=digest,phase='discover',runs=[x for x in report['new_runs']if x['passed']]),indent=2))
with(O/'replay-last-two.log').open('w')as log:
 p=subprocess.run([sys.executable,str(replay),'--rom',str(ROM),'--discoveries',str(index2),'--output',str(O/'direct-last-two')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
report.update(complete=True,replay_last_two_exit=p.returncode,passed=all(x['passed']for x in all_rows)and report['replay34_exit']==0 and p.returncode==0);save()
(O/'proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(passed=report['passed'],complete=True,goal_complete=False)),flush=True)
raise SystemExit(0 if report['passed']else 1)
