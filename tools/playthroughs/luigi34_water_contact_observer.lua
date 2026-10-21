-- Read-only real-controller water-contact receipts; no emulated writes.
local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))
local policy=assert(dofile(root..'/tools/playthroughs/native34_current_stage_tail.lua'))
local frame=0
local out=assert(io.open(ROSTER_CONFIG.out..'water-contact-writes.csv','w'))
local fields={'SelectedCharacter','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos',
 'Player_X_Speed','Player_Y_Speed','Player_Y_MoveForce','Player_State','PlayerSize','CrouchingFlag',
 'Player_CollisionBits','SideCollisionTimer','Player_X_Scroll','Player_MovingDir','Local_eb',
 'R0','R1','R2','R3','R4','R5','R6','R7','SavedJoypadBits','A_B_Buttons','PreviousA_B_Buttons'}
out:write('frame,event,pc,address,old,value,'..table.concat(fields,',')..'\n')
local function r(n)return emu.read(assert(L[n]),emu.memType.nesDebug)end
local function emit(event,address,value)
 local x=r('Player_X_Position')+256*r('Player_PageLoc')
 if r('WorldNumber')~=1 or r('LevelNumber')~=1 or r('AreaType')~=0 or x<2000 or x>2256 then return end
 local row={frame+1,event,emu.getState()['cpu.pc'],address or -1,address and emu.read(address,emu.memType.nesDebug)or -1,value or -1}
 for _,n in ipairs(fields)do row[#row+1]=r(n)end
 out:write(table.concat(row,',')..'\n');out:flush()
end
for _,n in ipairs({'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_Speed'})do
 emu.addMemoryCallback(function(address,value)emit(n,address,value)end,emu.callbackType.write,assert(L[n]))
end
for _,n in ipairs({'GuestFootContactSide','SamusStopAtWall','ImpedePlayerMove','DoFootCheck','DoPlayerSideCheck'})do
 emu.addMemoryCallback(function()if r('CurrentBank')%128==1 then emit('exec-'..n)end end,emu.callbackType.exec,assert(L[n]))
end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
return policy
