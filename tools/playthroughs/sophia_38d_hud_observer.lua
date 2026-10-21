-- Owned bounded read-only HUD diagnostic. Fixed ordinary inputs; no writes.
local cfg=assert(ROSTER_CONFIG)
local root=assert(cfg.out:match('^(.*)/build/'))
local base=assert(dofile(root..'/tools/playthroughs/sophia_38d_policy.lua'))
local frame=0
local snapshots=assert(io.open(cfg.out..'hud-snapshots.csv','w'))
local writes=assert(io.open(cfg.out..'hud-ppu-writes.csv','w'))
snapshots:write('frame,bank,mode,task,engine,world,level,area,x,y,bufferOffset,dirty,char,hud0,hud1,hud2,hud3,text0,text1,text2,text3\n')
writes:write('frame,pc,bank,target,value,R0,R1,R2,R3,R7,bufferOffset,world,level,engine,siteBytes\n')
local function r(n,i) return L[n] and emu.read(L[n]+(i or 0),emu.memType.nesDebug) or -1 end
local function hexbyte(v) return string.format('%02x',v) end
local latch,high,address,increment=0,0,0,1
emu.addMemoryCallback(function() latch=0 end,emu.callbackType.read,0x2002)
emu.addMemoryCallback(function(a,v)
 if a==0x2000 then increment=(v&4)~=0 and 32 or 1
 elseif a==0x2005 then latch=1-latch
 elseif a==0x2006 then
  if latch==0 then high=v&63 else address=high*256+v end
  latch=1-latch
 elseif a==0x2007 then
  if frame>=500 and address>=0x2000 and address<0x2080 then
   local st=emu.getState();local pc=st['cpu.pc'] or -1
   local bytes={}
   for i=-3,-1 do bytes[#bytes+1]=hexbyte(emu.read((pc+i)&65535,emu.memType.nesDebug)) end
   writes:write(table.concat({frame,pc,r('CurrentBank'),address,v,r('R0'),r('R1'),r('R2'),r('R3'),r('R7'),r('VRAM_Buffer1_Offset'),r('WorldNumber'),r('LevelNumber'),r('GameEngineSubroutine'),table.concat(bytes)},',')..'\n')
  end
  address=(address+increment)&0x3fff
 end
end,emu.callbackType.write,0x2000,0x2007)
local last=''
emu.addEventCallback(function()
 frame=frame+1
 if frame<500 or frame>5720 then return end
 local rows,texts={},{}
 for row=0,3 do
  local b,t={},{}
  for col=0,31 do
   local v=emu.read(0x2000+row*32+col,emu.memType.nesPpuDebug)
   b[#b+1]=hexbyte(v)
   t[#t+1]=v<10 and tostring(v) or v<36 and string.char(65+v-10) or v==36 and ' ' or '.'
  end
  rows[#rows+1]=table.concat(b);texts[#texts+1]=table.concat(t)
 end
 local signature=table.concat(rows)
 if signature~=last then
  local fields={frame,r('CurrentBank'),r('OperMode'),r('OperMode_Task'),r('GameEngineSubroutine'),r('WorldNumber'),r('LevelNumber'),r('AreaPointer'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('VRAM_Buffer1_Offset'),r('InvDirty'),r('SelectedCharacter')}
  for _,v in ipairs(rows)do fields[#fields+1]=v end
  for _,v in ipairs(texts)do fields[#fields+1]=v end
  snapshots:write(table.concat(fields,',')..'\n');snapshots:flush();writes:flush();last=signature
 end
 if frame==541 or frame==4103 or frame==5650 then
  local f=assert(io.open(cfg.out..'hud-frame-'..frame..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
end,emu.eventType.endFrame)
return base
