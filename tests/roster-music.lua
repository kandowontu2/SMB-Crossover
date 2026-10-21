local frame=0
local character=assert(ROSTER_CHARACTER)
local writes=0
local function r(n) return emu.read(assert(L[n],n),emu.memType.nesDebug) end
local function w(n,v) emu.write(assert(L[n],n),v,emu.memType.nesDebug) end
local expected=({[3]={0x2a,0x36,0x3e,0x3a,0x26,0x46},[4]={1,0x80,0x20,0x20,8,4},[5]={0x2a,0x30,0x33,0x3c,0x27,0x48}})[character]
emu.addMemoryCallback(function() writes=writes+1 end,emu.callbackType.write,0x4000,0x400f)
emu.addEventCallback(function()
 emu.setInput({right=frame>=80 and frame<80+20*character and (frame-80)%20==0,start=frame==200,b=frame==700},0)
end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame==550 then assert(r('RgAudioSong')==expected[1] and writes>200,'Native starting music') end
 local queue=({[560]=2,[590]=4,[620]=8,[650]=0x20})[frame]
 if queue then w('AreaMusicQueue',queue) end
 local index=({[565]=2,[595]=3,[625]=4,[655]=5,[685]=6})[frame]
 if index then assert(r('RgAudioSong')==expected[index],'Character-specific native area/fanfare '..index) end
 if frame==680 then w('EventMusicQueue',0x20) end
 if frame==710 then assert(r('OperMode')==1 and r('SelectedCharacter')==character,'Weapons and fanfares preserve the running game') end
 if frame==740 then w('GamePauseStatus',1) end
 if frame==745 then assert(emu.read(0x4015,emu.memType.nesDebug)%16==0,'Pause silences native APU') end
 if frame==760 then w('GamePauseStatus',0) end
 if frame==780 then
  assert(r('RgAudioSong')==expected[6] and emu.read(0x4015,emu.memType.nesDebug)%16~=0,'Unpause resumes the current driver')
  print('PASS guest '..character..' native music routing, fanfare, weapon effect, pause and resume');emu.stop(0)
 end
end,emu.eventType.endFrame)
