-- Explicit beam/power fixtures, with actual controller shooting and physical
-- APU stores. Native indirect SFX writes must not bypass the register mixer.
local frame=0
local rawWrites,indirect,shots=0,0,0
local modes={}
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addEventCallback(function()
 emu.setInput({right=frame==80 or frame==100,start=frame==200,b=frame==600 or frame==700 or frame==800},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame>=580 then
  local pc=emu.getState()['cpu.pc']
  if pc>=0xb200 and pc<0xc000 then rawWrites=rawWrites+1 end
 end
end,emu.callbackType.write,0x4000,0x400f)
emu.addMemoryCallback(function()
 if frame>=580 then indirect=indirect+1 end
end,emu.callbackType.exec,L.GuestMetroidStoreIndirectY)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame==590 or frame==690 or frame==790 then
  local power=math.floor((frame-590)/100)
  w('PlayerStatus',power)
  for i=0,2 do w('SmShotType',0,i) end
 end
 if frame==603 or frame==703 or frame==803 then
  local power=math.floor((frame-603)/100)
  local expected=({0x4d,0x49,0x5d})[power+1]
  local bank=15
  for reg=0,3 do
   local original=emu.read(bank*0x2000+0x1200+expected+reg,emu.memType.nesPrgRom)
   local value=r('GuestNativeApu',reg)
   -- Wave beam alternates its native $58/$6f timer low immediately.
   assert(value==original or (power==2 and reg==2 and value==0x58),'Beam '..power..' retains its original envelope/sweep/timer register '..reg..': '..value..'/'..original)
  end
  assert(r('SmAudioRam',0x8d)==1,'Brinstar music remains active during beam SFX')
  modes[power]=true;shots=shots+1
 end
 if frame==850 then
  assert(rawWrites==0,'Metroid indirect SFX must never write the hardware behind the mixer: '..rawWrites)
  assert(indirect>=12 and shots==3,'Short, long and wave beam register loads exercised')
  assert(r('SmAudioRam',0x8d)==1,'Music continues after all beam sounds finish')
  print('PASS Samus short/long/wave beam native envelopes, sweeps and timers stay buffered; no direct SFX/mixer conflict; music continues')
  emu.stop(0)
 end
end,emu.eventType.endFrame)
