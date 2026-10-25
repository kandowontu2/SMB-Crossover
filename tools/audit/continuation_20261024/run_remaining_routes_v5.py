"""Current native attempts for nine historically unqualified controller pairs."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;A=D.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rom=D/'food-candidate-v3/candidate.nes';driver=A/'2026-10-24-roster-pe/matrix-v1/bound-runner.py';out=D/'remaining-routes-v5';out.mkdir(exist_ok=False)
known=A/'2026-10-24-roster-pn/known-pairs-v1';general=known/'discover-dale-easy-v1/policy.lua'
cases=[('mario','hard',R/'tools/playthroughs/mario_luigi_scrooge_nav.lua'),('link','easy',general),('link','hard',general),('pit','hard',known/'discover-pit-easy-v1/policy.lua'),('rygar','hard',known/'discover-rygar-easy-v1/policy.lua'),('bass','hard',known/'discover-bass-easy-v1/policy.lua'),('chip','easy',general),('chip','hard',general),('dale','hard',general)]
cases=[(x['identity'],x['mode'],Path(x['policy']))for x in json.loads((D/'remaining-controls-v5/proof.json').read_text())['cases']]
q=dict(passed=False,complete=False,goal_complete=False,phase='discover',ROM_sha256=sha(rom),driver_sha256=sha(driver),native_workers=1,runs=[],scope='Current attempts for nine older unsuccessful controller pairs, using retained real controller policies. No emulator gameplay-state writes. A failed policy is diagnostic evidence, not by itself a game defect. Original strict native outcomes retained.')
def save():(out/'progress.json').write_text(json.dumps(q,indent=2)+'\n')
save()
for name,mode,source in cases:
 key=name+'-'+mode;policy=out/(key+'-policy.lua');text=source.read_text()
 if False:
  assert text.count('local height=32')==1;text=text.replace('local height=32',"local height=(c.char==0 or c.char==8)and(c.r('PlayerSize')~=0 and 16 or 32)or 32")
 assert 'emu.write('not in text and 'dofile('not in text;policy.write_text(text)
 folder=out/('discover-'+key);cmd=[sys.executable,str(driver),name,'--rom',str(rom),'--output',str(folder),'--behavior',mode,'--frames','10000','--capture','12','--chr-commit','--policy',str(policy),'--timeout','180'];t=time.monotonic()
 with(out/(key+'.log')).open('w')as f:p=subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 path=folder/'manifest.json';m=json.loads(path.read_text())if path.exists()else{};result=m.get('result')or{}
 entry=dict(identity=name,mode=mode,passed=p.returncode==0 and result.get('cleared')is True and result.get('deaths')==0 and m.get('chr_commit',{}).get('passed')is True,exit=p.returncode,folder=str(folder),manifest_sha256=sha(path)if path.exists()else None,policy_sha256=sha(policy),frames=result.get('frames'),deaths=result.get('deaths'),failure=result.get('failure'),seconds=round(time.monotonic()-t,2))
 q['runs'].append(entry);save();print(json.dumps({k:entry[k]for k in ['identity','mode','passed','frames','failure','seconds']}),flush=True)
q.update(complete=True,passed=all(x['passed']for x in q['runs']));save();(out/'discover-results.json').write_text(json.dumps(q,indent=2)+'\n')
raise SystemExit(0 if q['passed']else 1)
