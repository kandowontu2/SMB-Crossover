-- Read-only actual-mapper observer around an existing authored audio fixture.
-- No new controller policy, RAM seed, register write or emulator setting.
local physicalA,nmiDepth,irqDepth=nil,0,0
local stage,left,right,transactions=0,0,0,0
local nmis,irqs,lagNmis=0,0,0
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
emu.addMemoryCallback(function(_,v)physicalA=v%128 end,emu.callbackType.write,0x5115)
emu.addMemoryCallback(function()
 nmiDepth=nmiDepth+1;nmis=nmis+1
 if r('NmiDisable')>=128 then lagNmis=lagNmis+1 end
end,emu.callbackType.exec,assert(L.NonMaskableInterrupt))
emu.addMemoryCallback(function()
 assert(stage==0,'A multiplier transaction finishes within its owning NMI')
 nmiDepth=nmiDepth-1;assert(nmiDepth>=0,'Balanced NMI observation')
end,emu.callbackType.exec,assert(L.NonMaskableInterrupt_RTI))
emu.addMemoryCallback(function()irqDepth=irqDepth+1;irqs=irqs+1 end,emu.callbackType.exec,assert(L.IrqScrollSplit))
emu.addMemoryCallback(function()irqDepth=irqDepth-1;assert(irqDepth>=0,'Balanced IRQ observation')end,emu.callbackType.exec,assert(L.IrqScrollSplit_RTI))
local function owned()
 local pc=emu.getState()['cpu.pc']
 assert(physicalA==11 and nmiDepth==1 and pc>=L._fraction255_mmc5 and pc<L._fraction255_mmc5+100,
  string.format('Multiplier access belongs to native audio: bank%s NMI%d IRQ%d PC%04x',tostring(physicalA),nmiDepth,irqDepth,pc))
end
emu.addMemoryCallback(function(a,v)
 owned()
 if a==0x5205 then
  assert(stage==0,'First factor begins a new transaction');left=v;stage=1
 else
  assert(stage==1,'Second factor follows the first');right=v;stage=2
 end
end,emu.callbackType.write,0x5205,0x5206)
emu.addMemoryCallback(function(a,v)
 owned()
 local product=left*right
 if a==0x5205 then
  assert(stage==2 and v==product%256,'Actual MMC5 low product matches both factors');stage=3
 else
  assert(stage==3 and v==product//256,'Actual MMC5 high product matches both factors')
  transactions=transactions+1;stage=0
 end
end,emu.callbackType.read,0x5205,0x5206)
local stop,finishing=emu.stop,false
emu.stop=function(code)
 if not finishing and code==0 then
  finishing=true
  assert(stage==0 and transactions>50,'A substantial set of complete hardware products was observed')
  assert(nmis>500 and irqs>100,'Actual NMI and scanline IRQ paths were exercised')
  local f=assert(io.open(OWNERSHIP_OUTPUT,'w'))
  f:write(string.format('{"result":"passed","transactions":%d,"nmis":%d,"irqs":%d,"lag_nmis":%d,"scope":"Read-only hardware-port ownership and products around authored audio fixture; no traversal claim"}\n',transactions,nmis,irqs,lagNmis));f:close()
  print('PASS MMC5 multiplier: '..transactions..' exact products, exclusive native-NMI ownership, '..nmis..' NMI and '..irqs..' IRQ entries ('..lagNmis..' lag NMI)')
 end
 stop(code)
end
dofile(OWNERSHIP_ROOT..'/tests/menu-bootstrap.lua')
TEST_DIR=OWNERSHIP_ROOT..'/tests/'
dofile(OWNERSHIP_ROOT..'/tests/guest-audio-flush-differential.lua')
