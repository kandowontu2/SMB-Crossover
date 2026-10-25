-- Read-only protection of the complete actual bank-switch code, including
-- the return tail that an older33-byte observer did not cover.
local C=assert(FULL_SMC_GUARD);local ready=false;local writes=0
local function read(a)return emu.read(a,emu.memType.nesDebug)end
emu.addEventCallback(function()
 if emu.getState()['ppu.frameCount']>=180 then
  ready=true
  for i,v in ipairs(C.bytes)do local a=C.start+i-1;if not C.mutable[tostring(a)]then assert(read(a)==v,'Entire native farcall opcode remains intact '..a)end end
 end
end,emu.eventType.endFrame)
emu.addMemoryCallback(function(a,v)
 if not ready then return end
 writes=writes+1
 assert(C.mutable[tostring(a)],'Immutable native farcall byte overwritten at '..a..' PC '..emu.getState()['cpu.pc']..' SP '..emu.getState()['cpu.sp'])
end,emu.callbackType.write,C.start,C.start+#C.bytes-1)
local stop=emu.stop;emu.stop=function(code)
 local f=assert(io.open(ROSTER_CONFIG.out..'full-smc-guard.json','w'));f:write(string.format('{"passed":%s,"protected_code_bytes":%d,"observed_declared_operand_writes":%d,"observer_game_state_writes":false}',tostring(code==0 and ready),#C.bytes,writes));f:close();stop(code)
end
