-- Controller startup/crouch followed by explicit zero-pose renderer fixtures.
local frame,checked,last=0,0,-1
local before,offset
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({down=(frame>=550 and frame<590),select=frame==180,start=frame==240},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame<600 or frame>=664 or last==frame then return end
 last=frame;before={}
 for i=0,255 do before[i]=r('Sprite_Y_Position',i) end
 offset=(frame-600)*4
 w('CurrentOAMOffset',offset)
 w('RgMeleeBlocks',0);w('RgMeleeBlocks',255,1)
 w('R0',L.RgMeleeBlocks%256);w('R1',math.floor(L.RgMeleeBlocks/256))
end,emu.callbackType.exec,L.MetaspriteRenderLoop)
emu.addMemoryCallback(function()
 if not before then return end
 assert(r('CurrentOAMOffset')==offset,'Empty metasprite preserves the allocation cursor')
 for i=0,255 do assert(r('Sprite_Y_Position',i)==before[i],'Empty metasprite changes no OAM byte at '..i) end
 checked=checked+1;before=nil
end,emu.callbackType.exec,L.EmptyMetaspriteReturn)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=552 and frame<590 then
  assert(r('SelectedCharacter')==8 and r('PlayerStatus')==0,'Fresh small Luigi')
  assert(r('RgCrouch')==0 and r('CrouchingFlag')==0,'Small Luigi ignores Down for crouching')
 end
 if frame==665 then
  assert(checked==64,'All 64 OAM cursor values exercised: '..checked)
  assert(r('GameEngineSubroutine')==8,'Gameplay survives all empty draws')
  print('PASS small Luigi crouch and zero-length metasprites preserve every OAM byte at all 64 allocation offsets');emu.stop(0)
 end
end,emu.eventType.endFrame)
