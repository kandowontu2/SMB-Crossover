-- Passive actual-ROM scope timings. Runs under the ordinary roster harness.
-- No memory/register writes, save states, controller changes or synthetic actors.
local C=assert(ORDINARY_PROFILE)
local H,A=C.hooks,C.ram
local frame,poll,nmi,irq=0,0,0,0
local calls,returns={},{}
local f=assert(io.open(ROSTER_CONFIG.out..'ordinary-profile.jsonl','w'))
local function r(n,i)return emu.read(assert(A[n],n)+(i or 0),emu.memType.nesDebug)end
local function physical(pc)
 local p=emu.convertAddress(pc)
 return p and p.memType==emu.memType.nesPrgRom and p.address//8192 or -1
end
local function snapshot()
 local s=emu.getState()
 return {frame=frame,poll=poll,cycle=s['cpu.cycleCount'],sp=s['cpu.sp'],
  nmi=nmi,irq=irq,lag=r('NmiSkipped'),world=r('WorldNumber'),level=r('LevelNumber'),
  x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),
  state=r('Player_State'),engine=r('GameEngineSubroutine'),skip=r('ShouldSkipDrawSprites')}
end
local function hook(n,fn)
 local h=assert(H[n],n)
 emu.addMemoryCallback(function()
  if physical(h.address)~=h.physical_bank then return end
  for j,v in ipairs(h.bytes)do
   assert(emu.read(h.address+j-1,emu.memType.nesDebug)==v,'Actual ordinary profile entry8 '..n)
  end
  fn()
 end,emu.callbackType.exec,h.address)
end
local function enabled()
 return frame>=C.start_frame and frame<C.stop_frame and r('OperMode')==1
  and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8
end
local function emit(q,z)
 local t={name=string.format('%q',q.name),frame=q.entry.frame,poll=q.entry.poll,
  world=q.entry.world,level=q.entry.level,x=q.entry.x,y=q.entry.y,state=q.entry.state,
  cycles=z.cycle-q.entry.cycle,frame_delta=z.frame-q.entry.frame,
  nmi=z.nmi-q.entry.nmi,irq=z.irq-q.entry.irq,lag=(z.lag-q.entry.lag)&255,
  skip=q.entry.skip,return_frame=z.frame,return_cycle=z.cycle,
  entry_bank=q.entry_bank,return_bank=q.bank,entry_sp=q.entry.sp,return_sp=z.sp}
 local a={}
 for k,v in pairs(t)do a[#a+1]=string.format('%q',k)..':'..tostring(v)end
 table.sort(a);f:write('{'..table.concat(a,',')..'}'..string.char(10))
end
local function begin(n)
 if not enabled()then return end
 local e=snapshot()
 local pc=(emu.read(0x100+(e.sp+1)%256,emu.memType.nesDebug)
  +256*emu.read(0x100+(e.sp+2)%256,emu.memType.nesDebug)+1)%65536
 local guard={}
 for j=0,7 do guard[j+1]=emu.read(pc+j,emu.memType.nesDebug)end
 local q={name=n,entry=e,entry_bank=H[n].physical_bank,pc=pc,
  sp=(e.sp+2)%256,bank=physical(pc),guard=guard}
 assert(q.bank>=0,'Only actual ROM callers are timed')
 calls[#calls+1]=q
 if returns[pc]then return end
 returns[pc]=true
 emu.addMemoryCallback(function()
  local z=snapshot()
  -- Tail-called scopes can have the same genuine parent and return together.
  for i=#calls,1,-1 do
   local c=calls[i]
   if c.pc==pc and c.sp==z.sp and c.bank==physical(pc)then
    for j,v in ipairs(c.guard)do
     assert(emu.read(pc+j-1,emu.memType.nesDebug)==v,'Actual ordinary profile return8 '..c.name)
    end
    emit(c,z);table.remove(calls,i)
   end
  end
 end,emu.callbackType.exec,pc)
end
hook('NMI',function()nmi=nmi+1 end)
hook('IRQ',function()irq=irq+1 end)
for n in pairs(H)do if n~='NMI'and n~='IRQ'then hook(n,function()begin(n)end)end end
emu.addEventCallback(function()poll=poll+1 end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 frame=frame+1
 if frame%60==0 then f:flush()end
 if frame==C.stop_frame+30 then
  assert(#calls==0,'All sampled ordinary scopes returned before profile window closes')
  f:flush()
 end
end,emu.eventType.endFrame)
return dofile(C.base_policy)
