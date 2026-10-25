from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=P/'route-corrections-v2';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
driver=D.parent/'2026-10-24-roster-pe/matrix-v1/bound-runner.py'
ledge=r'''
local ledges=LEDGES
local hold=0
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 then return b end
 for _,s in ipairs(ledges)do
  if c.x>=s.finish then s.phase='done'end
  if c.x>=s.start and c.x<s.finish and s.phase~='done'then
   if not s.phase then s.phase='approach';s.wait=0 end
   b.b=false
   if s.phase=='approach'then
    b.right=c.x<s.target;b.left=c.x>s.target+2
    if c.grounded and not c.lastA and c.y>s.top then b.a=true end
    if c.x>=s.target-1 and c.x<=s.target+2 and c.y<=s.top then s.phase='land'end
   end
   if s.phase=='land'then
    b={right=c.x<s.target,left=c.x>s.target+2}
    if c.grounded then
     if c.y<=s.top then
      s.wait=s.wait+1
      if s.wait>=6 and not c.lastA then s.phase='cross';hold=34;b={right=true,a=true}end
     else s.phase='approach';s.wait=0 end
    end
   elseif s.phase=='cross'then b={right=true,a=hold>0}end
  end
 end
 if hold>0 then b.a=true;hold=hold-1 end
 EXTRA
 return b
end
'''
specs=[('link','easy',None,''),
 ('donatello','easy',None,ledge.replace('LEDGES',"{{start=1195,target=1250,top=112,finish=1285},{start=1285,target=1352,top=48,finish=1496},{start=2160,target=2197,top=112,finish=2258},{start=2390,target=2412,top=112,finish=2516}}").replace('EXTRA','')),
 ('dale','hard',None,ledge.replace('LEDGES',"{{start=2160,target=2197,top=112,finish=2258},{start=2390,target=2440,top=112,finish=2516}}").replace('EXTRA','')),
 ('simon','easy',P/'route-corrections-v1/simon-easy',r'''
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.x>=1140 and c.x<1496 then
  b.b=false
  if c.grounded and not c.lastA then b.a=true;b.right=true;b.left=false end
  if not c.grounded and c.r('RgDoubleJump')~=0 and c.vy<128 then b.a=not c.lastA end
 end
 return b
end
'''),
 ('bass','hard',None,r'''
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 or c.x<1152 or c.x>1320 then return b end
 local enemy=c.enemy()
 if c.grounded and enemy and enemy.dx>0 then
  -- Bass can aim while the native ground-firing state keeps him stationary.
  -- Remove the real enemies above the row before advancing beneath them.
  return {right=true,up=enemy.y<c.y-28,b=true}
 end
 return b
end
'''),
 ('chip','easy',None,r'''
local held=0
return function(c)
 local b=original(c)
 if c.world~=0 or c.level~=0 or c.x<2680 or c.x>2760 then return b end
 local e=c.enemy()
 if e and e.dx>0 and e.dx<110 and e.y>150 then
  b={}
  if c.grounded and e.dx<38 and not c.lastA then held=36 end
  if held>0 then b.a=true;held=held-1 end
 end
 return b
end
''')]
report=dict(ROM_sha256=sha(P/'candidate.nes'),phase='discover',complete=False,passed=False,goal_complete=False,runs=[],scope='Fresh controller-only route corrections. The previous failed inputs remain retained. No emulated state, equipment, health or source changes; successful discoveries still need independent physical replay.')
for name,mode,source,tail in specs:
 source=source or P/'remaining-roster-v1'/(name+'-'+mode)
 policy=O/(name+'-'+mode+'-policy.lua')
 text=(source/'policy.lua').read_text()
 policy.write_text('local original=(function()\n'+text+'\nend)()\n'+tail if tail else text)
 out=O/(name+'-'+mode)
 with(O/(name+'-'+mode+'.log')).open('w')as f:
  p=subprocess.run([sys.executable,str(driver),name,'--rom',str(P/'candidate.nes'),'--output',str(out),'--behavior',mode,'--frames','14000','--capture','12','--chr-commit','--policy',str(policy),'--timeout','200'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 path=out/'manifest.json';m=json.loads(path.read_text())if path.exists()else{};z=m.get('result')or{}
 row=dict(identity=name,mode=mode,folder=str(out),passed=p.returncode==0 and z.get('cleared')is True and z.get('deaths')==0 and m.get('chr_commit',{}).get('passed')is True,exit=p.returncode,frames=z.get('frames'),failure=z.get('failure'),manifest_sha256=sha(path)if path.exists()else None,policy_sha256=sha(policy))
 report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
report['complete']=True;report['passed']=all(r['passed']for r in report['runs']);(O/'progress.json').write_text(json.dumps(report,indent=2));(O/'replay-index.json').write_text(json.dumps(report,indent=2))
