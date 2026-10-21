-- Ordinary control only, based on the actual G/H final-lift trajectory.
local phase='approach'
local began,at,launchAt,target
local log
local function xof(c,i)return c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)end
local function live(c,i)
 return i~=nil and c.r('Enemy_Flag',i)==1 and c.r('Enemy_ID',i)==0x26 and c.r('Enemy_State',i)==0
end
local function supported(c,i)
 return live(c,i)and c.r('Enemy_Y_HighPos',i)==1 and c.grounded and c.yHigh==1
 and c.r('PlatformCollisionFlag',i)==i and c.y+32==c.r('Enemy_Y_Position',i)
 and c.x+2>=xof(c,i)and c.x+13<xof(c,i)+48
end
local function go(p,c)phase=p;at=c.poll end
local function mask(b)
 local m=0;for k,n in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1})do if b[k]then m=m+n end end
 return m
end
return function(c)
 local inherited=base(c)
 if c.char~=6 or c.world~=0 or c.level~=1 or c.areaType~=2 or c.area~=37 or phase=='done'then return inherited end
 if not began then
  if c.x<2390 or c.x>2432 then return inherited end
  began=c.poll;at=c.poll
  log=assert(io.open(ROSTER_CONFIG.out..'pit-final-lift-i-controller.csv','w'))
  log:write('frame,poll,phase,age,phaseAge,x,y,state,grounded,vy,qYFraction,previousAB,jumpUsed,target,feetLeft,feetRight,actors,inherited,returned\n')
 end
 local b={b=c.poll%8<4}
 if phase=='approach'then
  b.right=c.x<2418;b.left=c.x>2421
  if c.grounded and c.yHigh==1 and c.y==176 and c.x>=2418 and c.x<=2421
  and c.block(c.x+8,208)~=0 and not c.lastA and(c.r('PreviousA_B_Buttons')&128)==0 then
   -- Choose from CURRENT takeoff data after the offscreen wrap, not
   -- the earlier approach where both copies can be above the player.
   target=nil
   for i=0,5 do
    if live(c,i)and c.r('Enemy_Y_HighPos',i)==1 and xof(c,i)>=2450 and xof(c,i)<=2500
    and c.r('Enemy_Y_Position',i)>=208 then target=i end
   end
   if target~=nil then go('lift-air',c);launchAt=c.poll;b.right=true;b.left=false;b.a=true end
  end
 elseif phase=='lift-air'then
  assert(live(c,target),'Pit I2 target lift identity retained')
  local goal=xof(c,target)+16
  b.right=c.x<goal;b.left=c.x>goal+2;b.a=c.poll-launchAt<34
  if supported(c,target)then go('ride',c);b.a=false;b.right=false;b.left=false end
 elseif phase=='ride'then
  assert(live(c,target),'Pit I2 supported lift identity retained')
  local goal=xof(c,target)+16
  b.right=c.x<goal;b.left=c.x>goal+2
  if supported(c,target)and c.r('Enemy_Y_Position',target)<=128
  and c.block(2560,160)==0x52 and c.block(2576,160)==0x52
  and not c.lastA and(c.r('PreviousA_B_Buttons')&128)==0 then
   go('bank-air',c);launchAt=c.poll;b.right=true;b.left=false;b.a=true
  end
 elseif phase=='bank-air'then
  b.right=c.x<2584;b.left=c.x>2586;b.a=c.poll-launchAt<34
  if c.grounded and c.yHigh==1 and c.y==128 and c.x>=2576
  and c.block(c.x+2,160)==0x52 and c.block(c.x+13,160)==0x52 then
   go('done',c);b=inherited
  end
 end
 local actors={}
 for i=0,5 do actors[#actors+1]=table.concat({i,c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i),
  xof(c,i),c.r('Enemy_Y_Position',i),c.r('Enemy_Y_HighPos',i),c.r('Enemy_YMoveForceFractional',i),
  c.r('Enemy_Y_MoveForce',i),c.r('Enemy_Y_Speed',i),c.r('PlatformCollisionFlag',i)},':')end
 log:write(table.concat({c.frame,c.poll,phase,c.poll-began,c.poll-at,c.x,c.y,c.state,c.grounded and 1 or 0,c.vy,
  c.r('MmYFraction')+256*c.r('MmYFraction',1),c.r('PreviousA_B_Buttons'),c.r('XgJumpUsed'),target or -1,
  c.block(c.x+2,math.min(239,c.y+32)),c.block(c.x+13,math.min(239,c.y+32)),table.concat(actors,';'),
  mask(inherited),mask(b)},',')..'\n');log:flush()
 assert(c.poll-began<1000,'Pit I2 finite real lift mount/ride/bank attempt')
 if phase=='done'then log:close();log=nil end
 return b
end
