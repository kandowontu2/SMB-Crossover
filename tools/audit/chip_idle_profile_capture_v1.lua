-- Read-only bounded component profiler. All real callbacks are startup-static.
-- No emulated writes, controller changes, clock changes or instruction log.
do
 local P=assert(CHIP_IDLE_PROFILE)
 local pw,serial,sourceCalls=0,0,0
 local calls,spans,boundaries,snaps,isrs={},{},{},{},{}
 local ramBytes,counts,aggregate=0,{},{}
 local registered={};for _,pc in ipairs(P.return_pcs)do registered[pc]=true end
 local function read(at)return emu.read(at,emu.memType.nesDebug)end
 local function r(n)return read(assert(L[n],n))end
 local function bank(pc)if pc<0x8000 then return -1 end;return emu.convertAddress(pc).address//8192 end
 local function active()return r('SelectedCharacter')==14 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end
 local function window()return pw>=P.first_wall and pw<=P.last_wall and active()end
 local function json(v)
  if type(v)=='table'then local q={};if #v>0 then for _,x in ipairs(v)do q[#q+1]=json(x)end;return'['..table.concat(q,',')..']'end;for k,x in pairs(v)do q[#q+1]=string.format('%q',tostring(k))..':'..json(x)end;return'{'..table.concat(q,',')..'}'
  elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
 end
 local function state(kind)
  local s=emu.getState();return{kind=kind,wall_completed=pw,upcoming_endFrame_row=pw+1,sourceCalls=sourceCalls,cpuCycle=s['cpu.cycleCount'],pc=s['cpu.pc'],a=s['cpu.a'],x=s['cpu.x'],y=s['cpu.y'],p=s['cpu.ps'],sp=s['cpu.sp'],ppuFrame=s['ppu.frameCount'],scanline=s['ppu.scanline'],dot=s['ppu.cycle'],banks={bank(0x8000),bank(0xa000),bank(0xc000),bank(0xe000)},currentBank=r('CurrentBank'),currentBankC=r('CurrentBankC'),nmiDisable=r('NmiDisable'),nmiSkipped=r('NmiSkipped'),skipDraw=r('ShouldSkipDrawSprites'),framesSinceDraw=r('FramesSinceLastSpriteDraw'),song=r('RgAudioSong'),request=r('RgAudioRequest'),parent=calls[#calls]and calls[#calls].id or 0,isrDepth=#isrs}
 end
 local function event(kind,extra)
  assert(#boundaries<P.max_events,'Bounded boundary capture');local v=state(kind);if extra then for k,x in pairs(extra)do v[k]=x end end;boundaries[#boundaries+1]=v;return v
 end
 local function snapshot(kind,detail)
  assert(#snaps<P.max_snapshots,'Bounded full-state captures');local bytes={}
  for _,range in ipairs(P.ram_ranges)do for at=range[1],range[2]do bytes[#bytes+1]=string.char(read(at))end end
  local data=table.concat(bytes);assert(#data==P.ram_bytes);local row=state(kind);row.ramOffset=ramBytes;row.ramBytes=#data;row.detail=detail;row.data=data;snaps[#snaps+1]=row;ramBytes=ramBytes+#data
 end
 local function captureWindow()for _,v in ipairs(P.snapshot_windows)do if pw>=v[1]and pw<=v[2]then return true end end;return false end
 local function valid(h)
  if bank(h.address)~=h.physical_bank then return false end
  for i,b in ipairs(h.bytes)do assert(read(h.address+i-1)==b,'Pinned profile instruction '..h.name)end;return true
 end
 local function closeReturns(pc)
  local s=emu.getState()
  while #calls>0 do
   local q=calls[#calls];if q.ret~=pc or q.returnSP~=s['cpu.sp']or q.returnBank~=bank(pc)then break end
   calls[#calls]=nil;local elapsed=s['cpu.cycleCount']-q.start;local cpu=elapsed-q.interruptCycles
   assert(cpu>=0 and q.childCpu<=cpu,'Causal span/interrupt accounting');local row={id=q.id,name=q.name,parent=q.parent,entry=q.entry,returnPC=pc,returnBank=q.returnBank,entrySP=q.entrySP,returnSP=s['cpu.sp'],wall_completed=pw,sourceCalls=sourceCalls,startCycle=q.start,endCycle=s['cpu.cycleCount'],elapsedCycles=elapsed,interruptCycles=q.interruptCycles,cpuCycles=cpu,same_context_child_cycles=q.childCpu,exclusiveCpuCycles=cpu-q.childCpu,isrDepth=q.depth,entryBanks=q.entryBanks}
   assert(#spans<P.max_spans,'Bounded function-span capture');spans[#spans+1]=row
   local parent=calls[#calls];if parent and parent.depth==q.depth then parent.childCpu=parent.childCpu+cpu end
   local a=aggregate[q.name]or{calls=0,cpu=0,exclusive=0,min=cpu,max=cpu};a.calls=a.calls+1;a.cpu=a.cpu+cpu;a.exclusive=a.exclusive+row.exclusiveCpuCycles;a.min=math.min(a.min,cpu);a.max=math.max(a.max,cpu);aggregate[q.name]=a
  end
 end
 -- Return PCs are collected from pinned real caller windows at preparation.
 -- One small copied-SMC exec range covers real RAM farcall return wrappers.
 for _,pc in ipairs(P.return_pcs)do emu.addMemoryCallback(closeReturns,emu.callbackType.exec,pc)end
 emu.addMemoryCallback(closeReturns,emu.callbackType.exec,P.smc_start,P.smc_end)
 for _,h in ipairs(P.functions)do
  emu.addMemoryCallback(function()
   if not window()or not valid(h)then return end
   local s=emu.getState();local sp=s['cpu.sp'];local ret=(read(0x100+(sp+1)%256)+256*read(0x100+(sp+2)%256)+1)%65536
   assert(registered[ret]or(ret>=P.smc_start and ret<=P.smc_end),'Unbound actual return '..h.name..' '..ret)
   local top=calls[#calls];if top and top.entry==h.address and top.entrySP==sp and top.ret==ret then return end -- exact pre-instruction ISR resumption
   serial=serial+1;local row={id=serial,name=h.name,parent=top and top.id or 0,entry=h.address,entrySP=sp,returnSP=(sp+2)%256,ret=ret,returnBank=bank(ret),start=s['cpu.cycleCount'],interruptCycles=0,childCpu=0,depth=#isrs,entryBanks={bank(0x8000),bank(0xa000),bank(0xc000),bank(0xe000)}};calls[#calls+1]=row
   counts[h.name]=(counts[h.name]or 0)+1
   if captureWindow()and(h.name=='GameLoop'or h.name=='AudioUpdate')then snapshot('component-entry',h.name)
   elseif h.name=='ChNativeSourcePlay'and counts[h.name]<=4 then snapshot('source-play-entry',h.name)end
  end,emu.callbackType.exec,h.address)
 end
 for _,kind in ipairs({'NMI','IRQ'})do
  local h=P.interrupts[kind];local stop=P.interrupts[kind..'Return']
  emu.addMemoryCallback(function()
   if not(window()or#calls>0)or not valid(h)then return end
   local s=emu.getState();local sp=s['cpu.sp'];local depth=#isrs;local owners={}
   for _,c in ipairs(calls)do if c.depth==depth then owners[#owners+1]=c end end
   local pc=read(0x100+(sp+2)%256)+256*read(0x100+(sp+3)%256);local p=read(0x100+(sp+1)%256)
   isrs[#isrs+1]={kind=kind,start=s['cpu.cycleCount'],owners=owners,sp=sp,pc=pc,p=p};event(kind..'-entry',{interruptedPC=pc,stackedP=p,foregroundSP=(sp+3)%256,last_foreground_instruction_boundary=s['cpu.cycleCount']-7})
   if kind=='NMI'and r('NmiDisable')~=0 and(P.lag_snapshots or 0)<3 then P.lag_snapshots=(P.lag_snapshots or 0)+1;snapshot('post-hardware-NMI-entry',{interruptedPC=pc,stackedP=p,foregroundSP=(sp+3)%256,qualification='RAM is after the3 hardware stack pushes, not a pretended preinterrupt full snapshot'})end
  end,emu.callbackType.exec,h.address)
  emu.addMemoryCallback(function()
   if #isrs==0 or not valid(stop)then return end
   local q=isrs[#isrs];assert(q.kind==kind,'Actual nested interrupt owner');local s=emu.getState();assert(s['cpu.sp']==q.sp,'Actual ISR pre-RTI stack restored');assert(read(stop.address)==0x40)
   local cycles=s['cpu.cycleCount']+6-(q.start-7)
   for _,c in ipairs(q.owners)do c.interruptCycles=c.interruptCycles+cycles end
   event(kind..'-pre-RTI',{complete_hardware_entry_and_RTI_cycles=cycles,interruptedPC=q.pc});isrs[#isrs]=nil
  end,emu.callbackType.exec,stop.address)
 end
 emu.addMemoryCallback(function()if bank(P.source_return.address)==P.source_return.physical_bank then sourceCalls=sourceCalls+1 end end,emu.callbackType.exec,P.source_return.address)
 emu.addMemoryCallback(function(at,v)if window()then event('NmiDisable-write',{value=v})end end,emu.callbackType.write,L.NmiDisable)
 emu.addMemoryCallback(function(at,v)if window()then event('NmiSkipped-write',{value=v})end end,emu.callbackType.write,L.NmiSkipped)
 emu.addMemoryCallback(function(at,v)if window()then event('draw-decision-write',{value=v})end end,emu.callbackType.write,L.ShouldSkipDrawSprites)
 emu.addMemoryCallback(function(at,v)if window()then event('DMA-start',{page=v})end end,emu.callbackType.write,0x4014)
 for _,h in ipairs(P.markers)do emu.addMemoryCallback(function()if window()and valid(h)then event(h.name)end end,emu.callbackType.exec,h.address)end
 local function finish()
  assert(#calls==0 and#isrs==0,'All bounded profile spans/ISRs returned before1300 stop')
  local raw=assert(io.open(OUTPUT..'profile-snapshots.ram','wb'));local meta=assert(io.open(OUTPUT..'profile-snapshots.jsonl','w'))
  for _,q in ipairs(snaps)do raw:write(q.data);q.data=nil;meta:write(json(q)..'\n')end;raw:close();meta:close()
  local f=assert(io.open(OUTPUT..'profile-spans.jsonl','w'));for _,q in ipairs(spans)do f:write(json(q)..'\n')end;f:close()
  f=assert(io.open(OUTPUT..'profile-boundaries.jsonl','w'));for _,q in ipairs(boundaries)do f:write(json(q)..'\n')end;f:close()
  f=assert(io.open(OUTPUT..'profile-summary.json','w'));f:write(json({passed=true,wall_frames=pw,source_returns=sourceCalls,profile_first_wall=P.first_wall,profile_last_wall=P.last_wall,spans=#spans,boundaries=#boundaries,snapshots=#snaps,snapshot_bytes=ramBytes,aggregate=aggregate,no_emulated_writes=true,no_runtime_callback_registration=true,scope='Measured native function spans and read-only entry RAM/CPU/mapping capture only. Any later CPU counterfactual omits actual NMI/PPU unless separately modeled; not an optimization or lag acceptance.'}));f:close()
 end
 -- Registered before the untouched original1300 endFrame/stop callback.
 emu.addEventCallback(function()pw=pw+1;if pw==1300 then finish()end end,emu.eventType.endFrame)
end
