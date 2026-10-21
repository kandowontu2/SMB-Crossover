-- Explicit collision/pickup fixtures after controller-only menu startup.
local frame=0
local c=assert(EXPANDED_CHARACTER)
local startX,jumpY
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function shots()local n=0;for i=0,9 do if r('RgShotType',i)>0 then n=n+1 end end;return n end
local function pickup()
 for i=0,5 do w('Enemy_Flag',0,i) end
 w('Enemy_Flag',1,5);w('Enemy_ID',0x2e,5);w('Enemy_State',0x80,5)
 w('PowerUpType',0,5);w('Enemy_BoundBoxCtrl',3,5)
 w('Enemy_X_Position',r('Player_X_Position'),5);w('Enemy_PageLoc',r('Player_PageLoc'),5)
 w('Enemy_Y_Position',184,5);w('Enemy_Y_HighPos',1,5)
 w('Enemy_X_Speed',0,5);w('Enemy_Y_Speed',0,5)
end
local function shot(tag)
 local f=assert(io.open(OUTPUT..ROM_NAME..'-expanded-'..c..'-'..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
emu.addEventCallback(function()
 emu.setInput({down=c~=8 and frame==80,right=(c~=8 and frame>=100 and frame<100+20*(c-6) and (frame-100)%20==0) or (frame>=640 and frame<665),start=frame==240,
 a=frame>=700 and frame<720,b=(frame>=1000 and frame<1020) or frame==1040,up=frame==1040,select=(c==8 and frame==180) or (c==10 and frame==1040) or (c==11 and frame==1060)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=590 then for i=0,5 do if r('Enemy_ID',i)~=0x2e then w('Enemy_Flag',0,i) end end end
 if frame==620 then
  assert(r('SelectedCharacter')==c and r('GameEngineSubroutine')==8,'Added character starts World 1-1')
  assert(r('ObjectMetasprite')==L.METASPRITE_SAMUS_BODY,'Private added-character pose is active')
  assert(r('SmChrBank')>=0xd1,'Added character uses its own CHR')
  startX=r('Player_X_Position');shot('standing')
  if c==6 then
   for i,v in ipairs({0x07,0x26,0x30}) do assert(emu.read(0x3f10+i,emu.memType.nesPpuDebug)==v,'Pit retains native brown hair, flesh and white wings') end
  end
 end
 if frame==670 then assert(r('Player_X_Position')>startX+8,'Character moves under controller input');jumpY=r('Player_Y_Position') end
 if frame==706 then assert(r('Player_Y_Position')<jumpY-8,'Character jumps');shot('jump') end
 if frame==749 then
  w('Player_X_Position',40);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0);w('Player_Y_Speed',0)
  for i=0,2 do w('MmVX',0,i);w('MmVY',0,i) end
 end
 if frame==750 then pickup() end
 if frame==840 then assert(r('PlayerStatus')==1 and r('GuestPowerupActive')==0,'Real mushroom collision completes first upgrade') end
 if frame==880 then pickup() end
 if frame==970 then assert(r('PlayerStatus')==2 and r('GuestPowerupActive')==0,'Real power-up collision completes second upgrade');shot('upgraded') end
 if frame==995 then
  if c==10 then w('InvOwnedLo',3,10);w('InvSelected',1,10);w('InvAmmo',50,160)end
  if c==11 then w('InvOwnedLo',3,11);w('InvSelected',1,11);w('InvAmmo',20,177)end
 end
 if frame==1006 then
  if c==10 then
   assert(r('RgAttack')>0,'Ryu swings the sword')
   local bladeParts=0
   for offset=0,255,4 do if r('Sprite_Y_Position',offset)<240 and (r('Sprite_Attributes',offset)&3)==2 then bladeParts=bladeParts+1 end end
   assert(bladeParts>=2,'The actual sword blade reaches OAM alongside the body')
   for line=176,207 do
    local count=0
    for offset=0,255,4 do local y=r('Sprite_Y_Position',offset)+1;if y<=line and line<y+16 then count=count+1 end end
    assert(count<=8,'Ryu and his sword fit the hardware scanline limit without other actors: '..count)
   end
  else assert(shots()>0,'Added character fires its primary weapon') end
  shot('attack')
 end
 if frame==1048 then
  if c==6 then
   local up=false;for i=0,9 do if r('RgShotType',i)==1 and r('RgShotVYHi',i)>=128 then up=true end end
   assert(up,'Pit fires arrows upward')
  elseif c==10 then assert(shots()>0,'Ryu throws a shuriken') end
 end
 if frame==1068 and c==11 then
  local missile=false;for i=0,9 do if r('RgShotType',i)==44 then missile=true end end
  assert(missile,'Sophia fires upgraded missiles')
 end
 if frame==1250 then
  if c==7 then assert(shots()==0,'Diskarmor returns to Rygar') end
  assert(r('GameEngineSubroutine')==8,'Gameplay stays active after movement and weapon interactions')
  print('PASS added character '..c..' selection, private graphics, movement, jump, real pickups, primary and special weapons');emu.stop(0)
 end
end,emu.eventType.endFrame)
