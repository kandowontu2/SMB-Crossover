-- Read-only write-time MMC5 background-font ownership during a native replay.
local out=assert(io.open(ROSTER_CONFIG.out..'hud-publication.csv','w'))
out:write('frame,physical,expected,active,hudUpper,pc,clearModes,gameplay,scanline,cycle,skipped\n')
local frame,upper,clears=0,0,0
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local masks={}
for tile=0,63 do
 masks[tile]={}
 for y=0,7 do
  local at=394*1024+tile*16+y
  masks[tile][y+1]=emu.read(at,emu.memType.nesChrRom)|emu.read(at+8,emu.memType.nesChrRom)
 end
end
local maskFile=assert(io.open(ROSTER_CONFIG.out..'hud-expected-masks.bin','wb'))
local maskIndex=assert(io.open(ROSTER_CONFIG.out..'hud-mask-index.csv','w'))
maskIndex:write('frame,offset,bytes\n')
local maskOffset=0
emu.addEventCallback(function()
 frame=frame+1;out:flush()
 if r('SelectedCharacter')==18 and r('VvVariant')==0 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 and r('InvHudActive')~=0 then
  local tiles={};local valid=true
  for x=0,23 do tiles[x+1]=emu.read(0x2024+x,emu.memType.nesPpuDebug);if tiles[x+1]>=64 then valid=false end end
  if valid then
   local bytes={}
   for y=1,8 do for x=1,24 do bytes[#bytes+1]=string.char(masks[tiles[x]][y])end end
   maskFile:write(table.concat(bytes));maskIndex:write(frame..','..maskOffset..',192\n');maskOffset=maskOffset+192
  end
 end
 maskFile:flush();maskIndex:flush()
end,emu.eventType.endFrame)
emu.addMemoryCallback(function(_,v)upper=v&3 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function()
 if r('SelectedCharacter')==18 and r('VvVariant')==0 then clears=clears+1 end
end,emu.callbackType.exec,L.X5ClearChrModes)
emu.addMemoryCallback(function(_,v)
 if r('SelectedCharacter')~=18 or r('VvVariant')~=0 or r('OperMode')~=1 then return end
 local active=r('InvHudActive')
 local gameplay=r('OperMode_Task')==3 and r('GameEngineSubroutine')==8
 local state=emu.getState()
 out:write(table.concat({frame,v+upper*256,394,active,emu.read(0x73ed,emu.memType.nesDebug),state['cpu.pc'],clears,gameplay and 1 or 0,state['ppu.scanline'],state['ppu.cycle'],r('NmiSkipped')},',')..'\n')
end,emu.callbackType.write,0x5128)
