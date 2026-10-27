-- Read-only timing diagnostic with ordinary controller navigation.
-- One CSV, one APU trace, and at most four screenshots; no frame files.
local frame,buttons,waitLeft=0,{},0
local active=false
local nmiStart=nil
local frameTicks,frameWrites,frameNmis,maxNmi=0,0,0,0
local totalTicks,totalNmis,totalWrites,lateEnables=0,0,0,0
local mask=0
-- Only the five exported browser aliases are in VICE labels. Resolve the
-- internal alias from that same assembled block; never register a nil range.
L.SoundTestReserved=L.SoundTestHero+7
local csv=assert(io.open(OUTPUT..'timing.csv','w'))
csv:write('frame,hero,playing,command,ticks,nmis,apu_writes,nmi_max_cycles,nmi_disable,skipped,note1,note2,offset1,offset2,music_lo,music_hi,area_queue,event_queue,bankA,bankC\n')
local apu=assert(io.open(OUTPUT..'apu.csv','w'))
apu:write('frame,cycle,address,value,pc\n')
local events=assert(io.open(OUTPUT..'events.csv','w'))
events:write('frame,event,value,pc,scanline,dot\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(pc)return emu.convertAddress(pc).address//8192 end
local function event(name,v)
 local s=emu.getState();events:write(frame..','..name..','..v..','..s['cpu.pc']..','..s['ppu.scanline']..','..s['ppu.cycle']..'\n')
end
emu.addEventCallback(function()emu.setInput(buttons,0)end,emu.eventType.inputPolled)
emu.addMemoryCallback(function()
 if not active then return end
 local s=emu.getState();nmiStart=s['cpu.cycleCount'];frameNmis=frameNmis+1;totalNmis=totalNmis+1
end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()
 if nmiStart then maxNmi=math.max(maxNmi,emu.getState()['cpu.cycleCount']-nmiStart);nmiStart=nil end
end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()
 if not active or bank(L.SoundTestAudioTick)~=B.SoundTestAudioTick then return end
 frameTicks=frameTicks+1;totalTicks=totalTicks+1
end,emu.callbackType.exec,L.SoundTestAudioTick)
emu.addMemoryCallback(function(at,v)
 if not active then return end
 frameWrites=frameWrites+1;totalWrites=totalWrites+1
 assert(totalWrites<100000,'Bounded APU trace')
 local s=emu.getState();apu:write(frame..','..s['cpu.cycleCount']..','..at..','..v..','..s['cpu.pc']..'\n')
end,emu.callbackType.write,0x4000,0x4017)
emu.addMemoryCallback(function(_,v)
 local old=mask;mask=v
 if active and old&24==0 and v&24~=0 then
  local s=emu.getState();if not(s['ppu.scanline']>=241 and s['ppu.scanline']<=260 or s['ppu.scanline']==-1 and s['ppu.cycle']<=274)then lateEnables=lateEnables+1;event('late-render-enable',v)end
 end
end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function(at,v)if active then event('PPU'..string.format('%04x',at),v)end end,emu.callbackType.write,0x2000,0x2007)
emu.addMemoryCallback(function(_,v)if active then event('note-length-adder',v)end end,emu.callbackType.write,assert(L.NoteLengthTblAdder))
for _,name in ipairs({'MusicDataLow','MusicDataHigh','SoundTestCommand','SoundTestPlaying','SoundTestReserved','OperMode','SelectedCharacter'})do
 emu.addMemoryCallback(function(_,v)if active then event(name,v)end end,emu.callbackType.write,L[name])
end
local function wait(n)coroutine.yield(n)end
local function press(key)buttons={[key]=true};wait(2);buttons={};wait(8)end
local function shot(name)local f=assert(io.open(OUTPUT..name..'.png','wb'));f:write(emu.takeScreenshot());f:close()end
local task=coroutine.create(function()
 wait(70);press('down');press('start')
 for i=1,3 do press('down')end;press('a')
 assert(r('CrossoverMenuState')==8,'Real Audio Test opens')
 active=true;press('a');wait(420);shot('mario-playing');press('start');wait(10)
 press('down');press('down');press('a');wait(420);shot('megaman-playing');press('start');wait(10)
 press('down');press('down');press('a');wait(420);shot('samus-playing');press('start');wait(10)
 press('down');press('a');wait(420);shot('bill-playing');press('start');wait(10)
 active=false;csv:close();apu:close();events:close()
 local f=assert(io.open(OUTPUT..'timing-result.json','w'))
 f:write(string.format('{"diagnostic_only":true,"frames":%d,"ticks":%d,"nmis":%d,"apu_writes":%d,"late_render_enables":%d,"screenshots":4,"per_frame_files":0}\n',frame,totalTicks,totalNmis,totalWrites,lateEnables));f:close()
 print('DONE bounded music timing diagnostic');emu.stop(0)
end)
emu.addEventCallback(function()
 frame=frame+1;assert(frame<2500,'Bounded diagnostic duration')
 if active then
  csv:write(table.concat({frame,r('SoundTestHero'),r('SoundTestPlaying'),r('SoundTestCommand'),frameTicks,frameNmis,frameWrites,maxNmi,r('NmiDisable'),r('NmiSkipped'),r('Squ1_NoteLenCounter'),r('Squ2_NoteLenCounter'),r('MusicOffset_Square1'),r('MusicOffset_Square2'),r('MusicDataLow'),r('MusicDataHigh'),r('AreaMusicQueue'),r('EventMusicQueue'),bank(0xa000),bank(0xc000)},',')..'\n')
 end
 frameTicks,frameWrites,frameNmis,maxNmi=0,0,0,0
 if waitLeft>0 then waitLeft=waitLeft-1;return end
 if coroutine.status(task)=='dead'then return end
 local ok,n=coroutine.resume(task);assert(ok,n);waitLeft=n or 0
end,emu.eventType.endFrame)
