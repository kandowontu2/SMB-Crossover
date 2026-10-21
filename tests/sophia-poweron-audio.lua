-- Read-only cold boot regression. Every button is an ordinary controller input.
-- Selecting Sophia and starting a game must not let the LZ history write into
-- low memory while SMB clears RAM for the new area.
local frame=0
local writes=0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 if r('CurrentBankC')%128~=38 then return end
 local ptr=r('XgLzPosition')+256*r('XgLzPosition',1)
 assert(ptr>=L.XgLzHistory and ptr<L.XgLzHistory+2048,'Expanded audio history pointer stays in its own SRAM ring, frame '..frame..' ptr='..ptr)
 writes=writes+1
end,emu.callbackType.exec,assert(L.WriteHistory))
emu.addMemoryCallback(function(_,value)
 if frame>240 and r('OperMode')==1 then assert(value<=12,'Native gameplay dispatch remains valid during audio start: '..value..' at '..frame)end
end,emu.callbackType.write,L.GameEngineSubroutine)
emu.addEventCallback(function()
 emu.setInput({start=frame==240,down=frame==80,right=frame>=100 and frame<200 and(frame-100)%20==0},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==650 then
  assert(r('SelectedCharacter')==11,'Real menu selects Sophia')
  assert(r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8,'Real controller boot reaches active gameplay')
  assert(writes>100,'Native compressed music decoded during boot and gameplay')
  print('PASS read-only Sophia cold boot: native gameplay and bounded compressed-audio history');emu.stop(0)
 end
end,emu.eventType.endFrame)
