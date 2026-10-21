local frame,seen=0,false
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({right=frame==80,start=frame==200,a=frame>=550 and frame<580},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=540 then for i=0,5 do w('Enemy_Flag',0,i) end end
 if frame>550 and r('MmAudioSfx')==9 then
  assert(r('MmAudioSfxMask')==10,'Source landing effect uses pulse 2 and noise')
  seen=true
 end
 if frame==720 then
  assert(seen,'Actual jump/landing plays the native landing effect')
  assert(r('MmAudioSfxMask')==0 and r('MmAudioCurrentSong')==1,'Landing releases the channels to the area music')
  print('PASS Mega Man real landing, native pulse/noise effect and music restoration');emu.stop(0)
 end
end,emu.eventType.endFrame)
