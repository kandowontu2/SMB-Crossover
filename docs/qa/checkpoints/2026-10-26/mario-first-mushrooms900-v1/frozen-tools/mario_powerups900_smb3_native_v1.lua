-- Read-only first-mushroom component. Genuine cold menu/A/Down controls only.
local C=assert(MARIO_POWERUP_CONFIG)
local frame,entered,done=0,false,false
local revealed,collected,settled=0,0,0
local updateCalls,growthDraws,downFrames,airFrames=0,0,0,0
local revealSfx,pickupSfx=0,0
local firstActor,lastStamp,firstUpdate=nil,nil,nil
local minY,maxY=255,0
local records={}
local log=assert(io.open(ROSTER_CONFIG.out..'powerup-owner.jsonl','w'))
local csv=assert(io.open(ROSTER_CONFIG.out..'powerup-state.csv','w'))
csv:write('frame,x,y,power,size,engine,freeze,freezeAge,m3form,m3growth,crouch,playerState,actors\n')
local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end
local function pos()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function json(v)
 if type(v)=='table'then local t={};for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;table.sort(t);return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif type(v)=='boolean'then return tostring(v)else return tostring(v)end
end
local function event(kind,z)
 z.kind=kind;z.frame=frame;z.x=pos();z.y=r('Player_Y_Position');records[#records+1]=z
 log:write(json(z)..'\n');log:flush()
end
local function selected()
 return r('OperMode')==1 and r('OperMode_Task')==3 and r('SelectedCharacter')==C.character
end
local function hook(n,fn)
 local h=assert(C.hooks[n]);emu.addMemoryCallback(function()
  if not selected()then return end
  local a=emu.convertAddress(h.address)
  if not a or a.address//8192~=h.bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Actual item owner '..n)end
  fn(emu.getState())
 end,emu.callbackType.exec,h.address)
end
hook('PwrUpJmp',function(s)
 local x=s['cpu.x'];assert(x==5,'Native first-block item slot')
 assert(r('Enemy_ID',x)==0x2e,'Real SetupPowerUp actor')
 assert(r('Enemy_X_Position',x)+256*r('Enemy_PageLoc',x)==336,'First1-1 mushroom block column')
 assert(not firstActor,'Exactly one physical reveal in this component')
 firstActor={slot=x,x=336,y=r('Enemy_Y_Position',x)};revealed=revealed+1
 event('actual-block-delivery',{slot=x,item=r('PowerUpType',x),yActor=firstActor.y})
end)
local function collect(s)
 local x=s['cpu.x']
 if r('Enemy_ID',x)~=0x2e then return end
 if C.character==17 and r('InvPickupOwner',x)~=17 then return end
 assert(firstActor and revealed==1,'Native collection follows physical block reveal')
 assert(r('Enemy_Flag',x)>0 and r('Enemy_State',x)>=128,'Native mushroom fully emerged before contact')
 assert(collected==0,'One genuine pickup owner')
 assert(r('PowerUpType',x)==0,'Actual mature walking mushroom delivery type')
 if C.character==17 then
  assert(r('M3Form')==0 and r('InvPickup',x)==0xd1,'Source-owned small-to-super mushroom stamp')
 else assert(r('PlayerStatus')==0,'Cold unpowered collection')end
 collected=1;event('actual-collect',{slot=x,item=r('PowerUpType',x),stamp=r('InvPickup',x),owner=r('InvPickupOwner',x)})
end
hook(C.character==17 and'M3CollectPickup'or'MarioSourcePowerupCollision',collect)
hook(C.character==0 and'MarioSourcePowerupUpdate'or'GuestPowerupUpdate',function()
 if C.character==17 or collected==0 or r('GuestPowerupActive')==0 then return end
 updateCalls=updateCalls+1
 assert(r('GuestPowerupAge')==updateCalls-1,'Native sequential60-update transform')
 local p={x=pos(),y=r('Player_Y_Position')}
 if firstUpdate then assert(p.x==firstUpdate.x and p.y==firstUpdate.y,'Source freeze holds real position')else firstUpdate=p end
end)
hook('M3Graphics',function()
 if C.character==17 and collected>0 and r('M3Growth')>0 then
  growthDraws=growthDraws+1;assert(r('M3Growth')==48-growthDraws,'Source47-call growth sequence')
 end
end)
emu.addMemoryCallback(function(_,v)
 if not selected()then return end
 if v&C.sfx.reveal~=0 then revealSfx=revealSfx+1 end
 if v&C.sfx.pickup~=0 then pickupSfx=pickupSfx+1 end
end,emu.callbackType.write,C.ram.Square2SoundQueue)
local phase,age='travel',0
local function aim(c,target)
 local v=c.vx>=128 and c.vx-256 or c.vx
 if c.x>target+4 then return{left=true}elseif c.x<target-4 then return{right=true}
 elseif v>1 then return{left=true}elseif v< -1 then return{right=true}else return{}end
end
local function item(c)
 for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==0x2e then return c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)end end
end
function MARIO_POWERUP_CONTROL(c,base)
 if collected==0 then
  if C.character==17 then return base(c)end
  -- Reuse the historical successful unseeded mushroom detour; current ROM
  -- execution is still required. Camera, enemy and block state remain native.
  if phase=='travel'then if c.x<404 then return base(c)end;phase='drop';age=0 end
  age=age+1;assert(age<1500,'Bounded first physical mushroom controller')
  if phase=='drop'then if c.grounded and c.y>=160 then phase='under'end;return aim(c,420)
  elseif phase=='under'then
   if c.grounded and c.x>=328 and c.x<=343 and c.vx==0 then phase='bump';age=0;return{a=true}end
   return aim(c,336)
  elseif phase=='bump'then
   if item(c)then phase='chase';age=0;return{}end
   if c.grounded and age>45 then age=0 end
   return{a=age<24}
  else local x=item(c);assert(x,'Real mushroom remains active until collection');return aim(c,math.min(430,math.max(328,x)))end
 end
 local growing=C.character==17 and r('M3Growth')~=0 or C.character~=17 and r('GuestPowerupActive')~=0
 if growing then return{}end
 if phase~='probe'then phase='probe';age=0 end
 age=age+1
 if age<=24 then return{}
 elseif age<=48 then return{down=true}
 elseif age<=56 then return{}
 elseif age<=88 then return{a=true}
 else
  if age>=160 and c.grounded then MARIO_POWERUP_DONE=true end
  assert(age<300,'Bounded powered landing after real jump')
  return{}
 end
end
emu.addEventCallback(function()
 frame=frame+1
 if not selected()or done then return end
 if r('GameEngineSubroutine')~=8 and not entered then return end
 if not entered then
  entered=true;assert(r('CrossoverBehaviorVersion')==C.mode,'Actual numeric mode from cold menu')
  assert(r(C.variantSymbol)==C.variant,'Actual selected alternate')
  assert(r('PlayerStatus')==0 and(C.character~=17 or r('M3Form')==0),'Native cold unpowered start')
 end
 local actors={}
 for i=0,5 do if r('Enemy_Flag',i)>0 and r('Enemy_ID',i)==0x2e then
  local stamp=r('InvPickup',i)
  if C.character==17 then
   assert(stamp==0xd1 and r('InvPickupOwner',i)==17,'M3 mushroom world stamp and owner remain stable')
   if lastStamp then assert(stamp==lastStamp,'No random remap during rise')end;lastStamp=stamp
  end
  actors[#actors+1]=table.concat({i,r('Enemy_State',i),r('PowerUpType',i),stamp,r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i)},':')
 end end
 csv:write(table.concat({frame,pos(),r('Player_Y_Position'),r('PlayerStatus'),r('PlayerSize'),r('GameEngineSubroutine'),r('GuestPowerupActive'),r('GuestPowerupAge'),r('M3Form'),r('M3Growth'),r('CrouchingFlag'),r('Player_State'),table.concat(actors,';')},',')..'\n')
 if phase=='probe'then
  assert(r('PlayerStatus')==1 and r('PlayerSize')==0,'Collected super form retained during controls')
  if C.character==17 then assert(r('M3Form')==1,'Native SMB3 super form retained')end
  if r('CrouchingFlag')~=0 then downFrames=downFrames+1 end
  if r('Player_State')~=0 then airFrames=airFrames+1 end
  minY=math.min(minY,r('Player_Y_Position'));maxY=math.max(maxY,r('Player_Y_Position'))
 end
 if r('GuestPowerupActive')~=0 or C.character==17 and r('M3Growth')~=0 then
  local f=assert(io.open(ROSTER_CONFIG.out..'growth-'..frame..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
end,emu.eventType.endFrame)
function MARIO_POWERUP_FINISH()
 if done then return end;done=true
 local ok=MARIO_POWERUP_DONE==true
 if ok then
  assert(revealed==1 and collected==1,'Physical block and owner executed')
  assert(revealSfx>0 and pickupSfx>0,'Actual reveal and pickup request stores')
  assert(C.character==17 and growthDraws==47 or C.character~=17 and updateCalls==60,'Source transformation duration')
  assert(downFrames>0 and airFrames>10 and maxY-minY>=12,'Actual powered crouch and jump/landing')
 end
 local f=assert(io.open(ROSTER_CONFIG.out..'powerup-component.json','w'))
 f:write(json({passed=ok,native_executed=true,ROM_sha256=C.ROM_sha256,character=C.character,variant=C.variant,actual_mode=r('CrossoverBehaviorVersion'),reveal=revealed,collect=collected,transform_updates=updateCalls,growth_draws=growthDraws,crouch_frames=downFrames,air_frames=airFrames,reveal_requests=revealSfx,pickup_requests=pickupSfx,no_fixture_game_state_writes=true,scope='One natural first-mushroom and powered controls; no flower/star/1up/suit/use/campaign claim'})..'\n');f:close();csv:close();log:close()
end
