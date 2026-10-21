-- Do not shoot indefinitely into a solid pipe at its retracted plant.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/policies/agent49-s2-mm-o.lua'))
local jump,off=-1,0
local f=assert(io.open(ROSTER_CONFIG.out..'mm-21-pipe-control.csv','w'))
f:write('poll,x,y,state,power,slot,plantX,plantY,down,move,off,jump,map\n')
return function(c)
 local b=prior(c)
 if c.lastA then off=0 else off=off+1 end
 if c.world==1 and c.level==0 and c.x>=1800 and c.x<2060 then
  local plant
  for i=0,5 do
   if c.r('Enemy_Flag',i)>0 and c.r('Enemy_Flag',i)<128 and c.r('Enemy_ID',i)==13 then
    local p={slot=i,x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),down=c.r('PiranhaPlantDownYPos',i),move=c.r('PiranhaPlant_MoveFlag',i)}
    if p.x>=c.x-16 and p.x<c.x+128 and(not plant or p.x<plant.x)then plant=p end
   end
  end
  if c.poll%8==0 then
   local map={};for y=96,208,16 do map[#map+1]=y..':'..c.block(c.x+16,y)..'/'..c.block(c.x+32,y)end
   f:write(table.concat({c.poll,c.x,c.y,c.state,c.status,plant and plant.slot or-1,plant and plant.x or-1,plant and plant.y or-1,plant and plant.down or-1,plant and plant.move or-1,off,jump,table.concat(map,';')},',')..'\n');f:flush()
  end
  if jump>=0 then
   jump=jump+1
   if c.grounded and jump>10 then jump=-1;return{}end
   return{right=true,a=jump<64}
  end
  if plant and c.grounded then
   if plant.x-c.x<=30 then
    if off>=6 and plant.y==plant.down and plant.move==0 then jump=0;print('MM-S2 retracted plant pipe jump '..c.poll..' slot'..plant.slot);return{right=true,a=true}end
    return{}
   end
   return{right=true}
  end
 end
 return b
end
