-- Controller-only escape from the generic600-frame first-food wait.
-- Full HP and no live food actor justify continuing; no acquisition is claimed.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/full_roster_policy_og.lua'))
local quiet,resuming,finished,jumpAge=0,false,false,-1
local function solid(c,x,y)
 local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2
end
return function(c)
 local b=base(c)
 if c.world~=0 or c.level~=0 or finished then return b end
 local food=false
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then food=true;break end
 end
 if food then quiet=0;resuming=false;return b end
 if resuming and b.right then finished=true;return b end
 if not resuming then
  local waiting=c.x>=300 and c.x<=370 and c.grounded and c.r('KbHealth')==6
   and c.r('TimerControl')==0 and c.r('GuestPowerupActive')==0
   and not(b.right or b.left or b.a or b.b or b.up or b.down)
  quiet=waiting and quiet+1 or 0
  if quiet<64 then return b end
  resuming=true
 end
 -- The same generic route jump/float controls while its old wait times out.
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 local feet=c.y+32
 local obstacle=solid(c,c.x+42,feet-8)or solid(c,c.x+42,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c,c.x+32,y)then support=true;break end end
 local e=c.enemy();local near=e and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<55
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 b={right=true,b=not not near}
 if c.grounded and not c.lastA and(obstacle or not support or danger)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 if not c.grounded and obstacle and c.y>100 then b.up=true;b.a=true end
 if c.r('KbMouth')~=0 then b.down=true;b.b=false end
 return b
end
