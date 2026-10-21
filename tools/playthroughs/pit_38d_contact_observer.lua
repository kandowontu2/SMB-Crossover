-- Read-only contact receipt on the exact38d controller candidate.
-- Captures bounded native writes; no state loads or emulated writes.
local cfg=assert(ROSTER_CONFIG)
local root=assert(cfg.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/pit_38d_policy.lua'))
local frame=0
local names={'CurrentBank','SelectedCharacter','WorldNumber','LevelNumber','AreaType','GameEngineSubroutine','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_X_Speed','Player_Y_Speed','Player_State','Player_MovingDir','PlayerFacingDir','SavedJoypadBits','Player_CollisionBits','Player_BoundBoxCtrl','CrouchingFlag','RgCrouch','XgPitCrouchHeld','SideCollisionTimer','Local_eb','Local_ec','Local_ed','Local_ef','R0','R1','R2','R3','R4','R5','R6','R7'}
local function r(n) return L[n] and emu.read(L[n],emu.memType.nesDebug) or -1 end
local function cell(x,y)
 if y<32 or y>=240 then return -1 end
 return emu.read(L.Block_Buffer_1+math.floor(x/256)%2*208+math.floor((y-32)/16)*16+math.floor(x%256/16),emu.memType.nesDebug)
end
local log=assert(io.open(cfg.out..'contact-writes.csv','w'))
log:write('frame,address,old,value,pc,opcode_minus3,opcode_minus2,opcode_minus1,opcode,sp,stack,'..table.concat(names,',')..',nearby_cells\n')
emu.addMemoryCallback(function(address,value)
 if frame<12884 or frame>12894 then return end
 if r('SelectedCharacter')~=6 or r('WorldNumber')~=0 or r('LevelNumber')~=3 or r('AreaType')~=3 or r('GameEngineSubroutine')~=8 then return end
 local s=emu.getState(); local pc=s['cpu.pc']; local sp=s['cpu.sp']
 local row={frame+1,address,emu.read(address,emu.memType.nesDebug),value,pc}
 for offset=-3,0 do row[#row+1]=emu.read((pc+offset)&65535,emu.memType.nesDebug) end
 row[#row+1]=sp
 local stack={};for offset=1,12 do stack[#stack+1]=string.format('%02x',emu.read(256+((sp+offset)&255),emu.memType.nesDebug)) end
 row[#row+1]=table.concat(stack,':')
 for _,n in ipairs(names)do row[#row+1]=r(n)end
 local cells={};local x=r('Player_X_Position')+256*r('Player_PageLoc')
 for dx=-16,32,16 do for y=48,128,16 do cells[#cells+1]=(x+dx)..'/'..y..'/'..cell(x+dx,y)end end
 row[#row+1]=table.concat(cells,':')
 log:write(table.concat(row,',')..'\n');log:flush()
end,emu.callbackType.write,assert(L.Player_X_Position))
emu.addEventCallback(function()
 frame=frame+1
 if frame==12888 or frame==12890 or frame==12892 then
  local f=assert(io.open(cfg.out..'contact-frame-'..frame..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
end,emu.eventType.endFrame)
return base
