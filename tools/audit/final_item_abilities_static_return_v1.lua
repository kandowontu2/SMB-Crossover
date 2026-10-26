-- Lua-only return slots preserve first-registration order without changing the
-- host callback vector during an EXEC callback. All native mechanics stay in
-- the immutable original ability module.
local pendingReturns,installedReturns,returnSlotsByPC={},{},{}
local returnDispatcherInstalled=false
FINAL_ITEM_ABILITIES_STATIC_INSTALL_RETURNS=function()
 assert(not returnDispatcherInstalled,'Ability return dispatcher installed exactly once')
 returnDispatcherInstalled=true
 emu.addMemoryCallback(function(pc)
  local slots=returnSlotsByPC[pc];if not slots then return end
  for i=1,#slots do slots[i]()end
 end,emu.callbackType.exec,0,0xffff)
end
local function onReturn(name,fn)
 local st=emu.getState();local sp=st['cpu.sp'];local ret=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local key=name..':'..ret;pendingReturns[key]={sp=(sp+2)%256,bank=bank(ret),fn=fn}
 if not installedReturns[key]then
  installedReturns[key]=true
  local slots=returnSlotsByPC[ret]
  if not slots then slots={};returnSlotsByPC[ret]=slots end
  slots[#slots+1]=function()
   local q=pendingReturns[key];if not q or emu.getState()['cpu.sp']~=q.sp or bank(ret)~=q.bank then return end
   pendingReturns[key]=nil;q.fn()
  end
 end
end
