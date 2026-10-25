from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;source=D/'remaining-routes-v1/mario-hard-policy.lua';out=D/'mario-gap-controls-v2';out.mkdir(exist_ok=False)
t='local normal=(function()\n'+source.read_text()+'\nend)()\n'+r'''
local phase='land';local hold=0
return function(c)
 local b=normal(c)
 if c.char~=0 or c.world~=0 or c.level~=0 then return b end
 if c.x>=1280 and c.x<1490 and phase~='done'then
  if phase=='land'then
   b={right=c.x<1328,left=c.x>1336}
   if c.grounded and c.x>=1324 and c.x<=1340 then phase='release';hold=4 end
  elseif phase=='release'then
   b={};hold=hold-1
   if hold<=0 and not c.lastA then phase='cross';hold=34;b={right=true,b=true,a=true}end
  elseif phase=='cross'then
   b={right=true,b=true,a=hold>0};hold=hold-1
   if c.x>=1450 and c.grounded then phase='done'end
  end
 end
 return b
end
'''
assert 'emu.write('not in t and 'dofile('not in t
p=out/'policy.lua';p.write_text(t);(out/'proof.json').write_text(json.dumps(dict(prepared=True,game_changes=False,memory_writes=False,source_policy_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),policy_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='Stop the old automatic enemy/brick jump on solid ground before the second floor gap, release A, then make a fresh held running jump. Controller only; no game-state or terrain writes. Native clear/replay remain required.'),indent=2)+'\n')
