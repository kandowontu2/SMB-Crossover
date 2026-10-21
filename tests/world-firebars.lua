-- Explicit actor/terrain fixtures across twelve characters and Lance.
-- Collision runs natively; final OAM and the actual mapped CHR are inspected.
local frame,age,phase,checks=0,0,0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local mapper=ROM_NAME:find('mmc5',1,true)and'mmc5'or'mmc3'
local f=assert(io.open(TEST_DIR..'../chr/'..mapper..'/sprites_mario.chr','rb'));local mario=f:read('*a');f:close()
f=assert(io.open(TEST_DIR..'../chr/'..mapper..'/sprites_misc.chr','rb'));local misc=f:read('*a');f:close()
local base=mapper=='mmc3'and 0x1400 or 0x400
local tile=mapper=='mmc3'and 0x41 or 0x40
local function spriteChr(address)
 -- MMC5's debugger PPU read selects background CHR. Inspect the actual
 -- mapped sprite bank instead; its sprite/background windows are distinct.
 if mapper=='mmc5' then
  local bank=emu.getState()['mapper.chrBanks'..math.floor(address/1024)]
  return emu.read(bank*1024+address%1024,emu.memType.nesChrRom)
 end
 return emu.read(address,emu.memType.nesPpuDebug)
end
local function setup()
 local c=math.floor(phase/2)
 w('SelectedCharacter',c==12 and 3 or c==13 and 12 or c);w('BillVariant',c==12 and 1 or 0)
 for i=0,5 do w('Enemy_Flag',0,i);w('EnemyMetasprite',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i)end
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,p*208+176+x)end end
 w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_Y_Speed',0);w('Player_X_Speed',0);w('PlayerStatus',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 w('Enemy_Flag',1);w('Enemy_ID',phase%2==0 and 0x1b or 0x1f);w('Enemy_State',0)
 w('Enemy_X_Position',128);w('Enemy_PageLoc',0);w('Enemy_Y_Position',144);w('Enemy_Y_HighPos',1)
 w('FirebarSpinState_Low',0);w('FirebarSpinState_High',0);w('FirebarSpinSpeed',0);w('FirebarSpinDirection',0)
 w('TimerControl',0);w('StarInvincibleTimer',0);w('GameEngineSubroutine',8)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 age=0;checks=0
end
emu.addMemoryCallback(function()
 if frame<550 or age<8 or r('CurrentBank')%128~=7 then return end
 local length=phase%2==0 and 6 or 12
 assert(r('FirebarPartCount')==length,'Native short/long firebar retains every collision part')
 local found={};local count=0
 for o=0,255,4 do
  local t=r('Sprite_Tilenumber',o);local y=r('Sprite_Y_Position',o);local x=r('Sprite_X_Position',o)
  if y<240 and x==128 and(t==tile or t==tile+2)then found[y]=true;count=count+1 end
 end
 assert(count==length,'Every firebar part survives final guest OAM clearing, character '..math.floor(phase/2)..' count '..count..' / '..length)
 for p=0,length-1 do assert(found[140-p*8],'Complete native eight-pixel firebar spacing')end
 checks=checks+1
end,emu.callbackType.exec,L.WorldFirebarsOamReady)
emu.addEventCallback(function()emu.setInput({right=frame==80 or frame==100 or frame==120,start=frame==200},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==199 then w('LevelNumber',3);w('AreaNumber',4)end
 if frame<550 then return end
 if frame==550 then setup();return end
 age=age+1
 if age==30 then
  for i=0,63 do assert(spriteChr(base+i)==mario:byte(2*1024+0x3c*16+i+1),'Firebar uses native art independently of guest body CHR')end
  for i=0,63 do assert(spriteChr(base+0x3c*16+i)==misc:byte(0x3c*16+i+1),'Native mushroom graphics remain intact')end
  if phase==6 or phase==7 or phase==24 then
   local out=assert(io.open(OUTPUT..ROM_NAME..'-firebar-'..phase..'.png','wb'));out:write(emu.takeScreenshot());out:close()
  end
 end
 if age==40 then
  assert(checks>0,'Final firebar rendering executed for character '..math.floor(phase/2))
  phase=phase+1
  if phase==28 then
   print('PASS short/long firebars for all thirteen characters and Lance: all native parts, final OAM, spacing, independent CHR and preserved mushrooms')
   emu.stop(0)
  else setup()end
 end
end,emu.eventType.endFrame)
