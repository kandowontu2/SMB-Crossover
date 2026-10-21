-- Real draw-helper calls, independent record filtering and cycle measurements.
-- Two explicit RAM-pose receipts exercise mutable data; these are render
-- fixtures, not level-progress evidence. Normal source poses remain untouched.
local frame,pending,returnPC=0,nil,nil
local depth,interruptStart,interruptCycles=0,0,0
local rows={warm={},cold={},bank={},ram={}}
local checks,ramChecks=0,0
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(n,v,i)emu.write(assert(L[n],n)+(i or 0),v%256,emu.memType.nesDebug)end
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function write(a,v)emu.write(a,v%256,emu.memType.nesDebug)end
local function cycles()return emu.getState()['cpu.cycleCount']end
local function interrupt()if depth==0 then interruptStart=cycles()end;depth=depth+1 end
local function resume()depth=depth-1;if depth==0 then interruptCycles=interruptCycles+cycles()-interruptStart end end
emu.addMemoryCallback(interrupt,emu.callbackType.exec,L.NonMaskableInterrupt)
emu.addMemoryCallback(resume,emu.callbackType.exec,L.NonMaskableInterrupt_RTI)
emu.addMemoryCallback(interrupt,emu.callbackType.exec,L.IrqScrollSplit)
emu.addMemoryCallback(resume,emu.callbackType.exec,L.IrqScrollSplit_RTI)
emu.addMemoryCallback(function()
 if frame<600 or depth~=0 or r('CurrentBank')%128~=10 then return end
 assert(not pending,'Filter calls do not nest')
 local kind='warm'
 if frame>=800 and frame<850 then w('OutlineSourceHi',0);for i=0,3 do w('OutlineTinyHi',0,i)end;kind='cold'end
 if frame>=875 and frame<925 then w('OutlineSourceBank',r('CurrentBankC')~1);for i=0,3 do w('OutlineTinyBank',r('CurrentBankC')~1,i)end;kind='bank'end
 if frame>=950 and frame<956 then
  kind='ram';local p=L.OutlinePoseBuffer+96
  local bytes={12,2,0,0,0,4,4,8,0,6,1,16,frame%32}
  for i,v in ipairs(bytes)do write(p+i-1,v)end
  w('R0',p%256);w('R1',math.floor(p/256))
 end
 local source=r('R0')+256*r('R1');local count=read(source)
 assert(count>0 and count<129 and count%4==0,'Valid actual or authored render record')
 local expected={}
 for i=0,count-1,4 do
  if read(source+2+i)&4==0 then for j=1,4 do expected[#expected+1]=read(source+i+j)end end
 end
 local s=emu.getState();local sp=s['cpu.sp']
 local pc=read(0x100+(sp+1)%256)+256*read(0x100+(sp+2)%256)+1
 if not returnPC then
  returnPC=pc
  emu.addMemoryCallback(function()
   if not pending or depth~=0 or emu.getState()['cpu.sp']~=pending.sp+2 then return end
   local p=pending
   local result=r('R0')+256*r('R1')
   assert(result>=L.OutlinePoseBuffer and result+#p.expected<=L.OutlinePoseBuffer+128,'Returned record stays inside reserved output buffer')
   assert(read(result)==#p.expected,'Filtered byte count matches independent mask removal')
   for i,v in ipairs(p.expected)do assert(read(result+i)==v,'Filtered tile/attribute/offset byte matches source at'..i)end
   if p.kind=='ram'then assert(r('OutlineSourceHi')==0,'Mutable RAM pose invalidates the immutable cache');for i=0,3 do assert(r('OutlineTinyHi',i)==0,'Mutable RAM invalidates every small-pose cache slot')end;ramChecks=ramChecks+1 end
   rows[p.kind][#rows[p.kind]+1]=cycles()-p.start-(interruptCycles-p.interrupts)
   checks=checks+1;pending=nil
  end,emu.callbackType.exec,pc)
 end
 assert(pc==returnPC,'Stable helper return trampoline')
 pending={sp=sp,expected=expected,kind=kind,start=cycles(),interrupts=interruptCycles}
end,emu.callbackType.exec,L.PlayerRemoveOutlines)
emu.addEventCallback(function()emu.setInput({right=frame==80 or frame==100,start=frame==200},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame>=550 then
  assert(r('SelectedCharacter')==2 and r('PlayerOutlinesOff')==1,'Actual selected Samus uses the default-off preference')
  for i=0,5 do w('Enemy_Flag',0,i)end
 end
 if frame==1000 then
  assert(checks>250 and ramChecks>=3,'Warm, cold, bank-key and mutable-pose receipts were exercised')
  local function mean(a)local total=0;for _,v in ipairs(a)do total=total+v end;assert(#a>0,'Profile has samples');return total/#a end
  local warm,cold,bank=mean(rows.warm),mean(rows.cold),mean(rows.bank)
  assert(warm<cold*.35 and bank>cold*.8,'Cached static pose removes repeated filtering; a changed bank key rebuilds it')
  print(string.format('PASS outline cache: %d exact-byte real draws, %d mutable RAM receipts; helper cycles warm%.1f cold%.1f bank-key-miss%.1f',checks,ramChecks,warm,cold,bank));emu.stop(0)
 end
end,emu.eventType.endFrame)
