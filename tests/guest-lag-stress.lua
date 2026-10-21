-- Keep native enemies active while moving, jumping and shooting. Clearing
-- every enemy (as in the camera-only tests) masks the overloaded NMI path.
local frame=0
local character=LAG_CHARACTER or 1
local lag,irqs,writes=0,0,0
local inIrq=false
local log=assert(io.open(OUTPUT..ROM_NAME..'-lag-'..character..'.csv','w'))
log:write('frame,scanline,dot,address,value\n')
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
emu.addMemoryCallback(function()
 if frame>=550 and r('NmiDisable')>=128 then lag=lag+1 end
end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function() inIrq=true;if frame>=550 then irqs=irqs+1;writes=0 end end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()inIrq=false end,emu.callbackType.exec,L.IrqScrollSplit_RTI)
emu.addMemoryCallback(function(a,v)
 if frame<550 or not inIrq then return end
 local s=emu.getState()
 if s['ppu.scanline']<40 then
  writes=writes+1
  log:write(table.concat({frame,s['ppu.scanline'],s['ppu.cycle'],a,v},',')..'\n')
  if writes>=3 then
   assert(s['ppu.scanline']==31 and s['ppu.cycle']>=257 and s['ppu.cycle']<=320,
    'Busy-frame scroll split stays on line 31 in hblank: '..s['ppu.scanline']..'/'..s['ppu.cycle'])
  end
 end
end,emu.callbackType.write,0x2005,0x2006)
emu.addEventCallback(function()
 emu.setInput({right=(frame>=80 and frame<80+20*character and (frame-80)%20==0) or (frame>=550 and frame<950),
 start=frame==200,a=frame>=600 and frame%100<35,b=frame>=550 and frame%20<10},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==540 then emu.write(L.PlayerStatus,2,emu.memType.nesDebug);emu.write(L.StarInvincibleTimer,255,emu.memType.nesDebug) end
 if frame==1200 then
  assert(lag>0 and irqs>600,'Real enemies and weapons exercised lag frames and repeated HUD splits')
  log:close();print('PASS character '..character..' stable HUD/background split through '..lag..' lag frames and '..irqs..' IRQs');emu.stop(0)
 end
end,emu.eventType.endFrame)
