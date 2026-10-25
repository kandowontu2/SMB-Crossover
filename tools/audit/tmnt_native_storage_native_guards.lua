-- Read-only native hardware/source observations; no emulator state writes.
local C=assert(TMNT_STORAGE_NATIVE)
for n,a in pairs(C.ram)do L[n]=a end
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local function json(v)
 if type(v)=='table'then local t={};if #v>0 then for _,x in ipairs(v)do t[#t+1]=json(x)end;return'['..table.concat(t,',')..']'end;for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
local bus=assert(io.open(OUTPUT..'native-bus.jsonl','w'))
local function stamp()local s=emu.getState();return{frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],cycle=s['ppu.cycle'],cpu=s['cpu.cycleCount'],pc=s['cpu.pc'],sp=s['cpu.sp']}end
local function row(q)bus:write(json(q)..'\n');bus:flush()end
local function active()return C.entered==1 and r('SelectedCharacter')==19 and r('OperMode')==1 and r('GameEngineSubroutine')==8 end
local nmiDepth,nmis,irqs,maxNmiDepth=0,0,0,0
emu.addMemoryCallback(function()
 nmiDepth=nmiDepth+1;nmis=nmis+1;maxNmiDepth=math.max(maxNmiDepth,nmiDepth)
 assert(nmiDepth==1,'Actual NMI does not nest inside audio')
end,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(function()assert(nmiDepth==1,'Balanced actual NMI return');nmiDepth=nmiDepth-1 end,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(function()if active()then irqs=irqs+1 end end,emu.callbackType.exec,L.IrqScrollSplit)
local mask,pending,completed,unsafe,wrong,installed=0,nil,0,0,0,{}
emu.addMemoryCallback(function(_,v)mask=v end,emu.callbackType.write,0x2001)
local function bytes(at,kind)local t={};for i=0,255 do t[i+1]=emu.read(at+i,kind)end;return t end
local function equal(a,b)for i=1,#a do if a[i]~=b[i]then return false end end;return true end
local function safe(q)return q.mask&24==0 or(q.scanline>=241 and q.scanline<=260)end
local function failDMA(q,message)
 local f=assert(io.open(OUTPUT..'first-hardware-failure.json','w'));f:write(json({passed=false,message=message,DMA=q,nmi_depth=nmiDepth,requested_mode=C.behavior,actual_mode=r('CrossoverBehaviorVersion')}));f:close()
 local png=assert(io.open(OUTPUT..'first-hardware-failure.png','wb'));png:write(emu.takeScreenshot());png:close()
 assert(false,message)
end
emu.addMemoryCallback(function()if pending then pending.writes=pending.writes+1 end end,emu.callbackType.write,0x2004)
emu.addMemoryCallback(function(_,page)
 if not active()then return end
 assert(not pending,'One complete hardware DMA at a time')
 local s=stamp();s.mask=mask
 pending={start=s,source=bytes(page*256,emu.memType.nesDebug),page=page,writes=0,owner=bank(s.pc)}
 row({kind='DMA-start',data=pending})
 -- Mesen's write callback exposes the already fetched LDX#1 after STA4014.
 assert(emu.read(s.pc,emu.memType.nesDebug)==0xa2 and emu.read(s.pc+1,emu.memType.nesDebug)==1,'Exact actual DMA completion hook LDX1')
 local finish=s.pc+2;local owner=pending.owner;local key=owner..':'..finish
 if not installed[key]then
  installed[key]=true
  emu.addMemoryCallback(function()
   if not pending or bank(finish)~=owner then return end
   local q=pending;pending=nil;q.finish=stamp();q.finish.mask=mask;q.hardware=bytes(0,emu.memType.nesSpriteRam)
   q.exact=equal(q.source,q.hardware);q.safe=safe(q.start)and safe(q.finish)
   row({kind='DMA-complete',data=q})
   completed=completed+1
   if not q.exact then wrong=wrong+1;failDMA(q,'Actual completed DMA differs from complete source page')end
   if not q.safe then unsafe=unsafe+1;failDMA(q,'Actual completed DMA crosses rendering-enabled time')end
   assert(q.writes==256,'Exactly256 completed hardware DMA writes')
  end,emu.callbackType.exec,finish)
 end
end,emu.callbackType.write,0x4014)

local sourceActive,sourceCalls,sourceStores,gold,goldSong,sourceFrame=false,0,0,nil,nil,0
local events,actual,images={}, {}, {}
local hardware,drumActive,drumHeld=0,0,0
local returns,returnHooks={},{}
local function onReturn(fn)
 local s=emu.getState();local sp=s['cpu.sp'];local pc=(emu.read(256+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(256+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 local key=bank(pc)..':'..pc;returns[key]={sp=(sp+2)%256,fn=fn}
 if not returnHooks[key]then returnHooks[key]=true;local owner=bank(pc)
  emu.addMemoryCallback(function()local q=returns[key];if q and emu.getState()['cpu.sp']==q.sp and bank(pc)==owner then returns[key]=nil;q.fn()end end,emu.callbackType.exec,pc)
 end
end
local gameReturns,draws=0,0
emu.addMemoryCallback(function()
 if not active()or bank(L.DrawAllMetasprites)~=B.DrawAllMetasprites then return end
 draws=draws+1;row({kind='draw-construction',index=C.step,phase=C.phase,draws=draws,stamp=stamp(),nmi_depth=nmiDepth})
end,emu.callbackType.exec,L.DrawAllMetasprites)
emu.addMemoryCallback(function()
 if not active()or bank(L.GameLoop)~=B.GameLoop then return end
 onReturn(function()
  gameReturns=gameReturns+1;row({kind='completed-game-update',index=C.step,phase=C.phase,draws=draws,completed=gameReturns,stamp=stamp(),nmi_depth=nmiDepth,skipped=r('NmiSkipped')})
 end)
end,emu.callbackType.exec,L.GameLoop)
if C.native==1 then
 local function source(kind)
  if bank(L.TnNativeInit)~=63 or r('SelectedCharacter')~=19 then return end
  assert(not sourceActive,'One authentic source call at a time');sourceActive=true;events={}
  if kind=='init'then
   goldSong=r('TnAudioSong');sourceFrame=0;if gold then gold:close()end
   gold=assert(io.open(C.gold..'song-'..goldSong..'.bin','rb'))
  else sourceFrame=sourceFrame+1 end
  onReturn(function()
   local n=assert(gold:read(1),'Bounded original gold record'):byte();local record=assert(gold:read(n*2),'Original ordered APUs')
   assert(#events==n,'Exact original source APU count song='..goldSong..' frame='..sourceFrame)
   for i,q in ipairs(events)do assert(q[1]==record:byte(i*2-1)and q[2]==record:byte(i*2),'Exact original source APU sequence');if q[1]<20 then images[q[1]]=q[2]end end
   sourceCalls=sourceCalls+1;sourceStores=sourceStores+n;sourceActive=false
  end)
 end
 emu.addMemoryCallback(function()source('init')end,emu.callbackType.exec,L.TnNativeInit)
 emu.addMemoryCallback(function()source('play')end,emu.callbackType.exec,L.TnNativePlay)
 for _,site in ipairs(C.sites)do
  emu.addMemoryCallback(function()
   if not sourceActive or bank(site.pc)~=63 then return end
   local s=emu.getState();local add=site.mode=='abx'and s['cpu.x']or site.mode=='aby'and s['cpu.y']or 0
   events[#events+1]={site.address+add-0x4000,s['cpu.a']}
  end,emu.callbackType.exec,site.pc)
 end
end
emu.addMemoryCallback(function(at,v)actual[at-0x4000]=v end,emu.callbackType.write,0x4000,0x4017)
emu.addEventCallback(function()
 if not active()or C.native~=1 then return end
 assert(r('CrossoverBehaviorVersion')==C.behavior,'Every live frame retains actual numeric mode')
 local s=emu.getState()
 if r('GamePauseStatus')%2==0 and r('TnAudioSilenced')==0 and goldSong then
  for reg=0,15 do
   assert(r('GuestNativeApu',reg)==images[reg],'Original source register image')
   if reg~=9 and reg~=13 and not(reg>=12 and(r('GuestMixMask')&8)~=0)then assert(actual[reg]==r('GuestNativeApu',reg),'Actual mixer restores source register');hardware=hardware+1 end
  end
  for reg=0,3 do assert(r('TnAudioDmcRegs',reg)==images[reg+16],'Original DMC source parameter image')end
  assert(actual[21]==r('GuestCombinedEnable'),'Actual hardware4015 stores match merged enable image')
 end
 if r('BassDmcActive')==4 then
  assert(s['apu.dmc.sampleAddr']==L.TnMusicDpcm and s['apu.dmc.sampleLength']==129,'Actual full original drum/address')
  assert(s['apu.dmc.timer.period']==53 and not s['apu.dmc.irqEnabled']and not s['apu.dmc.loopFlag'],'Original DMC rate15/non-loop/noIRQ')
  drumActive=drumActive+1
 end
 if r('GamePauseStatus')%2==0 and r('TnAudioSilenced')==0 and r('TnAudioDacHold')==44 and s['apu.dmc.bytesRemaining']==0 and s['apu.dmc.bufferEmpty']and s['apu.dmc.silenceFlag']then
  assert(s['apu.dmc.outputLevel']==44,'Actual completed original drum holds DAC44');drumHeld=drumHeld+1
 end
end,emu.eventType.endFrame)
local originalStop=emu.stop
function emu.stop(code)
 if code==0 then
  assert(nmiDepth==0 and maxNmiDepth==1,'Final balanced real NMI scheduling')
  assert(completed>100 and wrong==0 and unsafe==0,'Sustained actual completed OAM DMA safety')
  if C.native==1 then assert(sourceCalls>500 and sourceStores>1000 and hardware>1000 and drumActive>0,'Actual original music/hardware/DMC coverage')end
  local f=assert(io.open(OUTPUT..'native-source-hardware.json','w'))
  f:write(json({passed=true,source_calls=sourceCalls,source_APU_writes=sourceStores,hardware_comparisons=hardware,active_DMC_frames=drumActive,held_DAC44_frames=drumHeld,completed_DMA=completed,wrong_DMA=wrong,unsafe_DMA=unsafe,nmis=nmis,irqs=irqs,max_NMI_depth=maxNmiDepth}));f:close();bus:close()
 end
 originalStop(code)
end
