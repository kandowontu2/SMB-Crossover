-- Isolated actual-DMA renderer arena. Bowser's native rear flag points to
-- its primary object; source FLASH colors the whole single source enemy.
local frame,depth,phase,drawn=0,0,0,nil
local mmc5=ROM_NAME:find('mmc5')~=nil
local remaining={24,22,20,18,0}
local palette={1,2,3,2,1}
local checked={}
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt),assert(L.IrqScrollSplit)})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({assert(L.NonMaskableInterrupt_RTI),assert(L.IrqScrollSplit_RTI)})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0,'Balanced composite FLASH interrupts')end,emu.callbackType.exec,pc)end
emu.addEventCallback(function()emu.setInput({right=frame>=80 and frame<160 and frame%20==0,start=frame==200},0)end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame<560 or frame>=660 or depth~=0 or r('CurrentBank')%128~=4 then return end
 phase=(frame-560)//20+1
 assert(r('SelectedCharacter')==4,'Real menu launches Link before composite rendering fixture')
 if mmc5 then w('CurrentCHRBank',0x17,4)else w('CurrentCHRBank',0x1b,4);w('CurrentCHRBank',0x1c,5)end
 w('SsChrActive',0);w('ReloadCHRBank',1)
 w('ScreenLeft_X_Pos',0);w('ScreenLeft_PageLoc',0)
 for i=0,23 do w('ObjectMetasprite',0,i)end
 for i=0,5 do w('Enemy_Flag',0,i);w('MmEnemyFlash',0,i)end
 w('Enemy_Flag',1);w('Enemy_ID',45);w('Enemy_Flag',0x80,1);w('Enemy_ID',45,1)
 w('MmEnemyFlash',remaining[phase])
 w('ObjectMetasprite',assert(L.METASPRITE_BOWSER_FRONT_MOUTH_OPEN),1)
 w('ObjectMetasprite',assert(L.METASPRITE_BOWSER_REAR_WALK_1),2)
 for i=1,2 do
  w('SprObject_X_Position',i==1 and 96 or 112,i);w('SprObject_PageLoc',0,i)
  w('SprObject_Y_Position',i==1 and 96 or 104,i);w('SprObject_Y_HighPos',1,i)
  w('PlayerFacingDir',1,i);w('ObjectVerticalFlip',0,i);w('SprObject_SprAttrib',0,i)
 end
 drawn=phase
end,emu.callbackType.exec,assert(L.DrawAllMetasprites))
local dma
emu.addMemoryCallback(function(_,page)
 if drawn then dma={phase=drawn,bytes={}};for i=0,255 do dma.bytes[i]=emu.read(page*256+i,emu.memType.nesDebug)end end
end,emu.callbackType.write,0x4014)
emu.addEventCallback(function()
 frame=frame+1
 if dma and frame>=566 and(frame-560)%20>=6 then
  local n=0
  for i=0,63 do
   local y=emu.read(i*4,emu.memType.nesSpriteRam)
   local x=emu.read(i*4+3,emu.memType.nesSpriteRam)
   if y>=88 and y<136 and x>=96 and x<128 then
    local a=emu.read(i*4+2,emu.memType.nesSpriteRam)
    assert(a&3==palette[dma.phase],'Whole source Bowser FLASH reaches actual DMA: phase'..dma.phase..' half'..(x<112 and 'front'or'rear')..' actual'..(a&3)..' expected'..palette[dma.phase])
    n=n+1
   end
  end
  assert(n==7,'All seven native front/rear sprites reach actual DMA')
  checked[dma.phase]=true
 end
 if frame==661 then for i=1,5 do assert(checked[i],'All source phases and normal restoration cover both native halves')end;print('PASS whole source Bowser FLASH across both native halves, all phases and normal restoration');emu.stop(0)end
end,emu.eventType.endFrame)
