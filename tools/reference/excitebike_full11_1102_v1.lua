-- Controller-only route. Original Right/B turbo, Up lean and fresh A jump.
-- Terrain and actors are observed; the controller never writes emulated RAM.
local frame,age,phase,menu,done=0,0,'title',0,false
local lastEpoch,updates,initialLives=nil,0,nil
local maxX,maxCamera,minY,lastX,lastY,lastProgress=0,0,255,0,0,0
local jump=nil
local jumpSequences,launches,sourceCalls=0,0,0
local cached={air=0,crash=0,recovery=0,speed=0,angle=6,heat=0}
local captures=0
local tallApproach,tallPassed=false,false
local rawA,rawC=0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function wx()return r('Player_PageLoc')*256+r('Player_X_Position')end
local function camera()return r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')end
local function shot(name)
 captures=captures+1;assert(captures<=4,'Four screenshots maximum')
 local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
local trace=assert(io.open(OUTPUT..'route.csv','w'))
trace:write('frame,updates,x,y,camera,state,engine,lives,speed,angle,air,crash,recovery,heat,jump_reason,source_launches\n')
local function row()
 trace:write(string.format('%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s,%d\n',frame,updates,wx(),r('Player_Y_Position'),camera(),r('Player_State'),r('GameEngineSubroutine'),r('NumberofLives'),cached.speed,cached.angle,cached.air,cached.crash,cached.recovery,cached.heat,jump and jump.reason or 'none',launches))
end
local function finish(passed,reason)
 if done then return end;done=true;row();trace:close();shot(passed and 'active-1-2' or 'route-stop')
 local pipes,gaps=0,0
 for _,edge in ipairs({480,640,768,944})do if maxX>=edge+16 then pipes=pipes+1 end end
 for _,edge in ipairs({1136,2240,2480})do if maxX>=edge+16 then gaps=gaps+1 end end
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(string.format('{"passed":%s,"reason":"%s","controller_only":true,"frames":%d,"updates":%d,"maximum_x":%d,"maximum_camera":%d,"minimum_y":%d,"initial_lives":%d,"final_lives":%d,"jump_sequences":%d,"source_launches":%d,"source_calls":%d,"initial_four_pipes_passed":%d,"three_gaps_passed":%d,"world":%d,"level":%d,"engine":%d,"helpers_added":false}\n',tostring(passed),reason,frame,updates,maxX,maxCamera,minY,initialLives or -1,r('NumberofLives'),jumpSequences,launches,sourceCalls,pipes,gaps,r('WorldNumber'),r('LevelNumber'),r('GameEngineSubroutine')));f:close()
 emu.stop(passed and 0 or 1)
end
local function block(x,y)
 if y<32 or y>=240 then return 0 end
 local base=math.floor(x/256)%2==0 and L.Block_Buffer_1 or L.Block_Buffer_2
 return emu.read(base+(math.floor(y/16)-2)*16+math.floor(x/16)%16,emu.memType.nesDebug)
end
local function solid(x,y)
 return emu.read(L.MTileAttribute+block(x,y),emu.memType.nesDebug)&1~=0
end
local function supported(x,y)
 return r('Player_Y_HighPos')==1 and (solid(x+2,y+32)or solid(x+13,y+32))
end
local function danger(x,y)
 for i=0,5 do
  local flag,id=r('Enemy_Flag',i),r('Enemy_ID',i)
  if flag>0 and flag<128 and id<0x15 and r('Enemy_State',i)&0x20==0 then
   local dx=r('Enemy_PageLoc',i)*256+r('Enemy_X_Position',i)-x
   if dx> -8 and dx<84 and math.abs(r('Enemy_Y_Position',i)-(y+16))<52 then return true end
  end
 end
 return false
end
local function travel()
 local b={right=true,b=true};local x,y=wx(),r('Player_Y_Position');local epoch=r('FrameCounter')
 if r('GameEngineSubroutine')~=8 then jump=nil;return b end
 if cached.crash~=0 or cached.recovery~=0 or cached.heat~=0 then jump=nil;return b end
 if jump then
  local elapsed=(epoch-jump.epoch)&255
  if jump.phase=='prelean' then
   b.up=true
   if elapsed>=4 and r('Player_State')==0 and supported(x,y)then
    jump.phase='air';jump.epoch=epoch;b.a=true
   elseif elapsed>=16 then jump=nil;b.up=false end
  else
   b.a=elapsed<8;b.up=elapsed<36
   if elapsed>=12 and cached.air==0 and r('Player_State')==0 and supported(x,y)then jump=nil end
  end
  return b
 end
 if cached.air==0 and supported(x,y)then
  local obstacle=solid(x+68,math.min(232,y+28))or solid(x+68,y+12)
  local gap=not solid(x+52,y+32)
  local threat=danger(x,y)
  if obstacle or gap or threat then
   jump={phase='prelean',epoch=epoch,reason=gap and 'edge' or(obstacle and 'terrain' or'enemy')}
   jumpSequences=jumpSequences+1;b.up=true
  end
 end
 return b
end
emu.addMemoryCallback(function(_,v)rawA=v end,emu.callbackType.write,0x5115)
emu.addMemoryCallback(function(_,v)rawC=v end,emu.callbackType.write,0x5116)
emu.addMemoryCallback(function()
 if rawA~=3 or rawC~=2 or r('SelectedCharacter')~=37 then return end
 local function p(at)return emu.read(at,emu.memType.nesDebug)end
 sourceCalls=sourceCalls+1
 cached={air=p(0xc0b0),crash=p(0xc098),recovery=p(0xc09c),speed=p(0xc090)+256*p(0xc094),angle=p(0xc0ac),heat=p(0xc3e0)}
end,emu.callbackType.exec,assert(L.ExHostMovement))
emu.addMemoryCallback(function()
 if rawA==3 and rawC==2 and r('SelectedCharacter')==37 then launches=launches+1 end
end,emu.callbackType.exec,assert(L.ExAirLaunch))
emu.addEventCallback(function()
 if done then return end
 local b={}
 if phase=='open'or phase=='start'then b.start=age<4
 elseif phase=='select'and age<4 then if menu<5 then b.right=true else b.down=true end
 elseif phase=='play'then b=travel()end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end
 frame=frame+1;age=age+1
 if phase=='title'and frame>=100 then phase='open';age=0
 elseif phase=='open'and age>=50 then assert(r('CrossoverMenuState')==2);phase='select';age=0
 elseif phase=='select'and age>=30 then
  menu=menu+1;age=0
  if menu==8 then assert(r('CrossoverMenuIndex')==29 and r('SelectedCharacter')==37);phase='start'end
 elseif phase=='start'and age>=300 then
  assert(r('SelectedCharacter')==37 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8)
  initialLives=r('NumberofLives');lastEpoch=r('FrameCounter');phase='play';age=0;lastX=wx();lastY=r('Player_Y_Position');shot('cold-spawn')
 elseif phase=='play'then
  local epoch=r('FrameCounter');local delta=(epoch-lastEpoch)&255;lastEpoch=epoch;assert(delta<=2,'Unexpected Main epoch gap');updates=updates+delta
  local x,y=wx(),r('Player_Y_Position')
  maxX=math.max(maxX,x);maxCamera=math.max(maxCamera,camera());minY=math.min(minY,y)
  if x~=lastX or y~=lastY then lastProgress=age;lastX=x;lastY=y end
  if age%24==0 then row()end
  if r('NumberofLives')~=initialLives then finish(false,'Lost life');return end
  if r('SelectedCharacter')~=37 then finish(false,'Lost owner');return end
  if r('GameEngineSubroutine')==11 then finish(false,'Entered death engine');return end
  if r('WorldNumber')==0 and r('LevelNumber')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   finish(maxX>=3000,'Reached active1-2');return
  end
  if not tallApproach and x>=668 then tallApproach=true;shot('third-pipe-approach')end
  if not tallPassed and x>=960 then tallPassed=true;shot('four-pipes-crossed')end
  local allowance=(cached.crash~=0 or cached.recovery~=0)and 720 or 360
  if age-lastProgress>=allowance then finish(false,'Stationary terrain or recovery bound');return end
  if age>=8800 then finish(false,'Full-stage frame bound');return end
 end
 if frame>=9500 then finish(false,'Global frame bound')end
end,emu.eventType.endFrame)
