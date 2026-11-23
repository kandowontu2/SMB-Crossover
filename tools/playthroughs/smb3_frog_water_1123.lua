-- Ordinary menu-selected2-1 rewards, retained Frog traversal, then2-2 swimming.
local acquire=assert(SMB3_ACTION_ACQUIRE)
local A={phase='acquire',requested='Frog',target=4,changes={}}
SMB3_ACTION_STATE=A
local F={phase='acquire',changes={},segments={},checkpoints={}}
SMB3_FROG_WATER=F
local jumpAt=-100
local spring='approach'
local function change(c,p)
 F.phase=p;F.at=c.motor
 F.changes[#F.changes+1]={phase=p,motor=c.motor,update=c.update,x=c.x,y=c.y}
 assert(#F.changes<=40,'Finite Frog route phases')
end
local function solid(c,x,y)
 local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3
end
local function signed(v)return v>=128 and v-256 or v end
local function steer(c,goal)
 local vx=signed(c.vx);local dx=goal-c.x;local stop=vx*vx/24+6
 if vx>2 and dx<=stop then return{left=true}end
 if vx< -2 and -dx<=stop then return{right=true}end
 return{right=dx>3,left=dx< -3}
end
local function gapPhase(c,g,phase)
 g.phase=phase;g.at=c.motor
 g.changes[#g.changes+1]={phase=phase,motor=c.motor,x=c.x,y=c.y,vx=c.vx}
 assert(#g.changes<=10,'Finite authored pipe/pit phases')
end
local function pipeGap(c)
 local g=F.gap
 if not g then g={phase='stage',at=c.motor,start=c.motor,changes={}};F.gap=g end
 assert(c.motor-g.start<480,'Finite ordinary pipe/pit crossing')
 local vx=signed(c.vx)
 if g.phase=='stage'then
  if c.grounded and c.y<=112 and c.x>=1640 and c.x<=1672 then
   g.pipe_landing={motor=c.motor,x=c.x,y=c.y};gapPhase(c,g,'pipe-release')
  elseif c.grounded and c.y==48 and math.abs(c.x-1512)<=3 and vx==0
      and c.r('M3Previous')&128==0 then
   assert(solid(c,1520,80),'Stand on the actual1472-to1535 authored brick ledge')
   local actors={}
   for i=0,5 do
    if c.r('Enemy_Flag',i)>0 then
     actors[#actors+1]={slot=i,id=c.r('Enemy_ID',i),state=c.r('Enemy_State',i),
      x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i)}
    end
   end
   g.bridge_transfer=true;g.bridge_staging={motor=c.motor,x=c.x,y=c.y,vx=c.vx,actors=actors}
   g.climb_input={motor=c.motor,x=c.x,y=c.y};gapPhase(c,g,'climb-pipe')
   return{right=true,b=true,a=true}
  else local b=steer(c,1512);b.a=not c.grounded and c.motor-jumpAt<32;return b end
 end
 if g.phase=='climb-pipe'then
  assert(c.motor-g.at<120,'Actual normal jump reaches the authored pipe top')
  if g.bridge_transfer and not g.bridge_jump and c.r('M3Native::Player_InAir')~=0
     and c.r('M3Native::Player_YVel')>=128 and c.r('SavedJoypadBits')&128~=0 then
   g.bridge_jump={motor=c.motor,x=c.x,y=c.y,native_air=c.r('M3Native::Player_InAir'),
    native_vy=c.r('M3Native::Player_YVel'),input=c.r('SavedJoypadBits')}
  end
  if c.grounded and c.y<=112 and c.x>=1640 and c.x<=1672 and c.motor-g.at>4 then
   g.pipe_landing={motor=c.motor,x=c.x,y=c.y};gapPhase(c,g,'pipe-release')
  else
   if g.bridge_transfer and c.x<1640 then return{right=true,b=true,a=c.motor-g.at<32}end
   local b=steer(c,1656);b.a=c.motor-g.at<32;return b
  end
 end
 if g.phase=='pipe-release'then
  assert(c.motor-g.at<80,'Settle on the32px authored pipe top with A released')
  if c.grounded and c.y==112 and math.abs(c.x-1656)<=4 and vx==0 and c.r('M3Previous')&128==0 then
   g.jump_input={motor=c.motor,x=c.x,y=c.y};gapPhase(c,g,'gap-launch')
   return{right=true,b=true,a=true}
  end
  return steer(c,1656)
 end
 if g.phase=='gap-launch'then
  assert(c.motor-g.at<12,'Actual fresh A starts the pipe-to-bank jump')
  if g.jump and g.jump.after then gapPhase(c,g,'cross-bank')
  else return{right=true,b=true,a=true}end
 end
 if g.phase=='cross-bank'then
  local b=steer(c,1752);b.b=true;b.a=c.motor-g.jump.before.motor<32
  if c.grounded and c.motor-g.jump.before.motor>8 then
   assert(c.x>=1744 and c.y==176,'Completed pipe jump lands beyond the48px pit')
   g.bank_landing={motor=c.motor,x=c.x,y=c.y};gapPhase(c,g,'land-bank');b.a=false;b.b=false
  end
  return b
 end
 assert(g.phase=='land-bank','Known pipe-to-bank continuation')
 return steer(c,1752)
end
local function plantAhead(c)
 local best
 for i=0,5 do
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);local dx=x-c.x
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==13 and dx>16 and dx<=144
     and(not best or dx<best.dx)then best={slot=i,x=x,dx=dx}end
 end
 return best
end
local function plantCross(c,plant)
 local g=F.plant_active
 if not g then
  F.plants=F.plants or{};assert(#F.plants<8,'Bounded authored Piranha pipes')
  g={phase='approach',slot=plant.slot,x=plant.x,at=c.motor};F.plant_active=g;F.plants[#F.plants+1]=g
 end
 assert(c.motor-g.at<480 and c.r('Enemy_ID',g.slot)==13,'Finite live authored plant crossing')
 local goal=g.x-28
 if g.phase=='enemy-jump'then
  local e=g.enemy;local state=c.r('Enemy_State',e.slot)
  if state>=2 or c.r('Enemy_Flag',e.slot)==0 then g.phase='enemy-recover'
  else
   assert(c.motor-g.enemy_at<90,'Actual approach stomp finishes before reaching the plant')
   local b=steer(c,g.enemy_goal);b.a=c.motor-g.enemy_at<18;return b
  end
 end
 if g.phase=='enemy-recover'then
  if not c.grounded or c.r('M3Previous')&128~=0 then return{}end
  g.phase='approach'
 end
 if g.phase=='approach'then
  local nearest
  for i=0,5 do
   local id=c.r('Enemy_ID',i);local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);local dx=x-c.x
   if c.r('Enemy_Flag',i)>0 and(id==0 or id==6)and c.r('Enemy_State',i)<2 and dx>=0 and dx<=64
      and x<g.x-16 and c.r('Enemy_Y_Position',i)>=c.y-16 and(not nearest or dx<nearest.dx)then
    nearest={slot=i,id=id,x=x,dx=dx,vx=c.r('Enemy_X_Speed',i)}
   end
  end
  if nearest and c.grounded then
   local vx=signed(c.vx)
   if vx>0 then return{left=true}end
   if vx<0 then return{right=true}end
   if nearest.vx<128 then return{}end
   if nearest.dx<=32 and c.r('M3Previous')&128==0 then
    g.enemy=nearest;g.enemy_goal=math.min(c.x+20,g.x-40);g.enemy_at=c.motor;g.phase='enemy-jump'
    return{right=true,a=true}
   end
   return{}
  end
  local distance=g.x-c.x
  local elevated=c.y<176 and c.y<=c.r('PiranhaPlantDownYPos',g.slot)and distance>=40 and distance<=96
  if c.grounded and((distance>=24 and distance<=32)or elevated)and c.vx==0 and c.r('M3Previous')&128==0 then
   g.phase='wait';g.elevated=elevated
  else return steer(c,goal)end
 end
 if g.phase=='wait'then
  local y=c.r('Enemy_Y_Position',g.slot);local down=c.r('PiranhaPlantDownYPos',g.slot)
  -- Nearby ground starts suppress rising altogether. An elevated start can be
  -- farther away, so use the actual64-frame pause freshly set at full retraction.
  local timer=c.r('EnemyFrameTimer',g.slot)
  if y==down and c.r('PiranhaPlant_MoveFlag',g.slot)==0 and(not g.elevated or timer>=40)then
   g.retracted={motor=c.motor,x=c.x,y=c.y,plant_y=y,down=down,distance=g.x-c.x,timer=timer}
   g.jump_input={motor=c.motor,x=c.x,y=c.y};g.jump_at=c.motor;g.phase='cross'
   return{right=true,b=true,a=true}
  end
  return{}
 end
 if g.phase=='cross'then
  -- Keep a real landing on this pipe when the next authored pipe rises higher.
  -- Dropping to the floor here leaves an80px wall above Frog's standing jump.
  if not g.next_step then
   for i=0,5 do
    local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
    if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==13 and x>g.x and x-g.x<=96
       and c.r('PiranhaPlantDownYPos',i)<c.r('PiranhaPlantDownYPos',g.slot)then
     g.next_step={slot=i,x=x,down=c.r('PiranhaPlantDownYPos',i)};break
    end
   end
  end
  if g.next_step then
   local goal=g.x+8;local vx=signed(c.vx)
   if c.grounded and c.y==c.r('PiranhaPlantDownYPos',g.slot)-32 and math.abs(c.x-goal)<=4
      and vx==0 and c.r('M3Previous')&128==0 and c.motor-g.jump_at>8 then
    g.clear={motor=c.motor,x=c.x,y=c.y};g.complete=g.clear;F.plant_active=nil;return{}
   end
   local b=steer(c,goal);b.b=true;b.a=c.motor-g.jump_at<32;return b
  end
  if c.x>=g.x+24 then g.clear={motor=c.motor,x=c.x,y=c.y};g.phase='brake'
  else return{right=true,b=true,a=c.motor-g.jump_at<32}end
 end
 assert(g.phase=='brake','Known retracted-plant crossing phase')
 local vx=signed(c.vx)
 if vx>0 then return{left=true}end
 if vx<0 then return{right=true}end
 if c.grounded then g.complete={motor=c.motor,x=c.x,y=c.y};F.plant_active=nil end
 return{}
end
local function laterPit(c,key,stage,edge,bank)
 key=key or'pit2';stage=stage or 2196;edge=edge or 2224;bank=bank or 2272
 local g=F[key]
 if not g then g={phase='approach',at=c.motor,edge=edge,bank=bank};F[key]=g end
 assert(c.motor-g.at<480,'Finite authored later pit continuation')
 if g.phase=='stomp'then
  if c.r('Enemy_Flag',g.enemy.slot)==0 or c.r('Enemy_State',g.enemy.slot)>=2 then g.phase='recover'
  else
   assert(c.motor-g.stomp_at<90,'Actual pre-pit ground enemy stomp')
   local b=steer(c,g.stomp_goal);b.a=c.motor-g.stomp_at<18;return b
  end
 end
 if g.phase=='recover'then
  if not c.grounded or c.r('M3Previous')&128~=0 then return{}end
  g.phase='approach'
 end
 if g.phase=='approach'then
  local nearest
  for i=0,5 do
   local id=c.r('Enemy_ID',i);local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);local dx=x-c.x
   if c.r('Enemy_Flag',i)>0 and(id==0 or id==6)and c.r('Enemy_State',i)<2 and dx>=0 and dx<=80
      and x<edge and c.r('Enemy_Y_Position',i)>=160 and(not nearest or dx<nearest.dx)then
    nearest={slot=i,id=id,x=x,dx=dx,vx=c.r('Enemy_X_Speed',i)}
   end
  end
  if nearest and c.grounded then
   g.last_enemy=nearest
   local vx=signed(c.vx)
   if vx>0 then return{left=true}end
   if vx<0 then return{right=true}end
   if nearest.vx>0 and nearest.vx<128 then return{}end
   if nearest.dx<=32 and c.r('M3Previous')&128==0 then
    g.enemy=nearest;g.stomp_at=c.motor;g.stomp_goal=math.min(c.x+16,edge-16);g.phase='stomp'
    return{right=true,a=true}
   end
   if nearest.vx==0 then return steer(c,math.min(stage,nearest.x-28))end
   return{}
  end
  if c.grounded and c.y==176 and math.abs(c.x-stage)<=3 and c.vx==0 and c.r('M3Previous')&128==0 then
   g.jump_input={motor=c.motor,x=c.x,y=c.y};g.jump_at=c.motor;g.phase='launch'
   return{right=true,b=true,a=true}
  end
  local b=steer(c,stage)
  -- Preserve the already accepted hopping-enemy jump while settling before
  -- the next hole; the separate pit jump starts only after an actual landing.
  b.a=not c.grounded and c.motor-jumpAt<32;return b
 end
 if g.phase=='launch'then
  assert(c.motor-g.jump_at<12,'Actual fresh A starts the second authored pit jump')
  if c.r('M3Native::Player_InAir')~=0 and c.r('M3Native::Player_YVel')>=128 and c.r('SavedJoypadBits')&128~=0 then
   g.jump={motor=c.motor,x=c.x,y=c.y,native_air=c.r('M3Native::Player_InAir'),native_vy=c.r('M3Native::Player_YVel')}
   g.phase='cross'
  else return{right=true,b=true,a=true}end
 end
 if g.phase=='cross'then
  assert(c.motor-g.jump_at<100,'Complete the48px authored hole with the native jump')
  if c.grounded and c.motor-g.jump_at>8 then
   assert(c.x>=bank and c.y==176,'Actual later pit jump lands on its authored far bank')
   g.landing={motor=c.motor,x=c.x,y=c.y};g.phase='land';g.ground=0
  elseif key=='pit3'and c.x>=bank then
   local vx=signed(c.vx);return{left=vx>0,right=vx<0,a=c.motor-g.jump_at<32}
  else return{right=true,b=true,a=c.motor-g.jump_at<32}end
 end
 assert(g.phase=='land','Known second authored pit continuation')
 local vx=signed(c.vx)
 if vx>0 then return{left=true}end
 if vx<0 then return{right=true}end
 assert(c.grounded and c.y==176 and c.x>=bank,'Retain the actual later far-bank landing')
 if g.last_motor~=c.motor then g.ground=g.ground+1;g.last_motor=c.motor end
 if g.ground==25 then g.complete={motor=c.motor,x=c.x,y=c.y}end
 return{}
end
local function axis(pos,goal,v)
 local distance=goal-pos;local stop=math.abs(v)*(math.abs(v)+1)/32+2
 if distance>3 and not(v>0 and distance<=stop)then return 1 end
 if distance< -3 and not(v<0 and -distance<=stop)then return -1 end
 return 0
end
local tests={
 {'right',1,16},{'right-release',0,20},{'left',2,16},{'left-release',0,20},
 {'up',8,16},{'up-release',0,20},{'down',4,16},{'down-release',0,20},
 {'right-A',129,8},{'right-A-release',0,36},{'left-A',130,8},{'left-A-release',0,36},
 {'up-A',136,8},{'up-A-release',0,36},{'down-A',132,8},{'down-A-release',0,36},
 {'retained-neutral',0,25}}
local function buttons(mask)
 return {a=mask&128~=0,up=mask&8~=0,down=mask&4~=0,left=mask&2~=0,right=mask&1~=0}
end
return function(c)
 if not A.acquired then return acquire(c)end
 assert(c.r('M3Form')==4,'Real earned Frog remains owned')
 if F.phase=='acquire'then change(c,'traverse-2-1')end
 if c.world==1 and c.level==0 then
  assert(c.areaType==1,'Use the full ground2-1 route without a bonus-pipe shortcut')
  assert(c.x<=3330 or F.flag,'Stop if the ordinary route misses the authored2-1 flag')
  if c.x>=2944 and c.x<3072 then
   local animation=c.r('JumpspringAnimCtrl')
   if spring=='approach'then
    if animation>0 then spring='compress';F.spring_compress={motor=c.motor,x=c.x,y=c.y,animation=animation};return{}end
    if c.grounded and c.x>=2990 and c.r('M3Previous')&128==0 then jumpAt=c.motor end
    return {right=c.x<3008,left=c.x>3012,a=c.motor-jumpAt<16}
   elseif spring=='compress'then
    if animation==0 and c.vy>=128 then
     spring='cross';F.spring_release={motor=c.motor,x=c.x,y=c.y,vy=c.vy}
     return {right=true,a=true}
    end
    return {a=animation>=2 and animation<=4}
   end
   return {right=true,b=true,a=F.spring_release and c.motor-F.spring_release.motor<24}
  end
  if c.x>=1472 and c.x<1808 and not(F.gap and F.gap.complete)then return pipeGap(c)end
  if F.gap and F.gap.complete then
   local plant=F.plant_active or plantAhead(c)
   if plant then return plantCross(c,plant)end
  end
  if c.x>=2128 and c.x<2352 and not(F.pit2 and F.pit2.complete)then return laterPit(c)end
  if c.x>=2336 and c.x<2544 and not(F.pit3 and F.pit3.complete)then return laterPit(c,'pit3',2404,2432,2464)end
  local obstacle=solid(c,c.x+38,c.y+8)or solid(c,c.x+38,c.y+24)
  local support=false
  for y=math.min(c.y+40,232),232,16 do if solid(c,c.x+34,y)then support=true;break end end
  local e=c.enemy();local danger=e and e.dx>8 and e.dx<60 and e.y>=c.y-24 and e.y<=c.y+72
  -- Native$0e hops only about42px above the ground. Notice it while it is
  -- above the standing collision band, rather than waiting for its descent.
  for i=0,5 do
   local dx=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)-c.x;local y=c.r('Enemy_Y_Position',i)
   if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==14 and dx>8 and dx<72 and y>=c.y-80 and y<=c.y+72 then danger=true end
  end
  if c.grounded and c.r('M3Previous')&128==0 and c.motor-jumpAt>20 and(obstacle or not support or danger)then
   jumpAt=c.motor;F.jumps=(F.jumps or 0)+1;assert(F.jumps<=50,'Bounded ordinary Frog traversal jumps')
  end
  return {right=true,b=true,a=c.motor-jumpAt<32}
 end
 assert(c.world==1 and c.level==1,'Only2-1 followed by2-2 is admitted')
 assert(F.flag and F.castle,'Authenticated flag and castle precede2-2')
 if F.phase=='traverse-2-1'then change(c,'water-position')end
 if F.phase=='water-position'then
  assert(c.areaType==0,'Actual2-2 water room')
  local vx=signed(c.r('M3Native::Player_XVel'));local vy=signed(c.r('M3Native::Player_YVel'))
  local hx=axis(c.x,112,vx);local hy=axis(c.y,112,vy)
  if math.abs(c.x-112)<=4 and math.abs(c.y-112)<=4 and vx==0 and vy==0
     and c.r('M3Native::Player_InWater')==1 then
   F.water_origin={motor=c.motor,x=c.x,y=c.y};F.test_index=1;change(c,'water-checks')
  else return{right=hx==1,left=hx==-1,down=hy==1,up=hy==-1}end
 end
 assert(F.phase=='water-checks','Known finite Frog swimming phase')
 assert(c.x>=48 and c.x<=176 and c.yHigh==1 and c.y>=48 and c.y<=192,
  'Keep actual swim exercises inside the visible opening water corridor')
 local test=assert(tests[F.test_index])
 if not F.segment then
  F.segment={name=test[1],mask=test[2],wanted=test[3],returns=0,stale=0,at=c.motor}
  F.segments[#F.segments+1]=F.segment
 end
 local q=F.segment
 assert(c.motor-q.at<120,'Bounded actual swim-input acceptance and movement')
 if q.returns>=q.wanted then
  if q.mask==0 then
   assert(c.r('M3Native::Player_XVel')==0 and c.r('M3Native::Player_YVel')==0,
    'Released swimming input naturally removes both native inertias')
  end
  q.done={motor=c.motor,x=c.x,y=c.y};F.segment=nil;F.test_index=F.test_index+1
  if F.test_index>#tests then F.complete=true;return{}end
  test=tests[F.test_index]
  F.segment={name=test[1],mask=test[2],wanted=test[3],returns=0,stale=0,at=c.motor}
  F.segments[#F.segments+1]=F.segment
 end
 return buttons(test[2])
end
