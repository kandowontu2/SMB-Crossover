-- Ordinary controller: mount the third pipe, let both Goombas move clear,
-- then descend and attack from the ground. All observations are read-only.
-- The generator encloses the exact inherited C geometry policy as base.
local phase='approach'
local startPoll=0
local tracked={}
local log
local rowCount=0
local function mask(b)
 local v=0
 for k,n in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1})do
  if b[k]then v=v+n end
 end
 return v
end
local function solid(c,x,y)
 local t=c.block(x,y)
 return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
end
local function snapshot(c)
 local actors,shots={},{}
 local count,minx,rightward=0,65535,true
 for slot=0,5 do
  local f,id,st=c.r('Enemy_Flag',slot),c.r('Enemy_ID',slot),c.r('Enemy_State',slot)
  local x=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot)
  local y=c.r('Enemy_Y_Position',slot)
  local dir=c.r('Enemy_MovingDir',slot)
  local hp=c.r('MmEnemyHealthLo',slot)+256*c.r('MmEnemyHealthHi',slot)
  actors[#actors+1]=table.concat({slot,f,id,st,x,y,dir,hp},':')
  if f>0 and f<128 and id==6 and x>=768 and x<912 and st<2 then tracked[slot]=true end
  if tracked[slot] and f>0 and f<128 and id==6 and st<2 then
   count=count+1;minx=math.min(minx,x);rightward=rightward and dir==1
  end
 end
 for slot=0,9 do
  shots[#shots+1]=table.concat({slot,c.r('RgShotType',slot),c.r('RgShotX',slot)+256*c.r('RgShotPage',slot),
   c.r('RgShotY',slot),c.r('RgShotYHigh',slot),c.r('RgShotAge',slot),c.r('RgShotHits',slot),
   c.r('RgShotHitsNow',slot),c.r('RgShotImpact',slot)},':')
 end
 return count,minx,rightward,table.concat(actors,';'),table.concat(shots,';')
end
return function(c)
 local inherited=base(c)
 if phase=='done' or not(c.world==0 and c.level==0 and c.areaType==1)then return inherited end
 if phase=='approach' then
  if c.x<700 or c.grounded then return inherited end
  phase='mount';startPoll=c.poll
 end
 if not log then
  log=assert(io.open(ROSTER_CONFIG.out..'third-pipe-d-controller.csv','w'))
  log:write('frame,poll,phase,x,y,yHigh,state,vx,vy,xFraction,yFraction,facing,power,feetLeft,feetRight,liveTracked,minTrackedX,allRight,inheritedMask,returnedMask,actors,shots\n')
 end
 local n,minx,rightward,actors,shots=snapshot(c)
 local seen=0;for _ in pairs(tracked)do seen=seen+1 end
 local b={b=c.poll%8<4}
 local supportedCap=c.grounded and c.yHigh==1 and c.y==112 and solid(c,c.x+2,144)and solid(c,c.x+13,144)
 if phase=='mount' then
  b.right=c.x<744;b.left=c.x>748;b.a=inherited.a
  if supportedCap then phase='wait';b.a=false;b.right=false;b.left=false end
 elseif phase=='wait' then
  b.right=c.x<744;b.left=c.x>748
  if seen>0 and(n==0 or(minx>=846 and rightward))then phase='drop';b.right=true;b.left=false end
 elseif phase=='drop' then
  b.right=c.x<814;b.left=c.x>818
  if c.grounded and c.yHigh==1 and c.y==176 and solid(c,c.x+8,208)then phase='attack' end
 elseif phase=='attack' then
  b.down=true
  if c.r('PlayerFacingDir')~=1 then b.right=true;b.down=false end
  if seen>0 and n==0 then phase='done';b=inherited end
 end
 rowCount=rowCount+1
 log:write(table.concat({c.frame,c.poll,phase,c.x,c.y,c.yHigh,c.state,c.vx,c.vy,
  c.r('MmXFraction')+256*c.r('MmXFraction',1),c.r('MmYFraction')+256*c.r('MmYFraction',1),
  c.r('PlayerFacingDir'),c.status,c.block(c.x+2,c.y+32),c.block(c.x+13,c.y+32),
  n,minx,tostring(rightward),mask(inherited),mask(b),actors,shots},',')..'\n');log:flush()
 assert(c.poll-startPoll<1200,'Third pipe controller exceeded its bounded ordinary attempt')
 assert(rowCount<1600,'Third pipe controller log cap')
 if phase=='done' then log:close();log=nil end
 return b
end
