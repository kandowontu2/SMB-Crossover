-- Actual fish admission before two grounded coral jumps. The second jump
-- uses the exposed ceiling column, as the historical controller did;
-- this is not proof of traversing below that ceiling.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/policies/agent49-s2-mm-q.lua'))
local column=assert(dofile(root..'/tools/playthroughs/megaman_v34_water_column.lua'))
local admitted=false
local f=assert(io.open(ROSTER_CONFIG.out..'mm-water-column-control.csv','w'))
f:write('poll,x,y,yHigh,state,power,admitted,fishClear,enemies,map\n')
return function(c)
 local b=prior(c)
 if c.world==1 and c.level==1 and c.areaType==0 and c.x>=2020 and c.x<2300 then
  local clear=true
  local es={}
  for i=0,5 do
   local id,flag=c.r('Enemy_ID',i),c.r('Enemy_Flag',i)
   if flag>0 and flag<128 and c.r('Enemy_State',i)<32 then
    local x,y=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),c.r('Enemy_Y_Position',i)
    es[#es+1]=table.concat({i,id,x,y},':')
    if (id==10 or id==11) and x>c.x-30 and x<c.x+110 then clear=false end
   end
  end
  if c.poll%8==0 then
   local map={};for y=32,208,16 do map[#map+1]=y..':'..c.block(2048,y)..'/'..c.block(2064,y)..'/'..c.block(2080,y)end
   f:write(table.concat({c.poll,c.x,c.y,c.yHigh,c.state,c.status,admitted and 1 or 0,clear and 1 or 0,table.concat(es,';'),table.concat(map,';')},',')..'\n');f:flush()
  end
  if not admitted then
   if c.grounded and clear then admitted=true;print('MM-S2 water column fish admission '..c.poll)
   else return{right=c.x<2030,left=c.x>2033,b=c.poll%8<4}end
  end
  return column(c)
 end
 return b
end
