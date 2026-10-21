-- Read-only controller feedback. An elevated enemy is above the standing or
-- crouched floor muzzle; launch before the first staircase instead of waiting
-- beneath it and repeatedly firing below its hit rectangle.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_castle_drop500.lua'))
local hold=0
return function(c)
 c.lastA=(c.r('PreviousA_B_Buttons')&128)~=0
 if c.world==1 and c.level==0 and c.x<480 then
  local e
  for i=0,5 do
   local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
   if flag>0 and flag<128 and id<0x15 and id~=13 and st<0x20 then
    local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
    local dx=x-c.x;local y=c.r('Enemy_Y_Position',i)
    if dx>0 and dx<112 and(not e or dx<e.dx)then e={dx=dx,y=y}end
   end
  end
  if hold==0 and c.grounded and not c.lastA and e and e.y<c.y-8 and e.dx<90 then hold=28 end
  if hold>0 then hold=hold-1;return {right=true,a=true,b=c.poll%8<3}end
 end
 return base(c)
end
