from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=P/'route-corrections-v5';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();driver=D.parent/'2026-10-24-roster-pe/matrix-v1/bound-runner.py'
assert json.loads((P/'gap-direct-v1/proof.json').read_text())['complete']
tails={
'simon':r'''
local phase='climb';local air=false
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 or c.x<2370 or c.x>=2516 then return b end
 if phase=='climb'then
  b={right=true,a=not c.grounded}
  if c.grounded and not c.lastA then b.a=true end
  -- Simon retains horizontal air momentum. Trigger his genuine second
  -- jump while rising, so he descends onto the final step before its edge.
  if not c.grounded and c.r('RgDoubleJump')~=0 and c.y<=128 then b.a=not c.lastA end
  if c.grounded and c.y<=80 then phase='release';b={}end
 elseif phase=='release'then
  b={}
  if not c.lastA then phase='cross';air=false;b={right=true,a=true}end
 else
  b={right=true,a=true}
  if not c.grounded then air=true end
  if air and c.grounded then b.a=false end
  if not c.grounded and c.r('RgDoubleJump')~=0 and c.vy<128 then b.a=not c.lastA end
 end
 return b
end
''',
'chip':r'''
local phase='approach';local air=false
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 or c.x<2590 or c.x>=2816 then return b end
 if phase=='done'then return b end
 if phase=='approach'then
  b.b=false;b.right=c.x<2630;b.left=c.x>2632
  if c.x>=2629 and c.x<=2632 and c.y<=144 then phase='land'end
 elseif phase=='land'then
  b={right=c.x<2630,left=c.x>2632}
  if c.grounded and c.y<=144 and not c.lastA then phase='jump';air=false;b={right=true,a=true}end
 else
  b={right=true,a=true}
  if not c.grounded then air=true end
  if air and c.grounded then b.a=false;phase='done'end
 end
 return b
end
'''}
report=dict(ROM_sha256=sha(P/'candidate.nes'),phase='discover',complete=False,passed=False,goal_complete=False,runs=[],scope='Controller-only retries using observed native ground landings and original Simon air-jump rules. No emulated writes, synthetic supports, health grants, failure waivers or source changes.')
for name,batch in [('simon','route-corrections-v2'),('chip','remaining-roster-v1')]:
 source=P/batch/(name+'-easy');policy=O/(name+'-policy.lua');policy.write_text('local original=(function()\n'+(source/'policy.lua').read_text()+'\nend)()\n'+tails[name]);out=O/(name+'-easy')
 with(O/(name+'.log')).open('w')as f:p=subprocess.run([sys.executable,str(driver),name,'--rom',str(P/'candidate.nes'),'--output',str(out),'--behavior','easy','--frames','14000','--capture','12','--chr-commit','--policy',str(policy),'--timeout','200'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 path=out/'manifest.json';m=json.loads(path.read_text())if path.exists()else{};z=m.get('result')or{};row=dict(identity=name,mode='easy',folder=str(out),passed=p.returncode==0 and z.get('cleared')is True and z.get('deaths')==0 and m.get('chr_commit',{}).get('passed')is True,exit=p.returncode,frames=z.get('frames'),failure=z.get('failure'),manifest_sha256=sha(path)if path.exists()else None,policy_sha256=sha(policy))
 report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
report['complete']=True;report['passed']=all(q['passed']for q in report['runs']);(O/'progress.json').write_text(json.dumps(report,indent=2));(O/'replay-index.json').write_text(json.dumps(report,indent=2))
if any(q['passed']for q in report['runs']):
 with(O/'independent-replay.log').open('w')as f:p=subprocess.run([sys.executable,str(D/'streaming-replay-v1/replay.py'),'--rom',str(P/'candidate.nes'),'--discoveries',str(O/'replay-index.json'),'--output',str(P/'landing-direct-v1')],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 report['independent_replay_exit']=p.returncode
(O/'pipeline.json').write_text(json.dumps(report,indent=2))
