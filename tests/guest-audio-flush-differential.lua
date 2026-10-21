-- Synthetic, stationary audio fixture. The reference is the pre-optimization
-- v5 hardware-write trace, not a second implementation of the fast flush.
-- Cues cover native-only updates, mixed owners, ownership release and pause.
local frame=0
local output=assert(io.open(OUTPUT..ROM_NAME..'-guest-audio-flush.bin','wb'))
local writes=0
local characters={1,2,3,4,5,6,7,9,10,11,12}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function capture(address,value)
 if frame>=550 and address~=0x4014 then
  output:write(string.pack('<I2I2B',frame,address,value));writes=writes+1
 end
end
emu.addMemoryCallback(capture,emu.callbackType.write,0x4000,0x4015)
emu.addMemoryCallback(capture,emu.callbackType.write,0x5000,0x5015)
emu.addEventCallback(function()
 emu.setInput({right=frame==80,start=frame==200},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 local index=(frame-550)//360+1
 if index>#characters then
  output:close()
  assert(writes>10000,'All native drivers and shared effects reach the hardware APU')
  print('PASS guest audio hardware flush trace: '..#characters..' native drivers, '..writes..' ordered writes, effects/transitions/pause');emu.stop(0);return
 end
 local age=(frame-550)%360
 for i=0,5 do w('Enemy_Flag',0,i)end
 w('Player_X_Position',64);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0)
 if age==0 then
  for i=0,415 do w('Block_Buffer_1',0,i)end
  for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
  w('SelectedCharacter',characters[index]);w('AreaMusicQueue',1)
  w('GamePauseStatus',0);w('GameEngineSubroutine',8)
 end
 if age==40 then w('Square1SoundQueue',2)end
 if age==90 then w('Square2SoundQueue',1)end
 if age==160 then w('NoiseSoundQueue',1)end
 if age==210 then
  w('Square1SoundQueue',2);w('Square2SoundQueue',2);w('NoiseSoundQueue',1)
 end
 if age==260 then w('GamePauseStatus',1)end
 if age==265 then w('GamePauseStatus',0)end
 if age==305 then w('AreaMusicQueue',1)end
end,emu.eventType.endFrame)
