local frame=0
local writes=0
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug) end
local function w(n,v,i) emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug) end
emu.addMemoryCallback(function() writes=writes+1 end,emu.callbackType.write,0x4000,0x400f)
emu.addEventCallback(function()
  emu.setInput({right=frame==80,start=frame==120},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
  frame=frame+1
  if frame==480 then
    assert(r('MmAudioCurrentSong')==1,'Overworld selects hosted MM3 title theme')
    assert(r('MmAudioEngine')==3,'Overworld runs MM3 native APU driver')
    assert(writes>100,'Native music writes APU registers')
    w('AreaMusicQueue',4)
  end
  if frame==490 then
    assert(r('MmAudioCurrentSong')==2 and r('MmAudioEngine')==2,'Underground selects Flash Man')
    w('AreaMusicQueue',2)
  end
  if frame==500 then
    assert(r('MmAudioCurrentSong')==3,'Water selects Bubble Man')
    w('AreaMusicQueue',8)
  end
  if frame==510 then
    assert(r('MmAudioCurrentSong')==4,'Castle selects MM2 boss theme')
    w('EventMusicQueue',0x20)
  end
  if frame==520 then
    assert(r('MmAudioCurrentSong')==6,'Level clear selects MM2 victory')
    w('AreaMusicQueue',1)
  end
  if frame==530 then
    w('EventMusicQueue',0x40)
  end
  if frame==540 then assert(r('MmAudioCurrentSong')==8,'Hurry cue selects New Weapon') end
  if frame==710 then
    assert(r('MmAudioCurrentSong')==1,'Hurry cue returns to area music')
    print('PASS native APU music, source-specific area tracks, victory and hurry cue')
    emu.stop(0)
  end
end,emu.eventType.endFrame)
