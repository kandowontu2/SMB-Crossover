-- Ordinary second-lift traversal from the real B controller prefix.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/policies/agent49-s2-mm-b.lua'))
local phase,off,age='board',0,0
return function(c)
 local b=prior(c)
 if c.lastA then off=0 else off=off+1 end
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=2456 and c.x<2580 and phase~='done'then
  local platform
  for i=0,5 do
   if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==38 then
    local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
    local y=c.r('Enemy_Y_Position',i)
    if math.abs(c.y+32-y)<5 and c.x+15>=x and c.x<x+48 then platform={x=x,y=y};break end
   end
  end
  if phase=='board'then
   if platform and c.grounded then phase='ride';print('MM-S2 rising lift boarded '..c.poll..' X'..c.x..' Y'..c.y)end
   return{right=true}
  elseif phase=='ride'then
   if platform and c.grounded and c.x>=platform.x+36 and off>=6 then phase='jump';age=0;return{right=true,a=true}end
   return{right=true}
  elseif phase=='jump'then
   age=age+1
   if c.grounded and c.x>=2544 then phase='done';print('MM-S2 rising lift exit '..c.poll)end
   return{right=true,a=age<64}
  end
 end
 return b
end
