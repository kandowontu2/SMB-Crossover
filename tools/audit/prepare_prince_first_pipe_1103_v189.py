"""Prepare a short, controller-only current-Prince first-pipe qualification.

Keeps the passed187 header/body/DMA/reservation observers. Starts at the first
real cold entrance, never at a manually repositioned actor. No emulator/ROM
or game-state writes. Root owns execution and interpretation of results.
"""
from pathlib import Path
import json, re, sys
import prepare_prince_current_body_root_1103_v185 as P
from observe_chip_committed_write import lua

R = P.R
O = R / 'build/prince-first-pipe-1103-v189'
ROM = R / 'build/prince-body-current-candidate-root-1103-v186/prince-body-current.nes'
PIN = '199d89a4a1c7747946154b5f6c5b079f90b9292aff0831a49cbb4303a130820a'
PAYLOAD = R / 'build/prince-pose-reservation-1103-v185'
ORIGINAL_PREPARE = P.prepare


ROUTE = r'''
local pipeRoute={pipe={left=448,right=480,top=176},events={},injuries={},climb_modes={},running_jump={},first_pipe_cleared=false,source_controls_only=true,helpers_added=false}
local priorHP=5
local lastSampleCommit=-1
local jumpAttempted=false
local jumpAdmitted=false
local jumpStartCommit=nil
local jumpInitialY=nil
local jumpMinY=nil
local firstNaturalEnemy=nil
local function goomba()
 local best=nil
 for i=0,5 do
  local flag=ram(L.Enemy_Flag+i);local id=ram(L.Enemy_ID+i)
  local x=ram(L.Enemy_X_Position+i)+256*ram(L.Enemy_PageLoc+i)
  local y=ram(L.Enemy_Y_Position+i);local high=ram(L.Enemy_Y_HighPos+i)
  if flag~=0 and flag<128 and id==6 and high==1 and y>=160 and x>=wx()-16 then
   local q={slot=i,flag=flag,id=id,x=x,y=y,high=high,gap=x-wx(),state=ram(L.Enemy_State+i)}
   if not best or q.gap<best.gap then best=q end
  end
 end
 return best
end
local function routeEvent(tag,extra)
 local q=state();q.tag=tag;q.frame=frame;q.Main=admitted;q.original_advances=advances;q.enemy=goomba();q.extra=extra
 pipeRoute.events[#pipeRoute.events+1]=q
 require(#pipeRoute.events<=96,'Bounded first-pipe event summary')
end
local function nativeFloor()
 local foot=ps(0x84)+256*ps(0x85)
 return ram(0xa4)==1 and math.abs(r('Player_Y_Position')-176)<=2 and foot>=207 and foot<=211
end
'''


KEYS = r'''local function control_keys()
 if part=='travel'then return{'right'}
 elseif part=='run-jump'then if not jumpAdmitted then return{'right','a'}end;return{'right'}
 elseif part=='pipe-up'then
  if ps(0x618)==2 or ps(0x618)==6 or admitted-partCommit<64 then return{'up'}end
  return{'right','up','a','b'} -- Exact existing compiled v8 C9 fallback.
 elseif part=='pipe-over'then return{'right'}end
 return{}
end
'''


TICK = r'''local function controls_tick(finish)
 require(sourceActive()and r('OperMode')==1 and r('GameEngineSubroutine')==8,'Authenticated native stage retained')
 headers()
 require(r('NumberofLives')==initialLives,'First-pipe route retains native lives')
 local hp=ps(0x6cf)
 if hp~=priorHP then
  pipeRoute.injuries[#pipeRoute.injuries+1]={frame=frame,Main=admitted,old=priorHP,new=hp,state=state(),enemy=goomba()}
  priorHP=hp
 end
 require(hp>0 and hp<=5,'Real source HP remains alive; injuries are recorded without health seeds')
 require(frame-partFrame<3200 and admitted-partCommit<1000,'Bounded actual first-pipe phase')
 if not nativeFloor()then pipeRoute.minimum_nativeY=math.min(pipeRoute.minimum_nativeY or initialY,r('Player_Y_Position'))end
 local enemy=goomba()
 if enemy and not firstNaturalEnemy then firstNaturalEnemy=enemy;routeEvent('first-natural-Goomba',enemy)end
 if part=='first-render'then
  require(wx()==firstX,'Original neutral stillness before first body image')
  if not renderEvidence and lastDMA and frame>lastDMA.complete.host_frame and advanceReturns>=4 then
   renderEvidence=visibleEvidence(lastDMA);renderFrame=frame;writejson('render-evidence.json',renderEvidence)
   shot('prince-after-draw-DMA')
   require(lastDMA.writes==256 and lastDMA.exact,'Actual complete256byte hardware DMA')
   require(lastDMA.body_preserved and #lastDMA.hardware_body>0,'Real body draw survives native publication/DMA')
   require(renderEvidence.opaque_onscreen_pixels>0 and renderEvidence.within_first8_opaque_pixels>0,'Actual mapped body CHR contains onscreen first8 sprite pixels')
   completePart();beginPart('travel');routeEvent('fresh-native40-approach')
  end
 elseif part=='travel'then
  -- Original191 windup is about22Main/59native pixels before first lift.
  -- Start from a real distant parsed Goomba, never a38px latejump window.
  if not jumpAttempted and enemy and enemy.gap>=60 and enemy.gap<=120 and ps(0x616)==1 and ps(0x618)==1 and ps(0x617)>=6 and ps(0x617)<14 and ps(0x6c0)==0 then
   jumpAttempted=true;jumpAdmitted=false;jumpInitialY=r('Player_Y_Position');jumpMinY=jumpInitialY
   completePart();beginPart('run-jump');jumpStartCommit=admitted
   pipeRoute.running_jump.request=state();routeEvent('original-running-A-request',enemy)
  elseif wx()>=400 then
   completePart();beginPart('pipe-settle');routeEvent('neutral-before-pipe-Up')
  end
 elseif part=='run-jump'then
  jumpMinY=math.min(jumpMinY,r('Player_Y_Position'))
  if not jumpAdmitted and ps(0x616)==4 then
   jumpAdmitted=true;pipeRoute.running_jump.admission=state();pipeRoute.running_jump.admission_Main=admitted
   routeEvent('original-action4-admitted')
  end
  if (jumpAdmitted and admitted-jumpStartCommit>=16 and ps(0x616)==1 and ps(0x618)==1 and nativeFloor())or(not jumpAdmitted and admitted-jumpStartCommit>=32)then
   pipeRoute.running_jump.completed=state();pipeRoute.running_jump.minimum_nativeY=jumpMinY
   pipeRoute.running_jump.admitted=jumpAdmitted
   routeEvent(jumpAdmitted and 'original-running-jump-landed'or'original-running-A-not-admitted')
   completePart();beginPart(wx()>=400 and'pipe-settle'or'travel')
  end
 elseif part=='pipe-settle'then
  if ps(0x617)==15 and ps(0x618)==0 and ps(0x6c0)==0 then
   require(ps(0x615)==255,'Real pipe approach retains original right facing')
   require(wx()>=390 and wx()<448 and nativeFloor(),'Real neutral pipe approach remains supported before448')
   completePart();beginPart('pipe-up');routeEvent('source-idle15-mode0-Up-begin')
  end
 elseif part=='pipe-up'then
  local mode=ps(0x618)
  if (mode==2 or mode==6)and not pipeRoute.climb_modes[mode]then
   pipeRoute.climb_modes[mode]=state();routeEvent('original-climb-mode'..mode)
   if shots<3 then shot('prince-original-pipe-hang')end
  end
  if ps(0x616)==10 and not pipeRoute.climb_action10 then pipeRoute.climb_action10=state();routeEvent('original-climb-action10')end
  if mode~=2 and mode~=6 and ps(0x84)+256*ps(0x85)<=179 and r('Player_Y_Position')<=147 then
   require(next(pipeRoute.climb_modes)~=nil,'Pipe height reached through actual original ledge states2/6')
   completePart();beginPart('pipe-over');routeEvent('actual-top-of-first-pipe')
  end
 elseif part=='pipe-over'then
  if wx()>=496 and nativeFloor()and advances==advanceReturns and phase0==advances then
   pipeRoute.first_pipe_cleared=true;pipeRoute.terminal=state();routeEvent('actual-far-side-floor')
   require(backdropCalls>0 and statusCalls>0 and renderEvidence~=nil,'Actual backdrop/status/body consumers')
   require(reservationReads>0,'Actual native projectile/enemy OAM reservation reader reached')
   completePart();shot('prince-first-pipe-cleared')
   summary(true,'Actual originalUp first32pxpipe cleared and far-side floor landed; native lives retained, genuine HP injuries recorded')
   csv:close();finish()
  end
 end
end
'''


def build(output, rom, controller, refs, **kwargs):
    assert P.sha(rom) == PIN
    assert not kwargs.get('scope', '').endswith('landing')
    text = controller
    alias_names = ['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_PageLoc','Enemy_X_Position','Enemy_Y_Position','Enemy_Y_HighPos']
    labels = {n: int(a,16) for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$', rom.with_suffix('.lbl').read_text(), re.M)}
    aliases = {n:labels[n] for n in alias_names}
    anchor = '-- Controller-only source; Q is supplied by the hash-bound plan preparer.'
    assert text.count(anchor) == 1
    text = text.replace(anchor, 'Q.mode="Prince-original-first-pipe189";Q.maxFrames=8000\nfor n,a in pairs('+lua(aliases)+')do L[n]=a end\n'+anchor)
    old="source_action=ps(0x616),source_frame=ps(0x617),source_facing=ps(0x615)"
    assert text.count(old)==1
    text=text.replace(old,old+',source_mode=ps(0x618),source_A_lock=ps(0x6c0)')
    # Route locals precede summary; route helpers reference the later local
    # require only at runtime. Keep a forward declaration to avoid global use.
    anchor='local rows={}'
    assert text.count(anchor)==1
    text=text.replace(anchor,'local require\n'+ROUTE+'\n'+anchor)
    old="local function require(v,why)if not v then summary(false,why);error(why)end end"
    assert text.count(old)==1
    text=text.replace(old,"require=function(v,why)if not v then if shots<4 then shot('prince-first-pipe-negative')end;summary(false,why);error(why)end end")
    old='render_evidence=renderEvidence~=nil,native_reservation_reads=reservationReads,full_stage=false'
    assert text.count(old)==1
    text=text.replace(old,'first_pipe_route=pipeRoute,'+old)
    begin=text.index('local function control_keys()');end=text.index('local function completePart()',begin)
    text=text[:begin]+KEYS+text[end:]
    begin=text.index('local function controls_tick(finish)');end=text.index('\nlocal log=assert(',begin)
    text=text[:begin]+TICK+text[end:]
    # Record the newly relevant original modes alongside the retained phase
    # CSV; one aggregate source CSV remains well below capture limits.
    text=text.replace('source_facing,source_phase,source_epoch,native_frame,pad,physical_foot,HP,lives\\n',
                      'source_facing,source_mode,source_A_lock,source_phase,source_epoch,native_frame,pad,physical_foot,HP,lives\\n')
    text=text.replace('s.source_facing,s.phase,s.epoch','s.source_facing,s.source_mode,s.source_A_lock,s.phase,s.epoch')
    assert not any(s in text for s in ['emu.write','emu.loadSavestate','emu.reset','emu.loadState'])
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    proof=R/'build/prince-control-recipe-1103-v190/control-recipe.json'
    assert json.loads(proof.read_text())['passed']
    extra=[Path(__file__),proof,R/'tools/audit/check_prince_host_world_compiled_1102_v8.py']
    run_proof=proof.parent/'run-jump.json'
    if run_proof.is_file():
        assert json.loads(run_proof.read_text())['passed'];extra.append(run_proof)
    kwargs['scope']='Controller-only freshcold40 Prince approach, original runningA from measured distant naturalGoomba if admitted, real neutral15/mode0/Alock0 thenUp ledge sequence across first authored32pxpipe448..480/top176 and far-floor≥496. All187 mapped hooks/fullheaders/body/DMA/reservation guards retained; native lives unchanged, real sourceHP injuries explicitly recorded. No reposition/health/invincibility/ability seeds, no gamecode change, no helper, no full1-1 claim. At most4PNG and one bounded phase CSV; exact originalv8 C9 fallback only after64actualadmittedMain.'
    return ORIGINAL_PREPARE(output,rom,text,[*refs,*extra],**kwargs)


def main():
    assert P.sha(ROM)==PIN
    assert not (O/'native/ready.json').exists(), 'Prepared packet is immutable'
    O.mkdir(exist_ok=True)
    manifest=json.loads((PAYLOAD/'pose-manifest.json').read_text())
    P.prepare=build
    sys.argv=[str(Path(P.__file__)), '--rom',str(ROM),'--sha',PIN,
        '--runtime',str(PAYLOAD/'pose-runtime.bin'),'--metadata',str(PAYLOAD/'pose-metadata.bin'),
        '--cookie',manifest['Prince_cookie'],
        '--ref',str(ROM.parent/'candidate.json'),
        '--ref',str(PAYLOAD/'pose-CPU-v187.json'),
        '--ref',str(PAYLOAD/'pose-ISR-v188.json'),
        '--output',str(O/'native')]
    P.main()
    ready=O/'native/ready.json'
    receipt=dict(prepared=True, native_run=False, ROM_sha256=PIN,
        ready=ready.relative_to(R).as_posix(),ready_SHA256=P.sha(ready),
        controller_SHA256=P.sha(ready.parent/'controller.lua'),
        first_pipe=dict(left=448,right=480,top=176,initial_floor=208),
        endpoint='Nativeleft>=496 with actual sourcefoot207..211/nativeY176±2 and both complete headers; lives retained. Genuine HP injuries recorded.',
        source_recipe='Originalv8 stop-Up CPU and current190/191 input contracts; no static screenshot/ability seed or gameplay mutation.',
        source_files_to_commit=[Path(__file__).relative_to(R).as_posix()],
        run_command='python '+(ready.parent/'run.py').relative_to(R).as_posix())
    (O/'prepared.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__': main()
