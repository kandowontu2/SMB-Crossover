"""One source-backed controller-only delayed air-jump retry, after originals."""
from pathlib import Path
import argparse,csv,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=['prepare','run']);p.add_argument('--batch',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--native-grant',action='store_true');a=p.parse_args();out=a.output
 if a.mode=='prepare':
  out.mkdir(parents=True,exist_ok=False);old=a.batch/'native/simon-easy';m=json.loads((old/'manifest.json').read_text());assert not m['result']['cleared']and m['result']['failure']=='death'and m['result']['frames']==3676
  trace=list(csv.DictReader((old/'trace.csv').open()));facts=[z for z in trace if 3609<=int(z['frame'])<=3676];assert next(z for z in facts if z['frame']=='3611')['state']=='0'
  first,body=(old/'policy.lua').read_text().split('\n',1);assert first.startswith('dofile(')
  guard=out/'native-guard.lua';guard.write_bytes((a.batch/'native/native-guard.lua').read_bytes());policy=out/'policy.lua'
  policy.write_text('dofile('+json.dumps(guard.as_posix())+')\nlocal original=(function()\n'+body+'''
end)()
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 or c.x<2370 or c.x>=2516 then return b end
 -- Preserve the unused native air jump until its apex, rather than spending
 -- both A edges two polls apart on the low stair. No physics/state writes.
 if not c.grounded and c.r('RgDoubleJump')~=0 then
  if c.vy<128 then b.a=not c.lastA else b.a=true end
 end
 return b
end
''',encoding='utf-8')
  q=json.loads((a.batch/'readiness.json').read_text());rom=Path(q['command'][q['command'].index('--rom')+1]);source=rom.parent/'source/src/roster.s'
  put(out/'failure-evidence.json',dict(original_failure_manifest=str(old/'manifest.json'),original_failure_manifest_sha256=sha(old/'manifest.json'),original_result=m['result'],trace=facts,source_jump_owner=str(source),source_jump_owner_sha256=sha(source),source_lines='roster.s NotVine/Input/Jump/Launch: ground grants SimonRgDoubleJump1; genuine freshA inair consumesit and callsnativeLaunch.',interpretation='Stair landing3611x2399/y128; firstA3613; release3614; secondA3615whileY115/VY251. Peaknear2427/y71 and descentinto final gap. This is controller timing evidence, no ROM defect claimed.',snapshots=[dict(path=str(old/'frames'/f'{f:06d}.png'),sha256=sha(old/'frames'/f'{f:06d}.png'),scope='Retained discovery screenshot, not an independent directPPU replay')for f in[3600,3624,3648,3660]]))
  b=dict(q['bindings']);files=[Path(__file__),a.batch/'readiness.json',old/'manifest.json',old/'trace.csv',old/'policy.lua',source,guard,policy,out/'failure-evidence.json']+[old/'frames'/f'{f:06d}.png'for f in[3600,3624,3648,3660]];b.update({str(f.resolve()):sha(f)for f in files})
  cmd=[sys.executable,'-B',str(a.batch/'runner.py'),'simon','--rom',str(rom),'--output',str(out/'discovery'),'--mapper','mmc5','--behavior','easy','--frames','18000','--capture','12','--policy',str(policy),'--chr-commit','--timeout','240'];replay=[sys.executable,'-B',str(a.batch/'capture.py'),'--rom',str(rom),'--route',str(out/'discovery'),'--output',str(out/'direct')]
  put(out/'readiness.json',dict(prepared=True,native_run=False,ROM_sha256=q['ROM_sha256'],retained_original_failure=str(old),outside_world0_level0_X2370_2516_original_policy_body_exact=True,original_called_once_everypoll=True,changed_input_only_A_when_unused_airjump_inside_bound=True,guard_byte_exact=True,new_policy_sha256=sha(policy),command=cmd,replay_command=replay,bindings=b,require_original_batch_worker_release=True,rationale='Delay genuine secondAedge untilapex/descent; native jumpvelocity/gravity/collision and every originalguard remain unchanged. One granted retry only, no source/ROM/state edits.'))
  print(json.dumps(dict(prepared=True,readiness_sha256=sha(out/'readiness.json'),policy_sha256=sha(policy),failure_evidence_sha256=sha(out/'failure-evidence.json')),indent=2))
 else:
  assert a.native_grant;assert not(out/'discovery').exists()and not(out/'execution.json').exists();batch=json.loads((a.batch/'execution.json').read_text());assert batch['native_workers_released']
  q=json.loads((out/'readiness.json').read_text());assert all(sha(f)==h for f,h in q['bindings'].items())
  with(out/'discovery-host.log').open('w')as f:r=subprocess.run(q['command'],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
  m=json.loads((out/'discovery/manifest.json').read_text());passed=r.returncode==0 and m['result']['cleared']and m['result']['deaths']==0;rp=None
  if passed:
   with(out/'replay-host.log').open('w')as f:rr=subprocess.run(q['replay_command'],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
   rp=json.loads((out/'direct/proof.json').read_text());passed=passed and rr.returncode==0 and rp['passed']
  z=dict(passed=passed,native_run=True,one_worker_released=True,ROM_sha256=q['ROM_sha256'],original_batch_FALSE_unchanged=True,controller_only=True,readiness_sha256=sha(out/'readiness.json'),result=m['result'],independent_replay=rp);put(out/'execution.json',z);print(json.dumps(z,indent=2));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main()or 0)
