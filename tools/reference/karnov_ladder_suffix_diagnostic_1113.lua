-- Passive bounded diagnostic. Original controller return values are retained.
local navDiagnostic={control_calls=0,nav_calls=0,handled_calls=0,gates={},samples={}}
stockFifth.native_suffix_diagnostic=navDiagnostic
local function diagnosticGate(x,y,ground)
 local reason='admitted'
 if nav.done then reason='nav.done'
 elseif #pickups~=4 then reason='pickup-count'
 elseif r('WorldNumber')~=0 then reason='world'
 elseif r('LevelNumber')~=1 then reason='level'
 elseif r('AreaType')~=2 then reason='AreaType'
 elseif not armed then reason='armed'
 elseif kr(0xc0)~=0 then reason='bomb'
 elseif nav.stage=='unstarted'then
  if x>=416 then reason='would-bypass'
  elseif x<351 or x>359 then reason='x-range'
  elseif not ground then reason='ground'
  elseif y<160 then reason='y-range'end
 end
 return{frame=frame,epoch=epoch,x=x,y=y,ground=ground,pickups=#pickups,
  world=r('WorldNumber'),level=r('LevelNumber'),AreaType=r('AreaType'),area_offset=r('AreaAddrsLOffset'),
  armed=armed,bomb=kr(0xc0),nav_done=nav.done,nav_stage=nav.stage,gate=reason,
  nav_bypassed=nav.bypassed,routePhase=routePhase,routeAge=routeAge,
  early_stage=early.stage,fifth_stage=stockFifth.stage,undergroundReady=undergroundReady,
  native_pad=r('SavedJoypadBits'),pad1=emu.read(DIAG_PAD1,emu.memType.nesDebug),
  native_state=r('Player_State'),native_dy=r('Player_Y_Speed'),
  source_flags=kr(0x62),source_held=kr(0x1b),source_pressed=kr(0x21)}
end
local function diagnosticActors()
 local list={};for i=0,5 do list[#list+1]=actor(i)end;return list
end
local originalNativeSuffix=nativeSuffixControl
nativeSuffixControl=function(x,y,ground,item)
 local q=diagnosticGate(x,y,ground)
 navDiagnostic.nav_calls=navDiagnostic.nav_calls+1
 navDiagnostic.gates[q.gate]=(navDiagnostic.gates[q.gate]or 0)+1
 local handled,pad=originalNativeSuffix(x,y,ground,item)
 q.handled=handled;q.returned_pad=pad;q.after_done=nav.done;q.after_stage=nav.stage
 navDiagnostic.last_nav=q
 if handled then navDiagnostic.handled_calls=navDiagnostic.handled_calls+1 end
 if nav.bypassed and not navDiagnostic.first_bypass then navDiagnostic.first_bypass=q end
 if nav.done and not navDiagnostic.first_done then navDiagnostic.first_done=q end
 return handled,pad
end
local originalDiagnosticControl=control
control=function(...)
 local x,y=wx(),r('Player_Y_Position')
 if #pickups>=4 then
  navDiagnostic.control_calls=navDiagnostic.control_calls+1
  navDiagnostic.last_control=diagnosticGate(x,y,r('Player_State')==0)
  navDiagnostic.min_x=math.min(navDiagnostic.min_x or x,x);navDiagnostic.max_x=math.max(navDiagnostic.max_x or x,x)
 end
 local pad=originalDiagnosticControl(...)
 if #pickups>=4 then navDiagnostic.requested_pad=pad end
 return pad
end
emu.addEventCallback(navGuard(function()
 if not game or #pickups~=4 or r('WorldNumber')~=0 or r('LevelNumber')~=1 then return end
 local x=wx()
 if x<351 or x>359 then navDiagnostic.stall_frames=0;navDiagnostic.stall_x=nil;return end
 if x==navDiagnostic.stall_x then navDiagnostic.stall_frames=navDiagnostic.stall_frames+1
 else navDiagnostic.stall_x=x;navDiagnostic.stall_frames=1 end
 local q=diagnosticGate(x,r('Player_Y_Position'),r('Player_State')==0)
 q.requested_pad=navDiagnostic.requested_pad;q.actors=diagnosticActors()
 navDiagnostic.wall_first=navDiagnostic.wall_first or q;navDiagnostic.wall_last=q
 if navDiagnostic.stall_frames%15==0 then
  navDiagnostic.samples[#navDiagnostic.samples+1]=q
  if #navDiagnostic.samples>12 then table.remove(navDiagnostic.samples,1)end
 end
 if navDiagnostic.stall_frames>=180 then
  finish(false,'passive-diagnostic-wall-stall180')
 end
end),emu.eventType.endFrame)
