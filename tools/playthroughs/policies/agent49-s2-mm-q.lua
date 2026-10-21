-- Let actual high Cheeps pass while on the low floor, before rising.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/policies/agent49-s2-mm-p.lua'))
local phase,age,off='wait',0,0
local f=assert(io.open(ROSTER_CONFIG.out..'mm-water-coral-control.csv','w'))
f:write('poll,phase,x,y,state,power,fishClear,blooperLow,off,enemies,map\n')
return function(c)
 local b=prior(c)
 if c.lastA then off=0 else off=off+1 end
 if c.world==1 and c.level==1 and c.areaType==0 and c.x>=1376 and c.x<1580 and phase~='done' then
  local fishClear,blooperLow=true,true
  local es={}
  for i=0,5 do
   local id,flag=c.r('Enemy_ID',i),c.r('Enemy_Flag',i)
   if flag>0 and flag<128 and c.r('Enemy_State',i)<32 then
    local x,y=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),c.r('Enemy_Y_Position',i)
    es[#es+1]=table.concat({i,id,x,y},':')
    if (id==10 or id==11) and x>c.x-30 and x<c.x+180 then fishClear=false end
    if id==7 and math.abs(x-c.x)<140 and y<144 then blooperLow=false end
   end
  end
  if c.poll%8==0 then
   local map={};for y=48,208,16 do map[#map+1]=y..':'..c.block(1440,y)..'/'..c.block(1456,y)..'/'..c.block(1472,y)end
   f:write(table.concat({c.poll,phase,c.x,c.y,c.state,c.status,fishClear and 1 or 0,blooperLow and 1 or 0,off,table.concat(es,';'),table.concat(map,';')},',')..'\n');f:flush()
  end
  if phase=='wait' then
   if c.grounded and fishClear and blooperLow and off>=6 then phase='air';age=0;print('MM-S2 water fish admission '..c.poll);return{right=true,a=true,b=true}end
   return{right=c.x<1390,left=c.x>1393,b=c.poll%8<4}
  else
   age=age+1
   if c.grounded and age>10 then
    if c.x>=1450 and c.y<=128 then phase='done';print('MM-S2 second coral landed '..c.poll)
    else phase='wait' end
    return{}
   end
   return{right=true,a=age<80,b=c.poll%8<4}
  end
 end
 return b
end
