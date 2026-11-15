"""Separate safe-phase full route; original full input negative stays frozen."""
from hashlib import sha256
from functools import lru_cache
import argparse,json
from types import SimpleNamespace
from unittest.mock import patch
import replay_prince_body_earned_stage_1114 as Frozen
from check_ff_stdout_controller_source_1110 import LuaRuntime

PIN=Frozen.PIN


@lru_cache(maxsize=2)
def controller(raw,*,brick_runup=False,combat=False):
    text=Frozen.controller(raw)
    def change(old,new):
        nonlocal text
        assert text.count(old)==1,old;text=text.replace(old,new,1)
    change("          switch('third-running-approach',1)","          switch('third-partial-wait',0)")
    change("  if progress=='third-running-approach' then", """  if progress=='third-partial-wait' then
    local left,right=capFeet(s,736,144)
    assert((left or right) and idle(s),'Real third-cap support throughout safe phase wait')
    local walkers=thirdWalkers()
    if #walkers==2 and walkers[1].direction==2 and walkers[2].direction==2 and walkers[1].x<=848 and walkers[2].x<=848 then
      switch('third-running-approach',1,walkers)
    end
  elseif progress=='third-running-approach' then""")
    # The old early-wall thresholds were navigation aids for the old query
    # geometry. Here ordinary Right reaches the actual authored wall; the
    # inherited bounded support/solid/stall observer then requests brake/Up.
    change("    if progress=='late-finish-run' and not earnedStage.early_wall then",
           "    if false and progress=='late-finish-run' and not earnedStage.early_wall then")
    change("    elseif age>165 then\n      error('Original Up did not reach support over the late wall')",
           "    elseif age>165 then\n      p.obstruction={state=s,tiles=finishGeometry(s),actors=lateWalkers(s),attempt=attempt}\n      error('Original Up did not reach support over the late wall')")
    if brick_runup:
        change("          p.jumps[#p.jumps+1]={kind='brick-walkers',request=s,actors=lateWalkers(s)}\n          switch('late-finish-jump',128)",
               "          switch('late-finish-brick-runup',1)")
        change("  elseif progress=='late-finish-brick-wait' then", """  elseif progress=='late-finish-brick-runup' then
    if running(s) and support(s) then
      p.jumps[#p.jumps+1]={kind='brick-running',request=s,actors=lateWalkers(s),tiles=finishGeometry(s)}
      switch('late-finish-jump',129)
    elseif age>64 then
      p.obstruction={state=s,tiles=finishGeometry(s),actors=lateWalkers(s)}
      error('Original brick running approach did not admit running')
    end
  elseif progress=='late-finish-brick-wait' then""")
    if combat:
        change("    elseif age>165 then\n      p.obstruction=",
               "    elseif age>165 and(not attempt.hang or commits-attempt.hang.commit>165)then\n      p.obstruction=")
        change("    assert(commits-earnedStage.sword_pause.start<300,'Bounded original sword encounter')\n    pad=128\n    changedAt=commits",
               """    local episode=earnedStage.sword_pause
    if episode.uid~=s.guard_uid then episode.uid=s.guard_uid;episode.start=commits;episode.parried=false end
    assert(commits-episode.start<700,'Bounded actual original parry/approach/attack encounter')
    local target
    for slot=0,5 do
      local flag,id,enemyState=read(0x10+slot),read(0x17+slot),read(0x1f+slot)
      local x,y=read(0x76+slot)+256*read(0x5d+slot),read(0xbe+slot)
      if flag>0 and flag<128 and id<21 and enemyState&32==0 and math.abs(y-s.y)<48
        and(not target or math.abs(x-s.x)<math.abs(target.x-s.x))then target={slot=slot,x=x,y=y}end
    end
    pad=0
    if s.pose==171 and not episode.parried then pad=64
    elseif s.action==62 then episode.parried=true
    elseif episode.parried and target then
      local direction=target.x>=s.x and 1 or 2
      local gap=math.abs(target.x-s.x)
      pad=gap>=(direction==1 and 38 or 32)and direction or 128
    end
    changedAt=commits""")
    assert not any(s in text for s in('pad=201','or 201','emu.write','emu.setState','io.open','takeScreenshot'))
    LuaRuntime().compile(text)
    return text


def metadata(raw,*,brick_runup=False,combat=False):
    text=controller(raw,brick_runup=brick_runup,combat=combat)
    return dict(ROM_SHA256=PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),required_native_variant=3,
        ordinary_controls_only=True,natural_items_and_sword=True,gameplay_seeds=0,
        actual_third_cap_Goomba_phase_wait=True,late_wall_actual_contact=True,brick_runup=brick_runup,
        original_parry_approach_attack_controls=combat,
        qualification_pending=True,current_Downloads_replacement=False,outputs=0,Mesen=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',action='store_true');parser.add_argument('--runup',action='store_true');parser.add_argument('--combat',action='store_true');parser.add_argument('--current-score-571',action='store_true');args=parser.parse_args()
    if args.current_score_571:import current_prince_body_research_571_1114 as Current
    else:import current_prince_body_research_f11_1114 as Current
    import check_prince_body_earned_stage_1114 as Check
    proxy=SimpleNamespace(controller=lambda raw:controller(raw,brick_runup=args.runup,combat=args.combat),metadata=lambda raw:metadata(raw,brick_runup=args.runup,combat=args.combat),Full=Frozen.Full)
    with patch.object(Check,'Factory',proxy):
        q=Check.run(Current.load(Check.Game.Factory.ROM),source=args.source)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
