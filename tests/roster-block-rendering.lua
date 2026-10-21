local frame=0
local character=assert(BLOCK_CHARACTER)
local rendering=false
local chunkFrames=0
local outsideWrites=0
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addMemoryCallback(function() rendering=false end,emu.callbackType.exec,L.GameCoreRoutine)
emu.addMemoryCallback(function() if r('CurrentBank')%128==4 then rendering=true end end,emu.callbackType.exec,L.DrawAllMetasprites)
emu.addMemoryCallback(function()
 if frame>=560 and not rendering then outsideWrites=outsideWrites+1 end
end,emu.callbackType.write,0x200,0x2ff)
emu.addEventCallback(function()
 emu.setInput({right=frame>=80 and frame<80+20*character and (frame-80)%20==0,start=frame==200,b=frame==560},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame==550 then
  for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i);w('BlockMetasprite',0,i) end
  for i=0,415 do w('Block_Buffer_1',0,i) end
  for col=0,15 do w('Block_Buffer_1',0x54,176+col) end
  w('Block_Buffer_1',0x51,167);w('MmSolidTerrain',0,167)
  w('Player_X_Position',88);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
  w('Player_State',0);w('Player_Y_Speed',0);w('PlayerStatus',0)
  w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 end
 if frame>=560 and frame<640 then
  assert(r('Player_X_Position')==88 and r('Player_PageLoc')==0 and r('Player_Y_Position')==176,'Block attack cannot teleport the player at '..frame)
  for i=0,1 do if r('Block_State',i)==2 then
   assert(r('Block_Orig_XPos',i)==112 and r('Block_PageLoc2',i)==0,'Destroyed block remains aligned to the struck cell')
   local count=0
   local tile=ROM_NAME:find('mmc5') and 0x56 or 0x57
   for offset=0,255,4 do if r('Sprite_Tilenumber',offset)==tile and r('Sprite_Y_Position',offset)<240 then count=count+1 end end
   if count>=4 then chunkFrames=chunkFrames+1 end
  end end
 end
 if frame==640 then
  assert(r('Block_Buffer_1',167)==0,'Sword/whip destroys the brick')
  assert(chunkFrames>8,'Four moving brick chunks persist through the final sprite pass: '..chunkFrames)
  assert(outsideWrites==0,'Physics must not overwrite the previous OAM on a skipped draw frame: '..outsideWrites)
  print('PASS guest '..character..' brick debris, cell alignment, stable player position and no premature OAM writes');emu.stop(0)
 end
end,emu.eventType.endFrame)
