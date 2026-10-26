-- Observe real accepted returns and source INC/DEC writes. The previous
-- entry-only count is retained separately; no game state is changed here.
local function riseExpected(b,a)
 if not b.accepted then
  assert(a.phase==b.phase and a.state==b.state and a.y==b.y,'Rejected/frozen rise preserves source state')
  return false
 end
 local move=b.phase==2
 assert(a.phase==(b.phase+1)%3,'Real source rise phase wraps every three accepted updates')
 assert(a.y==(b.y-(move and 1 or 0))%256,'Real source rise moves exactly one pixel on phase2')
 local state=b.state+(move and 1 or 0);if state>=17 then state=128 end
 assert(a.state==state,'Real source state17 commits mature128')
 return true
end
local function riseSnapshot()
 local s=emu.getState()
 return{phase=r('InvRisePhase',5),state=r('Enemy_State',5),y=r('Enemy_Y_Position',5),timer=r('TimerControl'),owner=r('InvPickupOwner',5),item=r('InvPickup',5),pc=s['cpu.pc'],sp=s['cpu.sp'],frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],cycle=s['ppu.cycle'],update=updates,wall=wall}
end
hook('DwRisePickup',function()
 if not entered or phase~='collect'or not current or emu.getState()['cpu.x']~=5 then return end
 local owner=current;local b=riseSnapshot()
 -- This reproduces the old entry predicate for diagnosis, even if a callback
 -- is revisited before its instruction really executes. It is not the clock.
 if current.item~=nil and current.item>0 and b.timer==0 then current.riseEntryCount=(current.riseEntryCount or 0)+1 end
 b.accepted=b.owner==9 and b.item>0 and(b.item<252 or b.item==254)and b.timer==0 and b.state>0 and b.state<128
 event('actual-rise-entry',b)
 onReturn('delivery-actual-rise-return',function()
  assert(current==owner,'Real rise return retains current physical actor')
  local a=riseSnapshot();local accepted=riseExpected(b,a)
  if accepted then
   if current.riseCalls==0 then current.riseStartY=b.y end
   current.riseCalls=current.riseCalls+1
  end
  event('actual-rise-full-return',{before=b,after=a,accepted=accepted,actual_accepted_returns=current.riseCalls,old_predicate_entries=current.riseEntryCount or 0})
 end)
end)
local function sourceRiseWrite(kind,base,op)
 emu.addMemoryCallback(function(_,value)
  if not entered or phase~='collect'or not current then return end
  local s=emu.getState();local pc=s['cpu.pc']
  if bank(op.address)~=op.bank or(pc~=op.address and pc~=op.address+#op.bytes)then return end
  for i,v in ipairs(op.bytes)do assert(emu.read(op.address+i-1,emu.memType.nesDebug)==v,'Actual source rise writer instruction')end
  local before=r(base,5)
  -- 6502 RMW may publish its unchanged dummy write; count only the genuine
  -- state-changing bus write. Keep both raw observations in the event log.
  local changing=value~=before
  if changing then
   assert(value==(before+(kind=='phase'and 1 or-1))%256,'Actual source rise write arithmetic')
   local field=kind=='phase'and'risePhaseWrites'or'riseYWrites';current[field]=(current[field]or 0)+1
  end
  event('actual-rise-source-write',{kind=kind,before=before,value=value,changing=changing,pc=pc,writer=op.address,frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],cycle=s['ppu.cycle'],old_predicate_entries=current.riseEntryCount or 0,accepted_returns=current.riseCalls})
 end,emu.callbackType.write,L[base]+5)
end
sourceRiseWrite('phase','InvRisePhase',C.rise_writers.phase)
sourceRiseWrite('y','Enemy_Y_Position',C.rise_writers.y)
