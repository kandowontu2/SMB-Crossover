-- Real controller-only Options/Cheats navigation, including every level value.
-- No RAM/ROM/register writes or menu bootstrap.
local frame=0
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function level()return r('CheatStartLevel')&31 end
local function text(at,s)
 for i=1,#s do
  local c=s:byte(i)
  local tile=c==32 and 0x24 or c==45 and 0x28 or c>=65 and c<=90 and c-65+0x0a or c-48
  assert(emu.read(at+i-1,emu.memType.nesPpuDebug)==tile,'Cheats visible text '..s..' at '..(at+i-1))
 end
end
local function shot(tag)
 local f=assert(io.open(OUTPUT..ROM_NAME..'-cheats-'..tag..'.png','wb'));f:write(emu.takeScreenshot());f:close()
end
emu.addEventCallback(function()
 local b={down=frame==60 or frame==120 or frame==140 or frame==260,
  start=frame==80 or frame==620 or frame==700,
  a=frame==160 or frame==200 or(frame>=220 and frame<226)or frame==240,
  left=frame==280,right=frame==300 or frame==320 or frame==640 or frame==660,
  b=frame==520 or frame==560}
 if frame>=360 and frame<=484 and(frame-360)%4==0 then b.right=true end
 emu.setInput(b,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==100 then
  assert(r('CrossoverMenuState')==4 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'Power-on cheats defaults are OFF and1-1')
  text(0x2265,'CHEATS');shot('options')
 end
 if frame==180 then
  assert(r('CrossoverMenuState')==6 and r('CrossoverOptionsFocus')==0,'Options opens the separate Cheats submenu')
  text(0x20cb,'CHEATS ');text(0x2176,'OFF');text(0x2216,'1-1')
  for i=0,23 do assert(emu.read(0x2263+i,emu.memType.nesPpuDebug)==0x24,'Parent Cheats row is absent in submenu')end
 end
 if frame==210 then assert(r('CheatInvincible')==1,'A enables invincibility');text(0x2176,'ON')end
 if frame==235 then assert(r('CheatInvincible')==0,'Held A toggles only once');text(0x2176,'OFF')end
 if frame==250 then assert(r('CheatInvincible')==1,'Invincibility can be enabled again')end
 if frame==290 then assert(level()==31,'Left wraps1-1 to8-4');text(0x2216,'8-4');shot('submenu')end
 if frame==310 then assert(level()==0,'Right wraps8-4 to1-1');text(0x2216,'1-1')end
 if frame>=362 and frame<=486 and(frame-362)%4==0 then
  local value=(2+(frame-362)//4)%32
  assert(level()==value and r('CheatStartLevel')&32~=0,'Each of32 controller level steps updates the stored selection')
  text(0x2216,tostring(value//4+1)..'-'..tostring(value%4+1))
 end
 if frame==540 then
  assert(r('CrossoverMenuState')==4,'B returns to Options')
  text(0x20cb,'OPTIONS');text(0x2265,'CHEATS')
  assert(r('PlayerOutlinesOff')==1 and r('CrossoverBehaviorVersion')==0,'Cheats navigation preserves outlines and Easy/Hard')
 end
 if frame==690 then assert(r('CrossoverMenuState')==2 and r('SelectedCharacter')==2,'Ordinary character select still selects Samus')end
 if frame==1400 then
  assert(r('OperMode')==1 and r('WorldNumber')==0 and r('LevelNumber')==1,'Selected1-2 launches through real character confirmation')
  assert(r('CheatInvincible')==1 and level()==1,'Cheats survive loading and area initialization')
  assert(r('AreaNumber')==2 and r('AreaType')==2 and r('GameEngineSubroutine')==8,'Native pipe intro reaches the selected underground area')
  shot('selected-level')
  print('PASS real Cheats UI: defaults, all32 values and wrap, edge toggles, parent/back navigation, unchanged options, Samus1-2 launch and native pipe intro')
  emu.stop(0)
 end
 if r('OperMode')==0 and(r('CrossoverMenuState')==4 or r('CrossoverMenuState')==6)then
  assert(r('VRAM_Buffer1_Offset')<=84,'Menu publication fits the native primary queue, frame '..frame..' offset '..r('VRAM_Buffer1_Offset'))
 end
end,emu.eventType.endFrame)
