-- Route discovery uses read-only telemetry and controller inputs. Final fixed
-- input replays will be verified independently from power-on.
local frame,poll=0,0
local replay={}
if RUN_REPLAY then
 for line in io.lines(RUN_REPLAY) do local p,f,m=line:match('^(%d+),(%d+),(%d+)$');if p then replay[tonumber(p)]={frame=tonumber(f),mask=tonumber(m)} end end
end
local r=function(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local bridgeStop
local done=false
local rawAddEvent,rawAddMemory=emu.addEventCallback,emu.addMemoryCallback
local function guarded(fn)
 return function(...)
  if done then return end
  local ok,result=pcall(fn,...)
  if not ok then done=true;print('FAIL replay harness: '..tostring(result));if bridgeStop then bridgeStop() end;emu.stop(1) end
  return result
 end
end
emu.addEventCallback=function(fn,...) return rawAddEvent(guarded(fn),...) end
emu.addMemoryCallback=function(fn,...) return rawAddMemory(guarded(fn),...) end
local phase='approach'
local jumpFrames=0
local goalIndex=1
local goals={
 {x=336,y=144,kind='upgrade'},
 {x=1024,y=128,kind='life'},
 {x=1248,y=144,kind='upgrade'},
 {x=1616,y=144,kind='star'},
 {x=1744,y=80,kind='upgrade',support=1744},
}
if RUN_ROUTE=='pipe' then goals={goals[1]} end
local pipeUsed=false
local pipeEntryCommitted=false
local goal=goals[1]
local goalsBeforeStatus=0
local goalRevealed=false
local jumpAge=-1
local lastA=false
local pickupSerial=0
local goalPickupSerial=0
local nextLevelControl=0
local nextLevelX
local cleared=false
local mountStep='back'
local upperStep='back'
local settleX,settlePhase
local sophiaStep='align'
local ryuStep='align'
local luigiGapReady=false
local function aim(b,x,target)
 local raw=r('Player_X_Speed');local v=(raw>=128 and raw-256 or raw)/16
 if RUN_CHARACTER==2 or RUN_CHARACTER==3 or RUN_CHARACTER==5 or (RUN_CHARACTER>=6 and RUN_CHARACTER~=8) then
  b.right=x<target-2;b.left=x>target+2
  return math.abs(x-target)<=2
 end
 local e=target-x-4*v
 if RUN_CHARACTER==8 then
  local rawv=r('MmVX')+256*r('MmVX',1)+65536*r('MmVX',2)
  v=(rawv>=8388608 and rawv-16777216 or rawv)/65536
  local speed=math.abs(v);local distance=0;local acceleration=200/7200
  if r('Player_State')==0 then
   -- The corrected source skid is exponential, not constant deceleration.
   for i=1,180 do
    speed=speed-acceleration
    if speed<=0 then break end
    speed=speed*0.0001^(1/60);distance=distance+speed
   end
  else distance=speed*speed/(2*acceleration) end
  e=target-x-(v<0 and -distance or distance)
 end
 b.right=e>1;b.left=e< -1
 return math.abs(x-target)<=3 and math.abs(v)<0.5
end
local function fight(b,x,enemy,distance)
 b.right=false;b.left=false
 if RUN_CHARACTER>=6 and r('Player_State')==0 and r('Enemy_Y_Position',enemy)>r('Player_Y_Position')+32 then
  b.left=true
  return
 end
 if RUN_CHARACTER==2 then
  local high=r('Enemy_Y_Position',enemy)<r('Player_Y_Position')-32
  if not high and r('Enemy_ID',enemy)==6 then
   -- Stomp Goombas; bombs remain useful against the other ground enemies.
   b.down=false;b.up=r('SmBall')>0 and poll%2==0
   local ex=r('Enemy_PageLoc',enemy)*256+r('Enemy_X_Position',enemy)
   if r('SmBall')==0 then
    if r('Player_State')==0 then b.a=not lastA
    elseif r('Player_Y_Position')<r('Enemy_Y_Position',enemy)-32 then aim(b,x,ex) end
   end
   return
  end
  if not high and r('Player_State')~=0 and r('SmBall')==0 and jumpAge>=0 then b.right=true;return end
  if high then
   b.up=poll%2==0;b.b=poll%8==0
   local ex=r('Enemy_PageLoc',enemy)*256+r('Enemy_X_Position',enemy)
   aim(b,x,ex-4)
   if r('Player_State')==0 then b.a=not lastA end
  else
   b.down=true;b.b=poll%8==0
   if math.abs(distance)<48 then b.left=distance>0;b.right=distance<0 end
  end
  return
 end
 if RUN_CHARACTER==0 and pipeUsed and r('PlayerStatus')<2 and distance<0 and distance> -30 and r('Player_State')==0 then b.right=true;return end
 local direction=distance<0 and 2 or 1
 if r('PlayerFacingDir')~=direction then b.left=direction==2;b.right=direction==1;return end
 if (RUN_CHARACTER==0 or RUN_CHARACTER==8) and r('PlayerStatus')<2 then
  local ex=r('Enemy_PageLoc',enemy)*256+r('Enemy_X_Position',enemy)
  local ey=r('Enemy_Y_Position',enemy)
  if ey<144 and r('Player_Y_Position')>=144 then
   if r('Player_State')==0 then
    aim(b,x,ex-4)
    if math.abs(x-ex+4)<8 then b.a=true end
   else b.a=jumpAge<35 end
   return
  end
  if r('Player_State')==0 and math.abs(distance)<35 then b.a=true end
  if r('Player_State')~=0 then
   if r('Player_Y_Position')<ey-32 then
    if RUN_CHARACTER==8 then aim(b,x,ex-4) else b.right=x<ex-3;b.left=x>ex+3 end
   end
   b.a=jumpAge<35
  end
 elseif RUN_CHARACTER==4 or RUN_CHARACTER==5 or RUN_CHARACTER==10 then
  local range=RUN_CHARACTER==4 and 39 or RUN_CHARACTER==10 and 27 or 53
  if math.abs(distance)<range and r('RgAttack')==0 then b.b=true end
  if RUN_CHARACTER==10 and math.abs(distance)>=range then b.select=poll%8==0 end
  if r('Enemy_Y_Position',enemy)<r('Player_Y_Position')-24 and r('Player_State')==0 then b.a=true end
 elseif RUN_CHARACTER==3 then b.down=true;b.b=poll%8==0
 else
  b.b=poll%8==0
  if RUN_CHARACTER==6 or RUN_CHARACTER==7 then b.down=r('Player_State')==0 end
 end
end
local inputs=assert(io.open(RUN_OUTPUT..'inputs.csv','w'));inputs:write('poll,frame,mask\n')
local trace=assert(io.open(RUN_OUTPUT..'trace.csv','w'));trace:write('frame,phase,x,y,state,vx,vy,status,engine,mode,task,area,lives,camera,bounce,enemyCount,powerX,powerY,powerState,upperStep,enemies,world,level,areaType\n')
local events=assert(io.open(RUN_OUTPUT..'events.csv','w'));events:write('frame,event,slot,value,x,y\n')
local function capture(name)
 local f=assert(io.open(RUN_OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
if RUN_RECORD then
 local start=assert(package.loadlib(RUN_BRIDGE,'luaopen_capture_start'))
 bridgeStop=assert(package.loadlib(RUN_BRIDGE,'luaopen_capture_stop'));start()
end
local function powerup()
 for i=0,5 do if r('Enemy_Flag',i)>0 and r('Enemy_ID',i)==0x2e then return i,r('Enemy_PageLoc',i)*256+r('Enemy_X_Position',i),r('Enemy_Y_Position',i),r('Enemy_State',i) end end
end
local function block(wx,wy)
 if wy<32 or wy>=240 then return 0 end
 local o=math.floor(wx/256)%2*208+math.floor((wy-32)/16)*16+math.floor(wx%256/16)
 return r('Block_Buffer_1',o)
end
local function nearestEnemy(x)
 local chosen,dist
 for i=0,5 do
  local id=r('Enemy_ID',i);local st=r('Enemy_State',i)
  if r('Enemy_Flag',i)>0 and id<0x15 and st<0x20 and not(id==6 and st>=2) then
   local d=r('Enemy_PageLoc',i)*256+r('Enemy_X_Position',i)-x
   if d> -200 and d<120 and (not dist or math.abs(d)<math.abs(dist)) then chosen=i;dist=d end
  end
 end
 return chosen,dist
end
emu.addMemoryCallback(function(a,v)
 if frame<500 then return end
 local name= a==L.PlayerStatus and 'power' or 'sound'
 events:write(table.concat({frame,name,a,v,r('Player_PageLoc')*256+r('Player_X_Position'),r('Player_Y_Position')},',')..'\n')
end,emu.callbackType.write,L.PlayerStatus)
emu.addMemoryCallback(function(a,v)
 if a==L.Square2SoundQueue and (v&0x60)>0 then pickupSerial=pickupSerial+1 end
 if frame>=500 and v>0 then events:write(table.concat({frame,'sfx',a,v,r('Player_PageLoc')*256+r('Player_X_Position'),r('Player_Y_Position')},',')..'\n') end
end,emu.callbackType.write,L.NoiseSoundQueue,L.Square1SoundQueue)
emu.addMemoryCallback(function(a,v)
 if frame<540 then return end
 local s=emu.getState()
 events:write(table.concat({frame,'health-'..string.format('%04x',s['cpu.pc']),a-L.MmEnemyHealthLo,v,r('MmEnemySlot'),r('ObjectOffset')},',')..'\n')
end,emu.callbackType.write,L.MmEnemyHealthLo,L.MmEnemyHealthHi+5)
emu.addMemoryCallback(function(a,v)
 if frame>=3780 and frame<=3790 then local s=emu.getState();print('STATE '..frame..' '..(a-L.Enemy_State)..' '..v..' PC='..string.format('%04x',s['cpu.pc'])..' BANK='..r('CurrentBank')) end
end,emu.callbackType.write,L.Enemy_State,L.Enemy_State+5)
emu.addMemoryCallback(function()
 if frame>=5900 and frame<5920 then print('ENDLEVEL '..frame..' timer='..r('TimerControl')..' joy='..r('SavedJoypadBits')) end
end,emu.callbackType.exec,L.PlayerEndLevel)
emu.addEventCallback(function()
 poll=poll+1
 local b={a=false,b=false,select=false,start=false,up=false,down=false,left=false,right=false}
 if frame<200 then
  if RUN_CHARACTER>=6 then
   b.start=frame==60;b.down=frame==80;b.right=frame>=100 and frame<100+20*(RUN_CHARACTER-6) and (frame-100)%20==0
  else b.start=frame==60;b.right=frame>=80 and frame<80+20*RUN_CHARACTER and (frame-80)%20==0 end
 elseif frame==200 then b.start=true
 elseif frame>=540 and r('GameEngineSubroutine')==8 then
  local x=r('Player_PageLoc')*256+r('Player_X_Position')
  local enemy,distance=nearestEnemy(x)
  local slot,px,py,ps=powerup()
  if phase=='settle' then
   aim(b,x,settleX)
   if r('Player_State')==0 then phase=settlePhase end
  elseif phase=='approach' then
   local target=goal.x-4
   if goal.y<128 then target=goal.x-40 end
   if goal.y<128 and RUN_CHARACTER==2 then target=goal.x+4 end
   local ready=aim(b,x,target)
   if enemy and distance<60 then
    fight(b,x,enemy,distance)
   elseif ready and r('Player_State')==0 then
    phase=r('Player_Y_Position')<=goal.y-16 and 'drop-under' or 'reveal'
    jumpFrames=0;goalsBeforeStatus=r('PlayerStatus');goalRevealed=false;goalPickupSerial=pickupSerial
   end
  elseif phase=='drop-under' then
   b.right=x<goal.x+(goal.y<128 and 17 or 36)
   if r('Player_Y_Position')>=goal.y+16 then phase='approach' end
  elseif phase=='reveal' then
   if r('Player_State')==0 and r('Player_Y_Position')<=goal.y-16 then phase='drop-under';jumpFrames=0 end
   if goal.y<128 and (RUN_CHARACTER==0 or RUN_CHARACTER==2) and r('Player_Y_Position')>144 and r('Player_State')==0 then
    phase='mount';mountStep='back';jumpFrames=0
   end
   b.a=jumpFrames<30;jumpFrames=jumpFrames+1
   aim(b,x,goal.x-4)
   if jumpFrames>60 and r('Player_State')==0 then jumpFrames=0 end
   if goal.y<128 then b.right=x<goal.x+4;b.left=x>goal.x+6 end
   if slot then phase='collect';goalRevealed=true end
  elseif phase=='collect' then
   if RUN_CHARACTER==8 and goal.kind=='life' then b.b=true end
   if RUN_CHARACTER==8 and goal.kind=='life' and r('Player_State')~=0 and jumpAge>=0 and jumpAge<35 then b.a=true end
   local collected=(goal.kind=='upgrade' and r('PlayerStatus')>goalsBeforeStatus) or (goal.kind=='life' and r('NumberofLives')>2) or (goal.kind=='star' and r('StarInvincibleTimer')>0)
   if pickupSerial>goalPickupSerial then collected=true end
   if collected then
    capture('powerup-'..goalIndex..'-collected')
    events:write(table.concat({frame,'goal-'..goal.kind,goalIndex,r('PlayerStatus'),x,r('Player_Y_Position')},',')..'\n')
    goalIndex=goalIndex+1;goal=goals[goalIndex]
    goalRevealed=false;goalPickupSerial=pickupSerial;goalsBeforeStatus=r('PlayerStatus')
    phase=goal and 'travel' or 'finish';jumpFrames=0
    if RUN_CHARACTER>=8 and r('Player_State')~=0 then settleX=x;settlePhase=phase;phase='settle' end
   elseif px and ps>=128 then
    b.right=x<px-8;b.left=x>px+8
    if py<r('Player_Y_Position')-8 and r('Player_State')==0 then
     if goal.y<128 then
      phase='upper';upperStep='back';jumpFrames=0
     else
     if r('PowerUpType',slot)==1 and r('Player_Y_Position')>144 then phase='mount';jumpFrames=0;mountStep='back' else b.a=not lastA end
     end
    elseif goal.y<128 and r('Player_Y_Position')<65 then
     b.right=x<goal.x+4;b.left=x>goal.x+6
    end
   end
  elseif phase=='mount' then
   local target=math.max(goal.x-72,r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')+1)
   if RUN_CHARACTER==0 and goal.y<128 and mountStep=='back' then mountStep='gap-align' end
   if mountStep=='gap-align' then
    if aim(b,x,goal.x-14) and r('Player_State')==0 then mountStep='gap-jump';jumpFrames=0 end
   elseif mountStep=='gap-jump' then
    b.a=jumpFrames<45;jumpFrames=jumpFrames+1
    if r('Player_Y_Position')<121 then aim(b,x,goal.x+4) else aim(b,x,goal.x-14) end
    if jumpFrames>45 and r('Player_State')==0 then
     if r('Player_Y_Position')<=112 then phase='reveal';jumpFrames=0 else mountStep='gap-align' end
    end
   elseif mountStep=='back' then
    b.left=x>target+1;b.right=x<target-1
    if math.abs(x-target)<=2 and r('Player_State')==0 then mountStep='runup' end
   elseif mountStep=='runup' then
    b.right=true;b.b=RUN_CHARACTER==0
    if x>=goal.x-48 then mountStep='jump';jumpFrames=1 end
   else
    b.a=jumpFrames<=40;b.b=RUN_CHARACTER==0;b.right=x<goal.x+6;b.left=x>goal.x+10;jumpFrames=jumpFrames+1
    if jumpFrames>80 then phase=goal.y<128 and not goalRevealed and 'reveal' or 'collect' end
   end
   if not slot and goalRevealed then phase='collect' end
  elseif phase=='upper' then
   local y=r('Player_Y_Position')
   if RUN_CHARACTER==0 or RUN_CHARACTER==2 or RUN_CHARACTER==3 or RUN_CHARACTER>=6 then
    -- The camera can prevent a long run-up here. Mount the middle lower
    -- block through its left gap, then jump from its supported left edge.
    if upperStep=='back' then upperStep='mario-gap' end
    if upperStep=='mario-gap' then
     if aim(b,x,goal.x-(RUN_CHARACTER==8 and 18 or 14)) and r('Player_State')==0 then upperStep='mario-mount';jumpFrames=0 end
     if RUN_CHARACTER==11 and x<goal.x-20 and block(x+24,y+24)>0 and r('Player_State')==0 then b.a=not lastA end
     if RUN_CHARACTER==11 and r('Player_State')~=0 and jumpAge>=0 and jumpAge<35 then b.a=true end
    elseif upperStep=='mario-mount' then
     b.a=jumpFrames<45;jumpFrames=jumpFrames+1
     aim(b,x,y<(RUN_CHARACTER==8 and 155 or 121) and goal.x+4 or goal.x-(RUN_CHARACTER==8 and 18 or 14))
     if jumpFrames>45 and r('Player_State')==0 then
      upperStep=y<=112 and 'mario-edge' or 'mario-gap'
     end
    elseif upperStep=='mario-edge' then
     if aim(b,x,goal.x-11) and r('Player_State')==0 then upperStep='mario-top';jumpFrames=0 end
    elseif upperStep=='mario-top' then
     b.a=jumpFrames<45;jumpFrames=jumpFrames+1
     aim(b,x,y<74 and goal.x+4 or goal.x-11)
     if jumpFrames>60 and r('Player_State')==0 then upperStep=y<=112 and 'mario-edge' or 'mario-gap' end
    end
   elseif upperStep=='back' then
    local target=math.max(goal.x-120,r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')+1)
    if RUN_CHARACTER==5 then target=goal.x+22 end
    local ready=aim(b,x,target)
    if ready and r('Player_State')==0 then
     if RUN_CHARACTER==5 then
      upperStep='drop'
     else upperStep='runup' end
    end
   elseif upperStep=='drop' then
    if y>=160 and r('Player_State')==0 then upperStep='align-right' end
   elseif upperStep=='align-right' then
    if aim(b,x,goal.x+15) and r('Player_State')==0 then upperStep='lower';jumpFrames=0 end
   elseif upperStep=='runup' then
    b.right=true
    if x>=goal.x-96 then upperStep='lower';jumpFrames=0 end
   elseif upperStep=='lower' then
    b.a=jumpFrames<30;aim(b,x,goal.x-42);jumpFrames=jumpFrames+1
    if RUN_CHARACTER==5 then b.a=jumpFrames==1 or jumpFrames==19;b.right=false;b.left=jumpFrames>=19 end
    if jumpFrames>30 and r('Player_State')==0 then
     if y<=112 then
      if RUN_CHARACTER==5 then upperStep='upper';jumpFrames=1;b.a=true;b.left=true;b.right=false
      else upperStep='pause';jumpFrames=0 end
     else upperStep='back' end
    end
   elseif upperStep=='pause' then
    aim(b,x,goal.x-42);jumpFrames=jumpFrames+1
    if jumpFrames>8 then upperStep='upper';jumpFrames=0 end
   else
    b.a=jumpFrames<30;b.right=x<goal.x+4;b.left=x>goal.x+6;jumpFrames=jumpFrames+1
    if RUN_CHARACTER==5 then b.left=jumpFrames<19;b.right=not b.left end
    if jumpFrames>70 and r('Player_State')==0 then
     if slot then phase='collect' else phase='reveal' end
    end
   end
   if slot then goalRevealed=true end
   if pickupSerial>goalPickupSerial then phase='collect' end
  elseif phase=='travel' or phase=='finish' then
   b.right=true
   local fighting=false
   if goal and x>goal.x-90 then phase='approach' end
   local gapBetween=false
   if enemy then for wx=x+8,x+distance+8,(distance>0 and 8 or -8) do if block(wx,208)==0 then gapBetween=true end end end
   if enemy and math.abs(distance)<60 and not gapBetween and block(x+(distance>0 and 28 or -12),r('Player_Y_Position')+24)==0 then
    fight(b,x,enemy,distance)
    fighting=true
   end
   if r('Player_State')==0 and not fighting then
    local y=r('Player_Y_Position')
    if block(x+28,y+24)>0 or block(x+12,208)==0 or block(x+24,208)==0 or block(x+40,208)==0 then b.a=true end
   end
   if jumpAge>=0 and r('Player_State')~=0 then
    if RUN_CHARACTER==5 or RUN_CHARACTER==9 then b.a=jumpAge==18 else b.a=jumpAge<30 end
   end
   if RUN_ROUTE=='pipe' and not pipeUsed and x>906 and x<960 and r('AreaType')==1 and r('Player_Y_Position')<=112 then
    aim(b,x,920)
    if math.abs(x-920)<=3 and r('Player_State')==0 then pipeEntryCommitted=true end
   end
   if pipeEntryCommitted and not pipeUsed then b.down=true;b.a=false;b.right=false;b.left=false end
   if RUN_ROUTE=='pipe' and r('LevelNumber')==0 and r('AreaType')==2 and x>160 then
    b.a=false
    if x<199 and r('Player_Y_Position')<176 then aim(b,x,185) end
   end
  end
 end
 if frame>=540 and r('GameEngineSubroutine')==8 then
  local x=r('Player_PageLoc')*256+r('Player_X_Position')
  local enemy,distance=nearestEnemy(x)
  if enemy and math.abs(distance)<80 and r('Player_State')==0 and r('Player_Y_Position')>=160 and ((phase=='collect' and goal and goal.kind=='star') or phase=='upper') then fight(b,x,enemy,distance) end
  if RUN_CHARACTER>=6 and enemy and math.abs(distance)<96 and r('Player_State')==0 and r('Enemy_Y_Position',enemy)>r('Player_Y_Position')+32 and (phase=='upper' or phase=='reveal' or phase=='collect') then fight(b,x,enemy,distance) end
  if RUN_CHARACTER==2 and phase=='collect' and enemy and math.abs(distance)<90 and r('Enemy_Y_Position',enemy)>=160 then fight(b,x,enemy,distance) end
  if enemy and distance<0 and not b.down and r('InjuryTimer')==0 and (phase=='travel' or phase=='finish' or phase=='approach') then
   local ey=r('Enemy_Y_Position',enemy)
   if math.abs(distance)>=45 or (r('Player_State')==0 and ey>r('Player_Y_Position')+32) then b.left=true;b.right=false end
  end
  if RUN_ROUTE=='pipe' and r('LevelNumber')==0 and r('AreaType')==2 then pipeUsed=true end
  if RUN_CHARACTER==2 and r('SmBall')>0 and not b.down then b.up=poll%2==0;b.a=false end
  if RUN_CHARACTER==2 and not b.down and r('Player_State')~=0 and r('SmBall')==0 and jumpAge>=0 then b.a=jumpAge<80 end
  if RUN_CHARACTER==2 and b.left and block(r('Player_PageLoc')*256+r('Player_X_Position')-12,208)==0 then b.left=false end
  if RUN_CHARACTER==5 and r('Player_State')~=0 and jumpAge>=0 then b.a=jumpAge==18 end
  if RUN_CHARACTER==9 and r('Player_State')~=0 and jumpAge>=0 and phase~='settle' then
   b.a=jumpAge<8 or (jumpAge==18 and r('XgJumpUsed')==0 and phase~='collect')
  end
  if RUN_CHARACTER==10 and r('XgWall')~=0 then
   b.up=true;b.right=r('PlayerFacingDir')==1;b.left=not b.right
   b.a=not lastA
  end
  if RUN_CHARACTER==11 and r('XgWall')~=0 and (phase=='travel' or phase=='finish') then
   b.up=true
   if r('Player_Y_Position')<=144 then b.a=not lastA end
  end
  if RUN_CHARACTER==8 and (phase=='travel' or phase=='finish') then
   b.b=false
   for offset=16,112,16 do if block(x+offset,208)==0 then b.b=true end end
   if r('PlayerStatus')==2 and enemy and math.abs(distance)<140 then
    local gap=false
    for wx=x+8,x+distance+8,(distance>0 and 8 or -8) do if block(wx,208)==0 then gap=true end end
    if not gap then b.b=poll%8~=0 end
   end
  end
  if RUN_CHARACTER==8 and (phase=='upper' or phase=='mount' or phase=='reveal') then b.b=true end
  if RUN_CHARACTER==8 and goalIndex==1 and enemy and r('Enemy_ID',enemy)==6 and x<336 then
   aim(b,x,250);b.b=false
   local ex=r('Enemy_PageLoc',enemy)*256+r('Enemy_X_Position',enemy)
   if r('Player_State')==0 then b.a=ex-x<25 and not lastA
   else b.a=jumpAge<8 end
  end
  if RUN_CHARACTER==8 and r('PlayerStatus')==2 and enemy and math.abs(distance)<140 and r('Player_Y_Position')>=144 then
   local gap=false
   for wx=x+8,x+distance+8,(distance>0 and 8 or -8) do if block(wx,208)==0 then gap=true end end
   if not gap then
    b.b=poll%8~=0
    if distance<0 then b.left=true;b.right=false;b.a=false end
   end
  end
  if RUN_CHARACTER==10 and goal and goal.y==80 and (phase=='reveal' or phase=='upper') then b.b=poll%12==0 end
  if RUN_CHARACTER==10 and goal and goal.y==80 and goalRevealed and not enemy then
   phase='upper';b.b=false;b.select=false;b.a=false;b.up=false
   if ryuStep=='align' then
    if r('Player_State')~=0 then b.left=false;b.right=false
    elseif aim(b,x,goal.x+20) then ryuStep='climb' end
   else
    b.left=true;b.right=false
    if r('Player_State')==0 or r('XgWall')~=0 then b.a=not lastA end
    b.up=r('XgWall')~=0
    if x<goal.x+8 and r('Player_Y_Position')<80 then aim(b,x,goal.x+4) end
   end
   if pickupSerial>goalPickupSerial then phase='collect' end
  end
  if RUN_CHARACTER==11 and goal and goal.y==80 and x>1640 then
   local y=r('Player_Y_Position')
   phase='upper';b.up=false;b.b=false
   if sophiaStep=='align' then
    if r('XgWall')~=0 then b.a=not lastA end
    if aim(b,x,goal.x-72) and r('Player_State')==0 then sophiaStep='rise';b.a=not lastA end
   elseif sophiaStep=='rise' then
    aim(b,x,goal.x-72);b.a=jumpAge~=18
    if y<=105 then sophiaStep='onto' end
   elseif sophiaStep=='onto' then
    aim(b,x,goal.x+4);b.a=false
    if r('Player_State')==0 and y<=112 then sophiaStep='reveal';b.a=not lastA end
   elseif sophiaStep=='reveal' then
    aim(b,x,goal.x+4);b.a=true
    if goalRevealed then sophiaStep='land' end
   elseif sophiaStep=='land' then
    aim(b,x,goal.x+4);b.a=false
    if r('Player_State')==0 then sophiaStep='left';b.a=not lastA end
   elseif sophiaStep=='left' then
    aim(b,x,goal.x-28);b.a=true
    if x<=goal.x-26 then sophiaStep='top' end
   elseif sophiaStep=='top' then
    aim(b,x,goal.x-28);b.a=true
    if y<=47 then sophiaStep='collect' end
   else
    aim(b,x,goal.x+4);b.a=y>47
    if pickupSerial>goalPickupSerial then phase='collect' end
   end
  end
  if goal and goal.y==80 and x>=1600 and x<goal.x-20 and enemy and r('Enemy_Y_Position',enemy)>=176 and math.abs(distance)<192 and r('Player_State')==0 and r('Player_Y_Position')>=160 then
   -- Clear approaching ground foes before the camera follows the high item.
   fight(b,x,enemy,distance);b.a=false
  end
  if RUN_CHARACTER==11 and goal and goal.y==80 and x>1640 and r('XgWall')~=0 then
   b.up=true;b.a=false
  end
  if RUN_CHARACTER==11 and goal and goal.y==80 and r('XgCeiling')~=0 then
   b.up=false;b.down=true;b.a=false
  end
  if RUN_CHARACTER==8 and goal and goal.kind=='life' and phase=='collect' then
   -- Let the 1-up fall off its single block, then meet it on safe ground.
   -- Repeated jumps underneath it only hit the used block and delay pursuit.
   b.a=false;b.b=true;aim(b,x,goal.x+36)
  end
  if (RUN_CHARACTER==8 and r('PlayerStatus')==2 or RUN_CHARACTER==11) and enemy and math.abs(distance)<140 and r('Player_State')==0 and r('Player_Y_Position')>=144 then
   local rawv=r('MmVX')+256*r('MmVX',1)+65536*r('MmVX',2)
   local v=(rawv>=8388608 and rawv-16777216 or rawv)/65536
   b.a=false
   if v*distance>0 and math.abs(v)>(RUN_CHARACTER==11 and 0.5 or 0.1) then
    b.left=v>0;b.right=v<0;b.b=false
   else
    local facing=distance>0 and 1 or 2
    b.right=r('PlayerFacingDir')~=facing and facing==1
    b.left=r('PlayerFacingDir')~=facing and facing==2
    -- Movement updates facing before the weapon handler, so the turn and
    -- fresh shot can share this input instead of endlessly alternating turns.
    b.b=(r('RgPreviousButtons')&64)==0 and r('RgCooldown')==0
   end
  end
  if RUN_CHARACTER==8 and phase=='finish' and x>2340 and x<2472 then
   -- Land on the first tall staircase before jumping its gap. A walking-speed
   -- takeoff from the floor cannot clear both staircases in one arc.
   if not luigiGapReady and r('Player_Y_Position')<=144 then
    aim(b,x,2434);b.b=true
    b.a=false
    if r('Player_State')==0 and x<2430 then b.a=not lastA end
    if r('Player_State')==0 and math.abs(x-2434)<=4 then luigiGapReady=true end
   end
   if luigiGapReady then
    b.right=true;b.left=false;b.b=true
    b.a=r('Player_State')==0 and not lastA or jumpAge<30
   end
  end
  if RUN_CHARACTER==11 and goal and goal.y==80 and goalRevealed and pickupSerial==goalPickupSerial then
   local flyX=math.max(goal.x-72,r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')+1)
   phase='upper';b.up=false;b.down=false;b.b=false
   if sophiaStep~='fly-return' and sophiaStep~='fly-rise' and sophiaStep~='fly-across' then sophiaStep='fly-return' end
   if sophiaStep=='fly-return' then
    aim(b,x,flyX);b.a=false
    if r('XgWall')~=0 then b.up=true end
    if r('XgCeiling')~=0 then b.down=true;b.up=false end
    if math.abs(x-flyX)<=2 then sophiaStep='fly-rise';b.a=not lastA end
   elseif sophiaStep=='fly-rise' then
    aim(b,x,flyX);b.a=jumpAge~=18
    if r('Player_Y_Position')<=76 then sophiaStep='fly-across' end
   else
    aim(b,x,goal.x+4);b.a=r('Player_Y_Position')>40
   end
  end
  if r('Player_State')==0 and lastA then b.a=false end
  if RUN_CHARACTER==2 and enemy and distance< -20 and distance> -200 and r('Player_State')==0 and r('Enemy_Y_Position',enemy)>r('Player_Y_Position')+32 and (phase=='approach' or phase=='travel' or phase=='collect') then
   -- Leave an elevated block before using ground bombs against a foe below.
   -- Otherwise it can walk into the preceding pit while Samus bombs above it.
   b.down=false;b.a=false;b.b=false;b.right=false;b.left=block(x-12,208)>0;b.up=r('SmBall')>0 and poll%2==0
  end
  if RUN_ROUTE=='pipe' and not pipeUsed and r('AreaType')==1 then
   if pipeEntryCommitted and math.abs(x-920)>5 and r('Player_State')==0 then pipeEntryCommitted=false end
   if pipeEntryCommitted then b.down=true;b.a=false;b.right=false;b.left=false;b.up=false
   elseif x>945 and x<1024 and r('Player_Y_Position')>112 then
    b.left=true;b.right=false
    if r('Player_State')==0 then b.a=not lastA end
   end
  end
 end
 if b.a and not lastA then jumpAge=0 end
 lastA=b.a
 local mask=(b.a and 128 or 0)+(b.b and 64 or 0)+(b.select and 32 or 0)+(b.start and 16 or 0)+(b.up and 8 or 0)+(b.down and 4 or 0)+(b.left and 2 or 0)+(b.right and 1 or 0)
 if RUN_REPLAY then
  local input=assert(replay[poll],'Fixed input stream exhausted at poll '..poll)
  assert(input.frame==frame,'Controller poll/frame synchronization diverged at '..poll)
  mask=input.mask
  for name,bit in pairs({a=128,b=64,select=32,start=16,up=8,down=4,left=2,right=1}) do b[name]=(mask&bit)>0 end
 end
 inputs:write(poll..','..frame..','..mask..'\n');emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if jumpAge>=0 then jumpAge=jumpAge+1 end
 if r('Player_State')==0 and not lastA then jumpAge=-1 end
 local slot,px,py,ps=powerup();local count=0;local enemies={}
 if goal and slot and not goalRevealed and math.abs(px-goal.x)<17 and py<=goal.y then
  goalRevealed=true;goalPickupSerial=pickupSerial;goalsBeforeStatus=r('PlayerStatus');phase='collect'
 end
 for i=0,5 do if r('Enemy_Flag',i)>0 then count=count+1;enemies[#enemies+1]=table.concat({i,r('Enemy_ID',i),r('Enemy_PageLoc',i)*256+r('Enemy_X_Position',i),r('Enemy_Y_Position',i),r('Enemy_State',i),r('MmEnemyHealthLo',i)},':') end end
 trace:write(table.concat({frame,phase,r('Player_PageLoc')*256+r('Player_X_Position'),r('Player_Y_Position'),r('Player_State'),r('Player_X_Speed'),r('Player_Y_Speed'),r('PlayerStatus'),r('GameEngineSubroutine'),r('OperMode'),r('OperMode_Task'),r('AreaPointer'),r('NumberofLives'),r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos'),r('BlockBounceTimer'),count,px or -1,py or -1,ps or -1,upperStep,table.concat(enemies,';'),r('WorldNumber'),r('LevelNumber'),r('AreaType')},',')..'\n')
 if frame%120==0 then capture('frame-'..frame);print('PROGRESS '..frame..' '..phase..' x='..(r('Player_PageLoc')*256+r('Player_X_Position'))..' y='..r('Player_Y_Position')..' status='..r('PlayerStatus')) end
 if frame%60==0 and r('GameEngineSubroutine')==5 then
  events:write(table.concat({frame,'flagpole',r('ClimbSideTimer'),r('Player_CollisionBits'),r('GamePauseStatus'),r('TimerControl')},',')..'\n')
 end
 if r('WorldNumber')==0 and r('LevelNumber')==1 and r('OperMode')==1 and r('GameEngineSubroutine')==8 and r('AreaType')==2 then
  nextLevelControl=nextLevelControl+1
  local x=r('Player_PageLoc')*256+r('Player_X_Position')
  if not nextLevelX then nextLevelX=x end
  if nextLevelControl>=25 and x>nextLevelX+5 then cleared=true end
 end
 if frame==RUN_LIMIT or cleared or (frame>540 and (r('GameEngineSubroutine')==11 or (r('Player_Y_HighPos')>=2 and r('OperMode')==1 and r('OperMode_Task')==3))) then
  done=true
  local report=assert(io.open(RUN_OUTPUT..'result.json','w'));report:write('{"cleared":'..tostring(cleared)..',"frames":'..frame..',"polls":'..poll..',"goals":'..(goalIndex-1)..',"died":'..tostring(r('GameEngineSubroutine')==11)..'}\n');report:close()
  capture('endpoint');trace:close();inputs:close();events:close();if bridgeStop then bridgeStop() end
  print('DISCOVERY endpoint '..phase..' after '..frame..' frames and '..poll..' controller polls, cleared='..tostring(cleared)..', goals='..(goalIndex-1));emu.stop(0)
 end
end,emu.eventType.endFrame)
