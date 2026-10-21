-- Explicit isolated renderer fixture, not traversal evidence. Completed DMA
-- OAM and actual mapped PPU pixels must match the authoritative native sheet.
-- Only fixture object/CHR shadow state is authored; no OAM/ROM/CPU patches.
local source=assert(io.open(TEST_DIR..'../chr/mmc5/sprites_enemies.chr','rb')):read('*a')
local poses={
 {'BOWSER_FRONT_MOUTH_OPEN',1,{{8,0,0},{10,8,0},{40,0,16}}},
 {'BOWSER_FRONT_MOUTH_CLOSED',1,{{12,0,0},{14,8,0},{40,0,16}}},
 {'BOWSER_REAR_WALK_1',1,{{4,0,0},{6,8,0},{32,0,16},{34,8,16}}},
 {'BOWSER_REAR_WALK_2',1,{{4,0,0},{6,8,0},{36,0,16},{38,8,16}}},
 {'PEACH_STANDING',2,{{20,0,0},{22,8,0},{52,0,16},{52,8,16,true}}},
 {'TOAD_STANDING',2,{{16,0,0},{16,8,0,true},{18,0,16},{18,8,16,true}}},
 -- Native flame faces left for either object-facing flag; its custom
 -- metasprite intentionally shares one pointer for both directions.
 {'BOWSER_FLAME',2,{{44,0,0},{46,8,0},{48,16,0}},24,-4,16,true},
}
local deadline=560+#poses*24
local frame,draw,dma=0,nil,nil
local checked={}
local mmc5=ROM_NAME:find('mmc5')~=nil
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local interruptDepth=0
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do
 emu.addMemoryCallback(function()interruptDepth=interruptDepth+1 end,emu.callbackType.exec,pc)
end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do
 emu.addMemoryCallback(function()interruptDepth=interruptDepth-1;assert(interruptDepth>=0,'Balanced native-art fixture interrupt scope')end,emu.callbackType.exec,pc)
end
local function expected(n)
 local pose=poses[n//2+1];local result={};local width=pose[4]or 16
 for _,s in ipairs(pose[3])do for y=0,15 do for x=0,7 do
  local bit=s[4]and x or 7-x
  local a=2048+s[1]*16+(y//8)*16+y%8+1
  local color=((source:byte(a)>>bit)&1)+2*((source:byte(a+8)>>bit)&1)
  local px=s[2]+x;if n%2==1 and not pose[7]then px=width-1-px end
  if color~=0 then result[(s[3]+y)*width+px]=color end
 end end end
 return result
end
emu.addEventCallback(function()emu.setInput({start=frame==120},0)end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame<560 or frame>=deadline or interruptDepth~=0 or r('CurrentBank')%128~=4 then return end
 local n=(frame-560)//12;local pose=poses[n//2+1]
 -- Native MMC3 castle sheet is logical $1b/$1c. MMC5's independent sprite
 -- window uses native bank $17. These are fixture inputs, not the oracle.
 if mmc5 then w('CurrentCHRBank',0x17,4)
 else w('CurrentCHRBank',0x1b,4);w('CurrentCHRBank',0x1c,5)end
 w('SsChrActive',0);w('ReloadCHRBank',1)
 for i=0,23 do w('ObjectMetasprite',0,i)end
 w('ObjectMetasprite',assert(L['METASPRITE_'..pose[1]]),1)
 w('SprObject_X_Position',112,1);w('SprObject_PageLoc',0,1)
 w('SprObject_Y_Position',80,1);w('SprObject_Y_HighPos',1,1)
 w('PlayerFacingDir',n%2+1,1);w('ObjectVerticalFlip',0,1);w('SprObject_SprAttrib',0,1)
 draw=n
end,emu.callbackType.exec,L.DrawAllMetasprites)
-- DMA is intentionally observed inside NMI; this read-only tag records which
-- foreground-authored picture actually reached hardware sprite memory.
emu.addMemoryCallback(function()dma=draw end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=550 and frame<deadline then for i=0,5 do w('Enemy_Flag',0,i)end end
 if dma and not checked[dma]then
  local state=mmc5 and emu.getState()or nil
  local function chr(a)
   if state then return emu.read(state['mapper.chrBanks'..(a//1024)]*1024+a%1024,emu.memType.nesChrRom)end
   return emu.read(a,emu.memType.nesPpuDebug)
  end
  local actual={};local count=0;local pose=poses[dma//2+1]
  local width,height=pose[4]or 16,pose[6]or 32
  local originY=81+(pose[5]or 0)
  for i=0,63 do
   local y=emu.read(i*4,emu.memType.nesSpriteRam)+1
   local t=emu.read(i*4+1,emu.memType.nesSpriteRam)
   local a=emu.read(i*4+2,emu.memType.nesSpriteRam)
   local x=emu.read(i*4+3,emu.memType.nesSpriteRam)
   if x>=112 and x<112+width and y>=originY and y<originY+height then
    count=count+1
    assert(a&3==poses[dma//2+1][2],'Native actor palette preserved')
    local base=(t&1)*4096+(t&254)*16
    for dy=0,15 do for dx=0,7 do
     local row=a&128~=0 and 15-dy or dy;local bit=a&64~=0 and dx or 7-dx
     local address=base+(row//8)*16+row%8
     local color=((chr(address)>>bit)&1)+2*((chr(address+8)>>bit)&1)
     if color~=0 then actual[(y+dy-originY)*width+x+dx-112]=color end
    end end
   end
  end
  local ref=expected(dma)
  assert(count==#poses[dma//2+1][3],'Every native actor sprite reaches completed DMA')
  for i=0,width*height-1 do assert(actual[i]==ref[i],'Exact native castle pixels: '..poses[dma//2+1][1]..' facing '..(dma%2+1)..' pixel '..i)end
  checked[dma]=true
 end
 if frame==deadline+1 then
  for n=0,#poses*2-1 do assert(checked[n],'Every native castle pose/facing rendered: '..n)end
  print('PASS native Bowser four poses, flame, Toad and Peach: both facings, palettes and exact completed-DMA PPU pixels');emu.stop(0)
 end
end,emu.eventType.endFrame)
