"""Sypha ordinary Easy 1-1 pickups on exact82e8/ffd708; source-only by default.

The Flower route earns Mushroom then Flame and casts with normal Up+B.
Root alone owns --run, its temporary two-file root and the Mesen queue.
"""
import argparse,json
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch

import run_alucard_stock_1123 as A

W,N,H,ROM,PIN,Stock,Engine=A.W,A.N,A.H,A.ROM,A.PIN,A.Stock,A.Engine
PINS={'mushroom':'726f6b51f5fc593d0c5d0d335c749e194e4c86f0e6ba94dfd2cddb49c6caddf4',
      'flower':'89c1567ae85fba516b1d05dc57e35197c41c426d2108d4d92d1cc7b228ff1357'}
CURRENT='ffd7081036bca9cb165d9f4c5527e909126df70f993b4ebec75b7dd7ac83a6b1'
CURRENT_PINS={'mushroom':'467b10ba27eca9eeba2b85020b4d061fe00f437d9138a2c0974f992b4fcd5e57',
              'flower':'8976459aca2b52a67a4615c0d98243de154a79be1019b08768ed7f1167b2c265',
              'life':'3c9156f9d505270b7e305e6f1dfe203450a2040404e984363fe17fdf264e65ca',
              'star':'839a1a2b248dd4d9a7510354f9bb24ab4668673f745f8667e714f5ef4d5db488'}

SPELL_OBSERVER=r'''
local function syphaSpell()
 local T=ROBOT_STOCK_STATE
 if not T.cast or T.weaponProof then return end
 T.weaponReturns=(T.weaponReturns or 0)+1
 assert(updates-T.cast.update<45,'Bounded natural Flame cast')
 local s=state()
 assert(s.sub==1 and s.hp==T.cast.hp and s.hearts==T.cast.hearts-1,'Flame costs one earned heart')
 T.castPaid=T.castPaid or s
 local shot
 local function signed(n)return n>=32768 and n-65536 or n end
 for i=0,3 do
  if r('Cv3ShotType',i)~=0 then
   assert(not shot and r('Cv3ShotType',i)==3,'One native Flame uses the empty pool')
   shot={slot=i,age=r('Cv3ShotAge',i),
    x=(r('Cv3ShotX',i)+256*r('Cv3ShotPage',i))*256+r('Cv3ShotFx',i),
    y=r('Cv3ShotY',i)*256+r('Cv3ShotFy',i),
    vx=signed(r('Cv3ShotVXLo',i)+256*r('Cv3ShotVXHi',i)),
    vy=signed(r('Cv3ShotVYLo',i)+256*r('Cv3ShotVYHi',i))}
  end
 end
 if not shot then assert(not T.flameFirst,'Flame survives through its first source advance');return end
 local direction=T.cast.facing==1 and 1 or -1
 assert(shot.age<=4 and shot.vx==(shot.age==4 and direction*1024 or 0)and shot.vy==0,
  'Source Flame first four movement phases')
 if not T.flameFirst then
  assert(shot.age==1,'A fresh Up+B cast creates this Flame')
  T.flameFirst=shot
 else
  local p=T.flamePrevious
  assert(shot.slot==p.slot and shot.age==p.age+1 and shot.x-p.x==shot.vx and shot.y==p.y,
   'Flame follows its native phase velocity on consecutive weapon returns')
 end
 T.flamePrevious=shot
 if shot.age==4 then T.weaponProof={request=T.cast,payment=T.castPaid,first=T.flameFirst,last=shot,
  weaponReturns=T.weaponReturns}end
end
'''


def policy(item):
    text=A.POLICY.replace('Alucard','Sypha')
    before=""" if e and math.abs(e.dx)<64 and math.abs(e.y-c.y)<32 and c.grounded and c.bat==0 then
  local facing=e.dx>=0 and 1 or 2
  if c.r('PlayerFacingDir')~=facing then return{right=facing==1,left=facing==2}end
  return{b=c.r('Cv3AttackAge')==0 and c.r('Cv3Previous')&64==0}
 end"""
    text=Stock.once(text,before,""" if e and e.dx>0 and e.dx<34 and e.x>=c.camera and e.y-c.y>=-11 and e.y-c.y<20
    and e.id<21 and e.id~=2 and e.id~=8 and e.id~=12 and c.grounded then
  if c.r('PlayerFacingDir')~=1 then return{right=true}end
  return{b=c.r('Cv3AttackAge')==0 and c.r('Cv3Previous')&64==0}
 end""")
    if item in('life','star'):return text
    text=Stock.once(text,'local goal=C.itemKind==3 and 1024 or 1616','local goal=336')
    old="if C.itemKind==3 and c.lives>=3 or C.itemKind==2 and c.star>0 then phase(c,'credited');return{}end"
    if item=='mushroom':
        text=Stock.once(text,old,"if c.status>0 then phase(c,'credited');return{}end")
    else:
        text=Stock.once(text,old,"""if T.kind==1 and c.sub>0 then
  phase(c,'credited')
  local empty=true;for i=0,3 do if c.r('Cv3ShotType',i)~=0 then empty=false end end
  if not T.cast and empty and c.grounded and c.r('Cv3AttackAge')==0 and c.r('Cv3Previous')&64==0 then
   T.cast={update=c.update,x=c.x,y=c.y,facing=c.r('PlayerFacingDir'),hp=c.hp,hearts=c.hearts,sub=c.sub}
   return{up=true,b=true}
  end
  return{}
 end
 if T.kind==0 and c.status>0 then
  T.mushroom=T.mushroom or sample(c)
  if c.update-T.mushroom.update<40 then return{}end
  T.kind=1;goal=1248;T.actor=nil;T.missing=nil;T.attempts=0;phase(c,'travel')
 end""")
    text=Stock.once(text,'  T.latest=sample(c,a)',"""  T.latest=sample(c,a)
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
    return text


def base_controller(raw,item):
    assert item in('mushroom','flower','life','star')and H(raw)==PIN
    text=A.controller(raw,'life'if item=='life'else'star')
    b=dict(W.Symbols.bundle(),raw=raw)
    fields=('InvPickup','InvPickupOwner','Cv3PickupVariant','Cv3Subweapon','Cv3ShotType','Cv3ShotAge',
            'Cv3ShotX','Cv3ShotPage','Cv3ShotY','Cv3ShotFx','Cv3ShotFy','Cv3ShotVXLo','Cv3ShotVXHi',
            'Cv3ShotVYLo','Cv3ShotVYHi')
    metadata=';'.join('C.ram.'+n+'='+str(W.address(b,n))for n in fields)
    kind={'mushroom':0,'flower':0,'life':3,'star':2}[item]
    expected=[0,1]if item=='flower'else[kind]
    prefix="C.name='SYPHA';C.form='sypha';C.variant=2;C.expected="+Stock.value(expected)
    prefix+=';C.itemKind='+str(kind)+";C.route='"+('upgrades'if item=='flower'else item)+"';"+metadata
    if item=='flower':
        name='Cv3WeaponsGate';at=W.location(b,name)
        hook=dict(pc=W.address(b,name),tag=((at-16)//8192)|128,offset=at-16,hex=raw[at:at+12].hex())
        prefix+=';C.hooks.Weapons='+Stock.value(hook)
    line,body=text.split('\n',1)
    text=line+'\n'+prefix+'\n'+Stock.once(body,A.POLICY,policy(item))
    changes=[("hp=r('Cv3Health',2),hearts=r('Cv3Hearts',2)","hp=r('Cv3Health',1),hearts=r('Cv3Hearts',1),sub=r('Cv3Subweapon',1)"),
        ("kind=r('PowerUpType',i),","kind=r('PowerUpType',i),stamp=r('InvPickup',i),owner=r('InvPickupOwner',i),variant=r('Cv3PickupVariant',i),"),
        ("assert(p.before.power==a.kind and s.growth~=0 and r('GuestPowerupTarget')==a.kind+1,'Actual source growth');return",
         """assert(a.owner==5 and a.variant==2 and a.stamp==(a.kind==0 and 208 or 209),'Actual Sypha pickup metadata')
  assert(s.status==1,'Actual Sypha pickup status')
  if a.kind==0 then
   assert(s.hp==math.min(64,p.before.hp+16)and s.hearts==p.before.hearts and s.sub==p.before.sub,'Mushroom heals with source cap')
  else
   assert(p.before.sub==0 and s.sub==1 and s.hearts==math.min(99,p.before.hearts+5)and s.hp==p.before.hp,'First Flower earns Flame and five hearts')
  end
  return"""),
        ('if q.collect and not q.grant and kind<2 and s.growth==0 and s.status==kind+1',
         'if q.collect and not q.grant and kind<2 and s.growth==0 and s.status==1'),
        ("else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end",
         """else local spent=kind==1 and ROBOT_STOCK_STATE.castPaid and 1 or 0
    assert(s.status==1 and s.hp==q.grant.hp and s.sub==q.grant.sub and s.hearts==q.grant.hearts-spent,
     'Sypha reward persists with only the observed cast cost') end""")]
    for a,z in changes:text=Stock.once(text,a,z)
    if item=='flower':
        text=Stock.once(text,'local function settle()',SPELL_OBSERVER+'\nlocal function settle()')
        text=Stock.once(text,"elseif p.name=='GameLoop' then afterMain()",
            "elseif p.name=='Weapons' then syphaSpell()\n  elseif p.name=='GameLoop' then afterMain()")
        text=Stock.once(text,'if complete then finish(true,','if complete and ROBOT_STOCK_STATE.weaponProof then finish(true,')
    assert not any(t in text for t in('emu.write','emu.setState','saveState','loadState','io.open','dofile','takeScreenshot'))
    Stock.LuaRuntime().compile(text)
    if item in PINS:assert H(text.encode())==PINS[item]
    return text


@lru_cache(maxsize=2)
def reference(raw):
    if H(raw)==PIN:return raw
    assert H(raw)==CURRENT,'Only the exact reviewed DK successor may rebind'
    import compose_dkjr_mushroom_slot_order_1123 as Slot
    import compose_dkjr_mushroom_scrooge_1123 as Mushroom
    assert Slot.CANDIDATE==CURRENT
    intermediate=Slot.inverse(raw)
    assert H(intermediate)==Mushroom.CANDIDATE
    original=Mushroom.inverse(intermediate)
    assert H(original)==PIN and len(original)==len(raw)
    return original


def binding(raw,item):
    original=reference(raw);text=base_controller(original,item)
    cfg=Stock.LuaRuntime().execute(text.split('\nlocal choose=',1)[0]+'\nreturn C')
    hooks={}
    for name,h in cfg['hooks'].items():
        at=16+h['offset'];before=bytes.fromhex(h['hex'])
        assert original[at:at+len(before)]==raw[at:at+len(before)]==before,('Changed Sypha hook',name)
        hooks[name]=dict(offset=at,bytes=len(before),hex=h['hex'])
    proof=dict(source_ROM_SHA256=PIN,actual_ROM_SHA256=H(raw),all_hook_bytes_identical=True,hooks=hooks,
        inverse_chain=[]if H(raw)==PIN else[CURRENT,'3b7b36cad368c89165b37892c3fd9110a1362b6c2579c17a1cad8cf5115cf289',PIN])
    return text,proof


def controller(raw,item):
    text,_=binding(raw,item)
    if H(raw)==PIN:return text
    original=text;assert text.count(PIN)==1
    text=Stock.once(text,PIN,H(raw))
    assert text.replace(H(raw),PIN,1)==original and text.count(H(raw))==1
    Stock.LuaRuntime().compile(text)
    if item in CURRENT_PINS:assert H(text.encode())==CURRENT_PINS[item]
    return text


def cold(raw):
    b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for _ in range(5):W.UI.key(m,1)
    for _ in range(2):W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]=='SYPHA'and N.get(m,'SelectedCharacter')==5 and N.get(m,'Cv3Variant')==2
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(A.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'Cv3Health',1)==64 and N.get(m,'Cv3Hearts',1)==10 and N.get(m,'Cv3Subweapon',1)==0
            return m
        m.controller_pad=0;Engine.Frames.frame(m,cold=True)
    raise AssertionError('Actual Sypha cold bound')


def source(raw,item,limit=2400):
    text=controller(raw,item).replace("assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha",
        "assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha",1)
    text+="\nemu.addEventCallback(guarded('Source bound',function()if physical>="+str(limit)+" then finish(false,'Bounded source diagnostic')end end),emu.eventType.endFrame)"
    with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',H(raw)):return Engine.run(raw,limit+1,text=text)


def native(raw,item,root):
    pins=PINS if H(raw)==PIN else CURRENT_PINS
    assert item in pins
    digest=H(raw);program=controller(raw,item).encode()
    root=root.resolve();assert root.is_relative_to(Stock.R/'build')and root not in(Stock.R/'build',Stock.OUT)
    guard=Stock.check(ROM);assert guard['ROM_sha256']==digest and not guard['matching_patch_files']
    root.mkdir()
    candidate,script=root/'candidate.nes',root/'controller.lua'
    try:
        candidate.write_bytes(raw);script.write_bytes(program)
        q=Stock.run(script,ROM,root/'capture',digest,180)
        print('SYPHA_STOCK_NATIVE '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['script_SHA256']==pins[item]and q['outputs_written']==0 and not q['images']
        return q
    finally:
        script.unlink(missing_ok=True);candidate.unlink(missing_ok=True);root.rmdir()
        assert ROM.read_bytes()==raw and Stock.check(ROM)==guard


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--item',choices=('mushroom','flower','life','star'),default='mushroom')
    g=p.add_mutually_exclusive_group();g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--native-root',type=Path);p.add_argument('--limit',type=int,default=2400);a=p.parse_args();assert 600<=a.limit<=3000
    raw=ROM.read_bytes()
    if a.run:
        assert a.native_root is not None
        return int(not native(raw,a.item,a.native_root)['passed'])
    def deny(*a,**k):raise AssertionError('Source attempted outputs/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        q=source(raw,a.item,a.limit)if a.source else dict(compiled=True,controller_SHA256=H(controller(raw,a.item).encode()),
            provenance=binding(raw,a.item)[1],outputs=0,native=False)
    print('SYPHA_STOCK_SOURCE '+json.dumps(q,separators=(',',':')),flush=True)
    return int(a.source and not q['passed'])


if __name__=='__main__':raise SystemExit(main())
