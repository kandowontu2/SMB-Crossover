-- Extend the existing native route without changing input during mode 10.
do
 local firstDrawPacket
 local function after_contact()
  return phase=='fullstage' and injury.force and r('SelectedCharacter')==41
   and r('OperMode')==1 and r('WorldNumber')==0 and r('LevelNumber')==0
 end
 local function first_source_frame()
  local q=injury.first_source_step
  return q and q.frame==frame and q.counter==r('FrameCounter')
 end
 emu.addMemoryCallback(guard(function()
  if not after_contact() or injury.fallback or not valid(injuryFallback) then return end
  check(r('PlayerStatus')==1 and r('GameEngineSubroutine')==8,
   'Actual C3 injury leaf receives the earned powered owner')
  injury.fallback={frame=frame,pc=injuryFallback.pc,old=r('PlayerStatus')}
 end),emu.callbackType.exec,injuryFallback.pc)
 emu.addMemoryCallback(guard(function()
  if not after_contact() or injury.status_store or not valid(injuryStatusStore) then return end
  local state=emu.getState()
  check(injury.fallback and injury.fallback.frame==frame and r('PlayerStatus')==1,
   'Native status store follows the authenticated fallback')
  check(state['cpu.a']==0 and state['cpu.ps']&1==0,
   'Actual native fallback returns A=0 and leaves the injury unhandled')
  injury.status_store={frame=frame,pc=injuryStatusStore.pc,old=r('PlayerStatus'),value=state['cpu.a'],carry=state['cpu.ps']&1}
 end),emu.callbackType.exec,injuryStatusStore.pc)
 local step=C.hooks.MiniStep
 emu.addMemoryCallback(guard(function()
  if not after_contact() or not active() or not valid(step) then return end
  if injury.first_source_step then
   check(not first_source_frame(),'One source step at the first resumed native update')
   return
  end
  check(injury.visible and #injury.native_steps==39,'Source movement resumes after the native injury window')
  local tier,top=ram(0xc244),ram(0xc256)
  check(r('PlayerStatus')==0 and tier==0 and top==1,'HostMain syncs the small source tier before the first step')
  injury.first_source_step={frame=frame,source=updates,counter=r('FrameCounter'),tier=tier,top=top}
 end),emu.callbackType.exec,step.pc)
 injuryBoxReturn=function(p,b)
  if not first_source_frame() or injury.first_source_box then return end
  local ulx,uly,lrx,lry=read(b),read(b+1),read(b+2),read(b+3)
  check(ram(0xc244)==0 and ram(0xc256)==1 and ((lrx-ulx)&255)==5 and ((lry-uly)&255)==6,
   'First resumed native collision box uses the small 6 by 7 source body')
  injury.first_source_box={frame=frame,counter=r('FrameCounter'),width=6,height=7,
   upper_left={ulx,uly},lower_right={lrx,lry},native_x=p.x,native_y=p.y}
 end
 injuryDrawReturn=function(p)
  if not injury.first_source_step or not active() then return end
  local tile=C.pose_tiles[p.pose+1]
  local small=p.pose<39 and tile and tile>0 and tile<=31 and ram(0xc315)==1
  if small then p.injury_small_source=true end
  if first_source_frame() and not injury.first_source_draw then
   check(small,'First resumed source pose actually emits the small donor tile')
   firstDrawPacket=p
   injury.first_source_draw={frame=frame,counter=r('FrameCounter'),pose=p.pose,tile=tile,slot=p.slot,x=p.x,y=p.y}
  end
 end
 injuryDma=function(p,a,tile,attr)
  if not p.injury_small_source or injury.first_small_dma then return end
  check(injury.first_source_update and read(a+1)==tile and read(a+2)==attr,
   'A normal OAM DMA publishes the resumed small source pose')
  injury.first_small_dma={frame=frame,pose=p.pose,tile=tile,slot=p.slot,
   first_draw_packet=p==firstDrawPacket,chr4=emu.getState()['mapper.chrBanks4']}
 end
end
