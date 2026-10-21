-- Under-ceiling trial from the real lower2080..2095 coral step.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/policies/agent49-s2-mm-r.lua'))
local late=assert(dofile(root..'/tools/playthroughs/megaman_v34_water_second_coral.lua'))
local phase,age,off='lower-step',0,0
local f=assert(io.open(ROSTER_CONFIG.out..'mm-water-underpass-control.csv','w'))
f:write('poll,phase,x,y,yHigh,state,power,xFraction,yFraction,vx24,vy24,collisionBits,sideTimer,pose,crouch,off,tiles\n')
local function word(c,n)return c.r(n)+256*c.r(n,1)end
local function trip(c,n)return c.r(n)+256*c.r(n,1)+65536*c.r(n,2)end
return function(c)
 local b=prior(c)
 if c.lastA then off=0 else off=off+1 end
 if c.world==1 and c.level==1 and c.areaType==0 and c.x>=2050 and c.x<2320 then
  local map={}
  for _,x in ipairs({2064,2080,2096,2176,2224,2240,2256})do
   if x>=c.camera and x<c.camera+256 then
    local row={};for y=32,208,16 do row[#row+1]=c.block(x,y)end
    map[#map+1]=x..':'..table.concat(row,'/')
   end
  end
  f:write(table.concat({c.poll,phase,c.x,c.y,c.yHigh,c.state,c.status,word(c,'MmXFraction'),word(c,'MmYFraction'),trip(c,'MmVX'),trip(c,'MmVY'),c.r('Player_CollisionBits'),c.r('SideCollisionTimer'),c.r('MmRenderPose'),c.r('CrouchingFlag'),off,table.concat(map,';')},',')..'\n');f:flush()
  if phase=='lower-step' then
   if c.grounded and c.y>=140 and c.x>=2086 then phase='lip';return{}end
   return{right=c.x<2088,left=c.x>2091}
  elseif phase=='lip' then
   if c.grounded and c.x>=2091 and off>=6 then phase='cross';age=0;print('MM-S2 below-ceiling lip jump '..c.poll..' Y'..c.y);return{right=true,a=true}end
   return{right=c.x<2092}
  elseif phase=='cross' then
   age=age+1
   if c.grounded and age>10 and c.x>=2220 then phase='done';print('MM-S2 underpass supported landing '..c.poll..' X'..c.x)end
   return{right=true,a=age<80,b=c.poll%8<4}
  else
   return late(c)
  end
 end
 if c.world==1 and c.level==1 and c.areaType==0 and c.x>=2320 then return late(c)end
 return b
end
