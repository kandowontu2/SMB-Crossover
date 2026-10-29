-- Genuine first-mushroom attempt: approach beneath the row before jumping.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local travel=assert(dofile(root..'/tools/playthroughs/supermaaa_11_v2.lua'))
local phase='first-enemy'
local held=0
local age=0
return function(c)
 local b=travel(c)
 if c.world~=0 or c.level~=0 or c.status>0 or phase=='done' then return b end
 local e=c.enemy()
 local actor
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then
   actor={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i)}
  end
 end
 if phase=='first-enemy' then
  b={right=c.x<276,b=false}
  if e and e.id==6 and e.dx>0 and e.dx<48 and c.grounded and not c.lastA then held=32 end
  if held>0 then b.a=true;held=held-1 end
  if c.x>=276 and c.grounded and c.y>=160 then phase='align' end
 elseif phase=='align' then
  b={right=c.x<330,left=c.x>334}
  if c.x>=330 and c.x<=334 and c.grounded and c.y>=160 then phase='bump';age=0 end
 elseif phase=='bump' then
  b={right=c.x<330,left=c.x>334,a=age<30};age=age+1
  if age>60 and c.grounded then age=0 end
  if actor then phase='back' end
 elseif phase=='back' then
  b={left=c.x>286,right=c.x<284}
  if c.x>=284 and c.x<=286 and c.grounded then phase='mount';age=0 end
 elseif phase=='mount' then
  b={a=age<32,b=true,right=age>7};age=age+1
  if actor and c.x>=actor.x-8 then phase='collect' end
  if age>65 and c.grounded and c.y>144 then phase='back' end
 elseif phase=='collect' then
  if not actor then phase='done';return b end
  b={right=c.x<actor.x-3,left=c.x>actor.x+3,a=c.grounded and not c.lastA}
 end
 return b
end
