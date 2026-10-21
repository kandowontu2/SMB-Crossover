-- Bounded real-controller transaction observation. No emulated writes.
local frame=0
local out=assert(io.open(ROSTER_CONFIG.out..'pending-writes.csv','w'))
local names={'CurrentBank','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_Speed',
 'Player_State','ScPogo','RgCrouch','R0','R1','R2','R3','R4','R6','R7','MmBreakBlock','MmBlockAttack',
 'BlockBounceTimer','VRAM_Buffer1','Block_State','Block_State:1','Block_RepFlag','Block_RepFlag:1',
 'Block_Metatile','Block_Metatile:1','Block_BBuf_Low','Block_BBuf_Low:1',
 'Block_Orig_YPos','Block_Orig_YPos:1','Block_Orig_XPos','Block_Orig_XPos:1'}
local function r(name)
 local base,offset=name:match('^(.*):(%d+)$')
 base=base or name
 return L[base]and emu.read(L[base]+tonumber(offset or 0),emu.memType.nesDebug)or -1
end
out:write('frame,event,address,old,value,pc,'..table.concat(names,',')..'\n')
local function emit(event,address,value)
 if frame<11860 or frame>11882 then return end
 local row={frame+1,event,address or -1,address and emu.read(address,emu.memType.nesDebug)or -1,value or -1,emu.getState()['cpu.pc']}
 for _,name in ipairs(names)do row[#row+1]=r(name)end
 out:write(table.concat(row,',')..'\n');out:flush()
end
emu.addMemoryCallback(function(a,v)emit('block-buffer',a,v)end,emu.callbackType.write,L.Block_Buffer_1,L.Block_Buffer_2+207)
for _,name in ipairs({'Block_State','Block_RepFlag','Block_Metatile'})do
 emu.addMemoryCallback(function(a,v)emit(name,a,v)end,emu.callbackType.write,L[name],L[name]+1)
end
for _,name in ipairs({'PlayerHeadCollision','BrickShatter','BumpBlock','GuestFootContactSide','BlockObjMT_Updater'})do
 if L[name]then emu.addMemoryCallback(function()emit('exec-'..name)end,emu.callbackType.exec,L[name])end
end
emu.addEventCallback(function()
 frame=frame+1
 if frame==11876 or frame==11877 then
  local p=assert(io.open(ROSTER_CONFIG.out..'pending-'..frame..'.png','wb'));p:write(emu.takeScreenshot());p:close()
  local f=assert(io.open(ROSTER_CONFIG.out..'pending-map-'..frame..'.csv','w'))
  f:write('y');for x=1648,1760,16 do f:write(','..x)end;f:write('\n')
  for y=96,208,16 do
   f:write(y)
   for x=1648,1760,16 do
    local a=L.Block_Buffer_1+math.floor(x/256)%2*208+math.floor((y-32)/16)*16+math.floor(x%256/16)
    f:write(','..emu.read(a,emu.memType.nesDebug))
   end
   f:write('\n')
  end
  f:close()
 end
 if frame>=11890 then out:close();emu.stop(0)end
end,emu.eventType.endFrame)
return function()return{}end
