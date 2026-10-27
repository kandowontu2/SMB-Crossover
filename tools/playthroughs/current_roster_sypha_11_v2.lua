-- Controller-only first-block wait recovery; no pickup/ownership claim.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/current_roster_sypha_11_v1.lua'))
local quiet,resuming,finished,jumpAge=0,false,false,-1
local function solid(c,x,y)
 local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2
end
return function(c)
 local b=prior(c)
 if c.char~=5 or c.r('Cv3Variant')~=2 or c.world~=0 or c.level~=0 or finished then return b end
 local item=false
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then item=true;break end
 end
 -- A genuine item keeps the original mature/emergence/pursuit decisions.
 if item then quiet=0;resuming=false;return b end
 if resuming and b.right then finished=true;return b end
 if not resuming then
  local waiting=c.x>=300 and c.x<=370 and c.grounded
   and c.r('TimerControl')==0 and c.r('GuestPowerupActive')==0
   and not(b.right or b.left or b.a or b.b or b.up or b.down)
  quiet=waiting and quiet+1 or 0
  if quiet<64 then return b end
  resuming=true
 end
 -- Ordinary source-controlled walking/jump during the old600-frame wait.
 -- Sypha has no Kirby float or Simon double jump here.
 if c.lastA then jumpAge=jumpAge+1 elseif c.grounded then jumpAge=-1 end
 local feet=c.y+32
 local obstacle=solid(c,c.x+42,feet-8)or solid(c,c.x+42,c.y+8)
 local support=false
 for y=math.min(feet+8,232),232,16 do if solid(c,c.x+32,y)then support=true;break end end
 local e=c.enemy()
 local danger=e and e.dx>0 and e.dx<32 and math.abs(e.y-c.y)<45
 local near=e and e.dx>0 and e.dx<34 and e.x>=c.camera
  and e.y-c.y>=-11 and e.y-c.y<20 and e.id<0x15
  and e.id~=2 and e.id~=8 and e.id~=12
 b={right=true,b=not not(c.poll%8<2 and near)}
 if c.grounded and not c.lastA and(obstacle or not support or danger)then b.a=true;jumpAge=0
 elseif not c.grounded and jumpAge>=0 then b.a=jumpAge<35 end
 return b
end
