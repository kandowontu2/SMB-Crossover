-- Sustained controller-only playback: static pixels, real frame cadence,
-- no stale world split, and a vanilla note trace for independent comparison.
local heroes={'MARIO','LUIGI','MEGA MAN','PROTO MAN','SAMUS','BILL','LANCE','LINK',
 'ZELDA II LINK','SIMON','GRANT','SYPHA','ALUCARD','PIT','RYGAR','SCROOGE',
 'DARKWING DUCK','BASS','ROLL','RYU','SOPHIA','KIRBY','META KNIGHT','CHIP','DALE',
 'LITTLE MAC','MIKE JONES','SMB3 MARIO','SMB3 LUIGI','VIC VIPER','OCTOPUS','TWINBEE',
 'PENTAROU','LEONARDO','RAPHAEL','MICHELANGELO','DONATELLO'}
local frame,waiting,buttons=0,0,{}
local active,nmiStart,pendingMario=false,nil,false
local ticks,nmis,irqCount,visibleWrites,apuWrites,maxCycles=0,0,0,0,0,0
local summary=assert(io.open(OUTPUT..'playback.csv','w'))
summary:write('character,ticks,nmis,irq_calls,visible_scroll_writes,apu_writes,max_nmi_cycles,stable_frames,pixel_hash\n')
local notes=assert(io.open(OUTPUT..'mario-notes.csv','w'))
local fields={'Squ1_NoteLenCounter','Squ2_NoteLenCounter','Tri_NoteLenCounter','MusicOffset_Square1','MusicOffset_Square2','MusicOffset_Triangle','MusicOffset_Noise','NoteLenLookupTblOfs','NoteLengthTblAdder','MusicDataLow','MusicDataHigh'}
notes:write('tick,'..table.concat(fields,',')..'\n')
local marioTicks=0
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
local function bank(pc)return emu.convertAddress(pc).address//8192 end
local function pixels()
 local h=2166136261;local p=emu.getScreenBuffer();assert(#p==256*240)
 for _,v in ipairs(p)do h=((h~v)*16777619)&0xffffffff end
 return h
end
local function shot(name)local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
emu.addEventCallback(function()emu.setInput(buttons,0)end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if active then nmis=nmis+1;nmiStart=emu.getState()['cpu.cycleCount']end
end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()
 if nmiStart then maxCycles=math.max(maxCycles,emu.getState()['cpu.cycleCount']-nmiStart);nmiStart=nil end
 if pendingMario then
  local row={marioTicks};for _,n in ipairs(fields)do row[#row+1]=r(n)end
  notes:write(table.concat(row,',')..'\n');pendingMario=false
 end
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()
 if not active or bank(L.SoundTestAudioTick)~=B.SoundTestAudioTick then return end
 ticks=ticks+1
 if r('SoundTestHero')==0 and r('SoundTestPlaying')==1 then marioTicks=marioTicks+1;pendingMario=true end
end,emu.callbackType.exec,L.SoundTestAudioTick)
emu.addMemoryCallback(function()if active then irqCount=irqCount+1 end end,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(function()
 if not active then return end
 local line=emu.getState()['ppu.scanline'];if line>=0 and line<240 then visibleWrites=visibleWrites+1 end
end,emu.callbackType.write,0x2005,0x2006)
emu.addMemoryCallback(function()if active then apuWrites=apuWrites+1 end end,emu.callbackType.write,0x4000,0x4013)
local function wait(n)coroutine.yield(n)end
local function press(key)buttons={[key]=true};wait(2);buttons={};wait(8)end
local task=coroutine.create(function()
 wait(70);press('down');press('start');for i=1,3 do press('down')end;press('a')
 assert(r('CrossoverMenuState')==8,'Real Audio Test opens')
 for i,name in ipairs(heroes)do
  assert(r('SoundTestHero')==i-1 and r('SoundTestKind')==0,'Actual selected identity '..name)
  ticks,nmis,irqCount,visibleWrites,apuWrites,maxCycles=0,0,0,0,0,0
  active=true;press('a');wait(240)
  local expected=pixels()
  for f=1,30 do wait(1);assert(pixels()==expected,'Static menu flickers during '..name)end
  assert(r('SoundTestPlaying')==1 and r('SoundTestCommand')==0,'Playback remains active '..name)
  assert(ticks==nmis and ticks>=270,'Audio advances once per physical frame '..name)
  assert(irqCount==0 and visibleWrites==0,'No gameplay HUD split on sound menu '..name)
  assert(apuWrites>0 and maxCycles<29780,'Native audio fits one frame '..name)
  summary:write(table.concat({name,ticks,nmis,irqCount,visibleWrites,apuWrites,maxCycles,30,expected},',')..'\n')
  if name=='MARIO'or name=='MEGA MAN'or name=='SAMUS'or name=='BILL'then shot(name..'-playing')end
  active=false;press('start');assert(r('SoundTestPlaying')==0,'Stop responds '..name);press('down')
  print('PASS sustained sound menu '..name)
 end
 press('b');assert(r('CrossoverMenuState')==4,'B returns to Options')
 summary:close();notes:close()
 local f=assert(io.open(OUTPUT..'regression-result.json','w'))
 f:write(string.format('{"passed":true,"characters":37,"stable_frames_per_character":30,"mario_note_ticks":%d,"frames":%d,"screenshots":4,"per_frame_files":0,"scope":"Sustained overworld playback cadence and static menu pixels; Mario notes compared separately with normal playback"}\n',marioTicks,frame));f:close()
 print('PASS sustained audio menu all37');emu.stop(0)
end)
emu.addEventCallback(function()
 frame=frame+1;assert(frame<16000,'Bounded sustained playback test')
 if waiting>0 then waiting=waiting-1;return end
 if coroutine.status(task)=='dead'then return end
 local ok,n=coroutine.resume(task);assert(ok,n);waiting=n or 0
end,emu.eventType.endFrame)
