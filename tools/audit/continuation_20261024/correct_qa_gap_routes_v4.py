from pathlib import Path
import hashlib,json,subprocess,sys,time
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=P/'route-corrections-v4';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();driver=D.parent/'2026-10-24-roster-pe/matrix-v1/bound-runner.py'
marker=P/'corrected-direct-v1/proof.json';(O/'queued.json').write_text(json.dumps(dict(waiting_for=str(marker),native_workers=1)))
while not marker.exists():time.sleep(10)
tails={
 'simon':r'''
local phase='approach';local air=false
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 or c.x<2390 or c.x>=2516 then return b end
 if phase=='approach'then
  b.b=false;b.right=c.x<2412;b.left=c.x>2414
  if c.grounded and not c.lastA then b.a=true end
  if not c.grounded then b.a=true end
  if c.x>=2411 and c.x<=2414 and c.y<=112 then phase='land'end
 elseif phase=='land'then
  b={right=c.x<2412,left=c.x>2414}
  if c.grounded and c.y<=112 and not c.lastA then phase='cross';air=false;b={right=true,a=true}end
 else
  b={right=true,a=true}
  if not c.grounded then air=true end
  if air and c.grounded then b.a=false end
 end
 if not c.grounded and c.r('RgDoubleJump')~=0 and c.vy<128 then b.a=not c.lastA end
 return b
end
''',
 'bass':r'''
local phase='approach';local air=false;local lateHold=false
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.x>=1290 and c.x<1496 then
  if phase=='approach'then
   b={right=c.x<1352,left=c.x>1354}
   if c.x>=1351 and c.x<=1354 and c.grounded and not c.lastA then phase='jump';air=false;b={right=true,a=true}end
  elseif phase=='rearm'then
   b={}
   if not c.lastA then phase='jump';air=false;b={right=true,a=true}end
  else
   b={right=true,a=true}
   if not c.grounded then air=true end
   -- The isolated real brick above the pit is a valid intermediate landing.
   -- Release/repress rather than walking off it with the same held A.
   if air and c.grounded and c.x<1456 then phase='rearm';b={}end
  end
 elseif(c.x>=2160 and c.x<2258)or(c.x>=2390 and c.x<2516)then
  if c.grounded and b.a and not c.lastA then lateHold=true end
  if lateHold and not c.grounded then b.a=true end
  if lateHold and c.grounded and c.lastA then lateHold=false end
 end
 return b
end
''',
 'chip':r'''
local phase='approach';local air=false
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 or c.x<2590 or c.x>=2816 then return b end
 if phase=='approach'then
  b.b=false;b.right=c.x<2644;b.left=c.x>2646
  if c.x>=2643 and c.x<=2646 and c.y<=144 then phase='land'end
 elseif phase=='land'then
  b={right=c.x<2644,left=c.x>2646}
  if c.grounded and c.y<=144 and not c.lastA then phase='jump';air=false;b={right=true,a=true}end
 else
  b={right=true,a=true}
  if not c.grounded then air=true end
  if air and c.grounded then b.a=false;phase='done'end
 end
 if phase=='done'then return original(c)end
 return b
end
'''}
report=dict(ROM_sha256=sha(P/'candidate.nes'),phase='discover',complete=False,passed=False,goal_complete=False,runs=[],scope='Three native controller-only gap/platform retries on the unmodified candidate. Prior contacts/gap failures remain retained. No game-state, health, equipment, collision or frame-bound changes.')
for name,mode,batch in [('simon','easy','route-corrections-v2'),('bass','hard','route-corrections-v2'),('chip','easy','remaining-roster-v1')]:
 source=P/batch/(name+'-'+mode);policy=O/(name+'-'+mode+'-policy.lua');policy.write_text('local original=(function()\n'+(source/'policy.lua').read_text()+'\nend)()\n'+tails[name]);out=O/(name+'-'+mode)
 with(O/(name+'-'+mode+'.log')).open('w')as f:p=subprocess.run([sys.executable,str(driver),name,'--rom',str(P/'candidate.nes'),'--output',str(out),'--behavior',mode,'--frames','14000','--capture','12','--chr-commit','--policy',str(policy),'--timeout','200'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 path=out/'manifest.json';m=json.loads(path.read_text())if path.exists()else{};z=m.get('result')or{};row=dict(identity=name,mode=mode,folder=str(out),passed=p.returncode==0 and z.get('cleared')is True and z.get('deaths')==0 and m.get('chr_commit',{}).get('passed')is True,exit=p.returncode,frames=z.get('frames'),failure=z.get('failure'),manifest_sha256=sha(path)if path.exists()else None,policy_sha256=sha(policy))
 report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
report['complete']=True;report['passed']=all(q['passed']for q in report['runs']);(O/'progress.json').write_text(json.dumps(report,indent=2));(O/'replay-index.json').write_text(json.dumps(report,indent=2))
if any(q['passed']for q in report['runs']):
 with(O/'independent-replay.log').open('w')as f:p=subprocess.run([sys.executable,str(D/'streaming-replay-v1/replay.py'),'--rom',str(P/'candidate.nes'),'--discoveries',str(O/'replay-index.json'),'--output',str(P/'gap-direct-v1')],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 report['independent_replay_exit']=p.returncode
(O/'pipeline.json').write_text(json.dumps(report,indent=2))
