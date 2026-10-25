from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=P/'route-corrections-v3';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();driver=D.parent/'2026-10-24-roster-pe/matrix-v1/bound-runner.py'
clock=r'''
local tick=0;local previous
return function(c)
 local value=c.r('FrameCounter')
 if previous then tick=tick+((value-previous)&255)end
 previous=value
 local logical={};for k,v in pairs(c)do logical[k]=v end
 logical.frame=tick;logical.poll=tick
 -- Gameplay timers advance per logical update. A physical lag frame should
 -- not shorten a requested held jump or change a timed attack into a tap.
 return original(logical)
end
'''
report=dict(ROM_sha256=sha(P/'candidate.nes'),phase='discover',complete=False,passed=False,goal_complete=False,runs=[],scope='Four fresh controller-only trials whose decisions use the real native logical FrameCounter rather than elapsed physical lag frames. No emulated writes, health/equipment grants, death waiver or previous-failure relabeling.')
for name,mode,batch in [('donatello','easy','remaining-roster-v1'),('simon','easy','route-corrections-v2'),('bass','hard','route-corrections-v2'),('chip','easy','remaining-roster-v1')]:
 source=P/batch/(name+'-'+mode);text=(source/'policy.lua').read_text()
 if name=='simon':
  text='local baseline=(function()\n'+text+'\nend)()\n'+r'''
local phase='approach';local hold=0
return function(c)
 local b=baseline(c)
 if c.world~=0 or c.level~=0 or c.x<2390 or c.x>=2516 then return b end
 if phase=='approach'then
  b.b=false;b.right=c.x<2412;b.left=c.x>2414
  if c.grounded and not c.lastA then hold=36 end
  if hold>0 then b.a=true;hold=hold-1 end
  if c.x>=2411 and c.x<=2414 and c.y<=112 then phase='land'end
 elseif phase=='land'then
  b={right=c.x<2412,left=c.x>2414}
  if c.grounded and c.y<=112 and not c.lastA then phase='cross';hold=36;b={right=true,a=true}end
 else b={right=true,a=hold>0};hold=math.max(0,hold-1)end
 if not c.grounded and c.r('RgDoubleJump')~=0 and c.vy<128 then b.a=not c.lastA end
 return b
end
'''
 policy=O/(name+'-'+mode+'-policy.lua');policy.write_text('local original=(function()\n'+text+'\nend)()\n'+clock)
 out=O/(name+'-'+mode)
 with(O/(name+'-'+mode+'.log')).open('w')as f:p=subprocess.run([sys.executable,str(driver),name,'--rom',str(P/'candidate.nes'),'--output',str(out),'--behavior',mode,'--frames','14000','--capture','12','--chr-commit','--policy',str(policy),'--timeout','200'],cwd=R,stdout=f,stderr=subprocess.STDOUT)
 path=out/'manifest.json';m=json.loads(path.read_text())if path.exists()else{};z=m.get('result')or{}
 row=dict(identity=name,mode=mode,folder=str(out),passed=p.returncode==0 and z.get('cleared')is True and z.get('deaths')==0 and m.get('chr_commit',{}).get('passed')is True,exit=p.returncode,frames=z.get('frames'),failure=z.get('failure'),manifest_sha256=sha(path)if path.exists()else None,policy_sha256=sha(policy))
 report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
report['complete']=True;report['passed']=all(q['passed']for q in report['runs']);(O/'progress.json').write_text(json.dumps(report,indent=2))
index=dict(report);index['runs']=[q for q in report['runs']if q['passed']]
for batch,names in [('route-corrections-v1',{'scrooge'}),('route-corrections-v2',{'link','dale'})]:
 q=json.loads((P/batch/'progress.json').read_text());assert q['complete']
 index['runs'] += [r for r in q['runs']if r['identity']in names and r['passed']]
assert len({(q['identity'],q['mode'])for q in index['runs']})==len(index['runs'])
(O/'replay-index.json').write_text(json.dumps(index,indent=2))
with(O/'independent-replay.log').open('w')as f:p=subprocess.run([sys.executable,str(D/'streaming-replay-v1/replay.py'),'--rom',str(P/'candidate.nes'),'--discoveries',str(O/'replay-index.json'),'--output',str(P/'corrected-direct-v1')],cwd=R,stdout=f,stderr=subprocess.STDOUT)
report['independent_replay_exit']=p.returncode;(O/'pipeline.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(independent_replay_exit=p.returncode)),flush=True)
