-- Pinned2.02 character DEFAULT_PROPS: Link STOP400+FLASH400; Simon
-- STOP400; Ryu FLASH400 with no STOP. Real B creates the isolated hit.
local character=assert(SOURCE_EFFECT_CHARACTER)
local boomerang=SOURCE_EFFECT_BOOMERANG or false
assert(not boomerang or character==4,'Link owns the independent boomerang properties')
local frame,depth,hit,checked=0,0,false,false
local samples,pending,first,draw,dma=0,nil,nil,nil,nil
local paletteReference,flashPhases={},{}
local dmaChecks,moved,resumed=0,false,false
local stopFrames=boomerang and 3000/(1000/60)or character==10 and 0 or 400/(1000/60)
local flashFrames=boomerang and 0 or character==5 and 0 or 400/(1000/60)
local targetHP=boomerang and 500 or 425
local stoppedPoses={}
local mapping={2,1,2,3} -- documented finite-NES approximation, source phases0..3.
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced source enemy-effect interrupts')end,emu.callbackType.exec,pc)end
emu.addEventCallback(function()
 local choosing=character<6 and frame>=80 and frame<80+20*character and frame%20==0 or character==10 and frame>=100 and frame<180 and frame%20==0
 emu.setInput({right=choosing,down=character==10 and(frame==80 or(frame>=550 and frame<600)),start=frame==240,b=not boomerang and frame==560,select=boomerang and frame==560},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function(_,value)
 if not boomerang and frame>=560 and depth==0 and r('CurrentBank')%128==8 and value==425%256 then
  assert(r('MmEnemySlot')==0,'Actual source attack hits the designated enemy')
  hit=true
 end
end,emu.callbackType.write,assert(L.MmEnemyHealthLo))
if boomerang then emu.addMemoryCallback(function()
 if frame>=560 and depth==0 and r('CurrentBank')%128==61 then
  assert(r('MmEnemySlot')==0,'Actual controller-launched boomerang collides with its designated enemy')
  hit=true
 end
end,emu.callbackType.exec,assert(L.LsrEffectsBoomerang))end
emu.addMemoryCallback(function()
 if not hit or depth~=0 or r('CurrentBank')%128~=0 or r('ObjectOffset')~=0 then return end
 assert(not pending,'One native enemy movement per complete source effect update')
 local expected=math.max(stopFrames-samples,0)
 local flash=math.max(flashFrames-samples,0)
 assert(r('RgEnemyStun')==expected,'Source STOP trajectory before native movement c'..character..' sample'..samples..': '..r('RgEnemyStun')..' expected'..expected)
 assert(r('MmEnemyFlash')==flash,'Source FLASH duration independent of STOP c'..character..' sample'..samples..': '..r('MmEnemyFlash')..' expected'..flash)
 assert(r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi')==targetHP,'Actual source attack has its own damage and no repeated contact damage')
 local sample={x=r('Enemy_X_Position')+256*r('Enemy_PageLoc'),y=r('Enemy_Y_Position'),
  frameTimer=r('EnemyFrameTimer'),interval=r('EnemyIntervalTimer'),pose=r('EnemyMetasprite')}
 if not first then first=sample end
 if expected>0 then
  assert(sample.x==first.x and sample.y==first.y,'STOP blocks all enemy physics, without enemy knockback')
  assert(sample.frameTimer==first.frameTimer and sample.interval==first.interval,'STOP pauses native per-object frame and interval timers')
  if boomerang then stoppedPoses[sample.pose]=true;assert(r('LsrFrozenPose')==0,'Boomerang STOP3000 explicitly leaves source animation running')else assert(sample.pose==first.pose,'STOP400 keeps the actual source animation frame')end
 elseif samples>=math.max(stopFrames+2,2)then
  if sample.x~=first.x then moved=true end
  assert(sample.frameTimer<first.frameTimer,'Own frame timer resumes when STOP expires')
  resumed=true
 end
 assert(r('Enemy_X_Speed')==8,'No registered source enemy knockback changes the native velocity')
 pending={n=samples,expected=expected,sample=sample};samples=samples+1
end,emu.callbackType.exec,assert(L.EnemyMovementSubs))
emu.addMemoryCallback(function()
 if not pending or depth~=0 or r('CurrentBank')%128~=0 then return end
 assert(r('RgEnemyStun')==math.max(pending.expected-1,0),'Exactly one STOP timer update after the complete enemy loop')
 if pending.expected>0 then
  assert(r('Enemy_X_Position')+256*r('Enemy_PageLoc')==first.x and r('Enemy_Y_Position')==first.y,'STOP position remains fixed through the whole native enemy loop')
  if not boomerang then assert(r('EnemyMetasprite')==first.pose,'Actual rendered metasprite stays fixed during STOP400')end
 end
 pending=nil
-- This native foreground tail follows deferred attacks and the optional
-- effects pass. An all-zero effect pass may now be omitted; source timing
-- assertions still run after EVERY complete enemy loop, including recovery.
end,emu.callbackType.exec,assert(L.GetPlayerOffscreenBits))
-- Observe completed foreground OAM writes, not a draw-entry tag: an NMI can
-- legitimately DMA the previous completed page while a new draw is in flight.
local targetWritten=false
local function inspectEnemyPalette()
 local remaining=r('MmEnemyFlash')
 local phase=remaining>0 and(((flashFrames-remaining)//2+1)%4)or nil
 if phase then flashPhases[phase]=true end
 local expected=phase and mapping[phase+1]or 3
 local count=0
 for i=0,63 do
  local tile=r('Sprite_Tilenumber',i*4)&254
  if r('Sprite_Y_Position',i*4)<240 and(tile==0xa2 or tile==0xa4)then
   local attr=r('Sprite_Attributes',i*4)
   assert(attr&3==expected,'Completed actual enemy OAM draw uses source FLASH phase: remaining'..remaining..' actual'..(attr&3)..' expected'..expected)
   assert(attr&12==0,'Outline/FLASH software tags never reach hardware OAM')
   count=count+1
  end
 end
 assert(count==2,'Both source enemy tiles complete their own draw')
 targetWritten=true
end
if L.LsrFlashDrawComplete then
 local drawingEnemy=false
 emu.addMemoryCallback(function()
  if hit and depth==0 and r('CurrentBank')%128==4 then drawingEnemy=emu.getState()['cpu.y']==1 end
 end,emu.callbackType.exec,assert(L.DrawMetasprite))
 emu.addMemoryCallback(function()
  if drawingEnemy and depth==0 and r('CurrentBank')%128==4 then drawingEnemy=false;inspectEnemyPalette()end
 end,emu.callbackType.exec,L.LsrFlashDrawComplete)
else
emu.addMemoryCallback(function(address,value)
 if not hit or depth~=0 or r('CurrentBank')%128~=4 or(address-L.Sprite_Tilenumber)%4~=0 then return end
 local tile=value&254;if tile~=0xa2 and tile~=0xa4 then return end
 local remaining=r('MmEnemyFlash')
 local phase=remaining>0 and(((flashFrames-remaining)//2+1)%4)or nil
 if phase then flashPhases[phase]=true end
 local expected=phase and mapping[phase+1]or 3
 local attr=emu.read(address+1,emu.memType.nesDebug)
 assert(attr&3==expected,'Actual foreground enemy OAM uses source FLASH phase: remaining'..remaining..' actual'..(attr&3)..' expected'..expected..' Atr'..r('R3'))
 assert(attr&12==0,'Outline/FLASH software tags never reach hardware OAM')
 targetWritten=true
end,emu.callbackType.write,assert(L.Sprite_Tilenumber),L.Sprite_Tilenumber+255)
end
emu.addMemoryCallback(function(_,page)
 if not hit or not targetWritten then return end
 dma={};for i=0,255 do dma[i]=emu.read(page*256+i,emu.memType.nesDebug)end
end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 if not dma then return end
 local count=0
 for i=0,255 do assert(emu.read(i,emu.memType.nesSpriteRam)==dma[i],'Actual hardware sprite DMA matches the completed foreground OAM page')end
 for i=0,63 do local tile=dma[i*4+1]&254;if dma[i*4]<240 and(tile==0xa2 or tile==0xa4)then count=count+1 end end
 assert(count==2,'Both actual Goomba sprites reach the completed DMA: '..count)
 for i=0,15 do
  local value=emu.read(0x3f10+i,emu.memType.nesPpuDebug)
  if paletteReference[i]~=nil then assert(value==paletteReference[i],'Enemy FLASH leaves all simultaneous player/powerup palette RAM unchanged')else paletteReference[i]=value end
 end
 dmaChecks=dmaChecks+1;dma=nil
 if samples>=math.max(stopFrames+12,36)and not pending then
  assert(moved and resumed,'Target resumes movement and own timers after STOP; Ryu never invents a stop')
  if flashFrames>0 then for phase=0,3 do assert(flashPhases[phase],'Every source FLASH phase reaches the renderer')end end
  assert(dmaChecks>=math.max(stopFrames,24),'Full visible source effect trajectory is observed through completed DMA')
  if boomerang then local n=0;for _ in pairs(stoppedPoses)do n=n+1 end;assert(n>=2,'Both native animation frames continue during the full180-update boomerang STOP')end
  print('PASS source enemy effects c'..character..' boomerang'..tostring(boomerang)..': controller hit, STOP'..stopFrames..'/FLASH'..flashFrames..' trajectory, own timers, fixed/continuing/resumed pose, no knockback, independent phase DMA mapping and unchanged palette RAM');emu.stop(0)
 end
end,emu.eventType.endFrame)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  assert(r('SelectedCharacter')==character and r('GameEngineSubroutine')==8,'Real menu launches source effect character'..character)
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col)end end
  for i=0,5 do w('Enemy_Flag',0,i);w('RgEnemyStun',0,i)end
  for i=0,9 do w('RgShotType',0,i)end
  w('Player_X_Position',96);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0);w('HorizontalScroll',0)
  w('Player_State',0);w('PlayerStatus',1);w('PlayerSize',0);w('InvOwnedLo',1,character);w('InvOwnedHi',0,character)
  w('PlayerFacingDir',1);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('InjuryTimer',255)
  w('RgAttack',0);w('RgMeleeHits',0);w('RgThrust',0);w('RgThrustReset',0);w('RgCrouch',0);w('RgPreviousButtons',0);w('AvSlash',0)
  w('GameEngineSubroutine',8);w('TimerControl',0);w('GuestPowerupActive',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  w('Enemy_Flag',1);w('Enemy_ID',6);w('Enemy_State',0);w('Enemy_BoundBoxCtrl',9)
  w('EnemyFrameTimer',90);w('EnemyIntervalTimer',11);w('InvSelected',0,character);w('Enemy_X_Position',boomerang and 132 or 116);w('Enemy_PageLoc',0);w('Enemy_Y_Position',176);w('Enemy_Y_HighPos',1);w('Enemy_X_Speed',8);w('Enemy_Y_Speed',0);w('EnemyOffscrBitsMasked',0);w('Enemy_MovingDir',1)
  w('MmEnemyHealthLo',500%256);w('MmEnemyHealthHi',1)
 end
 assert(frame<(boomerang and 1200 or 850),'One real character melee hit reaches its movement effect: char'..r('SelectedCharacter')..' hp'..(r('MmEnemyHealthLo')+256*r('MmEnemyHealthHi'))..' hit'..tostring(hit)..' attack'..r('RgAttack')..' pose'..r('RgPose')..' x'..r('Player_X_Position')..' y'..r('Player_Y_Position')..' enemy'..r('Enemy_X_Position')..'/'..r('Enemy_Y_Position'))
end,emu.eventType.endFrame)
