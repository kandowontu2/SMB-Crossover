local invSP,invFrame,minimumSP=255,0,255
emu.addMemoryCallback(function()
 local p=emu.convertAddress(L.InventorySupported)
 if not p or p.address//8192~=B.InventorySupported then return end
 local s=emu.getState();invSP=s['cpu.sp'];invFrame=s['ppu.frameCount'];minimumSP=math.min(minimumSP,invSP)
end,emu.callbackType.exec,L.InventorySupported)
-- $017c is the immutable PLA of the assembled MMC3 bank-return tail.
-- Ordinary farcall self-modification only touches its immediate/JSR operands.
emu.addMemoryCallback(function(address,value)
 local s=emu.getState();if s['ppu.frameCount']<700 or value==0x68 then return end
 local p=emu.convertAddress(s['cpu.pc']);local bank=p and p.address//8192 or -1
 local f=assert(io.open(ROSTER_CONFIG.out..'debug-stop.json','w'))
 f:write(string.format('{"observed":true,"reason":"immutable_farcall_return_opcode_overwritten","frame":%d,"address":%d,"oldExpected":104,"newValue":%d,"pc":%d,"bank":%d,"sp":%d,"latestInventoryEntrySP":%d,"latestInventoryEntryFrame":%d,"minInventoryEntrySP":%d,"game_state_writes":false,"campaign_pass":false}',s['ppu.frameCount'],address,value,s['cpu.pc'],bank,s['cpu.sp'],invSP,invFrame,minimumSP));f:close()
 print('OBSERVED first immutable bank-return PLA overwrite; native stack witness retained')
 emu.stop(0)
end,emu.callbackType.write,0x17c)
