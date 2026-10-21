-- Explicit pending-column fixture during the native screen loader. A lagged
-- producer must wait for NMI to consume the previous full column set.
local frame=0
local injected,consumed,rendered=false,false,false
local inNmi=false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame==100 or frame==120 or frame==140,start=frame==240},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if inNmi or injected or frame<250 or r('SelectedCharacter')~=9 or r('OperMode_Task')~=1 or r('ScreenRoutineTask')~=8 then return end
 w('VRAM_Buffer_AddrCtrl',6);w('VRAM_Buffer2_Offset',144);w('VRAM_Buffer2',0)
 injected=true
end,emu.callbackType.exec,L.AreaParserTaskControl)
emu.addMemoryCallback(function()
 if inNmi or not injected then return end
 if not consumed then
  assert(r('VRAM_Buffer2_Offset')==0,'Screen loader must wait for queued VRAM columns before producing another set')
  consumed=true
 end
 rendered=true
end,emu.callbackType.exec,L.AreaParserTaskLoop)
emu.addMemoryCallback(function()inNmi=true end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()inNmi=false end,emu.callbackType.exec,assert(L.NonMaskableInterrupt_RTI))
emu.addEventCallback(function()
 frame=frame+1
 if frame==650 then
  assert(injected and consumed and rendered,'Pending queue, NMI consumption and resumed loader were all exercised')
  assert(r('OperMode_Task')==3 and r('GameEngineSubroutine')==8,'Screen loader reaches playable gameplay')
  print('PASS screen loader waits for NMI consumption of a pending VRAM column set');emu.stop(0)
 end
end,emu.eventType.endFrame)
