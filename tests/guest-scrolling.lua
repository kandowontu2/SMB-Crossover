local frame=0
local character=assert(SCROLL_CHARACTER)
local tag=SCROLL_POWER and '-charged' or ''
local irqFile=assert(io.open(OUTPUT..ROM_NAME..'-scroll-'..character..tag..'.csv','w'))
irqFile:write('frame,scanline,cycle,scroll,nametable\n')
local lastCamera,lastX
local irqs=0
local splitWrites=0
local ppuFile=assert(io.open(OUTPUT..ROM_NAME..'-split-'..character..tag..'.csv','w'))
ppuFile:write('frame,scanline,cycle,address,value\n')
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addMemoryCallback(function()
 if frame>=550 then
  splitWrites=0
  local s=emu.getState();irqFile:write(table.concat({frame,s['ppu.scanline'] or -1,s['ppu.cycle'] or -1,r('IrqNewScroll'),r('IrqPPUCTRL')%2},',')..'\n');irqs=irqs+1
 end
end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function(address,value)
 if frame>=550 then
  local st=emu.getState();local line=st['ppu.scanline'] or -1
  if line>=29 and line<=35 then
   splitWrites=splitWrites+1
   if splitWrites>=3 then assert((st['ppu.cycle'] or 0)>=257 and (st['ppu.cycle'] or 999)<=320,'Final scroll-register writes stay in hblank: '..tostring(st['ppu.cycle'])) end
   ppuFile:write(table.concat({frame,line,st['ppu.cycle'] or -1,address,value},',')..'\n') end
 end
end,emu.callbackType.write,0x2005,0x2006)
emu.addEventCallback(function()
 emu.setInput({right=(frame>=80 and frame<80+20*character and (frame-80)%20==0) or (frame>=550 and frame<980),start=frame==200,
  a=(frame>=690 and frame<725) or (frame>=780 and frame<815) or (frame>=880 and frame<915),b=(SCROLL_POWER and frame>=560 and frame<680) or frame==600 or frame==630},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==540 and SCROLL_POWER then w('PlayerStatus',SCROLL_POWER) end
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame>=550 then
  local x=r('Player_PageLoc')*256+r('Player_X_Position')
  local camera=r('ScreenLeft_PageLoc')*256+r('ScreenLeft_X_Pos')
  if lastCamera then assert(camera>=lastCamera and camera-lastCamera<=5,'Camera advances smoothly: '..lastCamera..' -> '..camera) end
  lastCamera=camera;lastX=x
  if frame==650 then assert(camera>10,'Selected guest scrolls the camera: '..camera);print('PASS character '..character..' camera follows the player') end
  if frame==660 or frame==720 or frame==800 then
   local f=assert(io.open(OUTPUT..ROM_NAME..'-scroll-'..character..tag..'-'..frame..'.png','wb'));f:write(emu.takeScreenshot());f:close()
  end
 end
 if frame==980 then
  assert(lastCamera>150,'Camera crosses a background column/page boundary')
  assert(irqs>300,'HUD split remains active while scrolling')
  irqFile:close();ppuFile:close();print('PASS guest '..character..' forward camera motion and HUD split trace');emu.stop(0)
 end
end,emu.eventType.endFrame)
