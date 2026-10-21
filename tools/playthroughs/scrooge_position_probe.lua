-- Read-only diagnosis of an ordinary fixed controller prefix. No emulated
-- RAM/register/state writes; this stops early and is not a clear proof.
local frame=0
local out=assert(io.open(ROSTER_CONFIG.out..'position-writes.csv','w'))
local fields={'CurrentBank','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos',
 'Player_X_Speed','Player_Y_Speed','Player_State','PlayerFacingDir','Player_MovingDir',
 'ScPogo','ScAttack','RgCrouch','PlayerSize','CrouchingFlag','Player_CollisionBits',
 'Player_BoundBoxCtrl','BoundingBox_UL_XPos','BoundingBox_UL_YPos','BoundingBox_DR_XPos','BoundingBox_DR_YPos',
 'Local_eb','R0','R1','R2','R3','R4','R5','R6','R7','MmVY',
 'BlockBounceTimer','Block_Orig_XPos','Block_Orig_YPos','ObjectOffset','SavedJoypadBits'}
out:write('frame,event,address,old,value,pc,'..table.concat(fields,',')..'\n')
local function r(name)return L[name]and emu.read(L[name],emu.memType.nesDebug)or -1 end
local function emit(event,address,value)
 if frame<754 or frame>775 then return end
 local state=emu.getState()
 local row={frame+1,event,address or -1,address and emu.read(address,emu.memType.nesDebug)or -1,value or -1,state['cpu.pc']}
 for _,name in ipairs(fields)do row[#row+1]=r(name)end
 out:write(table.concat(row,',')..'\n');out:flush()
end
for _,name in ipairs({'Player_X_Position','Player_PageLoc','Player_Y_Position'})do
 emu.addMemoryCallback(function(address,value)emit(name,address,value)end,emu.callbackType.write,assert(L[name]))
end
for _,name in ipairs({'GuestFootContactSide','SamusStopAtWall','ImpedePlayerMove','PlayerHeadCollision',
 'CrossoverHeadProbe','DoFootCheck','DoPlayerSideCheck'})do
 if L[name]then emu.addMemoryCallback(function()emit('exec-'..name)end,emu.callbackType.exec,L[name])end
end
emu.addEventCallback(function()
 frame=frame+1
 if frame>=800 then out:close();emu.stop(0)end
end,emu.eventType.endFrame)
return function()return{}end
