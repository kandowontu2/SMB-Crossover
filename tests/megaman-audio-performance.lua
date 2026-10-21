-- Native MM music/SFX NMI cost with a full Water Shield fixture. Exclude nested
-- mapper IRQs; retain all native driver work and APU buffering.
local frame=0
local start,irqStart,irqCycles,irqAt=0,0,0,0
local samples={}
local function cycles()return emu.getState()['cpu.cycleCount']end
emu.addMemoryCallback(function()start=cycles();irqAt=irqCycles end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()irqStart=cycles()end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()irqCycles=irqCycles+cycles()-irqStart+6 end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
emu.addMemoryCallback(function()
 if frame>=800 and frame<900 then samples[#samples+1]=cycles()-start-(irqCycles-irqAt)+6 end
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addEventCallback(function()
 frame=frame+1
 if frame==1000 then
  local total,maximum=0,0;for _,v in ipairs(samples)do total=total+v;maximum=math.max(maximum,v)end
  assert(#samples==100,'Every hardware-frame NMI sampled')
  print('PASS PROFILE native MegaMan/Bass NMI '..math.floor(total/#samples)..' average / '..maximum..' maximum CPU cycles; '..#samples..' samples')
 end
end,emu.eventType.endFrame)
WATER_CHARACTER=9
dofile(TEST_DIR..'water-shield-performance.lua')
