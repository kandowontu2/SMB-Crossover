local frame=0
local apuWrites=0
emu.addMemoryCallback(function() apuWrites=apuWrites+1 end,emu.callbackType.write,0x4000,0x400f)
local character=assert(ROSTER_CHARACTER)
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
local function velocity(n) local a=r(n)+r(n,1)*256+r(n,2)*65536; if a>=0x800000 then a=a-0x1000000 end;return a/65536 end
local function shotCount() local n=0;for i=0,9 do if r('RgShotType',i)>0 then n=n+1 end end;return n end
local function spriteChr(address)
 if ROM_NAME:find('mmc5',1,true)then
  local bank=emu.getState()['mapper.chrBanks'..math.floor(address/1024)]
  return emu.read(bank*1024+address%1024,emu.memType.nesChrRom)
 end
 return emu.read(address,emu.memType.nesPpuDebug)
end
local function capture(tag) local f=assert(io.open(OUTPUT..ROM_NAME..'-roster-'..character..(ROSTER_LANCE and '-lance' or '')..'-'..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close() end
emu.addEventCallback(function()
  local choose=frame>=80 and frame<80+20*character and (frame-80)%20==0
  emu.setInput({right=choose or (frame>=560 and frame<580),start=frame==200,
    a=(frame>=620 and frame<650), b=frame==700 or (frame>=760 and frame<785) or frame==900,
    up=character==5 and frame==900,select=(character==4 and frame==900)or(ROSTER_LANCE and frame==160)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame==550 then
  assert(r('SelectedCharacter')==character and r('GameEngineSubroutine')==8,'Selected guest starts gameplay: character '..r('SelectedCharacter')..' engine '..r('GameEngineSubroutine')..' menu '..r('CrossoverMenuState')..' variant '..r('BillVariant'))
  if ROSTER_LANCE then assert(r('BillVariant')==1,'Lance stays selected after loading')end
  assert(r('ObjectMetasprite')==L.METASPRITE_SAMUS_BODY,'Guest uses private metasprite')
  assert(r('RgAudioCharacter')==character and r('RgAudioSong')>0 and apuWrites>200,'Native character music writes the APU')
  if character==3 or character==5 then
   assert(emu.read(0x3f19,emu.memType.nesPpuDebug)==0x16,'Guest preserves mushroom red')
   assert(emu.read(0x3f1a,emu.memType.nesPpuDebug)==0x30,'Guest preserves mushroom white')
   assert(emu.read(0x3f1b,emu.memType.nesPpuDebug)==0x27,'Guest preserves mushroom tan')
  end
  if character==3 then
   -- Both hosted bullet frames fit one sprite and use only red/white.
   -- Inspect actual mapped CHR so a future asset change cannot silently
   -- start using the shared tan entry as an intended black outline.
   for address=0,63 do
    local low=spriteChr(address)
    if address%16<8 then
     local high=spriteChr(address+8)
     assert((low & high)==0,'Bill bullet art does not use palette color 3')
    end
   end
  end
  capture('standing')
 end
 if frame==575 then
  assert(velocity('MmVX')>0.8 and velocity('MmVX')<1.6,'Source walk velocity')
  capture('walk')
 end
 if frame==625 then assert(velocity('MmVY')< -2,'Guest jumps');capture('jump') end
 if frame==699 then
  w('Player_X_Position',40);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_State',0);w('Player_Y_Speed',0)
  for i=0,2 do w('MmVY',0,i);w('MmVX',0,i) end
 end
 if frame==702 then
  if character==3 then assert(shotCount()==1,'Bill fires his normal gun') else assert(r('RgAttack')>0,'Guest starts melee attack') end
 end
 if frame==710 then capture('attack') end
 if frame==750 then w('PlayerStatus',1) end
 if frame==779 and character==3 then assert(shotCount()>=3,'Bill machine gun repeats while B is held') end
 if frame==899 then w('PlayerStatus',2);if character==4 then w('InvOwnedLo',9,4);w('InvSelected',3,4)elseif character==5 then w('InvOwnedLo',0x41,5);w('InvSelected',6,5);w('InvAmmo',10,80)end end
 if frame==916 then
  if character==3 then assert(shotCount()>=5,'Bill spread gun fires a five-shot fan')
  elseif character==4 then assert(shotCount()==1,'Link throws boomerang')
  else assert(shotCount()==1,'Simon throws axe') end
  capture('special')
 end
 if frame==980 then print('PASS roster '..character..' title selection, graphics, walk, jump, attacks and upgraded special');emu.stop(0) end
end,emu.eventType.endFrame)
