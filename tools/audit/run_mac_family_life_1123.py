"""Natural Easy Mac-family hidden1UP on exact3af; Root alone may --run.

The proven wounded-Mushroom opener is retained, followed by ordinary boxing
movement, the real X1024 hidden block, collector, delayed native life writer
and25 further movement returns. The shared slot candidate is never written.
"""
import argparse,json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch

import run_mac_family_stock_1123 as Old
import compose_dkjr_side_epoch_fast_1123 as Current
from check_ff_stdout_controller_source_1110 import LuaRuntime
from replay_sonic_hidden_life_f7c9_1116 import value
from run_mario_luigi_stock_native_1122 import H,OUT,R,ROM,preserve_script
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

PIN=Current.CANDIDATE
W,N,FORMS=Old.W,Old.N,Old.FORMS
PINS={'mac':'36ef195afae660439959023e4afbb72e72e71414dc84615d59c71efe00195588',
      'doc':'6483fe0253dcdffb42224ed09c4dafec4e60cd24d59615e309a4d98895af9370',
      'tyson':'f269b986cc15ffa07e22a52f2791af884669e6a66279e59db5ea3f26d6442a74'}
POLICY=r'''
local T={phase='mushroom',events={}}
MAC_STOCK_STATE=T
local holdUntil=0
local function snapshot(c,a)
 return{x=c.x,y=c.y,state=c.state,update=c.update,motor=c.motor,hp=c.hp,
        hearts=c.hearts,stars=c.stars,lives=c.lives,item=a}
end
local function phase(c,p,a)
 if T.phase==p then return end
 assert(#T.events<40,'Bounded Mac hidden-life phases')
 T.phase=p;T.since=c.update;T.events[#T.events+1]={phase=p,player=snapshot(c,a)}
end
local function steer(c,target,band)
 local v=c.vx<128 and c.vx or c.vx-256
 local d=target-c.x-v/5
 return{right=d>band,left=d< -band}
end
local function item(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==3 then
   return{x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),
          y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),slot=i}
  end
 end
end
local function defend(c,b)
 local e=c.enemy()
 if e and math.abs(e.dx)<56 and math.abs(e.y-c.y)<32 and c.grounded then
  local facing=e.dx>=0 and 1 or 2
  if c.r('PlayerFacingDir')~=facing then return{right=facing==1,left=facing==2}end
  return{down=true,b=c.update%12<3}
 end
 return b
end
return function(c)
 if c.lives==3 then phase(c,'credited');return{}end
 if c.status==0 then return prefix(c)end
 if not T.healed then T.healed=c.update;phase(c,'Mushroom-after');return{}end
 if c.update-T.healed<64 then return{}end
 if T.phase=='Mushroom-after'then phase(c,'travel')end
 local a=item(c)
 if a and not T.revealed then T.revealed=snapshot(c,a);phase(c,'rise',a)end
 if T.revealed and not a then
  T.missing=T.missing or snapshot(c)
  return{}
 end
 if a then
  T.latest=snapshot(c,a)
  if a.state&128==0 then return defend(c,steer(c,1052,3))end
  phase(c,'collect',a)
  local target=math.max(c.camera+2,math.min(1090,a.x-4))
  local b=steer(c,target,3)
  if c.grounded and c.y-a.y>14 and math.abs(c.x-a.x)<28 and not c.lastA then
   holdUntil=c.update+26
  end
  b.a=c.update<holdUntil
  return defend(c,b)
 end
 if T.phase=='travel'then
  if c.x<972 then return opening(c)end
  phase(c,'align')
 end
 if T.phase=='bump'then
  if c.update-T.since>52 then phase(c,'align')end
  return{a=c.update<holdUntil}
 end
 if not c.grounded or c.y<160 then
  -- Walk off the fourth pipe and land before requesting the hidden bump.
  local b=steer(c,984,3);b.a=false
  return defend(c,b)
 end
 if math.abs(c.x-1019)<=2 and math.abs(c.vx<128 and c.vx or c.vx-256)<=4 and not c.lastA then
  T.attempts=(T.attempts or 0)+1;assert(T.attempts<=8,'Bounded actual hidden1UP bump')
  holdUntil=c.update+28;phase(c,'bump');return{a=true}
 end
 return defend(c,steer(c,1019,2))
end
'''


@lru_cache(maxsize=1)
def reference(raw):
    assert H(raw)==PIN
    prior94=Current.inverse(raw)
    prior14=Current.Parent.inverse(prior94)
    assert H(prior14)==Old.PIN
    return prior14


def build(raw,form,*,kind=3,policy=POLICY):
    """Shared source-only factory; each Root-run controller needs its own pin."""
    assert kind in(2,3)
    ref=reference(raw);config=deepcopy(Old.bindings(ref,form))
    original=Old.controller(ref,form)
    assert H(original.encode())==Old.PINS[form]
    config.update(sha=PIN,route='life'if kind==3 else'star',expected=[0,3]if kind==3 else[0,1,2])
    for name,h in config['hooks'].items():
        at=16+h['offset'];expected=bytes.fromhex(h['hex'])
        assert raw[at:at+len(expected)]==ref[at:at+len(expected)]==expected,('old Mac hook changed',name)
    if kind==3:
        pc=0x8987;at=16+126*8192+(pc&8191)
        assert raw[at:at+3]==b'\xee'+config['ram']['NumberofLives'].to_bytes(2,'little')
        config['hooks']['LifeCredit']=dict(pc=pc,tag=254,offset=at-16,hex=raw[at:at+8].hex())
    first,rest=original.split('\n',1)
    text='local C='+value(config)+'\n'+rest
    anchor='local choose=(function()\n'+Old.POLICY+'\nend)()'
    assert text.count(anchor)==1
    text=text.replace(anchor,'local prefix=(function()\n'+Old.POLICY+'\nend)()\nlocal choose=(function()\n'+policy+'\nend)()',1)
    edits=[
      ("s.hp>0 and s.lives==2 and s.yHigh<2","s.hp>0 and s.lives>=2 and s.lives<=3 and s.yHigh<2"),
      ("if q.collect and not q.grant and score()>=q.collect.score_before+1000 then",
       "if kind<2 and q.collect and not q.grant and score()>=q.collect.score_before+1000 then"),
      ("if kind==3 then assert(s.lives==q.grant.lives,'Earned life persists during movement')",
       "if kind==3 then assert(s.lives==q.grant.lives and(sound[64]or 0)>q.collect.cue64_before,'Actual delayed life and cue persist')"),
      ("sound=r('Square2SoundQueue'),score_before=p.score}","sound=r('Square2SoundQueue'),score_before=p.score,cue64_before=p.cue64}"),
      ("p.actor=a;p.before=state();p.score=score();p.cue=sound[32]or 0",
       "p.actor=a;p.before=state();p.score=score();p.cue=sound[32]or 0;p.cue64=sound[64]or 0"),
      ("if entered and v==32 then","if entered and(v==32 or v==64)then"),
      ("Natural Mushroom heal and Flower star stock plus25 movement updates",
       "Natural Mushroom heal and requested native stock item plus25 movement returns"),
    ]
    for before,after in edits:
        assert text.count(before)==1,(before,text.count(before));text=text.replace(before,after,1)
    # Keep completed movement clocks honest during actual pause/freeze.
    a="if p.name=='MacMovement' then motor=motor+1"
    b="if p.name=='MacMovement' then if p.movement and scope()and r('TimerControl')==0 and r('GamePauseStatus')&1==0 then motor=motor+1 end"
    assert text.count(a)==1;text=text.replace(a,b,1)
    a=" if name=='FamilyGrant'then"
    b=" if name=='MacMovement'then p.movement=scope()and r('TimerControl')==0 and r('GamePauseStatus')&1==0 end\n if name=='FamilyGrant'then"
    assert text.count(a)==1;text=text.replace(a,b,1)
    # This field is absent from the older compact RAM binding.
    config_field='GamePauseStatus'
    assert config_field not in config['ram']
    text=text.replace('local C='+value(config),'local C='+value(dict(config,ram=dict(config['ram'],GamePauseStatus=W.address(W.Symbols.bundle(),'GamePauseStatus')))),1)
    assert not any(token in text for token in('emu.write','emu.setState','saveState','loadState','dofile','io.open','takeScreenshot'))
    LuaRuntime().compile(text)
    return text


def controller(raw,form):
    text=build(raw,form)
    if form in PINS:assert H(text.encode())==PINS[form]
    return text


def cold(raw,form):
    cfg=Old.bindings(reference(raw),form);bundle=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(bundle,0)
    for key in(4,2,2):W.UI.key(m,key)
    for _ in range(cfg['variant']):W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]==cfg['name']and N.get(m,'MacVariant')==cfg['variant']
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    import check_contra_force_fast_ingress_1122 as Fast
    prior=m.bundle['syms']['PauseRoutine']
    m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(prior,val=hex(Fast.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    import check_bub_current_budget_1113 as Frames
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'LmReady')==0x4d and N.get(m,'LmHealth')==96 and N.get(m,'NumberofLives')==2
            assert N.get(m,'SelectedCharacter')==15 and N.get(m,'CrossoverBehaviorVersion')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual boxing cold bound')


def source(raw,form,limit=3200,*,text=None):
    import inspect_rogue_missile_targets_cb95_1116 as Engine
    text=controller(raw,form)if text is None else text
    machines={}
    def enter(image):
        machines['machine']=cold(image,form)
        return machines['machine']
    with patch.object(Engine.J,'cold',enter),patch.object(Engine.J,'PIN',PIN):
        q=Engine.run(raw,limit,text=text)
    m=machines['machine']
    q['terminal_diagnostic']={n:N.get(m,n)for n in('Player_X_Position','Player_PageLoc','Player_Y_Position',
        'Player_State','NumberofLives','LmHealth','LmHearts','LmStars','LmPrevious','PlayerStatus','GameEngineSubroutine')}
    return q


def native(raw,form):
    assert form in PINS
    program=controller(raw,form).encode();guard=check(ROM)
    candidate,script=OUT/'candidate.nes',OUT/'controller.lua'
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(OUT.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    before=script.read_bytes()
    try:
        with preserve_script(script,candidate,raw)as stage:
            stage(program);q=run(script,ROM,OUT/'capture',PIN,180)
        print('MAC_LIFE_NATIVE '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['script_SHA256']==H(program)and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--form',choices=tuple(FORMS),default='mac')
    group=p.add_mutually_exclusive_group();group.add_argument('--source',action='store_true');group.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=3200);args=p.parse_args();assert 1000<=args.limit<=4000
    raw=ROM.read_bytes();assert H(raw)==PIN
    if args.run:return int(not native(raw,args.form)['passed'])
    def deny(*a,**k):raise AssertionError('Source attempted outputs or native process')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        if args.source:q=source(raw,args.form,args.limit)
        else:
            text=controller(raw,args.form);q=dict(passed=True,ROM_SHA256=PIN,controller_SHA256=H(text.encode()),route_executed=False,outputs=0)
    print('MAC_LIFE_SOURCE '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
