-- Extra read-only observers around the explicit ceiling fixture.
local frame=0
local f=assert(io.open(OUTPUT..ROM_NAME..'-scrooge-ceiling-diagnose.csv','w'))
local fields={'CurrentBank','SelectedCharacter','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_Speed','ScPogo','R0','R2','R4','R6','R7'}
f:write('frame,event,old,value,pc,'..table.concat(fields,',')..'\n')
local function r(n)return L[n]and emu.read(L[n],emu.memType.nesDebug)or -1 end
local function emit(e,a,v)
 if frame<619 or frame>625 then return end
 local row={frame,e,a and emu.read(a,emu.memType.nesDebug)or -1,v or -1,emu.getState()['cpu.pc']}
 for _,n in ipairs(fields)do row[#row+1]=r(n)end
 f:write(table.concat(row,',')..'\n');f:flush()
end
for _,n in ipairs({'CrossoverHeadProbe','CrossoverGuestHeadProbe','ScroogeHeadProbe','PlayerHeadCollision','SamusStopAtWall','DoFootCheck'})do
 if L[n]then emu.addMemoryCallback(function()emit(n)end,emu.callbackType.exec,L[n])end
end
for _,n in ipairs({'Player_X_Position','Player_Y_Position','R4'})do
 emu.addMemoryCallback(function(a,v)emit('write-'..n,a,v)end,emu.callbackType.write,L[n])
end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
dofile(TEST_DIR..'scrooge-ceiling-separation.lua')
