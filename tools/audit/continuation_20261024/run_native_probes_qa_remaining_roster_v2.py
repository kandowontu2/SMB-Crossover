from pathlib import Path
import json,hashlib,subprocess,sys,time
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;Q=D.parent/'2026-10-24-native-head-pz';P=D/'native-probes-qa-v2';O=P/'remaining-roster-v1';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ROM=P/'candidate.nes';digest=sha(ROM);assert digest=='054d9e33a84f628947b0dea15914ba2aae7796ca610a25548eab96407064384a'
driver=D.parent/'2026-10-24-roster-pe/matrix-v1/bound-runner.py';assert sha(driver)=='d6ab9cc1e938923797525704cf6d0e99e16fda6f007b98da1024cb167f00f167'
prior=json.loads((P/'direct-v1/proof.json').read_text());assert prior['passed']and prior['complete']and prior['ROM_sha256']==digest
reused={(r['identity'],r['mode'])for r in prior['runs']};assert len(reused)==4
selected=[]
for batch in (Q/'direct-v2-34',Q/'finish-v2/direct-last-two'):
 q=json.loads((batch/'proof.json').read_text());assert q['passed']and q['complete']
 for r in q['runs']:
  if(r['identity'],r['mode'])not in reused:selected.append((r['identity'],r['mode'],Path(r['discovery'])))
selected += [('ryu',mode,D/'ryu-head-discovery-v5'/mode)for mode in ('easy','hard')];assert len(selected)==34
report=dict(passed=False,complete=False,goal_complete=False,phase='discover',ROM_sha256=digest,reused_current_hash_four_proof=str(P/'direct-v1/proof.json'),reused_current_hash_four_proof_sha256=sha(P/'direct-v1/proof.json'),driver_sha256=sha(driver),native_workers=1,selected_cases=34,runs=[],scope='Fresh controller discoveries for every remaining identity on the performance candidate, plus both Ryu modes. Prior4 independent replays are exact same hash. No item/fidelity or final completion claim; full current physical replays follow.')
for name,mode,source in selected:
 out=O/(name+'-'+mode);policy=source/'policy.lua';manifest=json.loads((source/'manifest.json').read_text())
 with(O/(name+'-'+mode+'.log')).open('w')as f:p=subprocess.run([sys.executable,str(driver),name,'--rom',str(ROM),'--output',str(out),'--behavior',mode,'--frames',str(manifest['config']['limit']),'--capture','12','--chr-commit','--policy',str(policy),'--timeout','180'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 path=out/'manifest.json';m=json.loads(path.read_text())if path.exists()else{};z=m.get('result')or{}
 row=dict(identity=name,mode=mode,folder=str(out),exit=p.returncode,passed=p.returncode==0 and z.get('cleared')is True and z.get('deaths')==0 and m.get('chr_commit',{}).get('passed')is True,manifest_sha256=sha(path)if path.exists()else None,source_policy_sha256=sha(policy),frames=z.get('frames'),deaths=z.get('deaths'),failure=z.get('failure'))
 report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(completed=len(report['runs']),total=34,**row)),flush=True)
report['complete']=True;report['passed']=all(r['passed']for r in report['runs']);(O/'progress.json').write_text(json.dumps(report,indent=2));(O/'replay-index.json').write_text(json.dumps(report,indent=2))
with(O/'independent-replay.log').open('w')as f:p=subprocess.run([sys.executable,str(D/'streaming-replay-v1/replay.py'),'--rom',str(ROM),'--discoveries',str(O/'replay-index.json'),'--output',str(P/'remaining-direct-v1')],cwd=R,stdout=f,stderr=subprocess.STDOUT)
report['direct_replay_exit']=p.returncode;(O/'pipeline.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(direct_replay_exit=p.returncode,discoveries_passed=report['passed'])),flush=True)
raise SystemExit(0 if report['passed']and p.returncode==0 else 1)
