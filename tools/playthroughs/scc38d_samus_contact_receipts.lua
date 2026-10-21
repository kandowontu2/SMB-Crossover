-- Additional read-only receipt for the actual right-wall write. This wrapper
-- supplies the same controller policy and is also safe with a fixed replay.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_late_floor_landings.lua'))
local log=assert(io.open(ROSTER_CONFIG.out..'contact-writes.csv','w'))
log:write('cycle,pc,opcode,bank,xOld,xNew,y,state,side,row,r4,ptr,tile,probeWorldX,sourceJumped,headReceipt\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local bank,sel=0,0
emu.addMemoryCallback(function(_,v)sel=v%8 end,emu.callbackType.write,0x8000)
emu.addMemoryCallback(function(_,v)if sel==7 then bank=v%128 end end,emu.callbackType.write,0x8001)
emu.addMemoryCallback(function(_,v)
 local wx=r('Player_X_Position')+256*r('Player_PageLoc')
 if r('WorldNumber')~=0 or r('LevelNumber')~=3 or wx<1738 or wx>1762 then return end
 local st=emu.getState();local pc=st['cpu.pc']
 if bank~=10 or pc~=L.SamusStopAtWallBanked+40 then return end
 local ptr=r('R6')+256*r('R7')
 log:write(table.concat({st['cpu.cycleCount'],pc,emu.read(pc,emu.memType.nesDebug),bank,wx,v+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),r('R0'),r('R2'),r('R4'),ptr,emu.read((ptr+r('R2'))%65536,emu.memType.nesDebug),r('SmTempX')+256*r('SmTempPage'),r('SmSourceJumped'),r('SmCeilingHit')},',')..'\n');log:flush()
end,emu.callbackType.write,assert(L.Player_X_Position))
return base
