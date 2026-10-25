from pathlib import Path
import json,subprocess,hashlib,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;Q=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-head-pz');O=D/'native-probes-qa-v1/routes-v1';O.mkdir(exist_ok=False)
ROM=O.parent/'candidate.nes';driver=D.parent/'2026-10-24-roster-pe/matrix-v1/bound-runner.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(driver)=='d6ab9cc1e938923797525704cf6d0e99e16fda6f007b98da1024cb167f00f167'
report=dict(ROM_sha256=sha(ROM),phase='discover',passed=False,complete=False,goal_complete=False,runs=[],driver_sha256=sha(driver))
for name,mode,source in [('megaman','easy',Q/'finish-v2/discover-megaman-easy'),('proto','easy',Q/'discover-proto-easy')]:
 out=O/(name+'-'+mode);policy=source/'policy.lua';assert policy.exists()
 with(O/(name+'-'+mode+'.log')).open('w')as f:p=subprocess.run([sys.executable,str(driver),name,'--rom',str(ROM),'--output',str(out),'--behavior',mode,'--frames','12000','--capture','12','--chr-commit','--policy',str(policy),'--timeout','180'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 path=out/'manifest.json';m=json.loads(path.read_text())if path.exists()else{};z=m.get('result')or{}
 row=dict(identity=name,mode=mode,folder=str(out),exit=p.returncode,passed=p.returncode==0 and z.get('cleared')is True and z.get('deaths')==0 and m.get('chr_commit',{}).get('passed')is True,manifest_sha256=sha(path)if path.exists()else None,policy_sha256=sha(policy),frames=z.get('frames'),deaths=z.get('deaths'),failure=z.get('failure'))
 report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
report['complete']=True;report['passed']=all(r['passed']for r in report['runs']);(O/'progress.json').write_text(json.dumps(report,indent=2));(O/'replay-index.json').write_text(json.dumps(report,indent=2))
if report['passed']:
 with(O/'independent-replay.log').open('w')as f:p=subprocess.run([sys.executable,str(D/'streaming-replay-v1/replay.py'),'--rom',str(ROM),'--discoveries',str(O/'replay-index.json'),'--output',str(O.parent/'direct-v1')],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 report['direct_replay_exit']=p.returncode;(O/'pipeline.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(direct_replay_exit=p.returncode)),flush=True)
