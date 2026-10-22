-- Ordinary title/Options/roster inputs; only the final pit-death arena is seeded.
-- No menu-bootstrap: observe genuine behavior1.0 and shadows-OFF defaults.
local frame=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function count()
 local n=0
 for i=0,63 do if emu.read(i*4,emu.memType.nesSpriteRam)<240 then n=n+1 end end
 return n
end
local function shot(tag)
 local f=assert(io.open(OUTPUT..ROM_NAME..'-outlines-'..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
-- 'PLAYER OUTLINES  ' (17 tiles from $2165) puts the ON/OFF value at $2176.
local function text(address,expected)
 for i=1,#expected do
  local c=expected:byte(i)
  local tile=c==32 and 0x24 or c>=65 and c<=90 and c-65+0x0a or c-48
  assert(emu.read(address+i-1,emu.memType.nesPpuDebug)==tile,'Actual Options text at '..(address+i-1))
 end
end
emu.addEventCallback(function()
 emu.setInput({down=frame==60 or frame==510,
  start=frame==80 or frame==320 or frame==530 or frame==710 or frame==750,
  a=frame==120 or(frame>=140 and frame<148)or frame==570,
  select=frame==180,b=frame==220 or frame==420 or frame==610,
  right=frame==360 or frame==380},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==100 then
  assert(r('CrossoverMenuState')==4 and r('CrossoverOptionsFocus')==0,'Title OPTIONS opens the separate page with shadows focused')
  assert(r('PlayerOutlinesOff')==1 and r('CrossoverBehaviorVersion')==0,'Real power-on defaults are shadows OFF and behavior1.0')
  assert(emu.read(0x2163,emu.memType.nesPpuDebug)==0x3f,'Options page has its own shadow-row arrow')
  for a=0x3f09,0x3f0b do assert(emu.read(a,emu.memType.nesPpuDebug)==0x28,'Options glyphs retain the bright gold palette')end
  for a=0x23c0,0x23ff do assert(emu.read(a,emu.memType.nesPpuDebug)==0xaa,'Dedicated Options attributes select gold')end
  text(0x2176,'OFF')
 end
 if frame==130 then assert(r('PlayerOutlinesOff')==0,'A enables shadows');text(0x2176,'ON')end
 if frame==160 then
  assert(r('PlayerOutlinesOff')==1 and r('CrossoverMenuState')==4,'Held A toggles once and keeps Options open')
  text(0x2176,'OFF')
 end
 if frame==200 then assert(r('PlayerOutlinesOff')==0,'Select enables shadows without launching gameplay')end
 if frame==300 then assert(r('CrossoverMenuState')==0 and r('PlayerOutlinesOff')==0,'B returns to title preserving the preference')end
 if frame==400 then
  assert(r('SelectedCharacter')==2 and r('CrossoverMenuState')==2 and r('PlayerOutlinesOff')==0,'Roster selects Samus after ordinary Options navigation')
  assert(count()==11,'Outlined Samus preview includes all six black-mask sprites: '..count())
  for x=0,31 do assert(emu.read(0x2340+x,emu.memType.nesPpuDebug)==0x24,'Character select has no shadow option row')end
  shot('on')
 end
 if frame==590 then assert(r('CrossoverMenuState')==4 and r('PlayerOutlinesOff')==1,'Reopened Options can disable shadows');text(0x2176,'OFF')end
 if frame==730 then
  assert(r('SelectedCharacter')==2 and r('CrossoverMenuState')==2 and r('PlayerOutlinesOff')==1,'Returning to the roster preserves Samus and shadows OFF')
  assert(count()==5,'Outline-free Samus preview retains her five colored body sprites: '..count())
  shot('off')
 end
 if frame==1200 then
  assert(r('GameEngineSubroutine')==8 and r('SelectedCharacter')==2 and r('PlayerOutlinesOff')==1,'Preference survives ordinary gameplay launch')
  assert(r('CrossoverBehaviorVersion')==0,'This UI test never seeds source2.02 mode')
  for i=0,5 do w('Enemy_Flag',0,i)end
  shot('gameplay-off')
  w('Player_Y_Position',250);w('Player_Y_HighPos',2)
 end
 if frame==1600 then
  assert(r('MmDeathFlag')==0 and r('GameEngineSubroutine')==8 and r('PlayerOutlinesOff')==1,'Seeded pit death and respawn retain the shadow preference')
  assert(r('CrossoverBehaviorVersion')==0,'Respawn preserves the selected1.0 behavior')
  print('PASS dedicated title Options: edge shadow toggles, gold text, both Samus previews, gameplay launch and seeded-death persistence');emu.stop(0)
 end
end,emu.eventType.endFrame)
