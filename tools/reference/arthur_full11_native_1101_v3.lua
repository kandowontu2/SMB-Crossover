-- Actual-menu controller-only Arthur 1-1 discovery. No emulated memory writes.
local phase,age,frame,polls='title',0,0,0
local captures,mainCalls,sourceSteps,maxJumps=0,0,0,0
local startLives,startX
local lastX,lastY,lastChange=0,0,0
local jumpStart=nil
local jumpReason='none'
local jumps=0
local clearedPipes=0
local clearedGaps=0
local maxX,maxCamera,minY=0,0,255
local checkpoints={false,false}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function wx()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function camera()return r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')end
local function state(p)phase=p;age=0;polls=0 end
local function shot(name)
 captures=captures+1;assert(captures<=4,'At most four screenshots')
 local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
local trace=assert(io.open(OUTPUT..'route.csv','w'))
trace:write('frame,age,x,y,camera,engine,player_state,source_mode,jump_count,source_steps,reason,lives\n')
local function row()
 trace:write(string.format('%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s,%d\n',frame,age,wx(),r('Player_Y_Position'),camera(),r('GameEngineSubroutine'),r('Player_State'),r('ArMode'),r('ArJumpCount'),sourceSteps,jumpReason,r('NumberofLives')))
end
local function finish(passed,reason)
 row();trace:close();shot(passed and 'stage-1-2' or 'route-stop')
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(string.format('{"passed":%s,"reason":"%s","controller_only":true,"frames":%d,"play_frames":%d,"start_x":%d,"maximum_x":%d,"maximum_camera":%d,"minimum_y":%d,"main_calls":%d,"source_steps":%d,"jump_sequences":%d,"maximum_jump_count":%d,"initial_four_pipes_passed":%d,"three_gaps_passed":%d,"lives_start":%d,"lives_end":%d,"world":%d,"level":%d,"engine":%d,"helpers_added":false}',tostring(passed),reason,frame,age,startX or 0,maxX,maxCamera,minY,mainCalls,sourceSteps,jumps,maxJumps,clearedPipes,clearedGaps,startLives or 0,r('NumberofLives'),r('WorldNumber'),r('LevelNumber'),r('GameEngineSubroutine')))
 f:close();emu.stop(passed and 0 or 1)
end
local function block(x,y)
 if y<32 or y>=240 then return 0 end
 local page=math.floor(x/256)%2
 local col=math.floor(x/16)%16
 local at=(page==0 and L.Block_Buffer_1 or L.Block_Buffer_2)+(math.floor(y/16)-2)*16+col
 return emu.read(at,emu.memType.nesDebug)
end
local function solid(x,y)
 local tile=block(x,y)
 return emu.read(L.MTileAttribute+tile,emu.memType.nesDebug)%2==1
end
local function danger(x,y)
 for i=0,5 do
  local flag,id=r('Enemy_Flag',i),r('Enemy_ID',i)
  if flag>0 and flag<128 and id<0x15 and r('Enemy_State',i)&0x20==0 then
   local dx=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)-x
   if dx> -8 and dx<42 and math.abs(r('Enemy_Y_Position',i)-y)<44 then return true end
  end
 end
 return false
end
local function travel()
 local x,y=wx(),r('Player_Y_Position')
 local b={right=true,b=age%21<12}
 if r('GameEngineSubroutine')~=8 then jumpStart=nil;return b end
 local grounded=r('Player_State')==0 and r('ArMode')==0
 if jumpStart and age-jumpStart>=30 and grounded then jumpStart=nil end
 if not jumpStart and grounded then
  local obstacle=solid(x+40,math.min(232,y+28)) or solid(x+40,y+8)
  local gap=not solid(x+24,216)
  local threat=danger(x,y)
  if obstacle or gap or threat then
   jumpStart=age;jumps=jumps+1
   jumpReason=gap and 'gap' or (obstacle and 'terrain' or 'enemy')
  end
 end
 if jumpStart then
  local t=age-jumpStart
  b.a=t<6 or(t>=18 and t<27)
 end
 return b
end
emu.addMemoryCallback(function()
 if phase=='play' then mainCalls=mainCalls+1 end
end,emu.callbackType.exec,L.NoDecTimers)
emu.addMemoryCallback(function()
 if phase=='play' and r('CurrentBank')==154 then sourceSteps=sourceSteps+1 end
end,emu.callbackType.exec,L.ArStep)
emu.addEventCallback(function()
 local b={}
 if phase~='title' and phase~='play' and polls<8 then
  if phase=='open' or phase=='start' then b.start=true elseif phase=='up' then b.up=true elseif phase=='left' then b.left=true end
 elseif phase=='play' and age>=120 then b=travel() end
 emu.setInput(b,0);polls=polls+1
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1;age=age+1
 assert(frame<=9500,'Bounded full-stage discovery')
 if phase=='title' and age==100 then state('open')
 elseif phase=='open' and age>=36 and polls>=12 then assert(r('CrossoverMenuState')==2);state('up')
 elseif phase=='up' and age>=28 and polls>=12 then assert(r('CrossoverMenuIndex')==24);state('left')
 elseif phase=='left' and age>=36 and polls>=12 then assert(r('SelectedCharacter')==32);state('start')
 elseif phase=='start' and age>=300 then
  assert(r('OperMode')==1 and r('GameEngineSubroutine')==8 and r('SelectedCharacter')==32)
  startX=wx();startLives=r('NumberofLives');lastX=startX;lastY=r('Player_Y_Position');shot('idle-start');state('play')
 elseif phase=='play' then
  local x,y=wx(),r('Player_Y_Position')
  maxX=math.max(maxX,x);maxCamera=math.max(maxCamera,camera());minY=math.min(minY,y);maxJumps=math.max(maxJumps,r('ArJumpCount'))
  if x~=lastX or y~=lastY then lastChange=age;lastX=x;lastY=y end
  if age%12==0 then row() end
  if r('NumberofLives')~=startLives then finish(false,'Life lost');return end
  if r('SelectedCharacter')~=32 then finish(false,'Character changed');return end
  if r('WorldNumber')==0 and r('LevelNumber')==1 and r('GameEngineSubroutine')==8 and r('OperMode_Task')==3 then
   finish(clearedPipes==4 and clearedGaps==3,'Reached actual 1-2 gameplay');return
  end
  if r('WorldNumber')==0 and r('LevelNumber')==0 then
   clearedPipes=0;for _,edge in ipairs({480,640,768,944}) do if maxX>=edge+16 then clearedPipes=clearedPipes+1 end end
   clearedGaps=0;for _,edge in ipairs({1136,2240,2480}) do if maxX>=edge+16 then clearedGaps=clearedGaps+1 end end
   if not checkpoints[1] and x>=1000 then checkpoints[1]=true;shot('four-pipes') end
   if not checkpoints[2] and x>=2496 then checkpoints[2]=true;shot('stair-gaps') end
  end
  if age>120 and r('GameEngineSubroutine')==8 and age-lastChange>=480 then finish(false,'Stationary for 480 physical frames');return end
  if age>=8800 then finish(false,'Full-stage frame bound');return end
 end
end,emu.eventType.endFrame)
