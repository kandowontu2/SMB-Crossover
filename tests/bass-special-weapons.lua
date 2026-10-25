-- Explicit inventory/world fixtures, real NES controller attacks. Source
-- constants below are independently transcribed from the pinned 2.02 AS.
local frame=0
local phase=0
local age=0
local started=false
local cases=BASS_SPECIAL_PROFILE and {7} or {2,3,4,5,6,7,1}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
local function count(t)local n=0;for i=0,9 do if r('RgShotType',i)==t then n=n+1 end end;return n end
local function slot(t)for i=0,9 do if r('RgShotType',i)==t then return i end end end
local nmiBanks,nmiStack,nmiChecks={},{},0
local mainGraphicsBanks,forcedBanks={},{}
local coverageQueue,coverageIndex,requestedBank=nil,1,nil
local mmc5=ROM_NAME:find('mmc5')~=nil
local function windowBytes()
 local bytes={}
 for i=0,8191 do bytes[i+1]=emu.read(0xc000+i,emu.memType.nesDebug)end
 return bytes
end
-- Explicit isolated interrupt fixture. The ordinary ability checks above use
-- real controller attacks. Afterwards, map each main-thread observed graphics
-- bank only in the completed GameLoop's idle interval and let a real NMI run.
-- This does not depend on a slower renderer accidentally crossing VBlank.
emu.addMemoryCallback(function(_,value)
 if frame>=550 and #nmiStack==0 and not coverageQueue then mainGraphicsBanks[value]=true end
end,emu.callbackType.write,L.CurrentBankC)
emu.addMemoryCallback(function(_,value)
 if value~=0 or not coverageQueue or requestedBank or coverageIndex>#coverageQueue or #nmiStack~=0 then return end
 requestedBank=coverageQueue[coverageIndex]
 w('CurrentBankC',requestedBank)
 if mmc5 then
  emu.write(0x5116,requestedBank,emu.memType.nesMemory)
 else
  w('BankShadow',0x46)
  emu.write(0x8000,0x46,emu.memType.nesMemory)
  emu.write(0x8001,requestedBank,emu.memType.nesMemory)
 end
end,emu.callbackType.write,L.NmiDisable)
emu.addMemoryCallback(function()
 local bank=r('CurrentBankC')
 nmiStack[#nmiStack+1]={bank=bank,bytes=requestedBank==bank and windowBytes()or nil}
end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()
 local incoming=table.remove(nmiStack)
 if frame>=550 then
  assert(incoming.bank==r('CurrentBankC'),'NMI restores the interrupted graphics-data bank: incoming '..tostring(incoming.bank)..', outgoing '..r('CurrentBankC'))
  if incoming.bytes then
   for i=0,8191 do assert(emu.read(0xc000+i,emu.memType.nesDebug)==incoming.bytes[i+1],'NMI restores the actual complete mapped C window: bank '..incoming.bank..' byte '..i)end
   forcedBanks[incoming.bank]=true;requestedBank=nil;coverageIndex=coverageIndex+1
  end
  nmiBanks[incoming.bank]=true;nmiChecks=nmiChecks+1
 end
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
if ROM_NAME:find('mmc5')then
 emu.addMemoryCallback(function(address,value)
  if frame>=550 then assert(value&128~=0,'Guest sprite-data bank switches must select ROM, never MMC5 RAM')end
 end,emu.callbackType.write,0x5116)
end
if BASS_SPECIAL_PROFILE then
 local begin,drawbegin
 emu.addMemoryCallback(function()if frame>560 and r('CurrentBank')%128==60 then begin=emu.getState()['cpu.cycleCount']end end,emu.callbackType.exec,L.SpecialWeapons)
 emu.addMemoryCallback(function()if begin and age%10==0 then print('PROFILE physics '..age..' '..(emu.getState()['cpu.cycleCount']-begin));begin=nil end end,emu.callbackType.exec,L.SpecialWeaponsFinish)
 emu.addMemoryCallback(function()if frame>560 and r('CurrentBank')%128==60 then drawbegin=emu.getState()['cpu.cycleCount']end end,emu.callbackType.exec,L.SpecialDrawShots)
 emu.addMemoryCallback(function()if drawbegin and age%10==0 then print('PROFILE draw '..age..' '..(emu.getState()['cpu.cycleCount']-drawbegin));drawbegin=nil end end,emu.callbackType.exec,L.SpecialDrawFinish)
end
local function setup(id)
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmSolidTerrain',0,i)end
 for page=0,1 do for col=0,15 do w('Block_Buffer_1',0x54,page*208+176+col)end end
 for i=0,9 do w('RgShotType',0,i);w('SsMode',0,i)end
 for i=0,3 do w('MmBulletType',0,i)end
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 w('PlayerStatus',1);w('InvOwnedLo',255,9);w('InvOwnedHi',1,9);w('InvSelected',id,9)
 for i=1,7 do w('InvAmmo',112,9*16+i)end
 w('InvDirty',1);w('SsHeld',0);w('SsFreeze',0);w('SsBodyStop',0);w('SsKick',0);w('SsWaterExpand',0)
 w('XgDash',0);w('MmSliding',0);w('RgShootPose',0);w('RgCooldown',0)
 w('Player_X_Position',32);w('Player_PageLoc',0);w('Player_Y_Position',176);w('Player_Y_HighPos',1);w('Player_State',0)
 w('PlayerFacingDir',1);w('Player_X_Speed',0);w('Player_Y_Speed',0)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',255);w('ScreenRight_PageLoc',0)
 if id==1 then w('Block_Buffer_1',0x51,10*16+3)end
end
emu.addEventCallback(function()
 local id=cases[phase]
 emu.setInput({down=frame==80 or (started and id==5 and age==10),
  right=(frame==100 or frame==120 or frame==140) or (started and id==2 and age==10),
  up=started and id==2 and age==10,
  start=frame==200,a=started and id==5 and age==10,
  b=started and ((id==4 and age>=10 and age<80) or (id~=4 and id~=5 and age>=10 and age<15)
    or (id==7 and age>=165 and age<171) or (id==1 and age>=30 and age<35))},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 if not started then
  phase=phase+1
  if not cases[phase]then
   if not coverageQueue then
    coverageQueue={}
    for bank in pairs(mainGraphicsBanks)do coverageQueue[#coverageQueue+1]=bank end
    table.sort(coverageQueue)
    assert(#coverageQueue>=2,'Real weapon and body drawing observed both graphics-data banks')
   end
   if coverageIndex<=#coverageQueue or requestedBank then return end
   for _,bank in ipairs(coverageQueue)do assert(forcedBanks[bank],'Explicit real NMI exercised observed graphics bank '..bank)end
   print('PASS deterministic real-NMI physical C-window restoration: '..#coverageQueue..' observed graphics banks, 8192bytes each')
   local banks,bankValues=0,{};for bank in pairs(nmiBanks)do banks=banks+1;bankValues[#bankValues+1]=bank end
   table.sort(bankValues)
   print('PROFILE Bass weapon NMI coverage checks='..nmiChecks..' banks='..banks..' values='..table.concat(bankValues,','))
   assert(nmiChecks>=800 and banks>=2,'Weapon drawing exercises real interrupts in both graphics-data banks')
   print('PASS Bass source weapon pools, energy, directional blade, knuckle startup, Pharaoh charge, kick, flame, shield and Super Arm')
   print('PASS '..nmiChecks..' native NMIs restore interrupted graphics-data banks, including weapon art')
   emu.stop(0);return
  end
  setup(cases[phase]);started=true;age=0
 end
 age=age+1
 if BASS_SPECIAL_PROFILE and age==100 then emu.stop(0);return end
 for i=0,5 do w('Enemy_Flag',0,i)end
 local id=cases[phase]
 if age==14 then
  if id==2 then
   local s=assert(slot(10),'Metal Blade fires from B')
   assert(r('RgShotVXHi',s)==2 and r('RgShotVXLo',s)==0xd0,'Metal diagonal horizontal speed is 450/120*.75')
   assert(r('RgShotVYHi',s)==0xfd and r('RgShotVYLo',s)==0x30,'Metal diagonal vertical speed is -2.8125')
   assert(r('InvAmmo',146)==108,'Metal costs four units')
  elseif id==3 then
   local s=assert(slot(11),'Hard Knuckle spawns')
   assert(r('RgShotVXHi',s)==0 and r('RgShotVXLo',s)==0,'Knuckle stays still for its five 32 ms startup frames')
   assert(r('InvAmmo',147)==104,'Knuckle costs eight units')
  elseif id==4 then assert(count(12)==1 and count(18)==1,'Pharaoh fires a small shot and delayed head balloon')
  elseif id==5 then assert(count(19)==1 and r('InvAmmo',149)==108,'Down+A activates one four-unit Charge Kick')
  elseif id==6 then
   local s=assert(slot(15),'Flame Blast launches its falling bullet')
   assert(r('RgShotVYLo',s)>0,'Flame Blast uses 1300 Flash px/s2 gravity')
  elseif id==7 then assert(count(17)==8 and r('InvAmmo',151)==96,'One sixteen-unit Water Shield creates eight balls')
  elseif id==1 then
   assert(r('SsHeld')>0 and count(9)==1,'Super Arm lifts a contacted empty brick')
   assert(r('Block_Buffer_1',10*16+3)==0,'Lifting removes only the contacted masonry cell')
   assert(r('InvAmmo',145)==112,'Super Arm lift is free; eight units are paid at throw')
  end
 end
 if id==3 and age==35 then
  local s=assert(slot(11),'Knuckle remains live after startup')
  assert(r('RgShotVXHi',s)>=1,'Knuckle accelerates after startup')
 end
 if id==4 and age==84 then
  assert(count(18)==0 and count(14)==1,'Full charged Pharaoh shot launches when B is released')
  assert(r('InvAmmo',148)==100,'Pharaoh small plus charged shot costs twelve units')
 end
 if id==6 and age==45 then assert(count(16)==1,'Flame bullet becomes a stationary flame on ground contact')end
 if id==7 and age==160 then
  for i=0,9 do if r('RgShotType',i)==17 then assert(r('SsHidden',i)==0,'Every shield ball appears before expansion: slot '..i..' age '..r('RgShotAge',i)..' angle '..r('SsAngleHi',i))end end
 end
 if id==7 and age==175 then
  assert(r('SsWaterExpand')==1 and r('SsWaterRadius')>22,'Second press expands the completed shield: '..r('SsWaterExpand')..','..r('SsWaterRadius')..', energy '..r('InvAmmo',151))
  assert(r('InvAmmo',151)==96,'Expanding an existing shield costs no additional energy')
 end
 if id==1 and age==34 then assert(r('SsHeld')==0 and count(9)==1 and r('InvAmmo',145)==104,'Second B throws the held brick and pays eight units')end
 if age==18 or (id==4 and age==84)or(id==7 and age==175)then
  local f=assert(io.open(OUTPUT..ROM_NAME..'-bass-special-'..id..'-'..age..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
 if age==(id==7 and 210 or 155) then started=false end
end,emu.eventType.endFrame)
