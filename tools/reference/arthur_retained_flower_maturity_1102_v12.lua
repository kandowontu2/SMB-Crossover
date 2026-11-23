-- Actual-menu controller-only Arthur 1-1 discovery. No emulated memory writes.
local phase,age,frame,polls='title',0,0,0
local captures,mainCalls,sourceSteps,maxJumps=0,0,0,0
local startLives,startX
local lastX,lastY,lastChange=0,0,0
local jumpStart=nil
local jumpReason='none'
local jumps=0
local questJump=nil
local seenItem,mature=false,false
local approach=false
local onFlowerRow=false
local pickupCalls={}
local torchStart=nil
local torchCalls=0
local highChanges=0
local highLast=nil
local heights=assert(io.open(OUTPUT..'height-pages.csv','w'))
heights:write('frame,world_x,y_low,y_high,source_y,source_page,mode,pc,bank_a,bank_c\n')

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
 heights:close()
 local u=assert(io.open(OUTPUT..'torch.json','w'))
 u:write(string.format('{"collected_at_play_frame":%d,"original_torch_handler_calls":%d}',torchStart or -1,torchCalls));u:close()
 local p=assert(io.open(OUTPUT..'powerup.json','w'));local rows={}
 for value,n in pairs(pickupCalls)do rows[#rows+1]=string.format('"%d":%d',value,n)end
 p:write(string.format('{"seen_natural_flower":%s,"mature":%s,"last_pickup":%d,"source_weapon":%d,"source_pickup_calls":{%s},"x":%d,"y":%d}',tostring(seenItem),tostring(mature),r('ArLastPickup'),r('ArR_053A'),table.concat(rows,','),wx(),r('Player_Y_Position')));p:close()
 row();trace:close();shot(passed and 'powerup-complete' or 'route-stop')
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
 if torchStart then local n=age-torchStart;return {b=n<12 or(n>=60 and n<72)}end
 local b={right=true,b=age%21<12}
 if x>=284 or seenItem then
  b={}
  if not seenItem then
   b.right=x<328
   if x>=328 and not questJump and r('Player_State')==0 and r('ArMode')==0 then questJump=age end
  else
   if not approach then
    b.left=x>273
    if x<=273 and r('Player_State')==0 and r('ArMode')==0 then approach=true;questJump=age;b.right=true end
   else
    if r('Player_Y_HighPos')==1 and y<=112 and r('ArMode')==0 then onFlowerRow=true;questJump=nil end
    local target=r('Enemy_PageLoc',5)*256+r('Enemy_X_Position',5)
    b.right=x<target
    if not onFlowerRow and not questJump and r('Player_State')==0 and r('ArMode')==0 then questJump=age end
   end
  end
  if questJump then
   local n=age-questJump;b.a=n<6 or(n>=18 and n<27)
   if n>=45 and r('Player_State')==0 then questJump=nil end
  end
  return b
 end
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
 if phase=='play' and r('CurrentBankC')==(assert(B.ArHostNativePickup)|128) then
  local value=emu.getState()['cpu.a'];pickupCalls[value]=(pickupCalls[value]or 0)+1
 end
end,emu.callbackType.exec,assert(L.ArHostNativePickup))
emu.addMemoryCallback(function()
 local bank=assert(L.ArNativeTorch)<0xc000 and r('CurrentBank')or r('CurrentBankC')
 if phase=='play' and torchStart and bank==(assert(B.ArNativeTorch)|128)then torchCalls=torchCalls+1 end
end,emu.callbackType.exec,assert(L.ArNativeTorch))
emu.addMemoryCallback(function(_,value)
 if phase=='play' and value~=highLast and highChanges<32 then
  local s=emu.getState();highChanges=highChanges+1
  heights:write(string.format('%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n',frame,wx(),r('Player_Y_Position'),value,r('ArR_0599'),r('ArR_056D'),r('ArMode'),s['cpu.pc']or 0,r('CurrentBank'),r('CurrentBankC')))
 end
 highLast=value
end,emu.callbackType.write,assert(L.Player_Y_HighPos))
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
  if r('Enemy_Flag',5)>0 and r('Enemy_ID',5)==46 and r('PowerUpType',5)==1 then
   if not seenItem then seenItem=true;questJump=nil;shot('released')end
   if r('Enemy_State',5)>=128 then mature=true end
  end
  if mature and(pickupCalls[6]or 0)>0 and r('ArLastPickup')==6 and r('ArR_053A')==68 then if not torchStart then torchStart=age;shot('collected')end end
  if torchStart and age-torchStart>=120 then finish(r('NumberofLives')==startLives and torchCalls>0,'Natural flower and original B-driven torch');return end
  if age>=1600 then finish(false,'Natural flower controller bound');return end
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
