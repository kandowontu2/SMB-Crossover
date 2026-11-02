local frame,age,phase,done,cycles=0,0,'title',false,0
local route,ticks,initialLives=0,0,nil
local trace,spawned,matured,got={},false,false,false
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function shot(n)local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local function worldx()return r('Player_PageLoc')*256+r('Player_X_Position')end
emu.addEventCallback(function()
 local pad={}
 if age<4 then
  if phase=='open' or phase=='start' then pad.start=true
  elseif phase=='select' then
   if cycles<3 then pad.right=true elseif cycles==3 then pad.down=true else pad.select=true end
  end
 end
 if phase=='play' then
  local x=worldx()
  if route==0 then
   pad.right=true
   if x>=105 then route=1;ticks=0 end
  elseif route==1 then
   pad.right=true;pad.a=ticks<35
   if ticks>=50 then route=2 end
  elseif route==2 then
   if x<240 then pad.right=true else route=3;ticks=0 end
  elseif route==3 then
   pad.a=ticks<35
   if ticks>=65 then route=4 end
  elseif route==4 then pad.right=true end
  ticks=ticks+1
 end
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)
local function finish(reason)
 shot('final')
 local passed=got and spawned and matured and r('NumberofLives')==initialLives
 local f=assert(io.open(OUTPUT..'result.json','w'))
 f:write(string.format('{"passed":%s,"reason":"%s","frames":%d,"world_x":%d,"spawned":%s,"matured":%s,"collected":%s,"lives":%d,"initial_lives":%d,"trace":[%s]}\n',tostring(passed),reason,frame,worldx(),tostring(spawned),tostring(matured),tostring(got),r('NumberofLives'),initialLives or -1,table.concat(trace,',')))
 f:close();done=true;emu.stop(passed and 0 or 1)
end
emu.addEventCallback(function()
 if done then return end
 frame=frame+1;age=age+1
 if phase=='title' and frame>=100 then phase='open';age=0
 elseif phase=='open' and age>=50 then assert(r('CrossoverMenuState')==2);phase='select';age=0
 elseif phase=='select' and age>=30 then
  cycles=cycles+1
  if cycles==5 then assert(r('SelectedCharacter')==35);phase='start' end
  age=0
 elseif phase=='start' and age>=300 then
  assert(r('SelectedCharacter')==35 and r('OperMode')==1 and r('OperMode_Task')==3)
  initialLives=r('NumberofLives');phase='play';age=0
 elseif phase=='play' then
  if age%20==0 then trace[#trace+1]=string.format('{"t":%d,"x":%d,"y":%d,"state":%d,"engine":%d,"route":%d}',age,worldx(),r('Player_Y_Position'),r('Player_State'),r('GameEngineSubroutine'),route) end
  for slot=0,5 do
   if emu.read(L.Enemy_Flag+slot,emu.memType.nesDebug)~=0 and emu.read(L.Enemy_ID+slot,emu.memType.nesDebug)==46 then
    if not spawned then spawned=true;shot('released') end
    if emu.read(L.Enemy_State+slot,emu.memType.nesDebug)>=128 then matured=true end
   end
  end
  if r('PlayerStatus')==1 then got=true;finish('armor-collected')
  elseif r('NumberofLives')~=initialLives then finish('lost-life')
  elseif age>=1000 then finish('route-bound') end
 end
 if frame>1700 and not done then finish('global-bound') end
end,emu.eventType.endFrame)
