-- Check the hardware register selector across real regular and lag NMIs.
local frame=0
local actual,saved=0,0
local checked,lag,pending=0,0,0
local function r(n) return emu.read(assert(L[n],n),emu.memType.nesDebug) end
emu.addMemoryCallback(function(a,v) actual=v end,emu.callbackType.write,0x8000)
emu.addMemoryCallback(function()
 saved=actual
 -- The shadow is stored immediately before STA $8000. If NMI lands between
 -- that pair, restoring the new shadow is also safe: the interrupted next
 -- instruction writes that same selector before any main-thread bank data.
 if frame>=550 and actual~=r('BankShadow') then
  local sp=emu.getState()['cpu.sp']
  local pc=emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+3)%256,emu.memType.nesDebug)
  assert(emu.read(pc,emu.memType.nesDebug)==0x8d and emu.read(pc+1,emu.memType.nesDebug)==0 and emu.read(pc+2,emu.memType.nesDebug)==0x80,
   'A pending shadow must be followed immediately by STA $8000, return PC '..string.format('%04x',pc))
  saved=r('BankShadow');pending=pending+1
 end
 if frame>=550 and r('NmiDisable')>=128 then lag=lag+1 end
end,emu.callbackType.exec,L.NonMaskableInterrupt)
for _,a in ipairs({L.ContinueNMI-1,L.InitializeMemory-1}) do
 if emu.read(a,emu.memType.nesDebug)==0x40 then
  emu.addMemoryCallback(function()
   if frame>=550 then
    assert(actual==saved,'NMI changed the interrupted MMC3 bank selector: '..saved..' -> '..actual)
    checked=checked+1
   end
  end,emu.callbackType.exec,a)
 end
end
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100 or frame==120 or (frame>=550 and frame<760),start=frame==200,
 b=frame>=550 and frame%12<6,a=frame>=600 and frame%100<35},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==540 then emu.write(L.PlayerStatus,2,emu.memType.nesDebug);emu.write(L.StarInvincibleTimer,255,emu.memType.nesDebug) end
 if frame==1000 then
  assert(checked>400 and lag>5,'Both NMI paths were exercised: '..checked..', '..lag)
  assert(r('SelectedCharacter')==3 and r('OperMode')==1,'Bill continues running after interrupted banking')
  print('PASS MMC3 selector preserved across '..checked..' interrupts, including '..lag..' lag NMIs and '..pending..' pending selector stores');emu.stop(0)
 end
end,emu.eventType.endFrame)
