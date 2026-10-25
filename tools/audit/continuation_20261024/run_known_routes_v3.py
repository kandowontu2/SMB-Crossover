"""Fresh current-ROM discoveries with retained successful controller policies."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;A=D.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rom=D/'food-candidate-v3/candidate.nes';driver=A/'2026-10-24-roster-pe/matrix-v1/bound-runner.py'
assert sha(rom)=='70480630828a92839938b18b3e4f73acd8f9255879b2174df00f41c2e6cf98c9'
assert sha(driver)=='d6ab9cc1e938923797525704cf6d0e99e16fda6f007b98da1024cb167f00f167'
out=D/'known-routes-v3';out.mkdir(exist_ok=False)
parent=A/'2026-10-24-roster-pn/known-pairs-v1/proof.json';prior=json.loads(parent.read_text());selected={}
for row in prior['runs']:
 assert row['passed'];p=Path(row['folder']);m=json.loads((p/'manifest.json').read_text());assert sha(p/'manifest.json')==row['manifest_sha256']
 selected[(row['identity'],row['mode'])]=p
cv3=A/'2026-10-24-native-items-px/head-routes-v3/results.json'
for row in json.loads(cv3.read_text()):
 assert row['exit']==0 and row['result']['cleared'] and row['result']['deaths']==0
 selected[(row['identity'],row['mode'])]=Path(row['folder'])
assert len(selected)==65
q=dict(passed=False,complete=False,goal_complete=False,phase='discover',ROM_sha256=sha(rom),driver_sha256=sha(driver),wrapper_sha256=sha(Path(__file__)),parent_selection_sha256=sha(parent),CV3_policy_selection_sha256=sha(cv3),selected_cases=65,native_workers=1,runs=[],scope='Fresh actual cold-menu 1-1 discoveries using frozen previously successful controller policies. No equipment/terrain/health/position writes. Each old result is policy selection only; every discovery still needs independent exact replay and physical-frame review. Nine prior failing controller pairs and shortcut coverage remain separate.')
def save():(out/'progress.json').write_text(json.dumps(q,indent=2)+'\n')
save()
for (name,mode),before in selected.items():
 m=json.loads((before/'manifest.json').read_text());policy=before/'policy.lua';assert sha(policy)==m['policy_sha256']
 key=name+'-'+mode;folder=out/('discover-'+key);cmd=[sys.executable,str(driver),name,'--rom',str(rom),'--output',str(folder),'--behavior',mode,'--frames',str(m['config']['limit']),'--capture','12','--chr-commit','--policy',str(policy),'--timeout','180']
 assert sha(rom)==q['ROM_sha256'];t=time.monotonic()
 with(out/(key+'.log')).open('w')as log:p=subprocess.run(cmd,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 path=folder/'manifest.json';new=json.loads(path.read_text())if path.exists()else{};result=new.get('result')or{}
 entry=dict(identity=name,mode=mode,passed=p.returncode==0 and result.get('cleared')is True and result.get('deaths')==0 and new.get('chr_commit',{}).get('passed')is True,exit=p.returncode,folder=str(folder),manifest_sha256=sha(path)if path.exists()else None,policy_sha256=sha(policy),frames=result.get('frames'),deaths=result.get('deaths'),failure=result.get('failure'),seconds=round(time.monotonic()-t,2))
 if path.exists():assert new['ROM_sha256']==q['ROM_sha256']and not new['fixed_replay']
 q['runs'].append(entry);save();print(json.dumps({k:entry[k]for k in ['identity','mode','passed','frames','failure','seconds']}),flush=True)
q.update(complete=True,passed=all(x['passed']for x in q['runs']));save();(out/'discover-results.json').write_text(json.dumps(q,indent=2)+'\n')
raise SystemExit(0 if q['passed']else 1)
