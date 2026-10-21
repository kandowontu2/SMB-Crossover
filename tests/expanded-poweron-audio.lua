-- Read-only power-on regression. NMI decoder state must survive foreground
-- game/area clearing; this fixture never changes emulated memory/registers.
local character=assert(POWERON_CHARACTER)
local frame,depth,writes=0,0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()depth=depth-1 end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()
 if depth==0 or r('CurrentBankC')%128~=38 then return end
 local pointer=r('XgLzPosition')+256*r('XgLzPosition',1)
 assert(pointer>=L.XgLzHistory and pointer<L.XgLzHistory+2048,'Decoded music writes only to its history SRAM')
 writes=writes+1
end,emu.callbackType.exec,L.WriteHistory)
for _,name in ipairs({'XgAudioCharacter','XgAudioSong','XgAudioBank','XgAudioDelay','XgAudioEvent'})do
 emu.addMemoryCallback(function()
  if frame>=240 then assert(depth>0,'Foreground level clearing must preserve live '..name)end
 end,emu.callbackType.write,assert(L[name]))
end
emu.addMemoryCallback(function()
 if frame>=240 then assert(depth>0,'Foreground level clearing must preserve decoder-owned zero page')end
end,emu.callbackType.write,L.XgAudioPtr,L.XgLzSavedY)
emu.addEventCallback(function()
 local slot=character==12 and 8 or character
 emu.setInput({down=frame==80,right=frame>=100 and frame<100+20*(slot-6)and(frame-100)%20==0,start=frame==240},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==650 then
  assert(r('SelectedCharacter')==character,'Ordinary menu chooses the requested guest')
  assert(r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8,'Controller power-on reaches active native gameplay')
  assert(writes>100,'Compressed music decodes during initialization and gameplay')
  print('PASS character '..character..' read-only cold boot: bounded audio history, NMI-owned state survives foreground initialization');emu.stop(0)
 end
end,emu.eventType.endFrame)
