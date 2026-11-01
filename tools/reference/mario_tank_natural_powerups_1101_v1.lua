
local frame,age,phase,done,cycles=0,0,'title',false,0
local trace,maxStatus={},0
local routeStep=0
local jumpTicks=0
local initialLives=nil
local lastJump=false
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function shot(n)local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
emu.addEventCallback(function()
 local pad={}
 if age<4 then
  if phase=='open' or phase=='start' then pad.start=true
  elseif phase=='select' then pad.select=true end
 end
 if phase=='walk' then
  local x=r('Player_PageLoc')*256+r('Player_X_Position')
  pad.b=true
  if age<=200 then
   if x<330 then pad.right=true end
   if x>=290 and x<350 then pad.a=true end
  elseif routeStep==0 then
   pad.left=true
   if x<=350 then routeStep=1 end
  elseif routeStep==1 then
   pad.a=true;pad.right=true
   if r('Player_State')==0 and x>350 then routeStep=2 end
  elseif x<410 then pad.right=true end
 end
 if phase=='walk' and age>600 and r('GameEngineSubroutine')==8 then
  pad={right=true,b=true}
  local wx=r('Player_PageLoc')*256+r('Player_X_Position')
  if r('Player_State')==0 and jumpTicks==0 and not lastJump and (wx<1270 or wx>=1350) then jumpTicks=24 end
  if jumpTicks>0 then pad.a=true;jumpTicks=jumpTicks-1 end
 end
 if phase=='walk' and age>=1244 and age<1290 then
  pad={b=true}
  if age<1254 then pad.right=true else pad.a=true end
 end
 if phase=='walk' and age>=1340 then
  pad={b=true}
  if age<1450 then pad.left=true end
  if age>=1386 and age<1416 then pad.a=true end
 end
 lastJump=pad.a==true
 emu.setInput(pad,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1;age=age+1
 if phase=='title' and frame>=100 then phase='open';age=0
 elseif phase=='open' and age>=50 then assert(r('CrossoverMenuState')==2);phase='select';age=0
 elseif phase=='select' and age>=30 then
  cycles=cycles+1
  if cycles==7 then assert(r('MarioVariant')==7);phase='start';age=0 else age=0 end
 elseif phase=='start' and age>=300 then
  assert(r('SelectedCharacter')==0 and r('MarioVariant')==7 and r('OperMode')==1 and r('OperMode_Task')==3)
  initialLives=r('NumberofLives');shot('gameplay-entry');phase='walk';age=0
 elseif phase=='walk' then
  local x=r('Player_PageLoc')*256+r('Player_X_Position')
  maxStatus=math.max(maxStatus,r('PlayerStatus'))
  if age%12==0 then table.insert(trace,string.format('[%d,%d,%d,%d,%d,%d]',age,x,r('Player_Y_Position'),r('Player_State'),r('PlayerStatus'),r('GameEngineSubroutine'))) end
  if age==1430 or age==1438 then shot('route-'..age) end
  if age>=1600 or r('NumberofLives')~=initialLives or r('GameEngineSubroutine')==11 then
   shot('endpoint')
   local f=assert(io.open(OUTPUT..'result.json','w'))
   f:write(string.format('{"passed":%s,"natural_mushroom_collected":%s,"natural_boot_collected":%s,"max_status":%d,"world_x":%d,"controller_only":true,"full_stage":false,"lost_life":%s,"trace":[%s]}\n',tostring(maxStatus==2 and r('NumberofLives')==initialLives),tostring(maxStatus>=1),tostring(maxStatus==2),maxStatus,x,tostring(r('NumberofLives')~=initialLives),table.concat(trace,',')));f:close();done=true;emu.stop(0)
  end
 end
 if frame>3400 then error('Finite selection bound')end
end,emu.eventType.endFrame)
