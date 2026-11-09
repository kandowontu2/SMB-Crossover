-- An engine task switch does not identify the OAM page's producer. Observe
-- actual draw returns and actual whole-ring clears across the handoff.
do
 local generation,lastClear=0,nil
 local function sprite_bytes(page,slot)
  local a=page*256+slot
  return {read(a),read(a+1),read(a+2),read(a+3)}
 end
 local function equal(a,b)
  return a[1]==b[1] and a[2]==b[2] and a[3]==b[3] and a[4]==b[4]
 end
 local function expected(p)
  return {(p.y-1)&255,C.pose_tiles[p.pose+1],C.pose_attrs[p.pose+1],p.x}
 end
 emu.addMemoryCallback(guard(function()
  if not injuryOamScope() or not valid(injuryOamClear) then return end
  for slot=0,252,4 do check(read(0x200+slot)==0xf8,'Actual clear hides all 64 OAM sprites') end
  generation=generation+1
  lastClear={frame=frame,counter=r('FrameCounter'),generation=generation}
  latestDraw=nil
  injury.oam_clears=generation
 end),emu.callbackType.exec,injuryOamClear.pc)
 injuryOamDraw=function(p)
  if not injuryOamScope() then return end
  p.generation=generation
  p.bytes=sprite_bytes(2,p.slot)
  check(equal(p.bytes,expected(p)),'Actual Mini draw writes its exact one-part OAM packet')
  if p.engine==10 then injury.last_native_oam_draw=p end
 end
 injuryOamDma=function(page)
  if not injuryOamScope() then return end
  local p=latestDraw
  local counter=r('FrameCounter')
  check(page==2,'Native OAM DMA publishes the observed sprite page')
  if p and p.generation then
   check(p.generation==generation,'DMA packet belongs to the most recent OAM generation')
   check(equal(sprite_bytes(page,p.slot),p.bytes),'Actual OAM DMA publishes the complete observed Mini packet')
   injury.observed_injury_dmas=(injury.observed_injury_dmas or 0)+1
  elseif not p then
   check(lastClear and lastClear.generation==generation,'Absent Mini draw has a witnessed whole-ring clear')
   injury.cleared_without_mini_draw=(injury.cleared_without_mini_draw or 0)+1
  end
  if r('GameEngineSubroutine')~=8 or injury.first_source_step or injury.handoff_dma then return end
  check(injury.visible and #injury.native_steps==39,'Native injury and lift crossing precede handoff DMA')
  check(p and p.engine==10 and p.generation==generation,
   'Mode 8 handoff DMA still publishes the prior actual native injury draw')
  local stale=injury.preinjury_draw
  local staleActual=sprite_bytes(page,stale.slot)
  check(not equal(staleActual,expected(stale)),'The preinjury source draw is genuinely stale at handoff DMA')
  injury.handoff_dma={frame=frame,counter=counter,page=page,source=updates,
   draw_frame=p.frame,draw_counter=p.counter,draw_engine=p.engine,slot=p.slot,
   actual=sprite_bytes(page,p.slot),expected=p.bytes,
   stale_slot=stale.slot,stale_expected=expected(stale),stale_actual=staleActual}
 end
end
