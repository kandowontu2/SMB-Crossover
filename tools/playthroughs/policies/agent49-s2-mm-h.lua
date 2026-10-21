-- Ordinary-input floorbar crossing; native phase is read, never changed.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/policies/agent49-s2-mm-g.lua'))
local phase,age='approach',0
local f=assert(io.open(ROSTER_CONFIG.out..'mm-floorbar-control.csv','w'))
f:write('poll,phase,x,y,state,power,angle,low\n')
return function(c)
 local b=prior(c)
 if c.world==0 and c.level==3 and c.areaType==3 and c.x>=1208 and c.x<1460 and phase~='done' then
  local bar
  for i=0,5 do
   if c.r('Enemy_Flag',i)>0 and c.r('Enemy_Flag',i)<128 and c.r('Enemy_ID',i)==29 and c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)==1348 then
    bar={angle=c.r('FirebarSpinState_High',i),low=c.r('FirebarSpinState_Low',i)}
   end
  end
  if c.poll%4==0 then f:write(table.concat({c.poll,phase,c.x,c.y,c.state,c.status,bar and bar.angle or-1,bar and bar.low or-1},',')..'\n');f:flush()end
  if phase=='approach' then
   if c.grounded and c.x>=1274 then phase='wait';return{} end
   return{right=c.x<1276}
  elseif phase=='wait' then
   if bar and c.grounded and not c.lastA and bar.angle==10 then phase='air';age=0;print('MM-S2 floorbar admission '..c.poll..' X'..c.x);return{right=true,a=true}end
   return{right=c.x<1274,left=c.x>1278}
  elseif phase=='air' then
   age=age+1
   if c.grounded and age>10 then phase='walk';print('MM-S2 floorbar landing '..c.poll..' X'..c.x)end
   return{right=true,a=age<64}
  elseif phase=='walk' then
   if c.x>=1452 then phase='done';print('MM-S2 mixed firebar corridor passed '..c.poll)end
   return{right=true}
  end
 end
 return b
end
