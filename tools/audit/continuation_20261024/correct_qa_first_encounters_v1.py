from pathlib import Path
import subprocess,sys,json,hashlib
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=P/'route-corrections-v1';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();driver=D.parent/'2026-10-24-roster-pe/matrix-v1/bound-runner.py'
corrections={
'scrooge':r'''
local seen=false
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 or c.char~=12 or c.r('DarkwingVariant')~=0 or c.status>0 or c.x>448 then return b end
 local item
 for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e and c.r('PowerUpType',i)==0 then item=i;break end end
 if item then
  seen=true
  -- Catch the real mushroom when it walks off the first row. The former
  -- controller repeatedly tried to mount the row while it escaped left.
  if c.y<150 then return {right=c.x<405}end
  return {right=c.x<416,left=c.x>419}
 end
 return b
end
''',
'simon':r'''
local phase='approach';local held=0
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 or c.char~=5 or c.r('Cv3Variant')~=0 or c.x>=330 then return b end
 -- Cross the first Goomba after clearing the coin block's underside. An
 -- early whip can lock movement until the controller reacts too late.
 b.b=false
 local e=c.enemy()
 if e and e.id==6 and e.dx>0 and e.dx<100 and c.x>=230 then
  b.right=true;b.left=false;b.down=false
  if phase=='approach'then
   b.a=false
   if c.x>=264 and c.grounded and not c.lastA then phase='launch';held=8 end
  end
  if phase=='launch'then b.a=true;held=held-1;if not c.grounded then phase='air'end
  elseif phase=='air'then b.a=true;if c.grounded then phase='done';b.a=false end end
 end
 return b
end
'''}
report=dict(ROM_sha256=sha(P/'candidate.nes'),phase='discover',complete=False,passed=False,goal_complete=False,runs=[],scope='Controller-only corrections based on retained failed runs; no code, game state, health or equipment mutation. Failures remain retained. Physical independent replay still required.')
for name,tail in corrections.items():
 base=P/'remaining-roster-v1'/(name+'-easy')/'policy.lua';policy=O/(name+'-policy.lua');policy.write_text('local original=(function()\n'+base.read_text()+'\nend)()\n'+tail)
 out=O/(name+'-easy')
 with(O/(name+'.log')).open('w')as f:p=subprocess.run([sys.executable,str(driver),name,'--rom',str(P/'candidate.nes'),'--output',str(out),'--behavior','easy','--frames','12000','--capture','12','--chr-commit','--policy',str(policy),'--timeout','180'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 path=out/'manifest.json';m=json.loads(path.read_text())if path.exists()else{};z=m.get('result')or{}
 row=dict(identity=name,mode='easy',folder=str(out),passed=p.returncode==0 and z.get('cleared')is True and z.get('deaths')==0 and m.get('chr_commit',{}).get('passed')is True,exit=p.returncode,frames=z.get('frames'),failure=z.get('failure'),manifest_sha256=sha(path)if path.exists()else None,policy_sha256=sha(policy));report['runs'].append(row)
 (O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
report['complete']=True;report['passed']=all(r['passed']for r in report['runs']);(O/'progress.json').write_text(json.dumps(report,indent=2));(O/'replay-index.json').write_text(json.dumps(report,indent=2))
