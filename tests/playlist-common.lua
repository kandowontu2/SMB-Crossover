-- Explicit frozen-world fixtures; native captures are the expected output.
local c=assert(PLAYLIST_CHARACTER)
local role=({[7]='rygar',[9]='bass',[10]='ryu',[11]='sophia'})[c]
local frame,phase,sample=0,-1,0
local length=PLAYLIST_LOOP and 4500 or 400
local phaseCount=PLAYLIST_LOOP and 1 or 14
local expected={}
for p=0,phaseCount-1 do local f=assert(io.open(TEST_DIR..'fixtures/playlist/'..role..'-'..(PLAYLIST_LOOP and 3 or p)..'.bin','rb'));expected[p]=f:read('*a');f:close() end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v,emu.memType.nesDebug)end
emu.addEventCallback(function()
 emu.setInput({down=frame==80,right=frame>=100 and frame<100+20*(c-6) and (frame-100)%20==0,start=frame==240},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if phase<0 or sample>=length then return end
 local bytes=expected[phase];local index=sample*17
 for reg=0,15 do
  local want=bytes:byte(index+reg+1)
  assert(r('GuestNativeApu',reg)==want,'Playlist '..role..' phase '..phase..' frame '..sample..' register '..reg..': '..r('GuestNativeApu',reg)..' expected '..want)
 end
 assert(r('XgAudioStatus')==bytes:byte(index+17),'Native channel-enable mask')
 assert(r('XgAudioDepth')<=4,'Verified command-macro stack bound')
 sample=sample+1
end,emu.callbackType.exec,L.ExpandedAudioDecoded)
emu.addEventCallback(function()
 frame=frame+1
 if frame<550 then return end
 for i=0,5 do w('Enemy_Flag',0,i) end
 w('TimerControl',255);w('GameTimerCtrlTimer',255)
 if phase<0 or sample==length then
  if phase>=0 then print('PASS '..role..' native playlist selection '..phase..', '..length..' exact APU shadow frames') end
  phase=phase+1;sample=0
  if phase==phaseCount then print('PASS '..(PLAYLIST_LOOP and 'native song 04 crosses its verified 4032-update loop with exact APU output' or 'all source area/event playlists and compressed decoder for '..role));emu.stop(0);return end
  w('AreaMusicQueue',0);w('EventMusicQueue',0)
  if PLAYLIST_LOOP then w('AreaMusicQueue',8)
  elseif phase<7 then w('AreaMusicQueue',1<<phase) else w('EventMusicQueue',1<<(phase-7)) end
 end
end,emu.eventType.endFrame)
