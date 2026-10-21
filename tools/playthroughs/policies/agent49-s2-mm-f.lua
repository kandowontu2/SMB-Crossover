-- Ordinary moving-platform traversal; all geometry is native read-only state.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/policies/agent49-s2-mm-e.lua'))
local phase,off,age='approach',0,0
local f=assert(io.open(ROSTER_CONFIG.out..'mm-platform-control.csv','w'))
f:write('poll,phase,x,y,state,firstX,secondX,off\n')
return function(c)
 local b=prior(c)
 if c.lastA then off=0 else off=off+1 end
 if c.world==0 and c.level==2 and c.x>=1270 and c.x<1600 and phase~='done'then
  local one,two
  for i=0,5 do
   if c.r('Enemy_Flag',i)>0 and c.r('Enemy_Flag',i)<128 and c.r('Enemy_ID',i)==40 then
    local p={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i)}
    if p.y==128 then one=p elseif p.y==144 then two=p end
   end
  end
  if c.poll%4==0 then f:write(table.concat({c.poll,phase,c.x,c.y,c.state,one and one.x or-1,two and two.x or-1,off},',')..'\n');f:flush()end
  if phase=='approach'then
   if c.grounded and c.x>=1294 and off>=6 then phase='first-air';age=0;return{right=true,a=true}end
   return{right=c.x<1295}
  elseif phase=='first-air'then
   age=age+1
   if c.grounded and one and math.abs(c.y+32-one.y)<5 and c.x+14>=one.x then phase='first-ride';age=0;print('MM-S2 actual first moving platform '..c.poll)end
   local target=one and one.x+14 or 1340
   return{right=c.x<target-2,left=c.x>target+2,a=age<64}
  elseif phase=='first-ride'then
   if not one then return{}end
   local target=one.x+30
   if two and c.grounded and math.abs(c.x-target)<4 and two.x-one.x-48<=48 and off>=6 then phase='second-air';age=0;return{right=true,a=true}end
   return{right=c.x<target-2,left=c.x>target+2}
  elseif phase=='second-air'then
   age=age+1
   if c.grounded and two and math.abs(c.y+32-two.y)<5 and c.x+14>=two.x then phase='second-ride';age=0;print('MM-S2 actual second moving platform '..c.poll)end
   local target=two and two.x+14 or 1470
   return{right=c.x<target-2,left=c.x>target+2,a=age<64}
  elseif phase=='second-ride'then
   if not two then return{}end
   local target=two.x+30
   if c.grounded and math.abs(c.x-target)<4 and 1568-two.x-48<=60 and off>=6 then phase='bank-air';age=0;return{right=true,a=true}end
   return{right=c.x<target-2,left=c.x>target+2}
  elseif phase=='bank-air'then
   age=age+1
   if c.grounded and c.x>=1558 and c.y>=128 then phase='done';print('MM-S2 moving platforms cleared '..c.poll)end
   return{right=c.x<1584,left=c.x>1588,a=age<64}
  end
 end
 return b
end
