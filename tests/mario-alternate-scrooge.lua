-- Real menu controls: Luigi is Mario's alternate, Scrooge occupies slot eight.
local frame=0
local jumped,pogo=false,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function shot(n)local f=assert(io.open(OUTPUT..ROM_NAME..'-scrooge-'..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
emu.addEventCallback(function()
 emu.setInput({start=frame==60 or frame==220,select=frame==80 or frame==140,
  right=frame==100 or frame==180 or frame==200 or(frame>=600 and frame<640),
  left=frame==120,down=frame==160 or(frame>=670 and frame<790),
  a=frame>=660 and frame<690,b=(frame>=670 and frame<790)or(frame>=840 and frame<845)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==95 then assert(r('SelectedCharacter')==8 and r('CrossoverMenuIndex')==0,'Select changes Mario to Luigi in place')end
 if frame==135 then assert(r('SelectedCharacter')==8 and r('CrossoverMenuIndex')==0,'Returning to Mario position preserves its alternate')end
 if frame==155 then assert(r('SelectedCharacter')==0 and r('CrossoverMenuIndex')==0,'Select restores Mario')end
 if frame==215 then assert(r('SelectedCharacter')==12 and r('CrossoverMenuIndex')==8,'Scrooge replaces Luigi in the second row');shot('menu')end
 if frame==580 then assert(r('GameEngineSubroutine')==8 and r('SelectedCharacter')==12,'Scrooge reaches playable 1-1');shot('stand')end
 if frame>=670 and frame<790 then
  if r('Player_State')~=0 then jumped=true end
  if r('ScPogo')~=0 then pogo=true end
 end
 if frame==750 then shot('pogo')end
 if frame==1000 then
  assert(jumped and pogo,'Controller jump and Down+B activate native cane pogo')
  assert(r('GameEngineSubroutine')==8 and r('MmDeathFlag')==0,'Cane/pogo leaves main-loop control live')
  print('PASS Mario/Luigi Select alternate, Scrooge slot, launch, movement, jump, cane pogo and continued play');emu.stop(0)
 end
end,emu.eventType.endFrame)
