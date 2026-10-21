-- Verify the decoder against frozen source NSF register images, including
-- every owned register and the music image restored after releasing voices.
local refs=dofile(TEST_DIR..'fixtures/bass-source-sfx.lua')
local cases={{21,'Shoot'},{19,'Land'},{22,'TakeDamage'},{23,'Die'},
 {24,'HitEnemy'},{25,'Deflect'},{20,'GetNewLife'},{28,'GetEnergy'},
 {60,'PharaohShotSmall'},{61,'PharaohShotBig'},{63,'MetalBlade'},
 {64,'ChargeKick'},{65,'WaterShieldExpand'},{67,'Teleport'},
 {62,'GetEnergyLoop'}}
local frame,phase,age,cursor,checks=0,1,0,0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 if frame<550 or r('SelectedCharacter')~=9 or r('CurrentBankC')%128~=34 or r('BassSourceId')==0 then return end
 cursor=cursor+1
 local ref=refs[cases[phase][2]]
 local index=cursor
 if phase==#cases and index>7 then index=3+(index-8)%5 end
 local image=assert(ref.frames[index],'Sound lasts exactly the source duration: '..cases[phase][2]..'/'..cursor)
 assert(r('BassAudioMask')==ref.mask,'Source effect owns the source voices')
 for register=0,15 do
  if ref.mask&(1<<math.floor(register/4))~=0 then
   assert(r('BassAudioSfxApu',register)==image[register+1],cases[phase][2]..' frame '..cursor..' register '..register..' differs from source')
   checks=checks+1
  end
 end
end,emu.callbackType.exec,L.BassSourceFrameReady)
emu.addMemoryCallback(function()
 if frame<550 or r('SelectedCharacter')~=9 or r('CurrentBankC')%128~=34 then return end
 for register=0,15 do
  local active=r('BassAudioMask')&(1<<math.floor(register/4))~=0
  assert(r('GuestNativeApu',register)==r(active and 'BassAudioSfxApu' or 'XgMusicApu',register),'Effect/music mixing preserves every unowned voice')
 end
end,emu.callbackType.exec,L.BassSourceMixFinish)
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if frame==550 then
  for i=0,415 do w('Block_Buffer_1',0,i)end
  for x=0,15 do w('Block_Buffer_1',0x54,176+x)end
  w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 end
 for i=0,5 do w('Enemy_Flag',0,i)end
 age=age+1
 if age==10 then w('SsAudioRequest',cases[phase][1]+1)end
 local duration=phase==#cases and 27 or #refs[cases[phase][2]].frames
 if phase==#cases and cursor>=duration and age==10+duration then w('SsAudioRequest',242)end
 if age==duration+18 then
  assert(cursor==duration,'All native SFX frames were checked: '..cases[phase][2]..' '..cursor..'/'..duration)
  assert(r('BassSourceId')==0 and r('BassAudioMask')==0,'The effect releases all voices, including stopped refill loops')
  phase=phase+1;age=0;cursor=0
  if phase>#cases then print('PASS '..checks..' source NSF register comparisons across 15 Bass effects, refill looping/stop, and independent MM10 music restoration');emu.stop(0)end
 end
end,emu.eventType.endFrame)
