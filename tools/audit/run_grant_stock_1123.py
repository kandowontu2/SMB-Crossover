"""Exact82e8/ffd708 Grant Easy natural pickups, healing and dagger use.

Source declares linked real-menu/Start entry; Root alone may --run using the
existing two-file slot. Ordinary controls only, no actor/resource/state seeds.
Retained Hard clears and mature-actor component receipts keep their old scope.
"""
import argparse
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import run_alucard_stock_1123 as Family
import inspect_rogue_missile_targets_cb95_1116 as Engine

Stock,W,N,H,ROM=Family.Stock,Family.W,Family.N,Family.H,Family.ROM
PIN='82e8da0e293dee91da441347dfe4c675c88708c43b0b88d4fbd253312f00a131'
CURRENT='ffd7081036bca9cb165d9f4c5527e909126df70f993b4ebec75b7dd7ac83a6b1'
PINS={
 PIN:{'mushroom':'decbd84a67385b8ca0b7d4c8fe42a77bc0fd63def2ca350a2a19078aa2c46f25',
      'upgrades':'bb28825a0e77b14c743457a4c1c6aac95acc9a21f4ff2b9511bb2b7092824cba',
      'life':'faf94a404a6edba848c0b25bfaa2f97ace157623dec65ef43554f001e5c6db9c',
      'star':'e144e8014f3349a8d9d2328681d1cf56dd76802311faf7474ea80432cd0a5be4'},
 CURRENT:{'mushroom':'23c4fb8ed060e0e44ee6dc2b83dbc4db38fe80abf151c61b7cea070ca3abfce7',
          'upgrades':'0a5fd0c893da1230c26d11a23766aeddb57ecb593f2f5a03c0271dc356778c01',
          'life':'4a6e15b86baea5b01c829c08616c354f6e53cb35faa4d849af0e6215d37a32ba',
          'star':'fec710ae187bf093f0b6d3c526b83886c08a45f3806a02f99d8bb66123b42330'},
}
ROUTES=('mushroom','upgrades','life','star')

POLICY=r'''
local T={kind=0,phase='real-deficit',events={}}
ROBOT_STOCK_STATE=T
local function sample(c)return{x=c.x,y=c.y,update=c.update,hp=c.hp,hearts=c.hearts,sub=c.sub,state=c.state,climb=c.climb}end
local function phase(c,p)
 T.phase=p;T.at=c.update;assert(#T.events<50,'Bounded normal Grant phases')
 T.events[#T.events+1]={kind=T.kind,phase=p,player=sample(c)}
end
local function steer(c,x,n)return{right=c.x<x-n,left=c.x>x+n}end
local function target(c)
 for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==T.kind then
  return{slot=i,x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),mature=c.r('Enemy_State',i)&128~=0}
 end end
end
local function solid(c,x,y)local t=c.block(x,y);return t~=0 and t~=35 and t~=38 and t~=194 and t~=195 end
local function defend(c,b)
 local e=c.enemy()
 if e and e.dx>-8 and e.dx<34 and math.abs(e.y-c.y)<32 and c.grounded and c.climb==0 then
  local face=e.dx>=0 and 1 or 2
  if c.r('PlayerFacingDir')~=face then return{right=face==1,left=face==2}end
  return{b=c.r('Cv3AttackAge')==0 and c.r('Cv3Previous')&64==0}
 end
 return b
end
local function travel(c)
 if c.climb~=0 then return{right=c.climb==1,left=c.climb==2,up=true}end
 local b={right=true}
 local obstacle=solid(c,c.x+34,c.y+24)or solid(c,c.x+34,c.y+8)
 local floor=solid(c,c.x+28,math.min(c.y+40,232))
 if c.grounded and not c.lastA and c.r('Cv3AttackAge')==0 and(obstacle or not floor)then T.jump=c.update;b.a=true
 elseif not c.grounded then b.a=T.jump and c.update-T.jump<30 end
 return defend(c,b)
end
return function(c)
 if T.phase=='real-deficit'then
  if not GRANT_REAL_INJURY then return{right=c.x<240}end
  assert(c.hp==60,'Original4HP opener damage remains until real healing')
  T.injury=GRANT_REAL_INJURY
  if c.hurt~=0 or not c.grounded then return{}end
  phase(c,'travel')
 end
 if GRANT_FIRST_AFTER then
  if C.route=='mushroom'then return{}end
  if T.kind==0 then T.kind=1;T.actor=nil;T.missing=nil;T.attempts=0;phase(c,'travel')end
 end
 if GRANT_FLOWER_AFTER then
  if not T.use then T.use={requested=sample(c)}end
  local u=T.use
  if u.paid then return{}end
  if c.r('PlayerFacingDir')~=1 then return{right=true}end
  if not c.grounded or c.climb~=0 or c.r('Cv3AttackAge')~=0 or c.r('Cv3Previous')&64~=0 then return{}end
  for i=0,3 do if c.r('Cv3ShotType',i)~=0 then return{}end end
  assert(c.sub==1 and c.hearts==u.requested.hearts and c.hearts>=5 and c.hp==64,'Genuinely earned dagger and native heart stock before use')
  GRANT_USE_REQUEST=true;return{up=true,b=true}
 end
 if GRANT_TARGET_COLLECTED then return{}end
 local goal=T.kind==0 and 336 or 1248
 local a=target(c)
 if a and not T.actor then T.actor=a;phase(c,'emerge')end
 if T.actor and not a then T.missing=T.missing or sample(c);return{}end
 if T.phase=='travel'then
  if c.x<goal-76 then return travel(c)end
  phase(c,'align')
 end
 if T.phase=='align'then
  if not c.grounded or c.y<160 then return defend(c,steer(c,goal-56,2))end
  if math.abs(c.x-(goal-5))<=2 and not c.lastA and c.r('Cv3AttackAge')==0 then
   T.attempts=(T.attempts or 0)+1;assert(T.attempts<=6,'Bounded real authored Grant bump')
   phase(c,'bump');return{a=true}
  end
  return defend(c,steer(c,goal-5,2))
 end
 if T.phase=='bump'then
  if c.grounded and c.update-T.at>60 then phase(c,'align')end
  return{a=c.update-T.at<30}
 end
 if T.phase=='emerge'then
  if not a.mature then return defend(c,steer(c,goal+(T.kind==0 and 66 or 36),2))end
  phase(c,'collect')
 end
 if T.phase=='collect'then
  if T.kind==0 then return defend(c,steer(c,a.y>=148 and a.x-3 or goal+66,2))end
  if c.climb~=0 then return{left=c.climb==2,right=c.climb==1,up=true}end
  if c.grounded and c.y>=160 then
   if math.abs(c.x-(goal+36))<=2 and not c.lastA then phase(c,'catch');return{left=true,a=true}end
   return defend(c,steer(c,goal+36,2))
  end
  return defend(c,steer(c,a.x-2,2))
 end
 if T.phase=='catch'then
  if c.climb~=0 then return{left=c.climb==2,right=c.climb==1,up=true}end
  if c.grounded and c.update-T.at>4 then phase(c,'collect')end
  local b=steer(c,a.x-2,2);b.a=c.update-T.at<30;return b
 end
 return{}
end
'''

WEAPON_OBSERVER=r'''
local function grantWeapon(p)
 local T=ROBOT_STOCK_STATE;local u=T.use
 if not u or not GRANT_USE_REQUEST then return end
 local s=state()
 if not u.paid then
  if s.hearts==p.weapon.hearts then return end
  assert(p.weapon.hearts==u.requested.hearts and s.hearts==p.weapon.hearts-1 and s.sub==1 and r('Cv3AttackKind')==2 and r('Cv3AttackAge')==22,
   'Fresh ordinary Up+B pays one genuinely earned heart for the dagger')
  u.paid={before=p.weapon,after=s}
 end
 for i=0,3 do if r('Cv3ShotType',i)~=0 then
  assert(r('Cv3ShotType',i)==1,'Earned Grant dagger owns the otherwise empty native pool')
  local q={slot=i,age=r('Cv3ShotAge',i),x=pos('Cv3ShotX','Cv3ShotPage',i)*256+r('Cv3ShotFx',i),
   y=r('Cv3ShotY',i)*256+r('Cv3ShotFy',i),vx=r('Cv3ShotVXLo',i)+256*r('Cv3ShotVXHi',i),
   vy=r('Cv3ShotVYLo',i)+256*r('Cv3ShotVYHi',i),at=s}
  assert(q.vx==1024 and q.vy==0,'Native right dagger has original4px horizontal velocity')
  if not u.spawn then assert(q.age==1,'Actual new dagger allocation');u.spawn=q
  elseif not u.moved then
   assert(q.slot==u.spawn.slot and q.age==u.spawn.age+1 and q.x-u.spawn.x==1024 and q.y==u.spawn.y,
    'Earned dagger moves on the next actual weapon return')
   u.moved=q
  end
 end end
 if u.spawn and not u.retired and r('Cv3ShotType',u.spawn.slot)==0 then
  assert(u.moved,'Native dagger really moved before retirement');u.retired=s
 end
end
'''




REMAINING_CATCH=r"""
  if T.kind>=2 then
   if T.kind==2 and a.x<goal+80 then
    if math.abs(c.x-(goal+51))>2 then return defend(c,steer(c,goal+51,2))end
    if c.grounded and not c.lastA and a.y>=110 and math.abs(a.x-c.x-6)<=13 then
     phase(c,'catch');return{right=true,a=true}
    end
    return{}
   end
   local x=math.max(c.camera+2,a.x-3);if T.kind==3 then x=math.min(x,1091)end
   if c.grounded and not c.lastA and math.abs(a.x-c.x)<28 and c.y-a.y>12 then
    phase(c,'catch');local b=steer(c,x,2);b.a=true;return b
   end
   return defend(c,steer(c,x,2))
  end
"""


STAR_GAP=r"""
 if C.route=='star'and T.kind==2 and(c.x>=1328 and c.x<1440 or T.gap and T.gap.phase=='air')then
  local g=T.gap
  if not g then g={phase='approach'};T.gap=g end
  if g.phase=='approach'then
   if not c.grounded then return{right=true}end
   if c.x<1368 then return{right=true}end
   if c.lastA then return{}end
   g.terrain={left=1376,right=1424,y=208,lip=c.block(c.x,208),insideLeft=c.block(1384,208),insideRight=c.block(1416,208),far=c.block(1432,208)}
   assert(c.x<=1370 and c.y==176 and solid(c,c.x,208)and not solid(c,1384,208)and not solid(c,1416,208)and solid(c,1432,208),
    'Actual supported second-gap lip, empty span and far bank before ordinary jump')
   g.takeoff=sample(c);g.takeoff.held=c.r('Cv3Previous');g.phase='air';T.jump=c.update;return{right=true,a=true}
  end
  if g.phase=='air'then
   if not g.accepted and not c.grounded and c.r('Cv3Previous')&128~=0 then g.accepted=sample(c);g.accepted.held=c.r('Cv3Previous');g.accepted.vy=c.vy end
   if not g.rise and c.y<g.takeoff.y and c.vy>=128 then g.rise=sample(c);g.rise.vy=c.vy end
   if c.grounded and c.update-g.takeoff.update>4 then
    assert(g.accepted and g.rise and c.x>=1400 and c.y==176,'Actual fresh-A arc reaches native far-bank landing')
    g.landing=sample(c);g.phase='complete';return{right=true}
   end
   assert(c.update-g.takeoff.update<75,'Bounded ordinary Grant second-gap arc')
   return{right=true,a=c.update-g.takeoff.update<35}
  end
 end
"""


def remaining(program,route):
 if route not in('life','star'):return program
 original=program;edits=[]
 def change(a,b):
  nonlocal program
  assert program.count(a)==1,(a,program.count(a))
  program=program.replace(a,b,1);edits.append((a,b))
 change("T.kind=1;T.actor=nil","T.kind=C.expected[2];T.actor=nil")
 change("local goal=T.kind==0 and 336 or 1248","local goal=T.kind==0 and 336 or T.kind==1 and 1248 or T.kind==2 and 1616 or 1024")
 change(" if T.phase=='collect'then\n"," if T.phase=='collect'then\n"+REMAINING_CATCH)
 change("s.yHigh<2 and s.hp>0 and s.lives==2","s.yHigh<2 and s.hp>0 and(s.lives==2 or(C.route=='life'and checks['3'].grant and s.lives==3))")
 change("if complete and(C.route=='mushroom'or(stock.use and stock.use.after))then","if complete then")
 change("s.lives==q.grant.lives and (cues[64]or 0)>q.collect.life_cue,'Earned life and cue persist'","s.lives==q.grant.lives and (cues[64]or 0)>q.collect.life_cue and s.hp==q.grant.hp and s.hearts==q.grant.hearts and s.sub==q.grant.sub,'Earned life, cue and actual CV3 records persist'")
 change("s.star>0 and score()>=q.collect.score_before+1000,'Earned Star and score persist'","s.star>0 and score()>=q.collect.score_before+1000 and s.hp==q.grant.hp and s.hearts==q.grant.hearts and s.sub==q.grant.sub,'Earned Star, score and actual CV3 records persist'")
 if route=='star':change('local function travel(c)\n','local function travel(c)\n'+STAR_GAP)
 restored=program
 for a,b in reversed(edits):
  assert restored.count(b)==1;restored=restored.replace(b,a,1)
 assert restored==original
 return program


@lru_cache(maxsize=2)
def origin(raw):
    """Authenticate only the two named images; keep the exact82 source fixture."""
    if H(raw)==PIN:return raw
    import compose_dkjr_mushroom_slot_order_1123 as Order
    import compose_dkjr_mushroom_scrooge_1123 as Previous
    assert H(raw)==CURRENT==Order.CANDIDATE
    middle=Order.inverse(raw);assert H(middle)==Previous.CANDIDATE
    parent=Previous.inverse(middle);assert H(parent)==PIN==Previous.PIN
    return parent


@lru_cache(maxsize=2)
def bindings(raw,route):
    assert H(raw)==PIN and route in ROUTES
    parent=Family.reference(raw)
    cfg=deepcopy(Stock.bindings(parent,'simon',route));cfg.update(sha=PIN,form='grant',name='GRANT',variant=1)
    b=dict(W.Symbols.bundle(),raw=raw)
    for n in ('Cv3Variant','Cv3Health','Cv3Hearts','Cv3Subweapon','Cv3Previous','Cv3AttackAge','Cv3AttackKind',
              'Cv3HurtAge','Cv3Invul','Cv3Climb','InvPickup','InvPickupOwner','Cv3PickupVariant','Cv3ShotType',
              'Cv3ShotAge','Cv3ShotX','Cv3ShotPage','Cv3ShotY','Cv3ShotFx','Cv3ShotFy','Cv3ShotVXLo',
              'Cv3ShotVXHi','Cv3ShotVYLo','Cv3ShotVYHi','GamePauseStatus'):
        cfg['ram'][n]=W.address(b,n)
    for event,name in (('Movement','Cv3MovementGate'),('FamilyCollect','Cv3CollectPickupGate'),
                       ('Injury','Cv3InjuryStartGate'),('Weapons','Cv3WeaponsGate')):
        pc,at=W.address(b,name),W.location(b,name)
        cfg['hooks'][event]=dict(pc=pc,tag=((at-16)//8192)|128,offset=at-16,hex=raw[at:at+12].hex())
    for event,h in cfg['hooks'].items():
        at=16+h['offset'];assert raw[at:at+len(bytes.fromhex(h['hex']))]==bytes.fromhex(h['hex']),event
    return cfg


def base_controller(raw,route):
    cfg=bindings(raw,route)
    old=Stock.controller(Family.reference(raw),'simon',route).decode()
    marker="assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha"
    assert old.count(marker)==1;text=old[old.index(marker):];baseline=text;edits=[]
    def edit(a,b):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b,1);edits.append((a,b))
    edit(marker,"assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha")
    edit("assert(r(C.variant_field)&C.variant_mask==0,'Original identity in menu')", "if r(C.variant_field)~=C.variant then return pulse('select')end")
    edit('r(C.variant_field)&C.variant_mask==0','r(C.variant_field)==C.variant')
    edit("power=r('PlayerStatus'),growth=r('GuestPowerupActive')",
         "power=r('PlayerStatus'),growth=r('GuestPowerupActive'),hp=r('Cv3Health'),hearts=r('Cv3Hearts'),sub=r('Cv3Subweapon'),climb=r('Cv3Climb'),hurt=r('Cv3HurtAge'),invul=r('Cv3Invul')")
    edit("c.lastA=r('PreviousA_B_Buttons')&128~=0", "c.lastA=r('Cv3Previous')&128~=0")
    edit("kind=r('PowerUpType',i),", "kind=r('PowerUpType',i),stamp=r('InvPickup',i),owner=r('InvPickupOwner',i),variant=r('Cv3PickupVariant',i),")
    edit("assert(updates<5100 and s.yHigh<2,'Bounded living pickup route')",
         "assert(updates<3000 and s.yHigh<2 and s.hp>0 and s.lives==2,'Bounded living normal Grant route')")
    edit(' local complete=true', """ if checks['0'].after then GRANT_FIRST_AFTER=true end
 if C.route=='upgrades'and checks['1'].after then GRANT_FLOWER_AFTER=true end
 if checks[tostring(C.expected[#C.expected])].collect then GRANT_TARGET_COLLECTED=true end
 local use=stock.use
 if use and use.retired and not use.after and s.motor-use.retired.motor>=25 and scope()and s.state==0 then
  assert(s.hp==64 and s.hearts==use.paid.after.hearts and s.sub==1 and s.status==1 and r('Cv3AttackAge')==0,'Paid earned dagger and health persist25 returned movement workers')
  use.after=s
 end
 local complete=true""")
    edit("assert(p.before.power==a.kind and s.growth~=0 and r('GuestPowerupTarget')==a.kind+1,'Actual source growth');return", """assert(a.owner==5 and a.variant==1 and a.stamp==(a.kind==0 and 208 or 209),'Actual Grant pickup ownership and D0/D1 metadata')
  assert(s.status==1 and s.growth==0,'Original immediate CV3 reward without invented growth')
  if a.kind==0 then
   assert(GRANT_REAL_INJURY and p.before.hp==60 and s.hp==64 and s.hearts==p.before.hearts and s.sub==0,'Real deficit heals16 capped64 after natural Mushroom')
  else assert(p.before.sub==0 and s.sub==1 and s.hearts==math.min(99,p.before.hearts+5)and s.hp==64,'Natural first Flower grants dagger and five hearts')end
  return""")
    edit('if q.collect and not q.grant and kind<2 and s.growth==0 and s.status==kind+1',
         'if q.collect and not q.grant and kind<2 and s.growth==0 and s.status==1 and s.hp==64 and(kind==0 or s.sub==1)')
    edit("else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end",
         "else assert(s.status==1 and s.hp==64 and s.sub==q.grant.sub and s.hearts==q.grant.hearts,'Actual earned CV3 reward persists')end")
    edit("if complete then finish(true,", "if complete and(C.route=='mushroom'or(stock.use and stock.use.after))then assert(#pending==0,'All hooked native workers returned');finish(true,")
    edit('local function settle()',WEAPON_OBSERVER+'\nlocal function settle()')
    edit("  elseif p.name=='GameLoop' then afterMain()", """  elseif p.weapon then grantWeapon(p)
  elseif p.injury then
   local s=state()
   if p.injury.hp==64 and s.hp==60 then
    assert(not GRANT_REAL_INJURY and p.victim.flag>0 and p.victim.id==6 and p.victim.state<32 and s.invul==64 and s.hurt==16,
     'Naturally spawned live opener Goomba causes original4HP injury')
    GRANT_REAL_INJURY={before=p.injury,after=s,actor=p.victim}
   end
  elseif p.name=='GameLoop' then afterMain()""")
    edit(" if name=='HandlePowerUpCollision' then", """ if name=='Weapons'then p.weapon=state()
 elseif name=='Injury'then p.injury=state();p.victim=actor(r('ObjectOffset'))
 elseif name=='HandlePowerUpCollision' then""")
    edit('phase=ROBOT_STOCK_STATE or {},sound_cues=cues,controller_only=true,files=0,images=0',
         'phase=ROBOT_STOCK_STATE or {},injury=GRANT_REAL_INJURY,sound_cues=cues,pending_returns=#pending,controller_only=true,game_state_writes=false,files=0,images=0')
    restored=text
    for a,b in reversed(edits):assert restored.count(b)==1;restored=restored.replace(b,a,1)
    assert restored==baseline
    program='local C='+Stock.value(cfg)+'\nlocal choose=(function()\n'+POLICY+'\nend)()\n'+text
    assert not any(t in program for t in('emu.write','emu.setState','saveState','loadState','io.open','dofile','takeScreenshot'))
    Stock.LuaRuntime().compile(program)
    return program.encode()


def controller(raw,route):
    parent=origin(raw);program=base_controller(parent,route)
    if raw!=parent:
        for name,h in bindings(parent,route)['hooks'].items():
            at=16+h['offset'];assert raw[at:at+len(bytes.fromhex(h['hex']))]==bytes.fromhex(h['hex']),name
        assert program.count(PIN.encode())==1
        rebound=program.replace(PIN.encode(),H(raw).encode(),1)
        assert rebound.replace(H(raw).encode(),PIN.encode(),1)==program
        program=rebound
    program=remaining(program.decode(),route).encode()
    Stock.LuaRuntime().compile(program.decode())
    return program


def cold(raw):
    origin(raw)
    b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for _ in range(5):W.UI.key(m,1)
    W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]=='GRANT'and N.get(m,'SelectedCharacter')==5 and N.get(m,'Cv3Variant')==1
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Family.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'Cv3Health')==64 and N.get(m,'Cv3Hearts')==10 and N.get(m,'Cv3Subweapon')==0
            assert N.get(m,'NumberofLives')==2 and N.get(m,'CrossoverBehaviorVersion')==0
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Engine.Frames.frame(m,cold=True)
    raise AssertionError('Actual Grant linked menu entry bound')


def source(raw,route,limit):
    program=controller(raw,route);assert H(program)==PINS[H(raw)][route]
    with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',H(raw)):return Engine.run(raw,limit,text=program.decode())


def native(raw,route):
    program=controller(raw,route);assert H(program)==PINS[H(raw)][route]
    out=Stock.OUT;candidate,script=out/'candidate.nes',out/'controller.lua';before=script.read_bytes();guard=Stock.check(ROM)
    assert guard['ROM_sha256']==H(raw) and not guard['matching_patch_files']
    assert set(out.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Stock.preserve_script(script,candidate,raw)as stage:stage(program);q=Stock.run(script,ROM,out/'capture',H(raw),210)
        assert q['script_SHA256']==PINS[H(raw)][route]and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and Stock.check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--route',choices=ROUTES,default='mushroom')
    mode=p.add_mutually_exclusive_group();mode.add_argument('--source',action='store_true');mode.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=3200);a=p.parse_args();assert 800<=a.limit<=3500
    raw=ROM.read_bytes();origin(raw)
    if a.run:q=native(raw,a.route)
    else:
        def deny(*a,**k):raise AssertionError('Grant source attempted outputs/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.route,a.limit)
            else:
                program=controller(raw,a.route);assert H(program)==PINS[H(raw)][a.route]
                q=dict(passed=True,ROM_SHA256=H(raw),controller_SHA256=H(program),route_executed=False,outputs=0)
    print('GRANT_STOCK '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
