-- Read-only diagnosis of the fixed, ordinary controller stream. Not a clear.
local frame=0
local out=assert(io.open(ROSTER_CONFIG.out..'position-writes.csv','w'))
local fields={'CurrentBank','SelectedCharacter','Player_X_Position','Player_PageLoc',
 'Player_Y_Position','Player_Y_HighPos','Player_X_Speed','Player_Y_Speed',
 'Player_State','PlayerSize','CrouchingFlag','Player_CollisionBits','SideCollisionTimer',
 'ScreenLeft_X_Pos','ScreenLeft_PageLoc','Player_Pos_ForScroll','Player_X_Scroll',
 'PlayerFacingDir','Player_MovingDir','Local_eb','R0','R1','R2','R3','R4','R5','R6','R7',
 'ObjectOffset','SavedJoypadBits','A_B_Buttons','SwimmingFlag','MarioWaterActive'}
out:write('frame,event,address,old,value,pc,a,cpuX,cpuY,'..table.concat(fields,',')..'\n')
local function r(name)return L[name]and emu.read(L[name],emu.memType.nesDebug)or -1 end
local function emit(event,address,value)
 if frame<15245 or frame>15265 then return end
 local state=emu.getState()
 local row={frame+1,event,address or -1,address and emu.read(address,emu.memType.nesDebug)or -1,value or -1,
  state['cpu.pc']or -1,state['cpu.a']or -1,state['cpu.x']or -1,state['cpu.y']or -1}
 for _,name in ipairs(fields)do row[#row+1]=r(name)end
 out:write(table.concat(row,',')..'\n');out:flush()
end
for _,name in ipairs({'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_Speed','SideCollisionTimer'})do
 emu.addMemoryCallback(function(address,value)emit(name,address,value)end,emu.callbackType.write,assert(L[name]))
end
for _,name in ipairs({'GuestFootContactSide','SamusStopAtWall','ImpedePlayerMove','PlayerHeadCollision',
 'CrossoverHeadProbe','DoFootCheck','DoPlayerSideCheck','StopPlayerMove','ScrollHandler'})do
 if L[name]then emu.addMemoryCallback(function()emit('exec-'..name)end,emu.callbackType.exec,L[name])end
end
emu.addEventCallback(function()
 frame=frame+1
 if frame==15246 then
  local f=assert(io.open(ROSTER_CONFIG.out..'water-blocks.csv','w'));f:write('worldX,y,tile\n')
  for x=2000,2208,16 do for y=32,224,16 do
   local index=math.floor(x/256)%2*208+math.floor((y-32)/16)*16+math.floor(x%256/16)
   f:write(x..','..y..','..emu.read(L.Block_Buffer_1+index,emu.memType.nesDebug)..'\n')
  end end
  f:close()
 end
 if frame>=15272 then out:close();emu.stop(0)end
end,emu.eventType.endFrame)
return function()return{}end
