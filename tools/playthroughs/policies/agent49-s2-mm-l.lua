-- Wait on the controller-reached upper step, above the actual flame lane.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/policies/agent49-s2-mm-k.lua'))
local phase,saw,age='wait',false,0
local f=assert(io.open(ROSTER_CONFIG.out..'mm-flame-cap-control.csv','w'))
f:write('poll,phase,x,y,state,power,flameX,flameY,charge,types\n')
return function(c)
 local b=prior(c)
 if c.world==0 and c.level==3 and c.x>=1510 and c.x<1600 and phase~='done' then
  local flame
  for i=0,5 do
   if c.r('Enemy_Flag',i)>0 and c.r('Enemy_Flag',i)<128 and c.r('Enemy_ID',i)==21 then
    local p={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i)}
    if not flame or math.abs(p.x-c.x)<math.abs(flame.x-c.x)then flame=p end
   end
  end
  local types={};for i=0,3 do types[#types+1]=c.r('MmBulletType',i)end
  if c.poll%4==0 then f:write(table.concat({c.poll,phase,c.x,c.y,c.state,c.status,flame and flame.x or-1,flame and flame.y or-1,c.r('MmChargeFrames'),table.concat(types,':')},',')..'\n');f:flush()end
  if phase=='wait' then
   age=age+1;saw=saw or flame~=nil
   if c.grounded and saw and flame and flame.x<c.x-24 and age>8 then phase='walk';print('MM-S2 actual flame passed under upper step '..c.poll);return{right=true}end
   return{b=true}
  else
   if c.x>=1594 then phase='done' end
   return{right=true}
  end
 end
 return b
end
