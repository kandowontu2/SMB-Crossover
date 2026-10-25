from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;out=D/'turtle-controls-v1';out.mkdir(exist_ok=False);rows=[]
tail=(D/'remaining-controls-v2/chip-easy.lua').read_text();tail=tail[tail.rfind('local ledges='):].replace('target=2440','target=2412')
for name,mode in [('leonardo','easy'),('leonardo','hard'),('michelangelo','easy')]:
 source=D/'known-routes-v3'/('discover-'+name+'-'+mode)/'policy.lua';t='local normal=(function()\n'+source.read_text()+'\nend)()\n'+tail
 t='local normal=(function()\n'+t+'\nend)()\n'+r'''
local phase='land';local wait=0
return function(c)
 local b=normal(c)
 if c.world~=0 or c.level~=0 then return b end
 if c.x>=1290 and c.x<1496 and phase~='done'then
  if phase=='land'then
   b={right=c.x<1318,left=c.x>1322}
   if c.grounded and c.x>=1314 and c.x<=1326 then wait=wait+1;if wait>=6 and not c.lastA then phase='run'end end
  elseif phase=='run'then
   b={right=true}
   if c.x>=1358 and c.grounded and not c.lastA then phase='jump';b.a=true end
  elseif phase=='jump'then
   b={right=true,a=not c.grounded or c.lastA}
   if c.x>=1450 and c.grounded then phase='done';b.a=false end
  end
 end
 return b
end
'''
 assert 'emu.write('not in t and 'dofile('not in t;p=out/(name+'-'+mode+'.lua');p.write_text(t);rows.append(dict(identity=name,mode=mode,policy=str(p),policy_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
(out/'proof.json').write_text(json.dumps(dict(prepared=True,game_changes=False,memory_writes=False,cases=rows,scope='Controller-only second-gap setup: land on safe ground, release A, run to a later takeoff, then hold a genuine jump. Retain earlier stair-top braking. Original failures remain; no positions, physics, health or terrain edits. Native clear/replay required.'),indent=2)+'\n')
t=(D/'run_remaining_routes_v4.py').read_text().replace("out=D/'remaining-routes-v4'","out=D/'turtle-routes-v1'").replace("D/'remaining-controls-v4/proof.json'","D/'turtle-controls-v1/proof.json'");(D/'run_turtle_routes_v1.py').write_text(t)
