-- Explicit high-platform/block arenas; actual controller jumps and gunfire.
-- Sample every IRQ write, even when a broken split falls below the HUD.
local frame=0
local case=0
local age=0
local cases={}
for variant=0,1 do for outlines=0,1 do for _,gun in ipairs({0,4,5,2,3})do
 for _,mode in ipairs({'jump','blocks'})do cases[#cases+1]={variant=variant,outlines=outlines,gun=gun,mode=mode}end
end end end
local current
local irq=false
local writes=0
local faults,checked,hud,changed=0,0,0,0
local firstFault
local ppuCallback
local ppuLog=assert(io.open(OUTPUT..ROM_NAME..'-bill-hud-a12.csv','w'))
ppuLog:write('frame,line,dot,address,rise,lowDots,irqCounter,irqReload\n')
local a12=false
local lowSince=0
local function ppu(a,v)
 local s=emu.getState();local line,dot=s['ppu.scanline'],s['ppu.cycle']
 local high=a&0x1000~=0
 local t=line*341+dot
 if high~=a12 then
  if high then ppuLog:write(table.concat({frame,line,dot,a,1,t-lowSince,s['mapper.irqCounter']or -1,s['mapper.irqReload']or -1},',')..'\n')else lowSince=t end
  a12=high
 end
end

local diagnostic=assert(io.open(OUTPUT..ROM_NAME..'-bill-hud-oam.csv','w'))
diagnostic:write('frame,case,ppuLine,ppuDot,nextDelay,latchedDelay,row30,row31,oam\n')
local trace=assert(io.open(OUTPUT..ROM_NAME..'-bill-hud-split.csv','w'))
trace:write('frame,case,mode,variant,outlines,gun,playerY,line,dot,address,value\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function cell(x,y)return (x//256)%2*208+((y-32)//16)*16+(x%256)//16 end
local function setup()
 for i=0,415 do w('Block_Buffer_1',0,i);w('MmBrickHealth',0,i);w('MmSolidTerrain',0,i)end
 local py=current.mode=='jump' and 64 or 176
 for p=0,1 do for x=0,15 do w('Block_Buffer_1',0x54,cell(p*256+x*16,py+32))end end
 for i=0,5 do w('Enemy_Flag',0,i)end
 for i=0,9 do w('RgShotType',0,i)end
 for i=0,1 do w('Block_State',0,i);w('Block_RepFlag',0,i);w('BlockMetasprite',0,i)end
 w('BlockBounceTimer',0);w('RgCooldown',0);w('RgShootPose',0);w('RgAttack',0)
 w('BillVariant',current.variant);w('PlayerOutlinesOff',current.outlines)
 w('InvOwnedLo',1+(current.gun~=0 and (1<<current.gun)or 0),3);w('InvOwnedHi',0,3)
 w('InvSelected',current.gun,3);w('PlayerStatus',1);w('InvDirty',1)
 w('Player_X_Position',100);w('Player_PageLoc',0);w('Player_Y_Position',py);w('Player_Y_HighPos',1)
 w('Player_State',0);w('Player_X_Speed',0);w('Player_Y_Speed',0);w('PlayerFacingDir',1)
 w('ScreenLeft_X_Pos',64);w('ScreenLeft_PageLoc',0);w('ScreenRight_X_Pos',63);w('ScreenRight_PageLoc',1)
 w('HorizontalScroll',64)
 for i=0,2 do w('MmVX',0,i);w('MmVY',0,i)end
 for i=0,1 do w('MmXFraction',0,i);w('MmYFraction',0,i)end
 if current.mode=='blocks' then
  for x=144,224,16 do w('Block_Buffer_1',x%32==0 and 0xc1 or 0x51,cell(x,192))end
 end
end
emu.addMemoryCallback(function()
 irq=true;writes=0
end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()irq=false end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
emu.addMemoryCallback(function(a,v)
 if not irq or not current or age<5 then return end
 writes=writes+1
 local s=emu.getState();local line,dot=s['ppu.scanline'],s['ppu.cycle']
 trace:write(table.concat({frame,case,current.mode,current.variant,current.outlines,current.gun,r('Player_Y_Position'),line,dot,a,v},',')..'\n')
 if writes>=3 then
  checked=checked+1
  if line~=31 or dot<257 or dot>320 then
   faults=faults+1
   firstFault=firstFault or ('case '..case..' '..current.mode..' gun '..current.gun..' Y '..r('Player_Y_Position')..' split '..line..'/'..dot)
   if L.GuestHudIrqDelay then
    local bytes={};for o=0,255 do bytes[#bytes+1]=string.format('%02x',emu.read(o,emu.memType.nesSpriteRam))end
    diagnostic:write(table.concat({frame,case,line,dot,r('GuestHudNextDelay'),r('GuestHudIrqDelay'),r('GuestHudRows',30),r('GuestHudRows',31),table.concat(bytes)},',')..'\n')
   end
  end
 end
end,emu.callbackType.write,0x2005,0x2006)
emu.addEventCallback(function()
 local buttons={right=frame==80 or frame==100 or frame==120,start=frame==200}
 if current then
  buttons.a=current.mode=='jump' and(age>=8 and age<32 or age>=65 and age<85)
  buttons.b=age>=8 and age%12<6
 end
 emu.setInput(buttons,0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==1400 then ppuCallback=emu.addMemoryCallback(ppu,emu.callbackType.read,0,0x3fff,emu.cpuType.nes,emu.memType.nesPpuMemory)end
 if frame==1406 then ppuLog:close();emu.stop(0);return end
 if frame<550 then return end
 if not current or age==100 then
  if current and current.mode=='blocks' then
   for x=144,224,16 do if r('Block_Buffer_1',cell(x,192))~=(x%32==0 and 0xc1 or 0x51)then changed=changed+1;break end end
  end
  case=case+1;current=cases[case];age=0
  if not current then
   trace:close();diagnostic:close()
   assert(hud>100 and changed>=8,'Both high HUD jumps and actual bullet/block contacts exercised: '..hud..'/'..changed)
   assert(checked>2000 and faults==0,'Every final HUD split write stays in line-31 hblank: '..faults..' faults; '..(firstFault or 'none'))
   print('PASS Bill/Lance high HUD jumps and brick/question shooting, all five guns, outlines ON/OFF: '..checked..' final split writes, no displacement');emu.stop(0);return
  end
  setup()
 end
 age=age+1
 if current.mode=='jump' and r('Player_Y_HighPos')==1 and r('Player_Y_Position')<32 then hud=hud+1 end
 if faults>0 and faults<5 then
  local f=assert(io.open(OUTPUT..ROM_NAME..'-bill-hud-fault-'..frame..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
 if case<=2 and(age==20 or age==30 or age==45)then
  local f=assert(io.open(OUTPUT..ROM_NAME..'-bill-hud-'..current.mode..'-'..age..'.png','wb'));f:write(emu.takeScreenshot());f:close()
 end
end,emu.eventType.endFrame)
