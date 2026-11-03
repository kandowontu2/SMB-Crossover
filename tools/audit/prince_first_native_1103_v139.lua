-- Read-only observations and physical controller input; never emulated writes.
local sourceUpdates,sourceDraws,sourceTicks,contactCalls,defeatCalls,killCalls,initCalls=0,0,0,0,0,0,0
local profileMinSP=255
local function ps(off,bank)return emu.read((bank or 2)*8192+off,emu.memType.nesWorkRam)end
local function wx()return r('Player_PageLoc')*256+r('Player_X_Position')end
local function sourceActive()return r('SelectedCharacter')==38 and ps(0xab)==0xa7 end
local function headers()
 for i,v in ipairs(Q.cookie)do
  assert(ps(0x1fe0+i-1,2)==v and ps(0x1fe0+i-1,3)==v,'Both complete Prince auth headers')
 end
end
for name,h in pairs(Q.hooks)do
 emu.addMemoryCallback(function()
  if r('SelectedCharacter')~=38 then return end
  local a=emu.convertAddress(h.pc)
  if not a or a.memType~=emu.memType[h.memory]or a.address~=h.physical then return end
  for i,v in ipairs(h.bytes)do assert(ram(h.pc+i-1)==v,'Exact source hook '..name)end
  profileMinSP=math.min(profileMinSP,emu.getState()['cpu.sp'])
  if name=='PpHostUpdate'then sourceUpdates=sourceUpdates+1
  elseif name=='PpHostDraw'then sourceDraws=sourceDraws+1
  elseif name=='PpNativeTick'then sourceTicks=sourceTicks+1
  elseif name=='PpNativeContact'then contactCalls=contactCalls+1
  elseif name=='NativeDefeat'then defeatCalls=defeatCalls+1
  elseif name=='KillPlayer'then killCalls=killCalls+1
  elseif name=='PpNativeInit'then initCalls=initCalls+1 end
 end,emu.callbackType.exec,h.pc)
end
local phases={
 {name='idle',updates=16,keys={}},
 {name='right',updates=16,keys={'right'}},
 {name='left',updates=16,keys={'left'}},
 {name='unarmed-A-jump',updates=64,keys={'a'},hold=4},
 {name='supported-rest',updates=16,keys={}}
}
local part,step,last,initialLives,initialY,initialX=1,0,0,nil,nil,nil
local firstX,firstY,minY,firstUpdate,firstFrame=nil,nil,nil,nil,nil
local rows={};local deathSeen,resumedX,resumedUpdate=false,nil,nil
local jumpShot=false
local csv=assert(io.open(OUTPUT..'source-controls.csv','w'))
csv:write('frame,phase,updates,world_x,native_y,source_HP,sword,action,engine,lives,source_draws,contact,defeat,kill\n')
local function beginPart()
 step=0;last=sourceUpdates;firstX=wx();firstY=r('Player_Y_Position');minY=firstY;firstUpdate=sourceUpdates;firstFrame=frame
end
local function controls_begin()
 assert(sourceActive()and r('GameEngineSubroutine')==8,'Authenticated active Prince')
 headers();assert(ps(0x6cf)==5 and ps(0x6ee)==0,'Original 5HP/unarmed constructor')
 phase='controls';age=0;initialLives=r('NumberofLives');initialX=wx();initialY=r('Player_Y_Position');assert(initialLives==2,'Native initial lives2')
 shot('cold-active-prince');beginPart()
end
local function control_keys()
 if phase=='contact-death'then
  if not deathSeen or resumedX then return{'right'}end
  return{}
 end
 local p=phases[part];return(not p.hold or step<p.hold)and p.keys or{}
end
local function controls_finish(finish)
 assert(sourceDraws>0 and sourceUpdates>0,'Real original source update/render')
 csv:close()
 local f=assert(io.open(OUTPUT..'prince-native.json','w'))
 f:write(string.format('{"passed":true,"ROM_sha256":%q,"controller_only":true,"source_RAM_writes":false,"mode":%q,"physical_frames":%d,"source_updates":%d,"source_draws":%d,"tick_entries":%d,"contact_calls":%d,"native_defeats":%d,"native_kills":%d,"native_init_calls":%d,"minimum_observed_hook_SP":%d,"initial_lives":%d,"final_lives":%d,"unarmed_A_jump":true,"armed_strike_qualified":false,"full_stage":false,"helpers_added":false,"original_audio_qualified":false}\n',Q.ROM_sha256,Q.controlMode,frame,sourceUpdates,sourceDraws,sourceTicks,contactCalls,defeatCalls,killCalls,initCalls,profileMinSP,initialLives,r('NumberofLives')));f:close()
 finish()
end
local function controls_tick(finish)
 assert(r('SelectedCharacter')==38 and r('OperMode')==1,'Original native owner retained')
 if frame%6==0 then csv:write(table.concat({frame,phase=='controls'and phases[part].name or phase,sourceUpdates,wx(),r('Player_Y_Position'),ps(0x6cf),ps(0x6ee),ps(0x616),r('GameEngineSubroutine'),r('NumberofLives'),sourceDraws,contactCalls,defeatCalls,killCalls},',')..'\n')end
 if phase=='contact-death'then
  if r('GameEngineSubroutine')==11 then deathSeen=true end
  assert(r('NumberofLives')>=initialLives-1,'Exactly one intended life loss')
  if deathSeen and r('NumberofLives')==initialLives-1 and r('GameEngineSubroutine')==8 and r('OperMode_Task')==3 and sourceActive()and ps(0x6cf)==5 then
   headers()
   if not resumedX then resumedX=wx();resumedUpdate=sourceUpdates
   elseif wx()>=resumedX+16 then
    assert(killCalls==1 and contactCalls>0 and initCalls>=2,'Earned native contact/kill/full-cold constructor once')
    shot('native-respawn-right');controls_finish(finish)
   end
  end
  return
 end
 assert(sourceActive()and r('GameEngineSubroutine')==8 and r('NumberofLives')==initialLives,'Spawn controls retain source/native life')
 headers();minY=math.min(minY,r('Player_Y_Position'))
 if phases[part].name=='unarmed-A-jump'and not jumpShot and minY<firstY-8 then jumpShot=true;shot('original-unarmed-jump')end
 if sourceUpdates==last then return end
 assert(sourceUpdates==last+1,'At most one source update per observed physical frame');last=sourceUpdates;step=step+1
 local p=phases[part];if step<p.updates then return end
 if p.name=='idle'then assert(wx()==firstX,'Original idle stays still')
 elseif p.name=='right'then assert(wx()>firstX,'Original Right advances')
 elseif p.name=='left'then assert(wx()<firstX,'Original Left reverses')
 elseif p.name=='unarmed-A-jump'then assert(minY<firstY-8 and jumpShot,'Original unarmed A jumps');assert(r('Player_State')==0,'Original supported jump landing')
 elseif p.name=='supported-rest'then assert(r('Player_State')==0,'Original supported rest')end
 rows[#rows+1]={name=p.name,updates=step,frames=frame-firstFrame,first_x=firstX,last_x=wx(),min_y=minY}
 if part<#phases then part=part+1;beginPart();return end
 if Q.controlMode=='contact-death'then phase='contact-death';age=0;return end
 controls_finish(finish)
end
