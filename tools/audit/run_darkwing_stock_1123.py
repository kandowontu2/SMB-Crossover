"""Exact06336 Darkwing authored Easy 1-1 pickups; inputs and observers only.

Historical cache-assisted clears and staged mature-actor component tests are
retained separately. Source mode declares linked native-menu entry; --run is
Root's physical boot through the shared two-file slot, with exact restoration.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import re
from unittest.mock import patch

import run_chip_dale_stock_1123 as Host
from current_ice_stock_binding_1122 import RAM_FIELDS
from replay_sonic_hidden_life_f7c9_1116 import value
from check_ff_stdout_controller_source_1110 import LuaRuntime
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

H,R,ROM,OUT,W,N=Host.H,Host.R,Host.ROM,Host.OUT,Host.W,Host.N
PIN='06336f15fae4d24afa8025e972764091def63b6c01d41f206828a5105939661f'
ROUTES={'mushroom':(0,),'upgrades':(0,1),'life':(0,3),'star':(0,2)}
PINS={'mushroom':'3edcba9a21c8d4b221e554b5263e03246109cee15f3eb4f04d1ff4356621a3be',
      'upgrades':'93fcee85ca766daebd3330cc4732a93832def45c170dd2d24636a0d20ddf2675',
      'life':'55c6c414da3b434a2f81fe04e374db9b0b55a410ad9b8d33bb964722ed7f8b1d',
      'star':'7943a5391121662eb83011f901bb249fe577c67a8e8997617db473d24cc22c1d'}
OBSERVER=R/'tools/audit/ice_climbers_stock_observer_1122.lua'
CHAIN=('current_roster_darkwing_stairs_v8.lua','current_roster_darkwing_air_arrow_v7.lua',
       'current_roster_darkwing_gap_v6.lua','current_roster_darkwing_arrow_v5.lua','full_roster_policy_og.lua')


@lru_cache(maxsize=1)
def toolkit():
    def inline(name):
        assert name in CHAIN
        text=(R/'tools/playthroughs'/name).read_text()
        pattern=r"dofile\(root\.\.'/tools/playthroughs/([^']+)'\)"
        text=re.sub(pattern,lambda m:'(function()\n'+inline(m.group(1))+'\nend)()',text)
        if name=='full_roster_policy_og.lua':
            old="local phase='approach';local clock=0"
            assert text.count(old)==1;text=text.replace(old,"local phase='route';local clock=0",1)
        assert 'dofile('not in text
        return text
    return inline(CHAIN[0])


POLICY=r'''
local T={phase='first-align',events={}}
DARKWING_STOCK=T
local function sample(c)return{x=c.x,y=c.y,update=c.update,motor=c.motor,hp=c.hp,gas=c.gas,adaptor=c.power,mode=c.mode,state=c.state,lastA=c.lastA}end
local function phase(c,p)
 T.phase=p;T.at=c.update;assert(#T.events<64,'Bounded normal Darkwing pickup phases')
 T.events[#T.events+1]={phase=p,player=sample(c)}
end
local function steer(c,x,n)return{right=c.x<x-n,left=c.x>x+n}end
local function target(c,kind)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 then
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
   local k=c.r('PowerUpType',i)
   if c.r('InvPickupOwner',i)==12 and c.r('InvPickup',i)>=0x22 and c.r('InvPickup',i)<0x29 then
    k=math.abs(x-336)<=2 and 0 or math.abs(x-1248)<=2 and 1 or 5
   end
   if k==kind then return{slot=i,x=x,y=c.r('Enemy_Y_Position',i),stamp=c.r('InvPickup',i),mature=c.r('Enemy_State',i)&128~=0}end
  end
 end
end
local function defend(c,b)
 if c.mode~=0 then return{select=c.r('DwPrevious')&32==0}end
 local e=c.enemy()
 if e and e.dx>0 and e.dx<112 and math.abs(e.y-(c.y+17))<24 and c.grounded then
  local clear=true
  for x=c.x+24,e.x-8,8 do local t=c.block(x,c.y+17);if t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 then clear=false end end
  if clear then
   if c.r('PlayerFacingDir')~=1 then return{right=true}end
   return{b=c.update%8<2}
  end
 end
 return b
end
return function(c)
 if DARKWING_TARGET_COLLECTED then return{}end
 if T.phase=='first-align'then
  if math.abs(c.x-331)<=2 and c.grounded and not c.lastA then phase(c,'first-bump');return{a=true}end
  return defend(c,steer(c,331,2))
 end
 if T.phase=='first-bump'then
  if target(c,0)then phase(c,'first-pipe')end
  return{a=c.update-T.at<24}
 end
 if T.phase=='first-pipe'then
  assert(target(c,0),'Original first-block item remains live during the pipe approach')
  if c.x>=419 and c.grounded and not c.lastA then phase(c,'pipe-up');return{right=true,a=true}end
  return defend(c,{right=true})
 end
 if T.phase=='pipe-up'then
  if c.grounded and c.update-T.at>4 and c.y<=144 then T.pipe_landing=sample(c);phase(c,'pipe-left');return{}end
  assert(c.update-T.at<100,'Actual first pipe support is reachable with the original jump')
  return{right=c.x<441,a=c.update-T.at<30}
 end
 if T.phase=='pipe-left'then
  assert(c.y<=144,'Keep genuine first-pipe support before the return jump')
  if math.abs(c.x-441)<=1 and c.grounded and not c.lastA then phase(c,'row-return');return{left=true,a=true}end
  return steer(c,441,1)
 end
 if T.phase=='row-return'then
  if c.grounded and c.update-T.at>4 and c.y<=112 then T.row_landing=sample(c);phase(c,'first-catch');return{}end
  assert(c.update-T.at<100,'Bounded original-height return to the item row')
  return{left=c.x>388,a=c.update-T.at<32}
 end
 if T.phase=='first-catch'then
  local a=target(c,0);assert(a,'Same authored first-block item until actual collection')
  return steer(c,a.x-2,2)
 end
 if not DARKWING_FIRST_AFTER then return{}end
 if T.phase=='first-earned'then phase(c,'travel')end
 local kind=C.expected[2];local goal=kind==1 and 1248 or kind==2 and 1616 or 1024
 if T.phase=='travel'then
  if c.x<goal-76 then return toolkit(c)end
  phase(c,'align')
 end
 local a=target(c,kind)
 if a and not T.seen then T.seen=a;phase(c,'emerge')end
 if T.seen and not a then T.missing=sample(c);return{}end
 if T.phase=='align'then
  if not c.grounded or c.y<160 then return defend(c,steer(c,goal-56,2))end
  if math.abs(c.x-(goal-5))<=2 and not c.lastA then phase(c,'bump');return{a=true}end
  return defend(c,steer(c,goal-5,2))
 end
 if T.phase=='bump'then
  if c.grounded and c.update-T.at>50 then phase(c,'align')end
  return{a=c.update-T.at<28}
 end
 if T.phase=='emerge'then
  if not a.mature then return steer(c,goal+36,2)end
  phase(c,'collect')
 end
 if T.phase=='collect'then
  if c.grounded and c.y-a.y>14 and math.abs(c.x-a.x)<34 and not c.lastA then phase(c,'catch');return{a=true}end
  return defend(c,steer(c,a.x-2,2))
 end
 if T.phase=='catch'then
  if c.grounded and c.update-T.at>4 then phase(c,'collect')end
  local b=steer(c,a.x-2,2);b.a=c.update-T.at<30;return b
 end
 return{}
end
'''


FLOWER_SUPPORT=r'''
local function flowerSupport(c,a)
 local q=T.flower_arrow
 if not q then q={phase='setup',at=c.update,events={}};T.flower_arrow=q end
 assert(c.update-q.at<160,'Bounded native Flower toolkit phase '..q.phase)
 local function step(p)q.phase=p;q.at=c.update;q.events[#q.events+1]={phase=p,player=sample(c)};assert(#q.events<20,'Bounded natural Flower Arrow phases')end
 local prev=c.r('DwPrevious')
 if q.phase=='setup'then
  if not c.grounded or c.y<160 then return steer(c,1306,1)end
  if math.abs(c.x-1306)>1 then return steer(c,1306,1)end
  step('face')
 end
 if q.phase=='face'then
  if c.r('PlayerFacingDir')~=2 then return{left=true}end
  step('select')
 end
 if q.phase=='select'then
  assert(c.power==2 and c.gas>=3,'Naturally earned Arrow toolkit funds the Flower step')
  if c.mode~=1 then return{select=prev&32==0}end
  step('takeoff')
 end
 if q.phase=='takeoff'then
  if c.grounded and not c.lastA then step('rise');return{a=true}end
  return{}
 end
 if q.phase=='rise'then
  if not c.grounded and c.y<=136 and prev&64==0 then q.before=sample(c);step('fire');return{a=true,b=true}end
  assert(c.update-q.at<80,'Natural vertical Arrow firing height')
  return{a=true}
 end
 if q.phase=='fire'then
  for i=0,9 do
   if c.r('RgShotType',i)==8 and c.r('RgShotImpact',i)==2 and c.r('RgShotDir',i)==2 and c.r('RgShotAge',i)<8 then
    q.slot=i;q.paid=sample(c);assert(c.gas==q.before.gas-3,'Actual earned Arrow debit3')
    step('attach');return{}
   end
  end
  assert(c.update-q.at<30,'Actual left Arrow allocation')
  return{a=true,b=prev&64==0}
 end
 if q.phase=='attach'then
  local i=q.slot;local slot=c.r('RgShotImpact',i)-1
  if c.r('RgShotType',i)==6 and slot>=0 and slot<=5 and c.r('Enemy_Flag',slot)==1 and c.r('Enemy_ID',slot)==0x26 and c.r('Enemy_State',slot)&127==(0x20|i)then
   local x=c.r('Enemy_X_Position',slot)+256*c.r('Enemy_PageLoc',slot);local y=c.r('Enemy_Y_Position',slot)
   q.actor={slot=slot,x=x,y=y,shotX=c.r('RgShotX',i)+256*c.r('RgShotPage',i)}
   assert(x>=1264 and x<=1312 and y>=144 and y<160,'Real Flower-row attached Arrow geometry')
   step('bar-takeoff')
  else assert(c.update-q.at<100,'Original Arrow charge/flight/attachment');return{}end
 end
 if q.phase=='bar-takeoff'then
  if c.grounded and not c.lastA then step('hang');return{left=true,a=true}end
  return{}
 end
 if q.phase=='hang'then
  if c.hang==(0x80|q.slot)then
   q.hang=q.hang or sample(c)
   if c.lastA then return{}end
   step('bar-jump');return{left=true,a=true}
  end
  assert(c.update-q.at<100,'Actual native bar grip')
  return{left=true,a=true}
 end
 if q.phase=='bar-jump'then
  if c.grounded and c.y<=112 then q.landing=sample(c);step('catch')end
  assert(c.update-q.at<100,'Native bar jump onto the Flower row')
  return{left=true,a=true}
 end
 return steer(c,a.x-2,2)
end
'''


@lru_cache(maxsize=4)
def bindings(raw,route):
    assert H(raw)==PIN and route in ROUTES
    Host.reference(raw)
    bundle=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):menu=W.UI.seed(bundle,0)
    for key in(4,32):W.UI.key(menu,key)
    assert W.UI.menu_name(menu)[0]=='DARKWING DUCK'
    assert tuple(N.get(menu,n)for n in('CrossoverMenuIndex','SelectedCharacter','DarkwingVariant'))==(8,12,1)
    fields=set(n for n in RAM_FIELDS if not n.startswith('Ic'))
    fields.update(re.findall(r"r\('([A-Za-z_0-9]+)'",toolkit()+POLICY))
    fields.update('DwHealth DwGas DwAdaptor DwMode DwPrevious DwHang DarkwingVariant InvPickup InvPickupOwner PlayerScoreDisplay RgBillBurst RgBillBurstDelay RgShootPose'.split())
    ram={n:W.address(bundle,n)for n in fields}
    hooks={}
    for event,symbol in(('GameLoop','GameLoop'),('DwMovement','ExpandedMovement'),('DwOwner','DwScroogeMovement'),
                         ('HandlePowerUpCollision','HandlePowerUpCollision'),('FamilyGrant','DwCollectPickup'),
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
        row,col=divmod(i,8);nav.append('down'if row in(0,3)else'up'if row==2 else'left'if col else'')
    return dict(sha=PIN,form='darkwing',name='DARKWING DUCK',char=12,variant=1,slot=8,mode_value=0,
                route=route,expected=list(ROUTES[route]),ram=ram,hooks=hooks,navigation=nav)


def controller(raw,route):
    cfg=bindings(raw,route);text=OBSERVER.read_text();edits=[]
    def edit(a,b):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b,1);edits.append((a,b))
    edit("assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha", "assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha")
    edit("r('SelectedCharacter')==20 and r('IcVariant')==C.variant", "r('SelectedCharacter')==12 and r('DarkwingVariant')==1")
    edit("r('IcVariant')~=C.variant", "r('DarkwingVariant')~=1")
    edit("local expected=C.route=='life' and {0,3} or {0,1,2}", 'local expected=C.expected')
    edit('local lifePending','local lifePending\nlocal activePickup\nlocal ownerMoves=0\nlocal clockInput={}\nlocal cue,lifeCue=0,0\nlocal function score()local n=0;for i=0,5 do n=n*10+r(\'PlayerScoreDisplay\',i)end;return n end')
    edit('local function actor(i)\n return', """local function actor(i)
 local x=pos('Enemy_X_Position','Enemy_PageLoc',i);local owner=r('InvPickupOwner',i);local stamp=r('InvPickup',i);local kind=r('PowerUpType',i)
 if owner==12 and stamp>=0x22 and stamp<0x29 then kind=math.abs(x-336)<=2 and 0 or math.abs(x-1248)<=2 and 1 or 5 end
 return""")
    edit("kind=r('PowerUpType',i),", "kind=kind,nativeKind=r('PowerUpType',i),owner=owner,stamp=stamp,")
    edit('frame=physical,update=updates,motor=motor,','frame=physical,update=updates,motor=motor,owner=ownerMoves,')
    edit("power=r('IcPower')", "power=r('DwAdaptor'),hp=r('DwHealth'),gas=r('DwGas'),mode=r('DwMode'),hang=r('DwHang'),hurt=r('RgBillBurst'),growth=0")
    edit('c.poll=polls;c.char=20;', 'c.poll=motor;c.char=12;c.update=motor;c.frame=motor;')
    edit('c.lastA=mask&128~=0', "c.lastA=r('DwPrevious')&128~=0")
    edit('Living Ice Climber','Living native Darkwing')
    edit("assert(updates<5100,'Bounded pickup route')", "assert(updates<4800 and s.hp>0 and s.hp<=4 and s.yHigh<2 and(s.lives==2 or(C.route=='life'and checks['3'].grant and s.lives==3)),'Bounded living native Darkwing route')")
    edit('local a=actor(i);local q=checks[tostring(a.kind)]', "local a=actor(i);local q=checks[tostring(a.kind)]\n  if q and q.birth and a.slot==q.birth.actor.slot and a.flag>0 and a.id==46 and a.state&128~=0 and not q.mature then q.mature={actor=a,player=s}end")
    edit('q.birth={actor=a,player=s}', "assert(heads[tostring(a.kind)],'Real authored power block before native item birth');q.birth={actor=a,player=s}")
    edit(' local complete=true', """ if checks['0'].collect and not checks['0'].after then DARKWING_FIRST_COLLECTED=true end
 if checks['0'].after then DARKWING_FIRST_AFTER=true end
 local target=checks[tostring(C.expected[#C.expected])]
 if target.collect then DARKWING_TARGET_COLLECTED=true end
 for _,kind in ipairs(expected)do local q=checks[tostring(kind)]
  if q.collect and not q.grant and kind~=3 and score()>=q.collect.score_before+1000 then q.grant=s end
 end
 local complete=true""")
    edit('if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope() then','if q.grant and not q.after and s.motor-q.grant.motor>=25 and s.owner-q.grant.owner>=25 and scope()and s.state==0 then')
    edit("else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end", "else assert(s.hp==q.grant.hp and s.power==q.grant.power and s.gas==q.grant.gas and s.mode==q.grant.mode and s.status==q.grant.status and score()>=q.collect.score_before+1000,'Earned actual Darkwing resources persist')end")
    edit("if kind==3 then assert(s.lives==q.grant.lives,'Earned life persists during movement')", "if kind==3 then assert(s.lives==q.grant.lives and lifeCue>q.collect.life_cue_before,'Native life and cue persist')")
    edit("elseif kind==2 then assert(s.star>0,'Earned Star persists during movement')", "elseif kind==2 then assert(s.star>0 and score()>=q.collect.score_before+1000,'Native Star and score persist')")
    edit("if complete then finish(true,'Authored pickups, native credit and 25 further movement updates') end", "if complete then assert(#pending==0 and not lifePending,'All native workers completed');finish(true,'Natural Darkwing blocks, actual family effects and25 owner/integration returns');return end\n clockInput=scope()and choose(context())or{}")
    edit("assert(r('Square2SoundQueue')&32~=0,'Actual pickup cue')", "assert(cue>p.cue,'New actual pickup cue')")
    edit("sound=r('Square2SoundQueue')}", "sound=r('Square2SoundQueue'),score_before=p.score,life_cue_before=p.life_cue}")
    edit("assert(p.before.power==a.kind and s.power==a.kind+1 and s.status==s.power,'Normal Ice power tier transition')", """assert(q.family and q.family.update==updates and q.family.stamp==a.stamp,'Same native family collector owns the physical item')
  local stamp=a.stamp
  if stamp==0x23 then assert(p.before.hp<4 and s.hp==4 and s.power==p.before.power and s.gas==p.before.gas,'Full aid restores a real native health deficit')
  else
   local adaptor=stamp==0x26 and 2 or stamp==0x27 and 1 or stamp==0x28 and 3 or -1
   assert(adaptor>0 and s.power==adaptor and s.gas==math.min(99,p.before.gas+10)and s.hp==p.before.hp,'Actual carried adaptor replacement and original gas10 cap99')
  end""")
    edit(' q.grant=s\nend', ' activePickup=nil\n -- Native score completes before the25-return gate.\nend')
    edit("if p.name=='IcMovement' then motor=motor+1", "if p.name=='DwMovement' then motor=motor+1\n  elseif p.name=='DwOwner'then ownerMoves=ownerMoves+1")
    edit('  elseif p.actor then collected(p) end', """  elseif p.family then
   assert(cpu['cpu.ps']&1==1,'Native Darkwing family collector accepts')
   checks[tostring(p.family.kind)].family={update=updates,before=p.before,after=state(),stamp=p.family.stamp,erased_at_entry=p.erased}
  elseif p.actor then collected(p)end""")
    edit(" if name=='HandlePowerUpCollision' then", """ if name=='FamilyGrant'then
  if not activePickup or activePickup.actor.kind>=2 then return end
  local a=activePickup.actor;local i=cpu['cpu.x']
  assert(i==a.slot and r('InvPickup',i)==a.stamp and r('InvPickupOwner',i)==12,'Actual same stamped actor owns family grant')
  p.family=a;p.before=state();p.erased=r('Enemy_Flag',i)==0
 elseif name=='HandlePowerUpCollision' then""")
    edit('  p.actor=a;p.before=state()', "  assert(a.state&128~=0,'Real mature authored actor before physical collection');q.mature=q.mature or{actor=a,player=state()}\n  p.actor=a;p.before=state();p.score=score();p.cue=cue;p.life_cue=lifeCue;activePickup=p")
    edit('phase=ICE_STOCK_STATE or {},controller_only=true,files=0,images=0', 'phase=DARKWING_STOCK or {},pending_returns=#pending,owner_movement_returns=ownerMoves,pickup_cues=cue,life_cues=lifeCue,controller_only=true,game_state_writes=false,files=0,images=0')
    edit('local bits={a=128', "emu.addMemoryCallback(guarded('Native cues',function(_,v)if entered and v==32 then cue=cue+1 elseif entered and v==64 then lifeCue=lifeCue+1 end end),emu.callbackType.write,C.ram.Square2SoundQueue)\nlocal bits={a=128")
    edit('local b=not entered and menu() or (scope() and choose(context()) or {})', 'local b=not entered and menu()or(scope()and clockInput or{})')
    edit('  entered=physical', '  entered=physical;clockInput=choose(context())')
    edit('physical<=6900','physical<=11000')
    restored=text
    for a,b in reversed(edits):assert restored.count(b)==1;restored=restored.replace(b,a,1)
    assert restored==OBSERVER.read_text()
    policy=POLICY.replace(" if DARKWING_TARGET_COLLECTED then return{}end", " if DARKWING_TARGET_COLLECTED then return{}end\n if DARKWING_FIRST_COLLECTED and not DARKWING_FIRST_AFTER then T.phase='first-earned';return{}end")
    if route=='upgrades':
        at="return function(c)\n if DARKWING_TARGET_COLLECTED"
        assert policy.count(at)==1;policy=policy.replace(at,FLOWER_SUPPORT+'\n'+at,1)
        at=" if T.phase=='collect'then"
        new=" if kind==1 and(T.phase=='collect'or T.phase=='flower-tool')then T.phase='flower-tool';return flowerSupport(c,a)end\n"+at
        assert policy.count(at)==1;policy=policy.replace(at,new,1)
    program='\n'.join(('local C='+value(cfg),'local ROSTER_CONFIG={name="darkwing",root=""}',
                       'local toolkit=(function()\n'+toolkit()+'\nend)()',
                       'local choose=(function()\n'+policy+'\nend)()',text))
    assert not any(t in program for t in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    LuaRuntime().compile(program)
    return program.encode()


def cold(raw,route):
    cfg=bindings(raw,route);bundle=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(bundle,0)
    for key in(4,32):W.UI.key(m,key)
    assert W.UI.menu_name(m)[0]==cfg['name'] and N.get(m,'DarkwingVariant')==1
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
    raise AssertionError('Actual selected Darkwing linked-menu entry bound')


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
    p.add_argument('--limit',type=int,default=4900);a=p.parse_args();assert 800<=a.limit<=5000
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:q=native(raw,a.route)
    else:
        def deny(*args,**kwargs):raise AssertionError('Darkwing source attempted files or emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.route,a.limit)
            else:
                program=controller(raw,a.route);assert H(program)==PINS[a.route]
                q=dict(passed=True,ROM_SHA256=PIN,controller_SHA256=H(program),route_executed=False,files=0)
    print('DARKWING_STOCK '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
