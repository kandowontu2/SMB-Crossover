-- Regression: acquire a real masonry cell with Super Arm, then throw it
-- into a question block. All projectile creation comes from controller B.
local frame=0
local startTick
local used=false
local reward=false
local fragments=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==200,
  b=(frame>=560 and frame<566)or(frame>=585 and frame<591)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then
  for i=0,5 do w('Enemy_Flag',0,i)end
  for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
  for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
  w('Block_Buffer_1',0x51,160+3)
  w('Block_Buffer_1',0xc1,112+4)
  w('Block_Buffer_1',0x51,112+5)
  w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('Player_State',0);w('PlayerFacingDir',1);w('Player_X_Speed',0);w('Player_Y_Speed',0)
  w('PlayerStatus',1);w('InvOwnedLo',3,9);w('InvViewedLo',2,9);w('InvSelected',1,9);w('InvDirty',1)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
  startTick=r('FrameCounter')
 end
 if frame==580 then assert(r('SsHeld')>0,'Super Arm lifted the masonry brick')end
 if frame>=585 then
  if r('Block_Buffer_1',112+4)==0xc4 then used=true end
  local n=0;for i=0,9 do if r('RgShotType',i)==21 then n=n+1 end end
  fragments=math.max(fragments,n)
  for i=0,5 do if r('Enemy_Flag',i)>0 and r('Enemy_ID',i)==0x2e then reward=true end end
 end
 if frame==750 then
  local s=emu.getState()
  assert(r('GameEngineSubroutine')==8 and (r('FrameCounter')-startTick)%256>=100,
   'Thrown brick cannot lock the main loop: PC '..tostring(s['cpu.pc'])..' bank '..r('CurrentBank')..' RgSlot '..r('RgSlot'))
  assert(used,'Question block becomes its used cell')
  assert(reward,'Question block releases its native inventory reward')
  assert(fragments==4,'Thrown brick shatters into four independent fragments')
  assert(r('Block_Buffer_1',112+5)==0x51,'Adjacent masonry is not consumed by the question-block contact')
  print('PASS Bass Super Arm question-block reward, four fragments, adjacent masonry and live main loop');emu.stop(0)
 end
end,emu.eventType.endFrame)
