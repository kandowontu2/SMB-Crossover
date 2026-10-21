-- Explicit music-queue fixture. Hash music register images and decoder events
-- for every hardware update, independently of main-loop speed and lag.
local c=assert(DECODER_CHARACTER)
local frame,age,updates=0,0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local out=assert(io.open(OUTPUT..ROM_NAME..'-decoder-'..c..'.bin','wb'))
emu.addEventCallback(function()
 local logical=c
 emu.setInput({down=frame==80,right=frame>=100 and frame<100+(logical-6)*20 and(frame-100)%20==0,start=frame==240},0)
end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if frame<550 then return end
 age=age+1
 if age%300==1 then
  local group=(age-1)//300
  w('AreaMusicQueue',group<7 and(1<<group)or 0)
  w('EventMusicQueue',group>=7 and(1<<(group-7))or 0)
 end
end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()
 if age<1 or age>4200 then return end
 local data={};for i=0,15 do data[#data+1]=string.char(r('XgMusicApu',i))end
 data[#data+1]=string.char(r('XgAudioStatus'),r('XgAudioDelay'),r('XgAudioEvent'))
 out:write(table.concat(data));updates=updates+1
end,emu.callbackType.exec,L.ExpandedAudioDecoded)
emu.addEventCallback(function()
 frame=frame+1
 if frame==549 then assert(r('SelectedCharacter')==c,'Music fixture selected character')end
 if frame>=550 then
  for i=0,5 do w('Enemy_Flag',0,i)end
  w('GameTimerDisplay',9,2)
 end
 if age==4200 then
  out:close();assert(updates==4200,'Every music update recorded: '..updates)
  print('PASS 4200 expanded decoder music-register images, seven area songs and seven events, character '..c);emu.stop(0)
 end
end,emu.eventType.endFrame)
