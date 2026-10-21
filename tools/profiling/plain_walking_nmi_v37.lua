-- Read-only observer extension. Authored arenas remain the frozen aligned
-- benchmark. Separate the preceding NMI cost from the next logic update.
local base=assert(io.open(TEST_DIR..'../../../../tools/profiling/plain_walking_aligned.lua','r'))
local source=base:read('*a');base:close()
local declaration="local function observed()return scene and completed>=8 and completed<68 end\n"
local start=assert(source:find(declaration,1,true),'Frozen aligned observer')
local injection=[==[
-- Audio switches hardware PRG directly without changing foreground CurrentBank.
-- Observe the mapper writes, including NMI switches and their restoration.
local physicalA,physicalSelect=nil,nil
if ROM_NAME:find('mmc5')then
 emu.addMemoryCallback(function(_,value)physicalA=value%128 end,emu.callbackType.write,0x5115)
else
 emu.addMemoryCallback(function(_,value)physicalSelect=value%8 end,emu.callbackType.write,0x8000)
 emu.addMemoryCallback(function(_,value)if physicalSelect==7 then physicalA=value%128 end end,emu.callbackType.write,0x8001)
end
local nmiStart,nmiPrevious,nmiPeriod,nmiCost,nmiLag
local irqOnly,irqStart=0,nil
local outerStart,outerIrq,outerPreviousNmi,outerPreviousCost,outerPreviousLag,outerPeriod
local outer=assert(io.open(prefix..'-deadline.csv','w'))
outer:write('scene,character,outlinesOff,mode,enemies,update,preCoreForegroundCycles,gameStartSinceNmi,previousNmiElapsed,previousNmiLag,previousNmiPeriod\n')
local audio=assert(io.open(prefix..'-audio.csv','w'))
audio:write('scene,character,outlinesOff,mode,enemies,routine,cycles,irqCycles,lagNmi\n')
emu.addMemoryCallback(function()
 local now=cycles()-7
 nmiPeriod=nmiPrevious and now-nmiPrevious or 0
 nmiPrevious=now;nmiStart=now;nmiLag=r('NmiDisable')>=128
end,emu.callbackType.exec,assert(L.NonMaskableInterrupt))
emu.addMemoryCallback(function()
 nmiCost=cycles()+6-assert(nmiStart)
end,emu.callbackType.exec,assert(L.NonMaskableInterrupt_RTI))
emu.addMemoryCallback(function()
 assert(not irqStart,'IRQ does not recursively nest')
 irqStart=cycles()-7
end,emu.callbackType.exec,assert(L.IrqScrollSplit))
emu.addMemoryCallback(function()
 irqOnly=irqOnly+cycles()+6-assert(irqStart)
 irqStart=nil
end,emu.callbackType.exec,assert(L.IrqScrollSplit_RTI))
emu.addMemoryCallback(function()
 if depth~=0 then return end
 outerStart=cycles();outerIrq=irqCycles
 outerPreviousNmi=nmiStart;outerPreviousCost=nmiCost
 outerPreviousLag=nmiLag;outerPeriod=nmiPeriod
end,emu.callbackType.exec,assert(L.GameLoop))
local dbg=assert(io.open(prefix..'.dbg','r'))
local debug=dbg:read('*a');dbg:close()
local audioReturns,audioActive={},{}
for _,name in ipairs({'AudioUpdate','SamusAudioUpdate','GuestAudioBegin','GuestAudioFinish','GuestAudioNativeFlush','GuestExpansionFlush','RemainingAudioBegin','RemainingAudioTick'})do
 local address,segment=debug:match('sym%s+[^\n]*name="'..name..'",[^\n]*val=(0x%x+),seg=(%d+)')
 if address then
  address=tonumber(address)
  assert(address==L[name],name..' has one linked address')
  local bank=nil
  if address>=0xa000 and address<0xc000 then
   local segmentStart,offset=debug:match('seg%s+id='..segment..',name="[^"]+",start=(0x%x+),[^\n]*ooffs=(%d+)')
   assert(tonumber(segmentStart)==0xa000,name..' A000 bank')
   bank=(tonumber(offset)-16)//8192
  else assert(address>=0xe000,name..' is fixed')end
  print('NMI routine '..name..' bank '..tostring(bank or 'fixed'))
  emu.addMemoryCallback(function()
   if depth<1 or not observed()or(bank and physicalA~=bank)then return end
   assert(not audioActive[name],name..' is not recursive')
   local sp=emu.getState()['cpu.sp']
   local ret=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
   audioActive[name]={clock=cycles(),irq=irqOnly,sp=(sp+2)%256,ret=ret,bank=bank,depth=depth,scene=index,outline=scene.outline,mode=scene.mode,count=scene.count,lag=nmiLag and 1 or 0}
   if not audioReturns[ret]then
    audioReturns[ret]=true
    emu.addMemoryCallback(function()
     local spNow=emu.getState()['cpu.sp']
     for n,a in pairs(audioActive)do
      if a.ret==ret and a.sp==spNow and a.depth==depth and(not a.bank or physicalA==a.bank)then
       audio:write(table.concat({a.scene,char,a.outline,a.mode,a.count,n,cycles()-a.clock,irqOnly-a.irq,a.lag},',')..'\n');audio:flush()
       audioActive[n]=nil
      end
     end
    end,emu.callbackType.exec,ret)
   end
  end,emu.callbackType.exec,address)
 end
end
]==]
source=source:sub(1,start+#declaration-1)..injection..source:sub(start+#declaration)
local anchor=" if not scene then return end\n local pc=L.NoDecTimers"
local replacement=[==[ if not scene then return end
 if observed()and outerStart then
  outer:write(table.concat({index,char,scene.outline,scene.mode,scene.count,completed-7,cycles()-outerStart-(irqCycles-outerIrq),outerStart-assert(outerPreviousNmi),assert(outerPreviousCost),outerPreviousLag and 1 or 0,assert(outerPeriod)},',')..'\n');outer:flush()
 end
 local pc=L.NoDecTimers]==]
local position=assert(source:find(anchor,1,true))
source=source:sub(1,position-1)..replacement..source:sub(position+#anchor)
assert(load(source,'@aligned-nmi-v37','t',_ENV))()
