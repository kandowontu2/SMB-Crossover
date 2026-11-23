"""Exact82e8 default NES Pit natural 1-1 pickups and earned-reward use.

Source mode starts through the declared linked menu/Start entry. Root alone
uses --run for physical boot. No actor, resource, motion or outcome writes.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import re
from unittest.mock import patch

import run_chip_dale_stock_1123 as Host
import compose_scrooge_prepare_stack_1123 as Stack
from current_ice_stock_binding_1122 import RAM_FIELDS
from replay_sonic_hidden_life_f7c9_1116 import value
from check_ff_stdout_controller_source_1110 import LuaRuntime
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

H,R,ROM,OUT,W,N=Host.H,Host.R,Host.ROM,Host.OUT,Host.W,Host.N
PIN='82e8da0e293dee91da441347dfe4c675c88708c43b0b88d4fbd253312f00a131'
ROUTES={'mushroom':(0,),'upgrades':(0,1),'life':(0,3),'star':(0,2)}
PINS={
 'mushroom':'002349583230248e44017dfd2f30da07306693808e1426a50ff761d208b0d447',
 'upgrades':'bc17717c4af88a9d2b3c54bc3dedf13c2c4107ed196d2947f8639217586ed859',
 'life':'d2301f8a2799369c08ae8e766f41b2f8e1b4af364bbfa996e6bd415d1e14eeb3',
 'star':'4b86a2da9fea98b1a45bf64eacdd953d7f122e48f36492ca864b8648ca398309',
}
OBSERVER=R/'tools/audit/ice_climbers_stock_observer_1122.lua'
TRAVEL=R/'tools/playthroughs/pit_rygar_sophia_dry_policy.lua'

POLICY=r'''
local T={kind=0,phase='travel',events={}}
PIT_STOCK=T
PIT_USES={}
local function sample(c)return{x=c.x,y=c.y,update=c.update,motor=c.motor,tier=c.status,state=c.state,fuel=c.fuel,flight=c.flight}end
local function phase(c,p)T.phase=p;T.at=c.update;assert(#T.events<64,'Bounded organic NES Pit phases');T.events[#T.events+1]={kind=T.kind,phase=p,player=sample(c)}end
local function steer(c,x,n)return{right=c.x<x-n,left=c.x>x+n}end
local function target(c)
 for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==T.kind then
  return{slot=i,x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),mature=c.r('Enemy_State',i)&128~=0}
 end end
end
local function defend(c,b)
 local e=c.enemy()
 if e and e.dx>0 and e.dx<110 and math.abs(e.y-c.y)<32 and c.grounded then
  if c.r('PlayerFacingDir')~=1 then return{right=true}end
  return{b=c.update%8<3}
 end
 return b
end
local function use(c,kind)
 local u=PIT_USES[kind]
 if not u then u={kind=kind,requested=sample(c)};PIT_USES[kind]=u end
 if kind==1 then
  if u.spawn then return{}end
  if c.r('PlayerFacingDir')~=1 then return{right=true}end
  for i=0,9 do if c.r('RgShotType',i)~=0 then return{}end end
  PIT_USE_REQUEST=1
  return{b=c.r('RgPreviousButtons')&64==0}
 end
 error('Unimplemented earned-use input')
end
return function(c)
 if c.growth~=0 then return{}end
 if PIT_FIRST_AFTER and not PIT_FIRST_USED then return use(c,1)end
 if PIT_TARGET_AFTER and C.route=='upgrades'and not PIT_SECOND_USED then return use(c,2)end
 if PIT_TARGET_COLLECTED and T.kind~=0 then return{}end
 if T.kind==0 and PIT_FIRST_COLLECTED and not PIT_FIRST_AFTER then return{}end
 if T.kind==0 and PIT_FIRST_USED then
  if C.route=='mushroom'then return{}end
  T.kind=C.expected[2];T.seen=nil;T.missing=nil;T.attempts=0;phase(c,'travel')
 end
 local goal=T.kind==0 and 336 or T.kind==1 and 1248 or T.kind==2 and 1616 or 1024
 local a=target(c)
 if a and not T.seen then T.seen=a;phase(c,'emerge')end
 if T.seen and not a then T.missing=sample(c);return{}end
 if T.phase=='travel'then
  if c.x<goal-76 then return defend(c,travel(c))end
  phase(c,'align')
 end
 if T.phase=='align'then
  if not c.grounded or c.y<160 then return defend(c,steer(c,goal-56,2))end
  if math.abs(c.x-(goal-5))<=2 and not c.lastA then
   T.attempts=(T.attempts or 0)+1;assert(T.attempts<=8,'Bounded real powerblock bumps');phase(c,'bump');return{a=true}
  end
  return defend(c,steer(c,goal-5,2))
 end
 if T.phase=='bump'then
  if c.grounded and c.update-T.at>60 then phase(c,'align')end
  return{a=c.update-T.at<32}
 end
 if T.phase=='emerge'then
  if not a.mature then return defend(c,steer(c,T.kind==0 and goal+66 or goal+36,2))end
  phase(c,'collect')
 end
 if T.phase=='collect'then
  if T.kind==0 then return defend(c,steer(c,a.y>=148 and a.x-3 or goal+66,2))end
  if T.kind==1 and c.grounded and c.y>=160 then
   if math.abs(c.x-(goal+36))<=3 and not c.lastA then phase(c,'catch');return{left=true,a=true}end
   return defend(c,steer(c,goal+36,2))
  end
  if T.kind>=2 and c.grounded and c.y-a.y>14 and math.abs(c.x-a.x)<30 and not c.lastA then phase(c,'catch');return{a=true}end
  local x=T.kind==1 and a.x-2 or math.max(c.camera+2,a.x-3);if T.kind==3 then x=math.min(x,1091)end
  return defend(c,steer(c,x,2))
 end
 if T.phase=='catch'then
  if c.grounded and c.update-T.at>4 then phase(c,'collect')end
  local b=steer(c,a.x-2,2);b.a=c.update-T.at<34;return b
 end
 return{}
end
'''




FLIGHT_POLICY=r"""
 if kind==2 then
  u.phase=u.phase or 'setup'
  if u.phase=='setup'then
   if math.abs(c.x-1304)>2 then return steer(c,1304,2)end
   if not c.grounded or c.lastA then return{}end
   assert(c.y==176 and c.fuel==60 and c.flight==0,'Earned full flutter meter at actual clear floor')
   u.jump=sample(c);u.at=c.update;u.phase='jump';return{a=true}
  end
  if u.phase=='jump'then
   if c.update-u.at<6 then return{a=true}end
   assert(not c.grounded and c.y<u.jump.y,'Actual ordinary Pit jump before fresh flutter press')
   u.release=sample(c);u.at=c.update;u.phase='release';return{}
  end
  if u.phase=='release'then
   if c.update-u.at<3 or c.lastA then return{}end
   assert(not c.grounded and c.fuel==60,'Fresh A after real airborne release')
   u.armed=sample(c);u.phase='flutter';PIT_USE_REQUEST=2;return{a=true}
  end
  if u.phase=='flutter'then
   if(u.burn or 0)<8 then return{a=true}end
   assert(u.lift,'Actual earned flutter changes vertical position')
   u.released=sample(c);u.phase='landing';return{}
  end
  return{}
 end
 error('Unexpected earned-use input')"""
FLIGHT_AFTER=r"""
 local f=PIT_USES[2]
 if f and f.firstFlight and not f.after then
  if s.y<=f.firstFlight.after.y-2 then f.lift=f.lift or s end
  if f.phase=='landing'and s.state==0 and not f.landing then
   assert(f.burn>=8 and f.lift and s.flight==0,'Actual flutter lifted and returned to natural floor')
   f.landing=s
  end
  if f.landing and not f.recharge and s.motor>f.landing.motor then
   assert(s.motor==f.landing.motor+1 and s.fuel==60 and s.flight==0,'First following grounded worker recharges actual flutter meter')
   f.recharge=s
  end
  if f.recharge and s.motor-f.recharge.motor>=25 then
   assert(s.state==0 and s.y==176 and s.status==2 and s.growth==0 and s.fuel==60 and s.flight==0,'Earned tier2 survives25 completed workers after recharge')
   f.after=s;PIT_SECOND_USED=true
  end
 end
"""
FLIGHT_RETURN=r"""
  elseif p.flight then
   local f=PIT_USES[2];local s=state()
   if f and PIT_USE_REQUEST==2 and p.flight.fuel==s.fuel+1 then
    assert(s.flight==1 and s.status==2 and s.state~=0,'Actual earned airborne PitFlightUpdate consumes its own fuel')
    f.burn=(f.burn or 0)+1;f.firstFlight=f.firstFlight or{before=p.flight,after=s}
   end
"""


def successor(program,route):
    """Keep the native-qualified first-M controller exact; scope later witnesses."""
    if route=='mushroom':return program
    old=program;edits=[]
    def once(a,b):
        nonlocal program
        assert program.count(a)==1,(a,program.count(a))
        program=program.replace(a,b,1);edits.append((a,b))
    once("if PIT_USE_REQUEST==1 and p.before.status==1 then",
         "if PIT_USE_REQUEST==1 and p.before.status==1 and not PIT_FIRST_USED then")
    once("if u and u.spawn and p.bridge==u.spawn.slot then",
         "if u and u.spawn and not u.retired and p.bridge==u.spawn.slot then")
    if route=='upgrades':
        once(" error('Unimplemented earned-use input')",FLIGHT_POLICY)
        once(' local complete=true',FLIGHT_AFTER+'\n local complete=true')
        once('  elseif p.fire then',FLIGHT_RETURN+'  elseif p.fire then')
        once(" if name=='FireShot'then"," if name=='PitFlight'then p.flight=state()\n elseif name=='FireShot'then")
    restored=program
    for a,b in reversed(edits):
        assert restored.count(b)==1
        restored=restored.replace(b,a,1)
    assert restored==old
    return program


@lru_cache(maxsize=4)
def bindings(raw,route):
    assert H(raw)==PIN==Stack.CANDIDATE and route in ROUTES
    assert H(Stack.inverse(raw))==Host.CURRENT
    bundle=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):menu=W.UI.seed(bundle,0)
    for _ in range(6):W.UI.key(menu,1)
    assert W.UI.menu_name(menu)[0]=='PIT'
    assert tuple(N.get(menu,n)for n in('CrossoverMenuIndex','SelectedCharacter','PitVariant'))==(6,6,0)
    fields=set(n for n in RAM_FIELDS if not n.startswith('Ic'))
    fields.update(re.findall(r"r\('([A-Za-z_0-9]+)'",TRAVEL.read_text()+POLICY))
    fields.update('PitVariant GuestPowerupActive GuestPowerupAge GuestPowerupTarget GuestLegacyHurt PlayerScoreDisplay InvPickup InvPickupOwner XgPitFuel XgPitFlight XgPitBlocked RgShotAge RgShotX RgShotPage RgShotY RgShotDir RgSlot MmBulletType MmBulletX MmBulletPage MmBulletY RgPreviousButtons GamePauseStatus'.split())
    ram={n:W.address(bundle,n)for n in fields}
    hooks={}
    for event,symbol in(('GameLoop','GameLoop'),('PitMovement','ExpandedMovement'),
                         ('HandlePowerUpCollision','MarioSourcePowerupCollision'),('PlayerHeadCollision','PlayerHeadCollision'),
                         ('FireShot','ExpandedWeapons::FireShot'),('ShotBridge','ExpandedWeapons::Bridge'),('PitFlight','PitFlightUpdate')):
        pc,at=W.address(bundle,symbol),W.location(bundle,symbol);bank=(at-16)//8192
        assert at-16==bank*8192+(pc&8191)
        hooks[event]=dict(pc=pc,tag=bank|128,offset=at-16,hex=raw[at:at+12].hex())
    if route=='life':
        pc,bank=0x8987,126;at=16+bank*8192+(pc&8191)
        assert raw[at:at+3]==b'\xee'+ram['NumberofLives'].to_bytes(2,'little')
        hooks['LifeCredit']=dict(pc=pc,tag=bank|128,offset=at-16,hex=raw[at:at+8].hex())
    nav=[]
    for i in range(32):
        row,col=divmod(i,8);nav.append('up'if row in(1,2)else'down'if row==3 else'right'if col<6 else'left'if col>6 else'')
    return dict(sha=PIN,form='nes-pit',name='PIT',char=6,slot=6,variant=0,mode_value=0,route=route,
                expected=list(ROUTES[route]),ram=ram,hooks=hooks,navigation=nav)


def controller(raw,route):
    cfg=bindings(raw,route);text=OBSERVER.read_text();edits=[]
    def edit(a,b):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b,1);edits.append((a,b))
    edit("assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha", "assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha")
    edit("r('SelectedCharacter')==20 and r('IcVariant')==C.variant", "r('SelectedCharacter')==6 and r('PitVariant')==0")
    edit("r('IcVariant')~=C.variant", "r('PitVariant')~=0")
    edit("local expected=C.route=='life' and {0,3} or {0,1,2}", 'local expected=C.expected')
    edit("power=r('IcPower')", "power=r('PlayerStatus'),growth=r('GuestPowerupActive'),fuel=r('XgPitFuel'),flight=r('XgPitFlight')")
    edit('c.poll=polls;c.char=20;', 'c.poll=motor;c.char=6;c.update=motor;c.frame=motor;')
    edit('c.lastA=mask&128~=0', "c.lastA=r('PreviousA_B_Buttons')&128~=0")
    edit('local lifePending', "local lifePending\nlocal clockInput={}\nlocal cue,lifeCue=0,0\nlocal function score()local n=0;for i=0,5 do n=n*10+r('PlayerScoreDisplay',i)end;return n end")
    edit('Living Ice Climber','Living default NES Pit')
    edit("assert(updates<5100,'Bounded pickup route')", "assert(updates<4400 and s.yHigh<2 and(s.lives==2 or(C.route=='life'and checks['3'].grant and s.lives==3)),'Bounded living organic NES Pit route')\n assert(r('GuestLegacyHurt')~=1,'Keep naturally earned Pit tier')")
    edit('local a=actor(i);local q=checks[tostring(a.kind)]', "local a=actor(i);local q=checks[tostring(a.kind)]\n  if q and q.birth and a.slot==q.birth.actor.slot and a.flag>0 and a.id==46 and a.state&128~=0 and not q.mature then q.mature={actor=a,player=s}end")
    edit('q.birth={actor=a,player=s}', "assert(heads[tostring(a.kind)],'Actual authored head bump precedes item birth');q.birth={actor=a,player=s}")
    edit(' local complete=true', """ if checks['0'].collect then PIT_FIRST_COLLECTED=true end
 if checks['0'].after then PIT_FIRST_AFTER=true end
 local target=checks[tostring(C.expected[#C.expected])]
 if target.collect then PIT_TARGET_COLLECTED=true end
 if target.after then PIT_TARGET_AFTER=true end
 for _,kind in ipairs(expected)do local q=checks[tostring(kind)]
  if q.collect and not q.grant and kind~=3 and s.growth==0 and score()>=q.collect.score_before+1000 then
   if kind<2 then assert(s.status==kind+1,'Completed original60-update growth reaches earned Pit tier')else assert(s.star>0,'Native Star persists')end
   q.grant=s
  end
 end
 local u=PIT_USES[1]
 if u and u.spawn and not u.retired then
  local i=u.spawn.slot
  if r('RgShotType',i)==0 then assert(u.moved and u.proxy,'Real tier1 arrow moved and traversed native proxy27');u.retired=s
  else
   assert(r('RgShotType',i)==1 and s.status==1,'Actual earned tier1 arrow owns its natural lifetime')
   local x=pos('RgShotX','RgShotPage',i)
   if math.abs(x-u.spawn.x)>=3 then u.moved=u.moved or{x=x,y=r('RgShotY',i),at=s}end
  end
 end
 if u and u.retired and not u.after and s.motor-u.retired.motor>=25 and scope()and s.state==0 then
  assert(s.status==1 and s.growth==0,'Earned tier1 persists25 actual workers after arrow retirement');u.after=s;PIT_FIRST_USED=true
 end
 local complete=true""")
    edit('if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope() then','if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope()and s.state==0 then')
    edit("else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end", "else assert(s.status==q.grant.status and s.growth==0,'Actual earned progressive Pit tier persists')end")
    edit("if kind==3 then assert(s.lives==q.grant.lives,'Earned life persists during movement')", "if kind==3 then assert(s.lives==q.grant.lives and lifeCue>q.collect.life_cue_before,'Actual life and new native cue persist')")
    edit("elseif kind==2 then assert(s.star>0,'Earned Star persists during movement')", "elseif kind==2 then assert(s.star>0 and score()>=q.collect.score_before+1000,'Native Star and score persist')")
    edit("if complete then finish(true,'Authored pickups, native credit and 25 further movement updates') end", "if complete and PIT_FIRST_USED and(C.route~='upgrades'or PIT_SECOND_USED)then assert(#pending==0 and not lifePending,'All observed native workers returned');finish(true,'Natural NES Pit pickups plus earned reward use and25 returned workers');return end\n clockInput=scope()and choose(context())or{}")
    edit("assert(r('Square2SoundQueue')&32~=0,'Actual pickup cue')", "assert(cue>p.cue,'New actual native pickup cue')")
    edit("sound=r('Square2SoundQueue')}", "sound=r('Square2SoundQueue'),score_before=p.score,life_cue_before=p.life_cue}")
    edit("assert(p.before.power==a.kind and s.power==a.kind+1 and s.status==s.power,'Normal Ice power tier transition')", "assert(p.before.status==a.kind and s.growth==1 and r('GuestPowerupTarget')==a.kind+1,'Native Pit pickup starts actual progressive guest growth')")
    edit(' q.grant=s\nend',' -- Original growth and popup score finish before the post-credit25 gate.\nend')
    edit("if p.name=='IcMovement' then motor=motor+1", "if p.name=='PitMovement' then motor=motor+1")
    edit('  elseif p.actor then collected(p) end', """  elseif p.fire then
   if PIT_USE_REQUEST==1 and p.before.status==1 then
    local u=PIT_USES[1]
    for i=0,9 do if r('RgShotType',i)==1 and not p.fire[i]then
     assert(not u.spawn and state().status==1,'One genuine tier1 bow allocation after real Mushroom')
     u.spawn={slot=i,x=pos('RgShotX','RgShotPage',i),y=r('RgShotY',i),age=r('RgShotAge',i),at=state()}
    end end
   end
  elseif p.bridge then
   local u=PIT_USES[1]
   if u and u.spawn and p.bridge==u.spawn.slot then assert(r('MmBulletType')==27,'Actual live tier1 arrow bridge uses damage type27');u.proxy={type=27,at=state()}end
  elseif p.actor then collected(p)end""")
    edit(" if name=='HandlePowerUpCollision' then", """ if name=='FireShot'then
  p.fire={};p.before=state();for i=0,9 do p.fire[i]=r('RgShotType',i)>0 end
 elseif name=='ShotBridge'then p.bridge=r('RgSlot')
 elseif name=='HandlePowerUpCollision' then""")
    edit('  p.actor=a;p.before=state()', "  assert(a.state&128~=0,'Actual mature actor enters native physical collector');q.mature=q.mature or{actor=a,player=state()}\n  p.actor=a;p.before=state();p.score=score();p.cue=cue;p.life_cue=lifeCue")
    edit('phase=ICE_STOCK_STATE or {},controller_only=true,files=0,images=0', 'phase=PIT_STOCK or {},earned_uses=PIT_USES,pending_returns=#pending,pickup_cues=cue,life_cues=lifeCue,controller_only=true,game_state_writes=false,files=0,images=0')
    edit('local bits={a=128', "emu.addMemoryCallback(guarded('Native pickup cues',function(_,v)if entered and v==32 then cue=cue+1 elseif entered and v==64 then lifeCue=lifeCue+1 end end),emu.callbackType.write,C.ram.Square2SoundQueue)\nlocal bits={a=128")
    edit('local b=not entered and menu() or (scope() and choose(context()) or {})', 'local b=not entered and menu()or(scope()and clockInput or{})')
    edit('  entered=physical', '  entered=physical;clockInput=choose(context())')
    edit('physical<=6900','physical<=10000')
    restored=text
    for a,b in reversed(edits):assert restored.count(b)==1;restored=restored.replace(b,a,1)
    assert restored==OBSERVER.read_text()
    program='\n'.join(('local C='+value(cfg),'local travel=(function()\n'+TRAVEL.read_text()+'\nend)()',
                       'local choose=(function()\n'+POLICY+'\nend)()',text))
    program=successor(program,route)
    assert not any(t in program for t in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    LuaRuntime().compile(program)
    return program.encode()


def cold(raw,route):
    cfg=bindings(raw,route);bundle=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(bundle,0)
    for _ in range(6):W.UI.key(m,1)
    assert W.UI.menu_name(m)[0]=='PIT' and N.get(m,'PitVariant')==0
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    import check_contra_force_fast_ingress_1122 as Fast
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Fast.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    import check_bub_current_budget_1113 as Frames
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'PlayerStatus')==0 and N.get(m,'NumberofLives')==2 and N.get(m,'CrossoverBehaviorVersion')==0
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Genuine default NES Pit linked-menu entry bound')


def source(raw,route,limit):
    import inspect_rogue_missile_targets_cb95_1116 as Engine
    program=controller(raw,route);assert H(program)==PINS[route]
    with patch.object(Engine.J,'cold',lambda image:cold(image,route)),patch.object(Engine.J,'PIN',PIN):
        return Engine.run(raw,limit,text=program.decode())


def native(raw,route):
    program=controller(raw,route);assert H(program)==PINS[route]
    guard=check(ROM);candidate,script=OUT/'candidate.nes',OUT/'controller.lua';before=script.read_bytes()
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(OUT.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Host.Shared.preserve_script(script,candidate,raw)as stage:
            stage(program);q=run(script,ROM,OUT/'capture',PIN,210)
        assert q['script_SHA256']==H(program)and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--route',choices=tuple(ROUTES),default='mushroom')
    mode=p.add_mutually_exclusive_group();mode.add_argument('--source',action='store_true');mode.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=4500);a=p.parse_args();assert 800<=a.limit<=4800
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:q=native(raw,a.route)
    else:
        def deny(*args,**kwargs):raise AssertionError('NES Pit source attempted files or emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.route,a.limit)
            else:
                program=controller(raw,a.route);assert H(program)==PINS[a.route]
                q=dict(passed=True,ROM_SHA256=PIN,controller_SHA256=H(program),route_executed=False,files=0)
    print('NES_PIT_STOCK '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
