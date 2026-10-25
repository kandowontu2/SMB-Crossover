dofile(TEST_DIR..'../../tests/menu-bootstrap.lua')
local frame,depth=0,0
local f=assert(io.open(OUTPUT..ROM_NAME..'-projectile-overload-observer.csv','w'))
f:write('frame,depth,pc,bank,bankC,opcode,expected,playerStart,rotation,used\n')
local function r(n)return emu.read(assert(L[n]),emu.memType.nesDebug)end
for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,assert(pc))end
for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()depth=depth-1 end,emu.callbackType.exec,assert(pc))end
emu.addMemoryCallback(function()
 if frame<590 or frame>680 or r('CurrentBank')%128~=4 then return end
 local st=emu.getState();local actual,expected={},{}
 for i=0,7 do actual[#actual+1]=string.format('%02x',emu.read(L.RosterOamReady+i,emu.memType.nesDebug));expected[#expected+1]=string.format('%02x',emu.read(4*8192+(L.RosterOamReady+i)%8192,emu.memType.nesPrgRom))end
 f:write(table.concat({frame,depth,st['cpu.pc'],r('CurrentBank'),r('CurrentBankC'),table.concat(actual),table.concat(expected),r('RgOamPlayerStart'),r('RgOamRotation'),r('RgOamUsed')},',')..'\n');f:flush()
end,emu.callbackType.exec,L.RosterOamReady)
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
dofile(TEST_DIR..'../../tests/megaman-projectiles-overload.lua')
