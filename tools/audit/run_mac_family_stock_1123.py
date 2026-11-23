"""Normal-input Mac family Mushroom heal and Flower star-stock replay."""

import argparse
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

from check_ff_stdout_controller_source_1110 import LuaRuntime
from current_ice_stock_binding_1122 import RAM_FIELDS
import compose_dkjr_sonic_dispatch_1123 as Current
import profile_sonic_empty_cpu_1110 as Linked
from replay_sonic_hidden_life_f7c9_1116 import value
from run_mario_luigi_stock_native_1122 import H, OUT, R, ROM, preserve_script
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

PIN=Current.CANDIDATE
W,N=Linked.W,Linked.N
FORMS={'mac':(0,'LITTLE MAC'),'doc':(1,'DOC LOUIS'),'tyson':(2,'MIKE TYSON')}
PINS={'mac':'cbd374b793766742313b18555c784517af9e85d9803834170f6a9d697818a633',
      'doc':'a6c0a122b8ff40bd2f7a00a84718abe00aa01a9f666088349cfe261f240445b6',
      'tyson':'280f4c6d1c41ed4d80d5c38a0f986024ce79ef03af3945f183a99b62d4136147'}
OBSERVER=R/'tools/audit/ice_climbers_stock_observer_1122.lua'
OPENING=R/'tools/playthroughs/mac_roster_11_v2.lua'
SOURCE_PINS={OBSERVER:'c03ec6768f9b4e2b6e3fca0dc36363f2aa6ea4e835900a9d18c42c69444cd83f',
             OPENING:'29f62d0da3c489502c445d11c1c23081ecc89037470e499948ef8d3a51da7b55'}

POLICY=r'''
local T={phase='wound',events={},kind=0}
MAC_STOCK_STATE=T
local function sample(c)return{x=c.x,y=c.y,update=c.update,motor=c.motor,hp=c.hp,stars=c.stars,hearts=c.hearts,status=c.status,state=c.state}end
local function phase(c,p)
 T.phase=p;T.since=c.update
 assert(#T.events<32,'Bounded ordinary Mac pickup phases')
 T.events[#T.events+1]={phase=p,player=sample(c)}
end
local function steer(c,x,band)
 local v=c.vx<128 and c.vx or c.vx-256;local d=x-c.x-v/5
 return{right=d>band,left=d< -band}
end
local function flower(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==1 then
   return{x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),
          mature=c.r('Enemy_State',i)&128~=0}
  end
 end
end
local function defend(c,b)
 local nearest
 for i=0,5 do
  local f,id,s=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);local dx=x-c.x
  local y=c.r('Enemy_Y_Position',i)
  if f==1 and(id==6 or id==0 or id==3)and s<32 and not(id==6 and s>=2)
     and math.abs(y-c.y)<32 and math.abs(dx)<56 and(not nearest or math.abs(dx)<math.abs(nearest.dx))then
   nearest={dx=dx,id=id}
  end
 end
 if nearest and c.grounded then
  local facing=nearest.dx>=0 and 1 or 2
  if c.r('PlayerFacingDir')~=facing then return{right=facing==1,left=facing==2}end
  return{down=true,b=c.update%12<3}
 end
 return b
end
return function(c)
 if c.stars>0 then T.flowerEarned=T.flowerEarned or sample(c);return{}end
 if T.phase=='wound'then
  assert(c.hp>0 and c.hp<=96,'Living normal boxing health')
  if c.hp<96 then T.deficit=sample(c);phase(c,'opening');return opening(c)end
  -- Permit the ordinary first Goomba to make one real contact.  No actor,
  -- resource, position, protection or motion state is injected.
  return steer(c,264,2)
 end
 if T.phase=='opening'then
  if c.status==0 then return opening(c)end
  T.mushroomEarned=sample(c);phase(c,'heal-after');return{}
 end
 if T.phase=='heal-after'then
  if c.update-T.since<64 then return{}end
  phase(c,'flower-travel')
 end
 local a=flower(c)
 if a and not T.flower then T.flower=a;phase(c,'flower-emerge')end
 if T.phase=='flower-travel'then
  if c.x<1176 then return opening(c)end
  phase(c,'flower-align')
 end
 if T.phase=='flower-align'then
  if not c.grounded or c.y<160 then return defend(c,steer(c,1195,3))end
  local v=c.vx<128 and c.vx or c.vx-256
  if math.abs(c.x-1251)<=2 and math.abs(v)<=4 and not c.lastA then
   T.attempts=(T.attempts or 0)+1;assert(T.attempts<=6,'Bounded real Flower bump')
   phase(c,'flower-bump');return{a=true}
  end
  return defend(c,steer(c,1251,2))
 end
 if T.phase=='flower-bump'then
  if c.grounded and c.update-T.since>48 then phase(c,'flower-align')end
  return{a=c.update-T.since<24}
 end
 if T.phase=='flower-emerge'then
  assert(a,'The authored Flower remains present before collection')
  if not a.mature then return defend(c,steer(c,1280,3))end
  phase(c,'flower-collect')
 end
 if T.phase=='flower-collect'then
  assert(a,'The mature authored Flower remains present before actual credit')
  if c.grounded and c.y>=160 then
   if math.abs(c.x-1280)<=4 and not c.lastA then phase(c,'flower-catch');return{left=true,a=true}end
   return defend(c,steer(c,1280,2))
  end
  return steer(c,a.x-2,2)
 end
 if T.phase=='flower-catch'then
  assert(a,'Live Flower until the actual family stock grant')
  if c.grounded and c.update-T.since>4 then phase(c,'flower-collect')end
  local b=steer(c,a.x-2,2);b.a=c.update-T.since<27;return b
 end
 return{}
end
'''


@lru_cache(maxsize=3)
def bindings(raw,form):
    assert H(raw)==PIN
    variant,name=FORMS[form];bundle=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):menu=W.UI.seed(bundle,0)
    for k in(4,2,2):W.UI.key(menu,k)
    for _ in range(variant):W.UI.key(menu,32)
    assert W.UI.menu_name(menu)[0]==name
    assert(N.get(menu,'CrossoverMenuIndex'),N.get(menu,'SelectedCharacter'),N.get(menu,'MacVariant'))==(14,15,variant)
    fields=[n for n in RAM_FIELDS if not n.startswith('Ic')]
    fields+=['MacVariant','LmHealth','LmStars','LmHearts','LmReady','LmPrevious','LmHurt','LmInvul',
             'LmStamp','InvPickup','InvPickupOwner','LmAttack','LmSuper','ObjectOffset','PlayerScoreDisplay']
    ram={n:W.address(bundle,n)for n in fields}
    hooks={}
    for tag,symbol in(('GameLoop','GameLoop'),('MacMovement','LmMovementGate'),
                       ('HandlePowerUpCollision','MarioSourcePowerupCollision'),
                       ('FamilyGrant','LmCollectGate'),('Injury','LmInjuryGate'),
                       ('PlayerHeadCollision','PlayerHeadCollision')):
        pc,at=W.address(bundle,symbol),W.location(bundle,symbol);bank=(at-16)//8192
        assert at-16==bank*8192+(pc&8191)
        hooks[tag]=dict(pc=pc,tag=bank|128,offset=at-16,hex=raw[at:at+12].hex())
    nav=['down']*32;nav[8]=nav[15]='left'
    return dict(sha=PIN,form=form,route='upgrades',name=name,char=15,slot=14,variant=variant,
                mode_value=0,expected=[0,1],ram=ram,hooks=hooks,navigation=nav)


def controller(raw,form):
    cfg=bindings(raw,form)
    assert all(H(p.read_bytes())==h for p,h in SOURCE_PINS.items())
    text=OBSERVER.read_text();edits=[]
    def edit(a,b):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b,1);edits.append((a,b))
    edit("assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha", "assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha")
    edit("r('SelectedCharacter')==20 and r('IcVariant')==C.variant", "r('SelectedCharacter')==15 and r('MacVariant')==C.variant")
    edit("r('IcVariant')~=C.variant", "r('MacVariant')~=C.variant")
    edit("local expected=C.route=='life' and {0,3} or {0,1,2}", 'local expected=C.expected')
    edit("power=r('IcPower')", "power=r('PlayerStatus'),hp=r('LmHealth'),stars=r('LmStars'),hearts=r('LmHearts'),hurt=r('LmHurt'),invul=r('LmInvul')")
    edit('c.poll=polls;c.char=20;', 'c.poll=updates;c.char=15;c.update=updates;')
    edit('c.lastA=mask&128~=0', "c.lastA=r('LmPrevious')&128~=0")
    edit('local lifePending', 'local lifePending\nlocal clockInput={}\nlocal injury\nlocal sound={}\nlocal function score()local n=0;for i=0,5 do n=n*10+r(\'PlayerScoreDisplay\',i)end;return n end')
    edit('Living Ice Climber', 'Living requested boxing family member')
    edit("assert(updates<5100,'Bounded pickup route')", "assert(updates<3600 and s.hp>0 and s.lives==2 and s.yHigh<2,'Bounded living ordinary boxing pickup route')")
    edit('local a=actor(i);local q=checks[tostring(a.kind)]', "local a=actor(i);local q=checks[tostring(a.kind)]\n  if q and q.birth and a.slot==q.birth.actor.slot and a.id==46 and a.flag>0 and a.state&128~=0 and not q.mature then q.mature={actor=a,player=s}end")
    edit('q.birth={actor=a,player=s}', "assert(heads[tostring(a.kind)],'Real authored block bump before item birth');q.birth={actor=a,player=s,stamp=r('LmStamp',i),owner=r('InvPickupOwner',i)}")
    edit(' local complete=true', " local complete=true\n for _,kind in ipairs(expected)do local q=checks[tostring(kind)];if q.collect and not q.grant and score()>=q.collect.score_before+1000 then q.grant=s end end")
    edit("else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end", "else assert(s.hp==q.grant.hp and s.stars==q.grant.stars and s.status==1,'Earned boxing resource persists during movement') end")
    edit('if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope() then', 'if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope()and s.state==0 then')
    edit("if complete then finish(true,'Authored pickups, native credit and 25 further movement updates') end", "if complete then assert(injury and injury.before.hp==96 and injury.after.hp==88,'Real opener deficit precedes healing');finish(true,'Natural Mushroom heal and Flower star stock plus25 movement updates');return end\n clockInput=scope()and choose(context())or{}")
    edit("assert(r('Square2SoundQueue')&32~=0,'Actual pickup cue')", "assert((sound[32]or 0)>p.cue,'Actual new native pickup cue')")
    edit("sound=r('Square2SoundQueue')}", "sound=r('Square2SoundQueue'),score_before=p.score}")
    edit("assert(p.before.power==a.kind and s.power==a.kind+1 and s.status==s.power,'Normal Ice power tier transition')", "assert(q.family and q.family.update==updates and s.status==1,'Same-update actual erased-actor family grant')\n  if a.kind==0 then assert(p.before.hp<96 and s.hp==math.min(96,p.before.hp+24),'Real deficit receives original heal24 with cap96')\n  else assert(s.hp==p.before.hp and s.stars==p.before.stars+1 and s.stars<=3,'Actual Flower replacement grants one boxing star')end")
    edit(' q.grant=s\nend', ' -- Native popup score must also complete before the post-grant25 gate.\nend')
    edit("if p.name=='IcMovement' then", "if p.name=='MacMovement' then")
    edit("  elseif p.actor then collected(p) end", """  elseif p.family then
   local a=p.family;local q=checks[tostring(a.kind)];local s=state()
   assert(cpu['cpu.ps']&1==1 and s.status==1,'Original family grant returns accepted')
   q.family={update=updates,stamp=a.stamp,owner=a.owner,erased=a.erased,before=p.before,after=s}
  elseif p.injury then
   local s=state();if p.before.hp==96 and s.hp==88 then
    assert(p.injury.id==6 and p.injury.flag==1 and p.injury.state==0,'Authentic opener Goomba caused health deficit')
    injury={before=p.before,after=s,actor=p.injury}
   end
  elseif p.actor then collected(p) end""")
    edit(" if name=='HandlePowerUpCollision' then", """ if name=='FamilyGrant'then
  local i=cpu['cpu.x'];local kind=r('PowerUpType',i);local q=checks[tostring(kind)]
  if not(q and q.birth and not q.collect)then return end
  assert(r('Enemy_Flag',i)==0 and r('Enemy_ID',i)==0 and r('Enemy_State',i)==0,
         'Real source collision has already erased the same pickup at family grant')
  assert(i==q.birth.actor.slot and r('InvPickupOwner',i)==15 and r('LmStamp',i)==0xe0+kind and r('InvPickup',i)==0xe0+kind,
         'Original same item owner and E0/E1 stamps survive actual native erase')
  p.family={kind=kind,stamp=r('LmStamp',i),owner=15,erased=true};p.before=state()
 elseif name=='Injury'then p.injury=actor(r('ObjectOffset'));p.before=state()
 elseif name=='HandlePowerUpCollision' then""")
    edit('  p.actor=a;p.before=state()', "  assert(a.state&128~=0,'Actual mature actor at source collision before erase');q.mature=q.mature or{actor=a,player=state()}\n  p.actor=a;p.before=state();p.score=score();p.cue=sound[32]or 0")
    edit('phase=ICE_STOCK_STATE or {},controller_only=true,files=0,images=0', 'phase=MAC_STOCK_STATE or {},real_injury=injury,sound_cues=sound,pending_returns=#pending,controller_only=true,game_state_writes=false,files=0,images=0')
    edit("local bits={a=128", """emu.addMemoryCallback(guarded('Native pickup cue',function(_,v)
 if entered and v==32 then sound[v]=(sound[v]or 0)+1 end
end),emu.callbackType.write,C.ram.Square2SoundQueue)
local bits={a=128""")
    edit('local b=not entered and menu() or (scope() and choose(context()) or {})', 'local b=not entered and menu()or(scope()and clockInput or{})')
    edit('  entered=physical', '  entered=physical;clockInput=choose(context())')
    restored=text
    for a,b in reversed(edits):assert restored.count(b)==1;restored=restored.replace(b,a,1)
    assert restored==OBSERVER.read_text()
    program='\n'.join(('local C='+value(cfg),'local opening=(function()\n'+OPENING.read_text()+'\nend)()',
                       'local choose=(function()\n'+POLICY+'\nend)()',text))
    assert not any(t in program for t in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    LuaRuntime().compile(program)
    return program


def cold(raw,form):
    cfg=bindings(raw,form);bundle=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(bundle,0)
    for k in(4,2,2):W.UI.key(m,k)
    for _ in range(cfg['variant']):W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]==cfg['name'] and N.get(m,'MacVariant')==cfg['variant']
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    import check_contra_force_fast_ingress_1122 as Fast
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Fast.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    import check_bub_current_budget_1113 as Frames
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'LmReady')==0x4d and N.get(m,'LmHealth')==96 and N.get(m,'NumberofLives')==2
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual boxing compiled-menu cold bound')


def source(raw,form,limit):
    import inspect_rogue_missile_targets_cb95_1116 as Engine
    program=controller(raw,form);assert H(program.encode())==PINS[form]
    with patch.object(Engine.J,'cold',lambda image:cold(image,form)),patch.object(Engine.J,'PIN',PIN):
        return Engine.run(raw,limit,text=program)


def native(raw,form):
    program=controller(raw,form).encode();assert H(program)==PINS[form]
    guard=check(ROM);candidate,script=OUT/'candidate.nes',OUT/'controller.lua'
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(OUT.iterdir())=={candidate,script} and candidate.read_bytes()==raw
    before=script.read_bytes()
    try:
        with preserve_script(script,candidate,raw)as stage:
            stage(program);q=run(script,ROM,OUT/'capture',PIN,180)
        assert q['script_SHA256']==H(program)and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--form',choices=tuple(FORMS),default='mac')
    mode=p.add_mutually_exclusive_group();mode.add_argument('--source',action='store_true');mode.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=3200);a=p.parse_args();assert 1800<=a.limit<=4000
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:q=native(raw,a.form)
    else:
        def deny(*args,**kwargs):raise AssertionError('Mac source attempted files or native process')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.form,a.limit)
            else:
                program=controller(raw,a.form);q=dict(passed=True,controller_SHA256=H(program.encode()),ROM_SHA256=PIN,route_executed=False,outputs=0)
    print('MAC_FAMILY_STOCK '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
