-- STATIC_CV3_RETURN_CORE_START
-- Lua-only registration retains the old first-install order at each PC.
-- No real memory callback is added or removed after the complete script loads.
local pendingReturns,installedReturns,returnSlotsByPC={},{},{}
local function queueReturnSlot(pc,fn)
 local slots=returnSlotsByPC[pc]
 if not slots then slots={};returnSlotsByPC[pc]=slots end
 slots[#slots+1]=fn
end
local staticReturnsInstalled=false
local function installStaticReturns()
 assert(not staticReturnsInstalled,'CV3 static return dispatcher installed once')
 staticReturnsInstalled=true
 -- Must be called last, after every original fixed hook/controller callback.
 emu.addMemoryCallback(function(pc)
  local slots=returnSlotsByPC[pc];if not slots then return end
  local count=#slots
  for i=1,count do slots[i]()end
 end,emu.callbackType.exec,0,0xffff)
end
local function onReturn(name,fn)
 local st=emu.getState();local sp=st['cpu.sp']
 local ret=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local key=name..':'..ret
 pendingReturns[key]={sp=(sp+2)%256,bank=bank(ret),fn=fn}
 if not installedReturns[key]then
  installedReturns[key]=true
  queueReturnSlot(ret,function()
   local v=pendingReturns[key]
   if v and emu.getState()['cpu.sp']==v.sp and alias(ret,bank(ret),v.bank)then pendingReturns[key]=nil;v.fn()end
  end)
 end
end
-- STATIC_CV3_RETURN_CORE_END
