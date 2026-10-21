-- Read-only actual X-write receipts for two movement candidates in the same
-- genuine controller prefix. No game memory/register writes or state loads.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_samus_21_pipegap.lua'))
local log=assert(io.open(ROSTER_CONFIG.out..'movement-writes.csv','w'))
log:write('cycle,pc,bank,world,level,xOld,xNew,y,state,r0,r2,xSpeed,vy,headReceipt\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function q(n)local v=r(n)+256*r(n,1)+65536*r(n,2);return v>=0x800000 and v-0x1000000 or v end
local bank,sel=0,0
emu.addMemoryCallback(function(_,v)sel=v%8 end,emu.callbackType.write,0x8000)
emu.addMemoryCallback(function(_,v)if sel==7 then bank=v%128 end end,emu.callbackType.write,0x8001)
emu.addMemoryCallback(function(_,v)
 local wx=r('Player_X_Position')+256*r('Player_PageLoc')
 local le=r('LevelNumber')
 if r('WorldNumber')==0 and ((le==2 and wx>=2070 and wx<=2090)or(le==3 and wx>=1738 and wx<=1762))then
  local st=emu.getState()
  log:write(table.concat({st['cpu.cycleCount'],st['cpu.pc'],bank,r('WorldNumber'),le,wx,v+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),r('R0'),r('R2'),r('Player_X_Speed'),q('MmVY'),r('SmCeilingHit')},',')..'\n');log:flush()
 end
end,emu.callbackType.write,assert(L.Player_X_Position))
return base
