"""Alucard natural Easy 1-UP/Star/Flower on exact82e8; source-only by default.

Root alone may --run after the controller pin is qualified. Normal inputs,
real menu variant3, native item actors/credit and25 living movement returns,
ending grounded. Flower also checks normal use of the earned diagonal.
"""
import argparse,json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch

import compose_scrooge_prepare_stack_1123 as Current
import run_simon_ryu_stock_1123 as Stock
import inspect_rogue_missile_targets_cb95_1116 as Engine
import check_contra_force_fixed_layout_1122 as Layout

PIN=Current.CANDIDATE
W,N,H,ROM=Stock.W,Stock.N,Stock.H,Stock.ROM
PINS={'life':'7f69e8146e51a72c60ca774a2a4a312329d02de0eff598b8411173d8a944d0cb',
      'star':'9cf0c7cbf11a7ae8f6fa2eadf19f657720c13f28f228b2f7716e9c56befbe9bd',
      'flower':'c30e385df7a1c7e07d0b616d1f8755036279d1da140f077ee18aa7bcd3ceed7c'}
POLICY=r'''
local T={kind=C.itemKind,phase='travel',events={}}
ROBOT_STOCK_STATE=T
local untilA=0
local launchDirection=0
local previousX,still=nil,0
local goal=C.itemKind==3 and 1024 or 1616
local function sample(c,a)return{x=c.x,y=c.y,state=c.state,update=c.update,hp=c.hp,hearts=c.hearts,bat=c.bat,item=a}end
local function phase(c,p,a)
 if T.phase==p then return end
 assert(#T.events<40,'Bounded Alucard pickup phases')
 T.phase=p;T.since=c.update;T.events[#T.events+1]={phase=p,player=sample(c,a)}
end
local function steer(c,x,band)return{right=c.x<x-band,left=c.x>x+band}end
local function solid(c,x,y)
 local t=c.block(x,y);return t~=0 and t~=35 and t~=38 and t~=194 and t~=195
end
local function actor(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==T.kind then
   return{x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),
          y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),slot=i}
  end
 end
end
local function defend(c,b)
 local e=c.enemy()
 if e and math.abs(e.dx)<64 and math.abs(e.y-c.y)<32 and c.grounded and c.bat==0 then
  local facing=e.dx>=0 and 1 or 2
  if c.r('PlayerFacingDir')~=facing then return{right=facing==1,left=facing==2}end
  return{b=c.r('Cv3AttackAge')==0 and c.r('Cv3Previous')&64==0}
 end
 return b
end
local function launch(c,d,p)
 launchDirection=d;untilA=c.update+28;phase(c,p)
 return{right=d==1,left=d==-1,a=true}
end
return function(c)
 if previousX==c.x then still=still+1 else still=0 end;previousX=c.x
 if C.itemKind==3 and c.lives>=3 or C.itemKind==2 and c.star>0 then phase(c,'credited');return{}end
 local a=actor(c)
 if a and not T.actor then T.actor=sample(c,a);phase(c,'emerge',a)end
 if T.actor and not a then T.missing=T.missing or sample(c);return{}end
 if a then
  T.latest=sample(c,a)
  if a.state&128==0 then return defend(c,steer(c,goal+(T.kind==3 and 34 or 51),2))end
  if T.phase=='catch-jump'then
   if c.grounded and c.update-T.since>4 then phase(c,'catch',a)
   else return{right=launchDirection==1,left=launchDirection==-1,a=c.update<untilA}end
  end
  phase(c,'catch',a)
  local waitX=goal+(T.kind==3 and 34 or 51)
  if T.kind==2 and a.x<goal+80 then
   if math.abs(c.x-waitX)>2 then return defend(c,steer(c,waitX,2))end
   if c.grounded and not c.lastA and a.y>=110 and math.abs(a.x-c.x-6)<=13 then return launch(c,1,'catch-jump')end
   return{}
  end
  if c.grounded and not c.lastA and math.abs(a.x-c.x)<24 and c.y-a.y>12 then
   return launch(c,a.x<c.x and -1 or 1,'catch-jump')
  end
  return defend(c,steer(c,a.x-4,3))
 end
 if T.phase=='travel'then
  if c.x>=goal-64 then phase(c,'align')
  else
   local b={right=true}
   local obstacle=solid(c,c.x+42,c.y+24)or solid(c,c.x+42,c.y+8)
   local support=solid(c,c.x+32,math.min(c.y+40,232))
   if c.grounded and not c.lastA and c.r('Cv3AttackAge')==0 and(obstacle or not support or still>24)then
    untilA=c.update+28;b.a=true
   elseif not c.grounded then b.a=c.update<untilA end
   return defend(c,b)
  end
 end
 if T.phase=='bump'then
  if c.grounded and c.update-T.since>55 then phase(c,'align')end
  return{a=c.update<untilA}
 end
 if not c.grounded or c.y<160 then return defend(c,steer(c,goal-64,2))end
 if math.abs(c.x-(goal-5))<=2 and not c.lastA and c.r('Cv3AttackAge')==0 then
  T.attempts=(T.attempts or 0)+1;assert(T.attempts<=6,'Bounded authored Alucard head bump')
  return launch(c,0,'bump')
 end
 return defend(c,steer(c,goal-5,2))
end
'''


FLOWER_WEAPON_OBSERVER=r'''
local function alucardShots()
 local T=ROBOT_STOCK_STATE
 if not T.fire or T.weaponProof then return end
 T.weaponReturns=(T.weaponReturns or 0)+1
 assert(updates-T.fire.update<45,'Bounded fresh-B fireball use')
 local shots={}
 local function signed(n)return n>=32768 and n-65536 or n end
 for i=0,3 do
  if r('Cv3ShotType',i)~=0 then
   assert(r('Cv3ShotType',i)==6,'Only the earned primary attack uses the empty shot pool')
   shots[#shots+1]={slot=i,age=r('Cv3ShotAge',i),
    x=(r('Cv3ShotX',i)+256*r('Cv3ShotPage',i))*256+r('Cv3ShotFx',i),
    y=r('Cv3ShotY',i)*256+r('Cv3ShotFy',i),
    vx=signed(r('Cv3ShotVXLo',i)+256*r('Cv3ShotVXHi',i)),
    vy=signed(r('Cv3ShotVYLo',i)+256*r('Cv3ShotVYHi',i))}
  end
 end
 if #shots==0 then assert(not T.projectiles,'New fireballs persist for the second native return');return end
 assert(#shots==2,'One horizontal fireball and one earned upward diagonal')
 local direction=T.fire.facing==1 and 1 or -1
 local horizontal,upward
 for _,s in ipairs(shots)do
  if s.vy==0 then assert(s.vx==direction*1152,'Horizontal primary velocity');horizontal=s
  else assert(s.vx==direction*1062 and s.vy==-436,'Earned upward diagonal velocity');upward=s end
 end
 assert(horizontal and upward,'Distinct horizontal and upward primary shots')
 local now={update=updates,weaponReturn=T.weaponReturns,horizontal=horizontal,upward=upward}
 if not T.projectiles then
  assert(horizontal.age==1 and upward.age==1,'Both fireballs are newly spawned by this B edge')
  T.projectiles=now;return
 end
 for _,name in ipairs({'horizontal','upward'})do
  local p,s=T.projectiles[name],now[name]
  assert(s.slot==p.slot and s.age==p.age+1 and s.x-p.x==s.vx and s.y-p.y==s.vy,
   'Both shots move with their signed velocities on the next native return')
 end
 T.weaponProof={request=T.fire,first=T.projectiles,second=now}
end
'''


@lru_cache(maxsize=1)
def reference(raw):
    assert H(raw)==PIN
    return Current.Bridge.inverse(Current.inverse(raw))


def controller(raw,item):
    if item=='flower':return flower_controller(raw)
    assert item in('life','star');parent=reference(raw)
    cfg=deepcopy(Stock.bindings(parent,'simon',item));cfg.update(sha=PIN,form='alucard',name='ALUCARD',variant=3,
        expected=[3 if item=='life'else 2],itemKind=3 if item=='life'else 2)
    b=dict(W.Symbols.bundle(),raw=raw)
    for n in('Cv3Variant','Cv3Health','Cv3Hearts','Cv3Power','Cv3Previous','Cv3AttackAge','Cv3HurtAge',
              'Cv3Bat','Cv3BatTransform','Cv3VxLo','Cv3VxHi','Cv3VyLo','Cv3VyHi','GamePauseStatus'):
        cfg['ram'][n]=W.address(b,n)
    name='Cv3MovementGate';at=W.location(b,name)
    cfg['hooks']['Movement']=dict(pc=W.address(b,name),tag=((at-16)//8192)|128,offset=at-16,hex=raw[at:at+12].hex())
    for n,h in cfg['hooks'].items():
        at=16+h['offset'];assert raw[at:at+len(bytes.fromhex(h['hex']))]==bytes.fromhex(h['hex']),n
    old=Stock.controller(parent,'simon',item).decode()
    marker="assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha"
    assert old.count(marker)==1;body=old[old.index(marker):]
    a="assert(r(C.variant_field)&C.variant_mask==0,'Original identity in menu')"
    assert body.count(a)==1;body=body.replace(a,"if r(C.variant_field)~=C.variant then return pulse('select')end",1)
    a='r(C.variant_field)&C.variant_mask==0';assert body.count(a)==1;body=body.replace(a,'r(C.variant_field)==C.variant',1)
    changes=[("power=r('PlayerStatus'),growth=r('GuestPowerupActive')", "power=r('PlayerStatus'),growth=r('GuestPowerupActive'),hp=r('Cv3Health',2),hearts=r('Cv3Hearts',2),bat=r('Cv3Bat')"),
             ("c.lastA=r('PreviousA_B_Buttons')&128~=0", "c.lastA=r('Cv3Previous')&128~=0"),
             ("assert(updates<5100 and s.yHigh<2,'Bounded living pickup route')", "assert(updates<3000 and s.yHigh<2 and s.hp>0 and s.lives>=2,'Bounded living Alucard pickup route')"),
             ("if kind==3 then assert(s.lives==q.grant.lives and (cues[64]or 0)>q.collect.life_cue,'Earned life and cue persist')", "if kind==3 then assert(s.lives==q.grant.lives and (cues[64]or 0)>q.collect.life_cue and s.hp==q.grant.hp and s.hearts==q.grant.hearts,'Native life, health, hearts and cue persist')")]
    for a,z in changes:
        assert body.count(a)==1,(a,body.count(a));body=body.replace(a,z,1)
    text='local C='+Stock.value(cfg)+'\nlocal choose=(function()\n'+POLICY+'\nend)()\n'+body
    assert not any(t in text for t in('emu.write','emu.setState','saveState','loadState','io.open','dofile','takeScreenshot'))
    Stock.LuaRuntime().compile(text)
    if item in PINS:assert H(text.encode())==PINS[item]
    return text


def flower_controller(raw):
    """Earn the Mushroom and Alucard diagonal using ordinary floor/jump inputs."""
    text=controller(raw,'star')
    b=dict(W.Symbols.bundle(),raw=raw)
    fields=('InvPickup','InvPickupOwner','Cv3PickupVariant','Cv3ShotType','Cv3ShotAge','Cv3ShotX',
            'Cv3ShotPage','Cv3ShotY','Cv3ShotFx','Cv3ShotFy','Cv3ShotVXLo','Cv3ShotVXHi',
            'Cv3ShotVYLo','Cv3ShotVYHi')
    metadata=';'.join('C.ram.'+n+'='+str(W.address(b,n))for n in fields)
    name='Cv3WeaponsGate';at=W.location(b,name)
    hook=dict(pc=W.address(b,name),tag=((at-16)//8192)|128,offset=at-16,hex=raw[at:at+12].hex())
    line,body=text.split('\n',1)
    text=line+"\nC.expected={0,1};C.itemKind=0;C.route='upgrades';"+metadata+';C.hooks.Weapons='+Stock.value(hook)+'\n'+body
    policy=POLICY.replace('local goal=C.itemKind==3 and 1024 or 1616','local goal=336',1)
    policy=Stock.once(policy,
        "if C.itemKind==3 and c.lives>=3 or C.itemKind==2 and c.star>0 then phase(c,'credited');return{}end",
        """if T.kind==1 and c.shots>0 then
  phase(c,'credited')
  local empty=true;for i=0,3 do if c.r('Cv3ShotType',i)~=0 then empty=false end end
  if not T.fire and empty and c.grounded and c.r('Cv3AttackAge')==0 and c.r('Cv3Previous')&64==0 then
   T.fire={update=c.update,x=c.x,y=c.y,facing=c.r('PlayerFacingDir'),hp=c.hp,hearts=c.hearts,shots=c.shots}
   return{b=true}
  end
  return{}
 end
 if T.kind==0 and c.status>0 then
  T.mushroom=T.mushroom or sample(c)
  if c.update-T.mushroom.update<40 then return{}end
  T.kind=1;goal=1248;T.actor=nil;T.missing=nil;T.attempts=0;phase(c,'travel')
 end""")
    policy=Stock.once(policy,'  T.latest=sample(c,a)',"""  T.latest=sample(c,a)
  if T.kind==0 then
   return defend(c,steer(c,a.state&128==0 and 390 or math.max(396,a.x-4),3))
  end
  if T.kind==1 then
   if a.state&128==0 then return defend(c,steer(c,1280,2))end
   if T.phase=='flower-jump'then
    if not c.grounded or c.update-T.since<5 then return{left=true,a=c.update<untilA}end
    phase(c,'flower-mount',a)
   end
   if c.grounded and c.y>=160 then
    if math.abs(c.x-1280)<=2 and not c.lastA then return launch(c,-1,'flower-jump')end
    return defend(c,steer(c,1280,2))
   end
   return{left=true}
  end""")
    text=Stock.once(text,POLICY,policy)
    changes=[("bat=r('Cv3Bat')", "bat=r('Cv3Bat'),shots=r('Cv3Power',2)"),
        ("kind=r('PowerUpType',i),", "kind=r('PowerUpType',i),stamp=r('InvPickup',i),owner=r('InvPickupOwner',i),variant=r('Cv3PickupVariant',i),"),
        ("assert(p.before.power==a.kind and s.growth~=0 and r('GuestPowerupTarget')==a.kind+1,'Actual source growth');return",
         """assert(a.owner==5 and a.variant==3 and a.stamp==(a.kind==0 and 208 or 212),'Actual Alucard pickup metadata')
  assert(s.status==1 and s.hp>=p.before.hp,'Actual CV3 pickup status/health')
  if a.kind==1 then assert(s.shots==p.before.shots+1 and s.shots<=2,'Alucard earns a real diagonal')end
  return"""),
        ('if q.collect and not q.grant and kind<2 and s.growth==0 and s.status==kind+1',
         'if q.collect and not q.grant and kind<2 and s.growth==0 and s.status==1 and(kind==0 or s.shots>q.collect.before.shots)'),
        ("else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end",
         "else assert(s.status==1 and s.shots==q.grant.shots and s.hp==q.grant.hp and s.hearts==q.grant.hearts,'Earned Alucard upgrade, health and hearts persist') end")]
    for a,z in changes:text=Stock.once(text,a,z)
    text=Stock.once(text,'local function settle()',FLOWER_WEAPON_OBSERVER+'\nlocal function settle()')
    text=Stock.once(text,"elseif p.name=='GameLoop' then afterMain()",
        "elseif p.name=='Weapons' then alucardShots()\n  elseif p.name=='GameLoop' then afterMain()")
    text=Stock.once(text,"if complete then finish(true,", "if complete and ROBOT_STOCK_STATE.weaponProof then finish(true,")
    assert not any(t in text for t in('emu.write','emu.setState','saveState','loadState','io.open','dofile','takeScreenshot'))
    Stock.LuaRuntime().compile(text)
    if 'flower'in PINS:assert H(text.encode())==PINS['flower']
    return text


def cold(raw):
    b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for _ in range(5):W.UI.key(m,1)
    for _ in range(3):W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]=='ALUCARD'and N.get(m,'SelectedCharacter')==5 and N.get(m,'Cv3Variant')==3
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'Cv3Health',2)==64 and N.get(m,'Cv3Hearts',2)==10
            return m
        m.controller_pad=0;Engine.Frames.frame(m,cold=True)
    raise AssertionError('Actual Alucard cold bound')


def source(raw,item,limit=2300):
    text=controller(raw,item).replace("assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha",
        "assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha",1)
    text+="\nemu.addEventCallback(guarded('Source bound',function()if physical>="+str(limit)+" then finish(false,'Bounded source diagnostic')end end),emu.eventType.endFrame)"
    with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',PIN):return Engine.run(raw,limit+1,text=text)


def native_root(raw,item,root):
    """Root supplies a private two-file staging root; restore its controller."""
    assert item in PINS and H(raw)==PIN
    root=root.resolve();assert root.is_relative_to(Stock.R/'build')and root!=Stock.OUT.resolve()
    candidate,script=root/'candidate.nes',root/'controller.lua'
    assert set(root.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    program=controller(raw,item).encode();before=script.read_bytes();guard=Stock.check(ROM)
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    try:
        with Stock.preserve_script(script,candidate,raw)as stage:
            stage(program);q=Stock.run(script,ROM,root/'capture',PIN,180)
        print('ALUCARD_STOCK_NATIVE '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['script_SHA256']==PINS[item]and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw
        assert ROM.read_bytes()==raw and Stock.check(ROM)==guard
    return q


def isolated_native(raw, item, root):
    root = root.resolve()
    assert root.is_relative_to(Stock.R / 'build') and root not in (Stock.R / 'build', Stock.OUT)
    root.mkdir()
    candidate, script = root / 'candidate.nes', root / 'controller.lua'
    try:
        candidate.write_bytes(raw)
        script.write_bytes(b'')
        return native_root(raw, item, root)
    finally:
        script.unlink(missing_ok=True)
        candidate.unlink(missing_ok=True)
        root.rmdir()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--item',choices=('life','star','flower'),default='life')
    g=p.add_mutually_exclusive_group();g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--native-root',type=Path);p.add_argument('--limit',type=int,default=2300);a=p.parse_args();assert 1000<=a.limit<=3000
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:
        assert a.native_root is not None
        return int(not isolated_native(raw,a.item,a.native_root)['passed'])
    def deny(*a,**k):raise AssertionError('Source attempted outputs/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        q=source(raw,a.item,a.limit)if a.source else dict(compiled=True,controller_SHA256=H(controller(raw,a.item).encode()),outputs=0,native=False)
    print('ALUCARD_STOCK_SOURCE '+json.dumps(q,separators=(',',':')),flush=True)
    return int(a.source and not q['passed'])


if __name__=='__main__':raise SystemExit(main())
