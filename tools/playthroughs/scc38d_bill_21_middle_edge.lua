-- Launch only after clearing the overhead block bank. Read-only palette receipts.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/scc38d_bill_21_elevated.lua'))
local start=nil
local log=assert(io.open(ROSTER_CONFIG.out..'palette-changes.csv','w'));log:write('frame,world,level,x,y,engine,palette,mask\n')
local frame,last=0,nil
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
emu.addEventCallback(function()
 frame=frame+1
 if frame>540 and r('WorldNumber')==1 and r('LevelNumber')==0 then
  local bytes={};for i=0,31 do bytes[#bytes+1]=string.format('%02x',emu.read(0x3f00+i,emu.memType.nesPpuDebug))end
  local now=table.concat(bytes)
  if now~=last then log:write(table.concat({frame,r('WorldNumber'),r('LevelNumber'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('GameEngineSubroutine'),now,r('Mirror_PPUMASK')},',')..'\n');log:flush();last=now end
 end
end,emu.eventType.endFrame)
return function(c)
 if c.char==3 and c.world==1 and c.level==0 and c.x>=1260 and c.x<1420 then
  if start==nil and c.grounded and c.x>=1320 and(c.r('PreviousA_B_Buttons')&128)==0 then start=c.poll end
  return {right=true,b=c.poll%8<3,a=start~=nil and c.poll-start<32}
 end
 return base(c)
end
