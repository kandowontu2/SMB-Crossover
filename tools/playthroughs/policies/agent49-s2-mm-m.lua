for _,name in ipairs({'MmEnemyHealthLo','MmEnemyHealthHi','MmChargeFrames','MmBulletType','Enemy_ID','Enemy_Flag'})do assert(L[name],name)end
-- Ordinary native flame encounter and a ranged Bowser approach.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/policies/agent49-s2-mm-i.lua'))
local phase,age='wait',0
local bossAir,off,chargeSeen=-1,0,false
local f=assert(io.open(ROSTER_CONFIG.out..'mm-breath-control.csv','w'))
f:write('poll,x,y,state,power,phase,flameX,flameY,bossX,bossY,bossHP,charge,types\n')
return function(c)
 local b=prior(c)
 if c.lastA then off=0 else off=off+1 end
 if c.world==0 and c.level==3 and c.areaType==3 then
  local flame,boss
  for i=0,5 do
   local flag,id=c.r('Enemy_Flag',i),c.r('Enemy_ID',i)
   if flag>0 and flag<128 then
    local p={x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),slot=i,st=c.r('Enemy_State',i)}
    if id==21 and p.x>c.x-24 and(not flame or p.x<flame.x)then flame=p end
    if id==45 then p.hp=c.r('MmEnemyHealthLo',i)+256*c.r('MmEnemyHealthHi',i);boss=p end
   end
  end
  local types={}
  for i=0,3 do types[#types+1]=c.r('MmBulletType',i);if c.r('MmBulletType',i)==3 and not chargeSeen then chargeSeen=true;print('MM-S2 natural full-charge shot observed '..c.poll)end end
  if c.poll%4==0 and c.x>=1450 then f:write(table.concat({c.poll,c.x,c.y,c.state,c.status,phase,flame and flame.x or-1,flame and flame.y or-1,boss and boss.x or-1,boss and boss.y or-1,boss and boss.hp or-1,c.r('MmChargeFrames'),table.concat(types,':')},',')..'\n');f:flush()end
  if c.x>=1510 and c.x<1600 and phase~='done' then
   if phase=='wait' then
    if c.grounded and flame and flame.x-c.x<=84 and flame.x>c.x then phase='air';age=0;print('MM-S2 first breath vertical launch '..c.poll);return{a=true,b=true}end
    return{b=true}
   elseif phase=='air' then
    age=age+1
    if c.grounded and age>10 then phase='walk';print('MM-S2 vertical flame landing '..c.poll..' X'..c.x);return{right=true}end
    return{a=age<72,b=true}
   else
    if c.x>=1594 then phase='done'end
    return{right=true}
   end
  end
  if c.x>=2058 and c.x<2240 and boss and boss.hp>0 and boss.st<32 then
   if c.grounded and off>=6 and flame and flame.x-c.x<100 and flame.x>c.x-12 and flame.y+8>c.y and flame.y<c.y+32 then bossAir=0;return{b=c.poll%8<4,a=true}end
   if bossAir>=0 then bossAir=bossAir+1;if c.grounded and bossAir>10 then bossAir=-1 end end
   return{right=c.x<2072 or(c.x<=2076 and c.r('PlayerFacingDir')~=1),left=c.x>2076,b=c.poll%8<4,a=bossAir>=0 and bossAir<64}
  end
 end
 return b
end
