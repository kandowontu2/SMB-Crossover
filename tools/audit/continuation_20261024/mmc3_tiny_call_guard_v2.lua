-- Complete tiny code, resident code and hardware stack ownership. Everything
-- above015a in page1 is ordinary stack space after boot; record write addresses
-- directly rather than building a full emulator state on every hardware push.
local C=assert(TINY_CALL_GUARD)
local ready=false;local writes,calls,stackWrites=0,0,0;local minSP=255
local function r(a)return emu.read(a,emu.memType.nesDebug)end
emu.addEventCallback(function()
 if emu.getState()['ppu.frameCount']<180 then return end
 ready=true
 for i,v in ipairs(C.bytes)do
  local a=C.start+i-1
  if not C.mutable[tostring(a)]then assert(r(a)==v,'Actual tiny immutable opcode intact '..a)end
 end
 for i,v in ipairs(C.common.bytes)do
  assert(r(C.common.address+i-1)==v,'Actual resident bank dispatcher intact')
 end
end,emu.eventType.endFrame)
emu.addMemoryCallback(function(a,v)
 if not ready then return end
 writes=writes+1
 assert(C.mutable[tostring(a)],'Immutable tiny code overwritten at '..a)
end,emu.callbackType.write,C.start,C.start+#C.bytes-1)
emu.addMemoryCallback(function(a)
 if not ready then return end
 stackWrites=stackWrites+1;minSP=math.min(minSP,a-0x101)
 assert(a>0x100+C.stack_floor,'Native stack reaches tiny-code boundary: '..a)
end,emu.callbackType.write,0x100+C.stack_floor,0x1ff)
emu.addMemoryCallback(function()
 if not ready then return end
 local p=emu.convertAddress(C.common.address)
 assert(p and p.address//8192==C.common.physical_bank,'Common call executes from resident ROM')
 calls=calls+1
end,emu.callbackType.exec,C.common.address)
local stop=emu.stop;emu.stop=function(code)
 local f=assert(io.open(ROSTER_CONFIG.out..'full-smc-guard.json','w'))
 f:write(string.format('{"passed":%s,"protected_code_bytes":%d,"observed_declared_operand_writes":%d,"resident_call_entries":%d,"native_stack_writes":%d,"minimum_SP_from_stack_write_addresses":%d,"stack_floor":%d,"observer_game_state_writes":false}',tostring(code==0 and ready and calls>100 and stackWrites>100),#C.bytes,writes,calls,stackWrites,minSP,C.stack_floor));f:close();stop(code)
end
