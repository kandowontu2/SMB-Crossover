local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local prior=assert(dofile(root..'/tools/playthroughs/route_five_first_pit_kd.lua'))
local phase,target,age='approach',nil,0
local plantAge=0
return function(c)
 if c.world==0 and c.level==1 and c.x>=1170 and c.x<1280 and c.char~=1 and phase~='done' then
  if c.grounded and c.y<=112 then phase='done' end
  if phase=='approach' and c.y>112 then
   for x=1200,1264,16 do
    local t=c.block(x+8,152)
    if t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 then target=x-24;phase='back';age=0;break end
   end
   if not target then phase='done' end
  end
  if phase=='back' then
   age=age+1;assert(age<300,'Roof back-off did not settle')
   local vx=(c.vx>=128 and c.vx-256 or c.vx)/16
   local e=target-c.x-6*vx
   if math.abs(c.x-target)<=3 and c.grounded and not c.lastA then phase='rise';age=0 end
   return {right=e>1,left=e< -1}
  elseif phase=='rise' then
   age=age+1;assert(age<100,'Roof vertical mount did not rise')
   if c.y<=112 then phase='onto';age=0 end
   return {a=age<40}
  elseif phase=='onto' then
   age=age+1;assert(age<100,'Roof mount did not land')
   return {right=true,a=age<25}
  end
 end
 if c.char==1 and c.world==0 and c.level==1 and c.x>=1540 and c.x<1640 then
  local plant=false
  for i=0,5 do
   local f=c.r('Enemy_Flag',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   if f>0 and f<128 and c.r('Enemy_ID',i)==13 and c.r('Enemy_State',i)<32 and x>c.x and x<1710 then plant=true end
  end
  if plant then
   plantAge=plantAge+1;assert(plantAge<500,'Piranha combat made no progress')
   if c.x<1568 then return {right=true} end
   if c.r('PlayerFacingDir')~=1 then return {right=true} end
   return {a=c.grounded and not c.lastA or (not c.grounded and c.lastA),b=c.poll%10<4}
  end
 end
 return prior(c)
end
