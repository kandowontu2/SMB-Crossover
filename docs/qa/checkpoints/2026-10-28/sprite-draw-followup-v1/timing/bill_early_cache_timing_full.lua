-- Bounded, read-only timing during a full controller-only Bill route.
-- Every memory callback is registered at startup. No runtime registration.
local P=assert(BILL_PASSIVE_TIMING)
local wall,serial,depth=0,0,0
local calls,isrs,aggregate={},{},{}
local bucket={}
local rows,bytes=0,0
local first=P.first_frame
local csv=assert(io.open(P.output..'bill-timing.csv','w'))
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function r(name,i)return read(assert(P.ram[name],name)+(i or 0))end
local function bank(pc)
 if pc<0x8000 then return -1 end
 local q=emu.convertAddress(pc);return q and q.address//8192 or -1
end
local function valid(h)
 local actual=bank(h.pc);local allowed=false
 for _,b in ipairs(h.banks)do if b==actual then allowed=true end end
 if not allowed then return false end
 for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Pinned timing hook '..h.name)end
 return true
end
local function active()
 return r('SelectedCharacter')==3 and r('BillVariant')==0
  and r('CrossoverBehaviorVersion')==1 and r('OperMode')==1
  and r('OperMode_Task')==3 and r('WorldNumber')==0 and r('LevelNumber')==0
  and r('GameEngineSubroutine')==8
end
local function tracking()return wall>=first-2 and wall<P.last_frame and active()end
local function newBucket()
 local b={nmi=0,nmi_cycles=0,irq=0,irq_cycles=0,dmas=0}
 for _,h in ipairs(P.functions)do b[h.name]={calls=0,inclusive=0,exclusive=0,max=0,prewindow=0}end
 return b
end
bucket=newBucket()
local function json(v)
 if type(v)=='table'then
  local q={};if #v>0 then for _,x in ipairs(v)do q[#q+1]=json(x)end;return'['..table.concat(q,',')..']'end
  for k,x in pairs(v)do q[#q+1]=string.format('%q',tostring(k))..':'..json(x)end
  table.sort(q);return'{'..table.concat(q,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)
 elseif v==nil then return'null'else return tostring(v)end
end
local function write(line)
 assert(rows<P.row_cap and bytes+#line+1<=P.byte_cap,'Bounded timing CSV')
 csv:write(line..'\n');csv:flush();rows=rows+1;bytes=bytes+#line+1
end
local columns={'endframe_count','ppu_frame','ppu_line','ppu_dot','cpu_cycle','loops_closed','x','y','state','buttons','weapon',
 'ordinary_shots','advanced_shots','other_shots','enemy_slots','timer','powerup','refill',
 'nmi_skipped','lag_counter_delta','skip_draw','nmi_closed','nmi_elapsed','irq_closed','irq_elapsed','dmas'}
for _,h in ipairs(P.functions)do for _,k in ipairs({'calls','inclusive','exclusive','max','prewindow'})do columns[#columns+1]=h.name..'_'..k end end
write(table.concat(columns,','))
local function returnOwner(ret,name)
 if ret>=P.smc_start and ret<=P.smc_end then
  assert(read(ret-3)==0x20,'Actual RAM return follows JSR')
  local operand=read(ret-2)+256*read(ret-1)
  assert(P.smc_targets[name][tostring(operand)],'Unbound actual timing SMC target '..name..' '..operand)
  return {pc=ret,bank=-1,call_pc=ret-3,operand=operand,kind='actual_SMC_JSR'}
 end
 local alternatives=assert(P.source_callers[name][tostring(ret)],'Unbound actual timing return '..name..' '..ret)
 local actual=bank(ret)
 for _,a in ipairs(alternatives)do
  if a.bank==actual and read(ret-3)==a.bytes[1]and read(ret-2)==a.bytes[2]and read(ret-1)==a.bytes[3]then
   return {pc=ret,bank=actual,call_pc=ret-3,operand=a.bytes[2]+256*a.bytes[3],kind='pinned_ROM_JSR'}
  end
 end
 error('Actual timing caller bank/opcode differs at '..ret)
end
local function closeReturns(pc)
 if #calls==0 then return end
 local s=emu.getState()
 while #calls>0 do
  local c=calls[#calls]
  if c.ret~=pc or c.return_sp~=s['cpu.sp']or c.return_bank~=bank(pc)or c.depth~=depth then break end
  calls[#calls]=nil
  local elapsed=s['cpu.cycleCount']-c.start
  local cpu=elapsed-c.interrupt
  assert(cpu>=0 and c.child<=cpu,'Disjoint child/interrupt timing')
  local parent=calls[#calls]
  if parent and parent.depth==c.depth then parent.child=parent.child+cpu end
  local a=aggregate[c.name]or{calls=0,inclusive=0,exclusive=0,max=0,callers={},interrupt_depths={}}
  a.calls=a.calls+1;a.inclusive=a.inclusive+cpu;a.exclusive=a.exclusive+cpu-c.child;a.max=math.max(a.max,cpu)
  local key=c.owner.kind..':'..c.owner.bank..':'..c.owner.call_pc..':'..c.owner.operand
  a.callers[key]=(a.callers[key]or 0)+1;aggregate[c.name]=a
  local d=tostring(c.depth);a.interrupt_depths[d]=(a.interrupt_depths[d]or 0)+1
  if wall+1>=first and wall+1<=P.last_frame then
   local b=bucket[c.name];b.calls=b.calls+1;b.inclusive=b.inclusive+cpu
   b.exclusive=b.exclusive+cpu-c.child;b.max=math.max(b.max,cpu)
   if c.frame<first then b.prewindow=b.prewindow+1 end
  end
 end
end
-- Complete current ROM callsite alternatives and the genuine SMC span are
-- fixed before execution. Actual entry checks stack, bank and JSR bytes.
for ret in pairs(P.returns)do emu.addMemoryCallback(closeReturns,emu.callbackType.exec,tonumber(ret))end
emu.addMemoryCallback(closeReturns,emu.callbackType.exec,P.smc_start,P.smc_end)
for _,h in ipairs(P.functions)do
 emu.addMemoryCallback(function()
  if not tracking()or not valid(h)then return end
  local s=emu.getState();local sp=s['cpu.sp']
  local ret=(read(0x100+(sp+1)%256)+256*read(0x100+(sp+2)%256)+1)%65536
  local top=calls[#calls]
  -- An ISR may resume a pre-instruction callback at its exact old entry.
  if top and top.name==h.name and top.entry_sp==sp and top.ret==ret and top.depth==depth then return end
  serial=serial+1
  calls[#calls+1]={id=serial,name=h.name,entry_sp=sp,return_sp=(sp+2)%256,
   ret=ret,return_bank=bank(ret),owner=returnOwner(ret,h.name),start=s['cpu.cycleCount'],
   frame=wall+1,interrupt=0,child=0,depth=depth}
 end,emu.callbackType.exec,h.pc)
end
for _,kind in ipairs({'NMI','IRQ'})do
 local entry=P.interrupts[kind];local leave=P.interrupts[kind..'_return']
 emu.addMemoryCallback(function()
  if not(tracking()or #calls>0 or #isrs>0)or not valid(entry)then return end
  local s=emu.getState();local owners={}
  for _,c in ipairs(calls)do if c.depth==depth then owners[#owners+1]=c end end
  local sp=s['cpu.sp']
  isrs[#isrs+1]={kind=kind,start=s['cpu.cycleCount']-7,owners=owners,sp=sp,
   interrupted_pc=read(0x100+(sp+2)%256)+256*read(0x100+(sp+3)%256)}
  depth=depth+1
 end,emu.callbackType.exec,entry.pc)
 emu.addMemoryCallback(function()
  if #isrs==0 or not valid(leave)then return end
  local s=emu.getState();local q=isrs[#isrs]
  assert(q.kind==kind and s['cpu.sp']==q.sp,'Timing ISR stack/owner balance')
  -- This is the genuine pre-RTI instruction: include hardware entry7 andRTI6.
  local elapsed=s['cpu.cycleCount']+6-q.start
  for _,c in ipairs(q.owners)do c.interrupt=c.interrupt+elapsed end
  if wall+1>=first and wall+1<=P.last_frame then
   local k=kind=='NMI'and'nmi'or'irq';bucket[k]=bucket[k]+1;bucket[k..'_cycles']=bucket[k..'_cycles']+elapsed
  end
  isrs[#isrs]=nil;depth=depth-1
 end,emu.callbackType.exec,leave.pc)
end
emu.addMemoryCallback(function()
 if wall+1>=first and wall+1<=P.last_frame and valid(P.dma_complete)then bucket.dmas=bucket.dmas+1 end
end,emu.callbackType.exec,P.dma_complete.pc)
local previousLag
emu.addEventCallback(function()
 wall=wall+1
 local lag=r('NmiSkipped');local lagDelta=previousLag and(lag-previousLag)%256 or 0;previousLag=lag
 if wall>=first and wall<=P.last_frame then
  local ordinary,advanced,other,enemies=0,0,0,0
  for i=0,9 do local t=r('RgShotType',i)
   if t>=1 and t<=8 then ordinary=ordinary+1 elseif t>=32 and t<=46 then advanced=advanced+1 elseif t~=0 then other=other+1 end
  end
  for i=0,5 do if r('Enemy_Flag',i)~=0 then enemies=enemies+1 end end
  local s=emu.getState()
  assert(s['ppu.frameCount']==wall,'Actual physical frame matches pinned prefix epoch')
  if wall==first then assert(active(),'Actual Bill Hard 1-1 timing window')end
  local line={wall,s['ppu.frameCount'],s['ppu.scanline'],s['ppu.cycle'],s['cpu.cycleCount'],bucket.GameLoop.calls,
   r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position'),r('Player_State'),
   r('SavedJoypadBits'),r('InvSelected',3),ordinary,advanced,other,enemies,
   r('TimerControl'),r('GuestPowerupActive'),r('InvRefill'),lag,lagDelta,r('ShouldSkipDrawSprites'),
   bucket.nmi,bucket.nmi_cycles,bucket.irq,bucket.irq_cycles,bucket.dmas}
  for _,h in ipairs(P.functions)do local b=bucket[h.name]
   for _,k in ipairs({'calls','inclusive','exclusive','max','prewindow'})do line[#line+1]=b[k]end
  end
  write(table.concat(line,','))
 end
 bucket=newBucket()
 if wall==P.last_frame then
  assert(rows==P.last_frame-first+2,'Exact bounded timing row count')
  csv:close()
  local open={};for _,c in ipairs(calls)do
   assert(c.frame>=wall-4,'Unclosed old function span is an observer error, not a censored sample')
   open[#open+1]={name=c.name,start=c.start,frame=c.frame,depth=c.depth,entry_sp=c.entry_sp,return_pc=c.ret,owner=c.owner}
  end
  for _,name in ipairs({'GameLoop','RosterMovement','PlayerBGCollision','RosterWeapons','RemainingWeapons','DrawAllMetasprites','AudioUpdate'})do
   assert(aggregate[name]and aggregate[name].calls>0,'Required actual timing component '..name)
  end
  local q={timing_observation_complete=true,native_prefix_only=false,ROM_sha256=P.ROM_sha256,
   frames=wall,first_frame=first,last_frame=P.last_frame,csv_rows=rows,csv_bytes=bytes,
   complete_span_aggregates_include_warmup_from_frame=first-1,aggregate=aggregate,
   open_spans_censored=open,open_interrupts=#isrs,no_game_writes=true,
   no_runtime_callback_registration=true,
   scope='Completion-bucketed spans, not per-frame execution integrals. Inclusive/exclusive columns must not be added together; NMI gross includes nestedIRQ while AudioCPU excludesIRQ. Pending spans are censored. Only timing collection ends at3560. The unchanged route harness continues through controlled1-2 or its original8000-frame bound. This timing summary alone is not a route pass or matched-call FPS claim.'}
  local text=json(q)..'\n';assert(#text<=65536,'Bounded timing summary')
  local f=assert(io.open(P.output..'bill-timing-summary.json','w'));f:write(text);f:close()
 end
end,emu.eventType.endFrame)
