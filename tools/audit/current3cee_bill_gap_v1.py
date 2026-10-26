"""One evidenced controller-only late-takeoff retry; no game-state writes."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','run']);p.add_argument('--batch',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--native-grant',action='store_true');a=p.parse_args();out=a.output
 if a.mode=='prepare':
  out.mkdir(parents=True,exist_ok=False);old=a.batch/'native/bill-easy';m=json.loads((old/'manifest.json').read_text());assert not m['result']['cleared']and m['result']['failure']=='death'
  src=(old/'policy.lua').read_text();first,body=src.split('\n',1);assert first.startswith('dofile(')
  guard=out/'native-guard.lua';guard.write_bytes((a.batch/'native/native-guard.lua').read_bytes())
  policy=out/'policy.lua';policy.write_text('dofile('+json.dumps(guard.as_posix())+')\nlocal original=(function()\n'+body+'''
end)()
local phase,held,air='approach',0,false
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 or c.x<1304 or c.x>=1490 then return b end
 if phase=='approach' then
  if c.x>=1356 and c.grounded and not c.lastA then
   phase='jump';held=120;air=false
  else return{right=true} end
 end
 if phase=='jump' then
  if not c.grounded then air=true end
  if air and c.grounded then phase='landed';return b end
  held=held-1;return{right=true,a=held>0}
 end
 return b
end
''',encoding='utf-8')
  ready=json.loads((a.batch/'readiness.json').read_text());bindings=dict(ready['bindings']);bindings.update({str(f.resolve()):sha(f)for f in[Path(__file__),a.batch/'readiness.json',old/'manifest.json',old/'trace.csv',old/'policy.lua',guard,policy]})
  runner=a.batch/'runner.py';capture=a.batch/'capture.py';rom=Path(ready['command'][ready['command'].index('--rom')+1])
  command=[sys.executable,'-B',str(runner),'bill','--rom',str(rom),'--output',str(out/'discovery'),'--mapper','mmc5','--behavior','easy','--frames','18000','--capture','12','--policy',str(policy),'--chr-commit','--timeout','240']
  replay=[sys.executable,'-B',str(capture),'--rom',str(rom),'--route',str(out/'discovery'),'--output',str(out/'direct')]
  q=dict(prepared=True,native_run=False,ROM_sha256=ready['ROM_sha256'],retained_original_failure=str(old),source_manifest_sha256=sha(old/'manifest.json'),source_policy_sha256=sha(old/'policy.lua'),new_policy_sha256=sha(policy),outside_1304_1490_original_policy_body_exact=True,guard_byte_exact=True,command=command,replay_command=replay,bindings=bindings,
   rationale='Old grounded takeoff atx1323 spent most source jump arc before pit1376..1439 and failed at1419/y245. Controller now releases A and walks to a fresh grounded takeoff near1356, then holds Right/A until landing. No physics/outcome/resource/position writes; all original guards and limits retained.')
  put(out/'readiness.json',q);print(json.dumps(dict(prepared=True,readiness_sha256=sha(out/'readiness.json'),new_policy_sha256=sha(policy))))
 else:
  assert a.native_grant;assert not(out/'discovery').exists()and not(out/'execution.json').exists()
  batch=json.loads((a.batch/'execution.json').read_text());assert batch['native_workers_released'],'Original pipeline must release before this one worker is reused'
  q=json.loads((out/'readiness.json').read_text());assert all(sha(f)==h for f,h in q['bindings'].items())
  with(out/'discovery-host.log').open('w')as f:r=subprocess.run(q['command'],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
  m=json.loads((out/'discovery/manifest.json').read_text());passed=r.returncode==0 and m['result']['cleared']and m['result']['deaths']==0;rp=None
  if passed:
   with(out/'replay-host.log').open('w')as f:rr=subprocess.run(q['replay_command'],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
   rp=json.loads((out/'direct/proof.json').read_text());passed=passed and rr.returncode==0 and rp['passed']
  z=dict(passed=passed,native_run=True,one_worker_released=True,ROM_sha256=q['ROM_sha256'],original_batch_FALSE_unchanged=True,controller_only=True,readiness_sha256=sha(out/'readiness.json'),result=m['result'],independent_replay=rp)
  put(out/'execution.json',z);print(json.dumps(z,indent=2));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main()or 0)
