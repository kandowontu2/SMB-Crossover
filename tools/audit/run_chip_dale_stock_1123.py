"""Normal Easy 1-1 Chip/Dale food, life and Star inputs on exact3af5.

Source mode uses the declared linked-menu entry and the same Lua controller
in the owning CPU. Root alone uses --run for physical boot in the shared slot.
Historical staged mature-actor tests are separate from these authored blocks.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import run_link_family_stock_1123 as Shared
from current_ice_stock_binding_1122 import RAM_FIELDS
from check_ff_stdout_controller_source_1110 import LuaRuntime
from replay_sonic_hidden_life_f7c9_1116 import value
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

H,R,ROM,OUT,W,N=Shared.H,Shared.R,Shared.ROM,Shared.OUT,Shared.W,Shared.N
PIN='3af597a72c3ef048085de0a01e5f53443b8aa8ddf0a92d6e1882c2d225dccd1c'
CURRENT='06336f15fae4d24afa8025e972764091def63b6c01d41f206828a5105939661f'
FORMS={'chip':(0,'CHIP'),'dale':(1,'DALE')}
ROUTES={'mushroom':(0,),'upgrades':(0,1),'life':(0,3),'star':(0,2)}
PINS={('chip','mushroom'):'8f011a842d6ac9b8c447e7c25423773205ada5a750d5d77e0c1383b0e8ddac83',
      ('chip','upgrades'):'14294952b648739ad222c06111e0e8d46ce3542082c5d1e056c962d6874e36ad',
      ('chip','life'):'0f8d08c5a49b3bc8c7560be6f9d19cc073a03b418e57f5cf1479676e4b386157',
      ('chip','star'):'7f47ef83d77c110936d80d1220aa32be910ae3cd41faf494efebe4ba553a60b0',
      ('dale','mushroom'):'32c1069dbe742a01cf6a61c4e7f10929134fc338674f6b52b3d03659606991f8',
      ('dale','upgrades'):'237976db34bcd032525ce0869886c9458c87270124f764b4d290be90a33352f8',
      ('dale','life'):'3605cf38154569fdc9587f888ce3dbf08a602a39d6f2d37bc088ea78d40d441b',
      ('dale','star'):'58d6c03646d4e58d208ef856c18456c5a14df4299807209aed87b861a3032c53'}
OBSERVER=R/'tools/audit/ice_climbers_stock_observer_1122.lua'
OPENING=R/'tools/playthroughs/link_simon_ryu_policy.lua'

POLICY=r'''
local T={phase='wound',kind=0,events={}}
CHIP_STOCK=T
local untilA=0
local function sample(c)return{x=c.x,y=c.y,update=c.update,motor=c.motor,hp=c.hp,status=c.status,hurt=c.hurt,state=c.state,held=c.held}end
local function phase(c,p)
 T.phase=p;T.at=c.update;assert(#T.events<64,'Bounded natural Rescue Rangers phases')
 T.events[#T.events+1]={phase=p,kind=T.kind,player=sample(c)}
end
local function steer(c,x,n)return{right=c.x<x-n,left=c.x>x+n}end
local function floorEnemy(c)
 local e
 for i=0,5 do
  local id,st=c.r('Enemy_ID',i),c.r('Enemy_State',i)
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);local y=c.r('Enemy_Y_Position',i)
  if c.r('Enemy_Flag',i)==1 and(id==0 or id==3 or id==6)and st<32 and y>=168
     and x-c.x> -32 and x-c.x<160 and(not e or math.abs(x-c.x)<math.abs(e.dx))then
   e={slot=i,id=id,state=st,x=x,y=y,dx=x-c.x}
  end
 end
 return e
end
local function item(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==T.kind then
   return{slot=i,x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),mature=c.r('Enemy_State',i)&128~=0}
  end
 end
end
local function travel(c)
 local b=opening(c);b.b=false;b.select=false
 return b
end
return function(c)
 if c.r('CdReady')~=67 then return{}end
 if CHIP_COLLECTED then return{}end
 if T.kind==0 and CHIP_FIRST_COLLECTED and not CHIP_FIRST_AFTER then return{}end
 if T.kind==0 and CHIP_FIRST_AFTER then
  T.kind=C.expected[2];T.seen=nil;T.attempts=0
  if T.kind==1 then phase(c,'flower-wound')else phase(c,'travel')end
 end
 if T.phase=='wound'then
  if c.hp<3 then T.first_deficit=sample(c);phase(c,'recover');return{}end
  return steer(c,264,2)
 end
 if T.phase=='flower-wound'then
  if c.hp<3 then T.flower_deficit=sample(c);phase(c,'recover');return{}end
  assert(c.x<1190,'Actual second ground contact must precede the Flower block')
  local e=floorEnemy(c)
  if e and c.grounded and c.y>=160 and e.dx>0 then
   T.flower_target=T.flower_target or e
   return{right=e.dx>18}
  end
  return travel(c)
 end
 if T.phase=='recover'then
  assert(c.hp==2,'A single normal contact leaves two real HP')
  if c.hurt>0 or c.r('InjuryTimer')>0 then return{}end
  phase(c,'travel')
 end
 local goal=T.kind==0 and 336 or T.kind==1 and 1248 or T.kind==2 and 1616 or 1024
 local a=item(c)
 if a and not T.seen then T.seen=a;phase(c,'emerge')end
 if T.seen and not a then T.missing=sample(c);return{}end
 if T.phase=='travel'then
  if c.x<goal-76 then return travel(c)end
  phase(c,'align')
 end
 if T.phase=='align'then
  if not c.grounded or c.y<160 then return steer(c,goal-56,2)end
  if math.abs(c.x-(goal-5))<=2 and not c.lastA then
   T.attempts=(T.attempts or 0)+1;assert(T.attempts<=6,'Bounded actual authored block bumps')
   untilA=c.update+30;phase(c,'bump');return{a=true}
  end
  return steer(c,goal-5,2)
 end
 if T.phase=='bump'then
  if c.grounded and c.update-T.at>56 then phase(c,'align')end
  return{a=c.update<untilA}
 end
 if T.phase=='emerge'then
  if not a.mature then return steer(c,T.kind==0 and goal+66 or goal+36,2)end
  phase(c,'collect')
 end
 if T.phase=='collect'then
  if T.kind==0 then return steer(c,a.y>=148 and a.x-3 or goal+66,2)end
  if T.kind==1 and c.grounded and c.y>=160 then
   if math.abs(c.x-(goal+36))<=3 and not c.lastA then
    untilA=c.update+30;phase(c,'catch');return{left=true,a=true}
   end
   return steer(c,goal+36,2)
  end
  if T.kind>=2 and c.grounded and c.y-a.y>14 and math.abs(c.x-a.x)<30 and not c.lastA then
   untilA=c.update+30;phase(c,'catch');return{a=true}
  end
  local aim=T.kind==1 and a.x-2 or math.max(c.camera+2,a.x-3)
  if T.kind==3 then aim=math.min(aim,1091)end
  return steer(c,aim,2)
 end
 if T.phase=='catch'then
  if c.grounded and c.update-T.at>4 then phase(c,'collect')end
  local b=steer(c,a.x-2,2);b.a=c.update<untilA;return b
 end
 return{}
end
'''


@lru_cache(maxsize=8)
def bindings(raw,form,route):
    assert H(raw)==PIN and form in FORMS and route in ROUTES
    Shared.reference(raw)
    variant,name=FORMS[form];bundle=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):menu=W.UI.seed(bundle,0)
    for key in(4,2,2,2)+(32,)*variant:W.UI.key(menu,key)
    assert W.UI.menu_name(menu)[0]==name
    assert tuple(N.get(menu,n)for n in('CrossoverMenuIndex','SelectedCharacter','CdVariant'))==(13,14,variant)
    fields=[n for n in RAM_FIELDS if not n.startswith('Ic')]
    fields+='CdVariant CdHealth CdMagic CdReady CdPrevious CdHurtTimer CdHeld CdHide CdFlowers CdStars CdBoxKind CdBoxMode PlayerScoreDisplay InvPickup InvPickupOwner InjuryTimer'.split()
    ram={n:W.address(bundle,n)for n in fields}
    hooks={}
    for event,symbol in(('GameLoop','GameLoop'),('CdMovement','CdMovement'),
                         ('HandlePowerUpCollision','HandlePowerUpCollision'),
                         ('FamilyGrant','CdCollectPickup'),('Injury','CdInjury'),
                         ('PlayerHeadCollision','PlayerHeadCollision')):
        pc,at=W.address(bundle,symbol),W.location(bundle,symbol);bank=(at-16)//8192
        assert at-16==bank*8192+(pc&8191)
        hooks[event]=dict(pc=pc,tag=bank|128,offset=at-16,hex=raw[at:at+12].hex())
    if route=='life':
        pc,bank=0x8987,126;at=16+bank*8192+(pc&8191)
        assert raw[at:at+3]==b'\xee'+ram['NumberofLives'].to_bytes(2,'little')
        hooks['LifeCredit']=dict(pc=pc,tag=bank|128,offset=at-16,hex=raw[at:at+8].hex())
    nav=[]
    for i in range(32):
        row,col=divmod(i,8)
        nav.append('down'if row in(0,3)else'up'if row==2 else'right'if col<5 else'left'if col>5 else'')
    return dict(sha=PIN,form=form,name=name,char=14,slot=13,variant=variant,mode_value=0,
                route=route,expected=list(ROUTES[route]),ram=ram,hooks=hooks,navigation=nav)


def controller(raw,form,route):
    cfg=bindings(raw,form,route);text=OBSERVER.read_text();edits=[]
    def edit(a,b):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b,1);edits.append((a,b))
    edit("assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha", "assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha")
    edit("r('SelectedCharacter')==20 and r('IcVariant')==C.variant", "r('SelectedCharacter')==14 and r('CdVariant')==C.variant")
    edit("r('IcVariant')~=C.variant", "r('CdVariant')~=C.variant")
    edit("local expected=C.route=='life' and {0,3} or {0,1,2}", 'local expected=C.expected')
    edit("state=r('Enemy_State',i),x=pos('Enemy_X_Position','Enemy_PageLoc',i),",
         "state=r('Enemy_State',i),stamp=r('InvPickup',i),owner=r('InvPickupOwner',i),x=pos('Enemy_X_Position','Enemy_PageLoc',i),")
    edit("power=r('IcPower')", "power=r('PlayerStatus'),hp=r('CdHealth'),hurt=r('CdHurtTimer'),held=r('CdHeld'),flowers=r('CdFlowers'),stars=r('CdStars'),growth=0")
    edit('c.poll=polls;c.char=20;', 'c.poll=motor;c.char=14;c.update=motor;')
    edit('c.lastA=mask&128~=0', "c.lastA=r('CdPrevious')&128~=0")
    edit('local lifePending', "local lifePending\nlocal clockInput={}\nlocal injuries={}\nlocal cue=0\nlocal lifeCue=0\nlocal function score()local n=0;for i=0,5 do n=n*10+r('PlayerScoreDisplay',i)end;return n end")
    edit('Living Ice Climber','Living requested Rescue Ranger')
    edit("assert(updates<5100,'Bounded pickup route')", "assert(updates<4400 and s.hp>0 and s.yHigh<2 and(s.lives==2 or(C.route=='life'and checks['3'].grant and s.lives==3)),'Bounded living natural Rescue Rangers route')\n assert(r('CdMagic')==165 and r('CdReady')==67 and s.flowers==0 and s.stars==0,'Original health family without invented currency')")
    edit('local a=actor(i);local q=checks[tostring(a.kind)]', "local a=actor(i);local q=checks[tostring(a.kind)]\n  if q and q.birth and a.slot==q.birth.actor.slot and a.flag>0 and a.id==46 and a.state&128~=0 and not q.mature then q.mature={actor=a,player=s}end")
    edit('q.birth={actor=a,player=s}', "assert(heads[tostring(a.kind)],'Actual authored block bump precedes item birth');q.birth={actor=a,player=s}")
    edit(' local complete=true', """ if checks['0'].collect then CHIP_FIRST_COLLECTED=true end
 if checks['0'].after then CHIP_FIRST_AFTER=true end
 local target=checks[tostring(C.expected[#C.expected])]
 if target.collect then CHIP_COLLECTED=true end
 if CHIP_STOCK.missing and not target.collect then finish(false,'Authored target disappeared before actual collection');return end
 for _,kind in ipairs(expected)do local q=checks[tostring(kind)]
  if q.collect and not q.grant and kind~=3 and score()>=q.collect.score_before+1000 then q.grant=s end
 end
 local complete=true""")
    edit('if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope() then','if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope()and s.state==0 then')
    edit("else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end", "else assert(s.hp==3 and s.hp==q.grant.hp and s.status==q.grant.status and score()>=q.collect.score_before+1000,'Earned healing and food status persist')end")
    edit("if kind==3 then assert(s.lives==q.grant.lives,'Earned life persists during movement')", "if kind==3 then assert(s.lives==q.grant.lives and lifeCue>q.collect.life_cue_before,'Native life and cue persist')")
    edit("elseif kind==2 then assert(s.star>0,'Earned Star persists during movement')", "elseif kind==2 then assert(s.star>0 and score()>=q.collect.score_before+1000,'Native Star and score persist')")
    edit("if complete then finish(true,'Authored pickups, native credit and 25 further movement updates') end", "if complete then assert(#pending==0 and not lifePending,'All observed native workers returned');finish(true,'Natural Rescue Rangers items, real effects and25 movement returns');return end\n clockInput=scope()and choose(context())or{}")
    edit("assert(r('Square2SoundQueue')&32~=0,'Actual pickup cue')", "assert(cue>p.cue,'New native pickup cue')")
    edit("sound=r('Square2SoundQueue')}", "sound=r('Square2SoundQueue'),score_before=p.score,life_cue_before=p.life_cue}")
    edit("assert(p.before.power==a.kind and s.power==a.kind+1 and s.status==s.power,'Normal Ice power tier transition')", """assert(q.family and q.family.update==updates and q.family.before.hp==p.before.hp and q.family.after.hp==s.hp,
   'Matched native family collector and physical item return')
  assert(p.before.hp<3 and s.hp==(a.kind==0 and math.min(3,p.before.hp+1)or 3)and s.status==(a.kind~1),
         'Actual deficit receives original Mushroom plus1 or Flower full3')""")
    edit(' q.grant=s\nend',' -- Wait for actual native popup credit before the25 movement gate.\nend')
    edit("if p.name=='IcMovement' then", "if p.name=='CdMovement' then")
    edit('  elseif p.actor then collected(p) end', """  elseif p.family then
   local q=checks[tostring(p.family.kind)];local s=state()
   assert(cpu['cpu.ps']&1==1,'Original food collector accepts with carry')
   q.family={update=updates,before=p.before,after=s,stamp=p.family.stamp,owner=p.family.owner}
  elseif p.injury then
   local s=state()
   if s.hp==p.before.hp-1 then
    assert(p.injury.flag==1 and p.injury.id<21 and s.hurt==60,'Genuine stock enemy makes original oneHP deficit')
    injuries[#injuries+1]={before=p.before,after=s,actor=p.injury}
   end
  elseif p.actor then collected(p)end""")
    edit(" if name=='HandlePowerUpCollision' then", """ if name=='FamilyGrant'then
  local i=cpu['cpu.x'];local kind=r('PowerUpType',i);local q=checks[tostring(kind)]
  if not(q and q.birth and not q.collect and kind<2)then return end
  assert(i==q.birth.actor.slot and r('Enemy_Flag',i)>0 and r('Enemy_ID',i)==46 and r('Enemy_State',i)&128~=0
         and r('InvPickup',i)==q.birth.actor.stamp and r('InvPickupOwner',i)==q.birth.actor.owner,
         'Same naturally born mature actor enters original food grant before native erase')
  p.family={kind=kind,stamp=r('InvPickup',i),owner=r('InvPickupOwner',i)};p.before=state()
 elseif name=='Injury'then p.injury=actor(r('ObjectOffset'));p.before=state()
 elseif name=='HandlePowerUpCollision' then""")
    edit('  p.actor=a;p.before=state()', "  assert(a.state&128~=0,'Mature authored actor enters real native collision');q.mature=q.mature or{actor=a,player=state()}\n  p.actor=a;p.before=state();p.score=score();p.cue=cue;p.life_cue=lifeCue")
    edit('phase=ICE_STOCK_STATE or {},controller_only=true,files=0,images=0', 'phase=CHIP_STOCK or {},injuries=injuries,pending_returns=#pending,pickup_cues=cue,life_cues=lifeCue,controller_only=true,game_state_writes=false,files=0,images=0')
    edit('local bits={a=128', "emu.addMemoryCallback(guarded('Native pickup cues',function(_,v)if entered and v==32 then cue=cue+1 elseif entered and v==64 then lifeCue=lifeCue+1 end end),emu.callbackType.write,C.ram.Square2SoundQueue)\nlocal bits={a=128")
    edit('local b=not entered and menu() or (scope() and choose(context()) or {})', 'local b=not entered and menu()or(scope()and clockInput or{})')
    edit('  entered=physical', '  entered=physical;clockInput=choose(context())')
    edit('physical<=6900','physical<=10000')
    if route in('life','star'):
        extra=""" if a.kind>=2 then
  assert(s.hp==p.before.hp and s.status==p.before.status and s.held==p.before.held
         and s.flowers==p.before.flowers and s.stars==p.before.stars,
         'Native Star/life preserves actual health, food appearance and carrying state')
 end
"""
        edit(' if a.kind<2 then',extra+' if a.kind<2 then')
        for message in("'Native life and cue persist'","'Native Star and score persist'"):
            edit(','+message,' and s.hp==q.grant.hp and s.status==q.grant.status and s.held==q.grant.held,'+message)
    restored=text
    for a,b in reversed(edits):assert restored.count(b)==1;restored=restored.replace(b,a,1)
    assert restored==OBSERVER.read_text()
    policy=POLICY
    if route=='upgrades':
        old="  local e=floorEnemy(c)\n  if e and c.grounded and c.y>=160 and e.dx>0 then"
        new='''  local e=floorEnemy(c);local clear=true
  if e then
   local function solid(t)return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 end
   for x=c.x+20,e.x-8,16 do
    if solid(c.block(x,c.y+8))or solid(c.block(x,c.y+24))or not solid(c.block(x,c.y+34))then clear=false end
   end
  end
  if e and clear and c.grounded and c.y>=160 and e.dx>0 then'''
        assert policy.count(old)==1;policy=policy.replace(old,new,1)
    opening=OPENING.read_text()
    if route in('life','star'):
        old='''local function travel(c)
 local b=opening(c);b.b=false;b.select=false
 return b
end'''
        new='''local function travel(c)
 if T.hop then
  local h=T.hop;local age=c.update-h.at
  if c.grounded and age>4 then h.landing=sample(c);T.hop=nil
  else
   if not c.grounded and c.vy>=128 then h.takeoff=h.takeoff or sample(c)end
   assert(age<120,'Bounded native jump over a live ground enemy')
   return{right=true,a=age<30}
  end
 end
 local e=floorEnemy(c)
 if e and e.dx>0 and e.dx<=80 and c.grounded and c.y>=160 and not c.lastA then
  T.hops=T.hops or{};assert(#T.hops<16,'Bounded ordinary ground-enemy jumps')
  local h={at=c.update,before=sample(c),enemy=e};T.hops[#T.hops+1]=h;T.hop=h
  return{right=true,a=true}
 end
 local b=opening(c);b.b=false;b.select=false
 return b
end'''
        assert policy.count(old)==1;policy=policy.replace(old,new,1)
        old='if e and math.abs(e.dx)<(c.char==5 and 43 or 31)and math.abs(e.y-c.y)<32 and c.grounded then'
        new='if c.char~=14 and e and math.abs(e.dx)<(c.char==5 and 43 or 31)and math.abs(e.y-c.y)<32 and c.grounded then'
        assert opening.count(old)==1;opening=opening.replace(old,new,1)
    if route=='star':
        old='if not c.grounded or c.y<160 then return steer(c,goal-56,2)end'
        new='''if c.y<160 and not T.upper_exit_complete then T.upper_exit=true end
  if T.upper_exit then
   if c.grounded and c.y>=160 then T.upper_exit=nil;T.upper_exit_complete=sample(c)
   else return{right=c.x<goal+40,left=c.x>goal+44}end
  end
  if not c.grounded or c.y<160 then return steer(c,goal-56,2)end'''
        assert policy.count(old)==1;policy=policy.replace(old,new,1)
    program='\n'.join(('local C='+value(cfg),'local opening=(function()\n'+opening+'\nend)()',
                       'local choose=(function()\n'+policy+'\nend)()',text))
    assert not any(t in program for t in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    LuaRuntime().compile(program)
    return program.encode()


def cold(raw,form,route):
    cfg=bindings(reference(raw),form,route);bundle=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(bundle,0)
    for key in(4,2,2,2)+(32,)*cfg['variant']:W.UI.key(m,key)
    assert W.UI.menu_name(m)[0]==cfg['name'] and N.get(m,'CdVariant')==cfg['variant']
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    import check_contra_force_fast_ingress_1122 as Fast
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Fast.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    import check_bub_current_budget_1113 as Frames
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'NumberofLives')==2 and N.get(m,'CrossoverBehaviorVersion')==0
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual selected Rescue Rangers menu entry bound')


@lru_cache(maxsize=2)
def reference(raw):
    if H(raw)==PIN:return raw
    import compose_dkjr_head_bridge_current_1123 as Bridge
    assert H(raw)==CURRENT==Bridge.CANDIDATE and Bridge.PIN==PIN
    parent=Bridge.inverse(raw)
    assert H(parent)==PIN
    return parent


def native_program(raw,form,route):
    parent=reference(raw);program=controller(parent,form,route)
    assert H(program)==PINS[(form,route)]
    cfg=bindings(parent,form,route)
    for name,hook in cfg['hooks'].items():
        at=16+hook['offset'];expected=bytes.fromhex(hook['hex'])
        assert parent[at:at+len(expected)]==raw[at:at+len(expected)]==expected,name
    if H(raw)==PIN:return program
    import compose_dkjr_head_bridge_current_1123 as Bridge
    # All host/native Chip code, menu data, collisions and gameplay tables
    # remain exact. Only DK Jr.'s independently authenticated cookie changes
    # within PRG; the inverse also authenticates its three CHR envelopes.
    at=Bridge.COOKIE_AT;end=16+128*8192
    assert parent[:at]==raw[:at] and parent[at+16:end]==raw[at+16:end]
    assert all(not(16+h['offset']<at+16 and at<16+h['offset']+len(bytes.fromhex(h['hex'])))for h in cfg['hooks'].values())
    assert program.count(PIN.encode())==1
    rebound=program.replace(PIN.encode(),CURRENT.encode(),1)
    assert rebound.replace(CURRENT.encode(),PIN.encode(),1)==program
    LuaRuntime().compile(rebound.decode())
    return rebound


def source(raw,form,route,limit):
    import inspect_rogue_missile_targets_cb95_1116 as Engine
    program=native_program(raw,form,route)
    with patch.object(Engine.J,'cold',lambda image:cold(image,form,route)),patch.object(Engine.J,'PIN',H(raw)):
        return Engine.run(raw,limit,text=program.decode())


def native(raw,form,route):
    program=native_program(raw,form,route);expected=H(raw)
    guard=check(ROM);candidate,script=OUT/'candidate.nes',OUT/'controller.lua';before=script.read_bytes()
    assert guard['ROM_sha256']==expected and not guard['matching_patch_files']
    assert set(OUT.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Shared.preserve_script(script,candidate,raw)as stage:
            stage(program);q=run(script,ROM,OUT/'capture',expected,200)
        assert q['script_SHA256']==H(program)and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--form',choices=tuple(FORMS),default='chip')
    p.add_argument('--route',choices=tuple(ROUTES),default='mushroom')
    mode=p.add_mutually_exclusive_group();mode.add_argument('--source',action='store_true');mode.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=4200);a=p.parse_args();assert 1000<=a.limit<=4600
    raw=ROM.read_bytes();reference(raw)
    if a.run:q=native(raw,a.form,a.route)
    else:
        def deny(*args,**kwargs):raise AssertionError('Chip/Dale source attempted files or emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.form,a.route,a.limit)
            else:
                program=native_program(raw,a.form,a.route)
                q=dict(passed=True,ROM_SHA256=H(raw),reference_SHA256=PIN,controller_SHA256=H(program),reference_controller_SHA256=PINS[(a.form,a.route)],route_executed=False,files=0)
    print('CHIP_DALE_STOCK '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
