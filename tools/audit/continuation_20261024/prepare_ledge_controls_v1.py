"""Read-only controller correction: land on the stair top before crossing."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');A=D.parent
source=D/'known-routes-v3/discover-megaman-easy/policy.lua';out=D/'ledge-controls-v1';out.mkdir(exist_ok=False)
text='local normal=(function()\n'+source.read_text()+'\nend)()\n'+r'''
local ledges={{start=2160,target=2197,finish=2258,phase='approach',wait=0},{start=2390,target=2440,finish=2516,phase='approach',wait=0}}
local hold=0
return function(c)
 local b=normal(c)
 if c.world~=0 or c.level~=0 or c.char~=1 then return b end
 for _,s in ipairs(ledges)do
  if c.x>=s.finish then s.phase='done' end
  if c.x>=s.start and c.x<s.finish and s.phase~='done'then
   if s.phase=='approach'then
    b.right=c.x<s.target;b.left=c.x>s.target+2
    if c.x>=s.target-1 and c.x<=s.target+2 and c.y<=112 then s.phase='land'end
   end
   if s.phase=='land'then
    b={right=c.x<s.target,left=c.x>s.target+2}
    if c.grounded then
     if c.y<=112 then
      s.wait=s.wait+1
      if s.wait>=6 and not c.lastA then s.phase='cross';hold=12;b={right=true,a=true}end
     else s.phase='approach';s.wait=0 end
    end
   elseif s.phase=='cross'then b={right=true,a=hold>0 or c.vy>=128}end
  end
 end
 if hold>0 then b.a=true;hold=hold-1 end
 return b
end
'''
assert 'emu.write('not in text and 'dofile('not in text
p=out/'policy.lua';p.write_text(text)
q=dict(prepared=True,game_changes=False,memory_writes=False,parent_policy_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),policy_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='Mega Man/Proto Man controller-only stair-top landing and fresh held jump edge. No physics, health, powerup, terrain or position changes. Original failed discovery remains retained; a current native clear and independent replay are required.')
(out/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
