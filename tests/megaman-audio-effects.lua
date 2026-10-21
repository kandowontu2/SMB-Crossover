-- Controller-driven charging over each music engine. Only the helmet pickup
-- and area-song queue are fixtures; sound timing follows real held input.
local frame=0
local effectWrites=0
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addMemoryCallback(function() effectWrites=effectWrites+1 end,emu.callbackType.write,0x4004,0x4007)
emu.addEventCallback(function()
  emu.setInput({right=frame==80,start=frame==120,
    b=(frame>=520 and frame<680) or (frame>=760 and frame<920)},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame>=490 then for i=0,5 do w('Enemy_Flag',0,i) end end
  if frame==500 then w('PlayerStatus',1) end
  for _,start in ipairs({520,760}) do
    if frame==start+31 then
      assert(r('MmAudioChargeAge')==0,'Charging is silent before the source 550 ms threshold')
    end
    if frame==start+40 then
      assert(r('MmAudioChargeAge')>0,'Holding B starts the rising charge sound')
      assert(r('Mm3AudioZp',14)==7,'Original charge sound priority is active')
      assert(r('MmAudioSfxMask')==2,'Charge owns pulse 2 while music keeps other channels')
    end
    if frame==start+145 then
      assert(r('MmChargeFrames')==87,'Full charge stays capped while the sound continues')
      assert(r('MmAudioChargeAge')==77,'The rising tone reaches the repeating charged tone')
      assert(r('Mm3AudioZp',14)==7 and r('Mm3AudioZp',15)==2,'Charged tone loops on pulse 2')
    end
    if frame==start+163 then
      assert(r('MmAudioChargeAge')==0,'Releasing B cancels the charge loop')
      assert(r('Mm3AudioZp',14)==8,'A charged shot uses the original charged-shot effect')
      assert(r('MmAudioSfxMask')==12,'Charged shot owns triangle and noise')
    end
    if frame==start+185 then
      assert(r('MmAudioSfxMask')==0,'Sound channels return to music after the effect')
      print('PASS charge onset, rising tone, held loop, release and channel restoration over engine '..r('MmAudioEngine'))
    end
  end
  if frame==730 then w('AreaMusicQueue',4) end
  if frame==750 then assert(r('MmAudioEngine')==2,'Underground uses the other music driver') end
  if frame==960 then
    assert(r('MmAudioCurrentSong')==2,'Effects preserve the underground track')
    assert(effectWrites>200,'Native effects write the pulse channel throughout charging')
    print('PASS shared native APU effects over MM2 and MM3 music')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
