-- Ordinary inputs from the genuine S2 A prefix. Read-only native lift state.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/megaman_v34_water_late_wall.lua'))
local phase,age,off='approach',0,0
local f=assert(io.open(ROSTER_CONFIG.out..'mm-native-state.csv','w'))
f:write('poll,frame,phase,x,y,state,power,ownedLo,ownedHi,selected,ammo,platforms,enemies\n')
local function solid(c,x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 end
local function actors(c)
 local platforms,raw={},{}
 for i=0,5 do
  local flag,id=c.r('Enemy_Flag',i),c.r('Enemy_ID',i)
  if flag>0 and flag<128 then
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   local y=c.r('Enemy_Y_Position',i)
   raw[#raw+1]=table.concat({i,id,x,y,c.r('Enemy_State',i),c.r('MmEnemyHealthLo',i)+256*c.r('MmEnemyHealthHi',i)},':')
   if id>=0x24 and id<=0x2c then
    local box=c.r('Enemy_BoundBoxCtrl',i)
    platforms[#platforms+1]={slot=i,id=id,x=x,y=y,width=box==6 and 48 or box==5 and 32 or 24}
   end
  end
 end
 return platforms,table.concat(raw,';')
end
return function(c)
 local ps,raw=actors(c)
 local selected=c.r('InvSelected',c.char)
 local pr={};for _,p in ipairs(ps)do pr[#pr+1]=table.concat({p.slot,p.id,p.x,p.y,p.width},':')end
 if c.poll%4==0 then f:write(table.concat({c.poll,c.frame,phase,c.x,c.y,c.state,c.status,c.r('InvOwnedLo',c.char),c.r('InvOwnedHi',c.char),selected,c.r('InvAmmo',c.char*16+selected),table.concat(pr,';'),raw},',')..'\n');f:flush()end
 if c.lastA then off=0 else off=off+1 end
 if c.world==0 and c.level==1 and c.areaType==2 and c.x>=2144 and c.x<2336 and phase~='done'then
  local lift
  for _,p in ipairs(ps)do if p.x>=2224 and p.x<2336 then lift=p;break end end
  if phase=='approach'then
   if c.grounded and c.x>=2202 and c.x<=2207 then phase='wait';return{}end
   return{right=c.x<2202,left=c.x>2207}
  elseif phase=='wait'then
   if c.grounded and off>=6 and lift and lift.y>=64 and lift.y<=104 then
    phase='onto-lift';age=0;print('MM-S2 native first lift admission '..c.poll..' X'..lift.x..' Y'..lift.y)
    return{right=true,a=true}
   end
   return{}
  elseif phase=='onto-lift'then
   age=age+1
   if c.grounded and c.x>=2224 and not solid(c,c.x+8,c.y+34)then phase='release';age=0;return{}end
   return{right=true,a=age<64}
  elseif phase=='release'then
   age=age+1;if age>=6 then phase='lip'end
   return{}
  elseif phase=='lip'then
   if lift and c.grounded and c.x+20>=lift.x+lift.width and off>=6 then phase='next-bank';age=0;return{right=true,a=true}end
   return{right=true}
  elseif phase=='next-bank'then
   age=age+1
   if c.grounded and c.x>=2328 and solid(c,c.x+8,c.y+34)then phase='done';print('MM-S2 native first lift cleared '..c.poll)end
   return{right=true,a=age<64}
  end
 end
 return prior(c)
end
