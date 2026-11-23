"""Separate exact94fa natural Link family life/Star/Flower continuations."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch

import run_link_family_mushroom_1123 as First
from replay_sonic_hidden_life_f7c9_1116 import value
from check_ff_stdout_controller_source_1110 import LuaRuntime
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

H,R,ROM,OUT,W,N=First.H,First.R,First.ROM,First.OUT,First.W,First.N
preserve_script=First.preserve_script
PIN='94fa7a028ea86cc33eee50e9890e1eda05765bf6e8fd8fe82134a0388fa330db'
CURRENT='3af597a72c3ef048085de0a01e5f53443b8aa8ddf0a92d6e1882c2d225dccd1c'
SHORT={'link':'5b652e85d7c83a11aaa1e0dc2d8abf08ca6d447cdd994cc6e86599c710c41a5e',
       'zelda2':'07dd433297e28f9f5233504cf78b68f8d1c7a2725026b9e089913d48921e236d'}
KINDS={'life':3,'star':2,'flower':1}
PINS={('link','life'):'22db7f901508c1c405ea2121c7c6d9c41e766574a822fcba161cc7252ba108dd',
      ('link','star'):'689791c7a07bb34e7eeaf558d434495bf5725de04cc904dbc94681fa94eab2e4',
      ('link','flower'):'a58109219d01448efcbcfd8b9bc0a5bc5e818f157f6f1ae0800a33ee66739cfd',
      ('zelda2','life'):'d91e5610f8d7ff94907b06b53ab658f37961d3e5cdac753549c115877c28b2a1',
      ('zelda2','star'):'69b1b8ddedccb5790f73e76f5677e574d69b2c46a392aa6d7b5f57670625a818',
      ('zelda2','flower'):'a5d6739f086855b2fc5c8c8ced8b8bca9de37be0f9ec769d87ffa432af94be8d'}
HISTORICAL_STAR={'link':'6d03c9233a34adde56f849ebd033343f947d8ab87b7ce7c9461a1756693fbdc0',
                 'zelda2':'50e8c6dcf6f27202dbbf6421cdf2c05644e33343b9efe7c44425d42415a04e0b'}
GUARD_PIN='f69e1b06fcf6b853d205e83be99523543e9abf0a89010db23e79e4943a9cf2f9'
DOWNTHRUST_FLOWER_PIN='b0ba1ae2f3bf86c629fcec4661aa9e3fdb1e940d087f9cdc2e383e57fbb35546'

STAR_GUARD=r'''local function defend(c,b)
 if c.grounded and c.y>=160 then
  local e
  for i=0,5 do
   local id,st=c.r('Enemy_ID',i),c.r('Enemy_State',i)
   local dx=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)-c.x
   local y=c.r('Enemy_Y_Position',i)
   if c.r('Enemy_Flag',i)==1 and(id==0 or id==3 or id==6)and st<32 and y>=168
      and dx> -52 and dx<72 and(not e or math.abs(dx)<math.abs(e.dx))then e={dx=dx,slot=i,id=id,state=st}end
  end
  if e then
   local facing=e.dx<0 and 2 or 1
   if c.r('PlayerFacingDir')~=facing then return{right=facing==1,left=facing==2}end
   return{down=C.variant==1,b=C.variant==1 and c.update%12<3 or C.variant==0 and c.r('RgAttack')==0}
  end
 end
 return b
end
'''

POLICY=r'''
local T={phase='start',events={},target=C.target_kind}
LINK_FAMILY_STOCK=T
local holdUntil=-1
local function sample(c)
 return{x=c.x,y=c.y,update=c.update,motor=c.motor,state=c.state,power=c.status,
        hp=c.hp,learned=c.learned,selection=c.selection,tech=c.tech,mp=c.mp,active=c.active}
end
local function phase(c,p)
 T.phase=p;T.at=c.update
 assert(#T.events<48,'Bounded ordinary Link continuation phases')
 T.events[#T.events+1]={phase=p,player=sample(c)}
end
local function steer(c,x,band)return{right=c.x<x-band,left=c.x>x+band}end
local function targetItem(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 then
   local stamp=c.r('InvPickup',i);local native=c.r('PowerUpType',i)
   local kind=native
   if C.variant==1 and c.r('InvPickupOwner',i)==4 and stamp>=0xc0 and stamp<0xce then
    kind=c.r('InvPickupSaveLo',i)&1~=0 and 0 or 1
   end
   if kind==T.target then return{slot=i,kind=kind,stamp=stamp,
    x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),
    mature=c.r('Enemy_State',i)&128~=0}end
  end
 end
end
local function defend(c,b)
 local e=c.enemy()
 if e and e.dx>0 and e.dx<62 and math.abs(e.y-c.y)<42 and c.grounded then
  if c.r('PlayerFacingDir')~=1 then return{right=true}end
  if C.variant==1 then return{b=c.update%12<3}end
  return{b=c.r('RgAttack')==0,select=e.dx>32 and c.update%12==0}
 end
 return b
end
return function(c)
 if not LINK_FAMILY_CONTINUE then return shortChoose(c)end
 if C.variant==1 and c.r('GamePauseStatus')&1~=0 then return{b=c.update%4==0}end
 if T.phase=='start'then
  T.start=sample(c)
  if C.variant==1 then
   assert(c.learned&2~=0 and c.selection&7==1,'Naturally learned Jump precedes ordinary Select cast')
   if c.active&2==0 then
    T.cast_before=T.cast_before or sample(c);return{select=c.update%4==0}
   end
   T.cast_after=sample(c)
   assert(T.cast_before and c.mp<T.cast_before.mp,'Real earned Jump cast pays native magic')
  end
  phase(c,'travel')
 end
 if LINK_FAMILY_TARGET_COLLECTED then return{}end
 local kind=T.target;local goal=kind==3 and 1024 or kind==2 and 1616 or 1248
 local a=targetItem(c)
 if a and not T.seen then T.seen=a;phase(c,'emerge')end
 if T.seen and not a then T.missing=sample(c);return{}end
 if T.phase=='travel'then
  if kind==2 and c.x>=1176 and c.x<1272 then return defend(c,{right=true})end
  if c.x<goal-76 then return opening(c)end
  phase(c,'align')
 end
 if T.phase=='align'then
  local aim=kind==1 and goal+3 or goal-7
  if not c.grounded or c.y<160 then return defend(c,steer(c,goal-56,2))end
  if math.abs(c.x-aim)<=2 and not c.lastA and(C.variant==1 or c.r('RgAttack')==0)then
   T.attempts=(T.attempts or 0)+1;assert(T.attempts<=8,'Bounded actual authored head bumps')
   holdUntil=c.update+28;phase(c,'bump');return{a=true}
  end
  return defend(c,steer(c,aim,2))
 end
 if T.phase=='bump'then
  if c.grounded and c.update-T.at>52 then phase(c,'align')end
  return{a=c.update<holdUntil}
 end
 if T.phase=='emerge'then
  local wait=kind==1 and goal+36 or goal+38
  if not a.mature then return defend(c,steer(c,wait,3))end
  phase(c,'collect')
 end
 if T.phase=='collect'then
  if kind==1 then
   if c.grounded and c.y>=160 then
    if math.abs(c.x-(goal+36))<=3 and not c.lastA and(C.variant==1 or c.r('RgAttack')==0)then
     holdUntil=c.update+30;phase(c,'catch');return{left=true,a=true}
    end
    return defend(c,steer(c,goal+36,2))
   end
   return steer(c,a.x-2,2)
  end
  if c.grounded and c.y-a.y>14 and a.x>=goal+9 and math.abs(c.x-a.x)<30 and not c.lastA
     and(C.variant==1 or c.r('RgAttack')==0)then
   holdUntil=c.update+30;phase(c,'catch');return{a=true}
  end
  local aim=math.max(goal+34,a.x-3);if kind==3 then aim=math.min(aim,1091)end
  return defend(c,steer(c,aim,2))
 end
 if T.phase=='catch'then
  if c.grounded and c.update-T.at>4 then phase(c,'collect')end
  local b=steer(c,a.x-2,2);b.a=c.update<holdUntil;return b
 end
 return{}
end
'''


def controller(raw,form,route,*,historical_star=False):
    assert H(raw)==PIN and form in First.FORMS and route in KINDS
    assert not historical_star or route=='star'
    original=First.native_program(raw,form,pursuit=form=='zelda2').decode()
    assert H(original.encode())==SHORT[form]
    old=First.reference(raw);cfg=deepcopy(First.bindings(old,form))
    cfg.update(sha=PIN,route=route,expected=[0,KINDS[route]],target_kind=KINDS[route],short_controller=SHORT[form])
    for name in('Z2Tech','Z2Mp'):
        cfg['ram'][name]=W.address(dict(W.Symbols.bundle(),raw=raw),name)
    if route=='star' and not historical_star:
        cfg['ram']['Z2HurtTimer']=W.address(dict(W.Symbols.bundle(),raw=raw),'Z2HurtTimer')
    if route=='life':
        pc,bank=0x8987,126;at=16+bank*8192+(pc&8191)
        assert raw[at:at+3]==b'\xee'+cfg['ram']['NumberofLives'].to_bytes(2,'little')
        cfg['hooks']['LifeCredit']=dict(pc=pc,tag=bank|128,offset=at-16,hex=raw[at:at+8].hex())
    text=original;edits=[]
    def edit(a,b):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b,1);edits.append((a,b))
    edit(original.split('\n',1)[0],'local C='+value(cfg))
    marker="assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha"
    policy=POLICY
    if form=='link':
        policy=policy.replace("local function steer(c,x,band)return{right=c.x<x-band,left=c.x>x+band}end",
            "local function steer(c,x,band)local vx=c.vx<128 and c.vx or c.vx-256;local d=x-c.x-vx/4;return{right=d>band,left=d< -band}end",1)
        policy=policy.replace('local aim=kind==1 and goal+3 or goal-7','local aim=kind==1 and goal+3 or goal-5',1)
        policy=policy.replace('if math.abs(c.x-aim)<=2 and not c.lastA',
                              'if math.abs(c.x-aim)<=2 and c.vx==0 and not c.lastA',1)
    if route=='star' and not historical_star:
        marker_star=' local kind=T.target;local goal='
        assert policy.count(marker_star)==1
        evade=r'''
 if T.star_evade then
  local h=T.star_evade;local age=c.update-h.at
  if c.grounded and age>4 then T.star_evade=nil
  else
   if not c.grounded and c.vy>=128 then h.takeoff=h.takeoff or sample(c)end
   assert(age<100,'Bounded ordinary jump past the real pre-Star ground enemy')
   return{right=c.x<1590,a=age<24}
  end
 end
 if not T.seen and c.x>=1424 and c.x<1600 and c.grounded and not c.lastA
    and(C.variant==1 and c.hurt==0 or C.variant==0 and c.r('RgAttack')==0)then
  for i=0,5 do
   local id=c.r('Enemy_ID',i);local st=c.r('Enemy_State',i)
   local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i);local y=c.r('Enemy_Y_Position',i)
   if c.r('Enemy_Flag',i)==1 and(id==0 or id==3 or id==6)and st<32
      and x-c.x>=28 and x-c.x<=72 and y>=168 then
    T.evades=T.evades or{};assert(#T.evades<4,'Bounded real pre-Star ground threats')
    local h={at=c.update,before=sample(c),enemy={slot=i,id=id,state=st,x=x,y=y}}
    T.evades[#T.evades+1]=h;T.star_evade=h;return{right=true,a=true}
   end
  end
 end
'''
        policy=policy.replace(marker_star,evade+marker_star,1)
        policy=policy.replace('a.x>=goal+9 and math.abs(c.x-a.x)<30',
                              '(kind==2 or a.x>=goal+9)and math.abs(c.x-a.x)<30',1)
        policy=policy.replace('and(C.variant==1 or c.r(\'RgAttack\')==0)then\n   holdUntil=c.update+30;phase(c,\'catch\')',
                              "and(C.variant==1 and c.hurt==0 or C.variant==0 and c.r('RgAttack')==0)then\n   holdUntil=c.update+30;phase(c,'catch')",1)
        policy=policy.replace('local aim=math.max(goal+34,a.x-3);if kind==3 then aim=math.min(aim,1091)end',
                              'local aim=kind==2 and math.max(c.camera+2,a.x-3)or math.max(goal+34,a.x-3);if kind==3 then aim=math.min(aim,1091)end',1)
    edit(marker,'local shortChoose=choose\nchoose=(function()\n'+policy+'\nend)()\n'+marker)
    edit('kind=C.variant==1 and 0 or r(\'PowerUpType\',i),',
         "kind=C.variant==1 and r('InvPickupOwner',i)==4 and r('InvPickup',i)>=0xc0 and r('InvPickup',i)<0xce and(r('InvPickupSaveLo',i)&1~=0 and 0 or 1)or r('PowerUpType',i),")
    edit("hpPending=r('Z2HpPending')", "hpPending=r('Z2HpPending'),tech=r('Z2Tech'),mp=r('Z2Mp'),active=r('Z2ActiveSpells')")
    if route=='star' and not historical_star:
        edit("active=r('Z2ActiveSpells')", "active=r('Z2ActiveSpells'),hurt=r('Z2HurtTimer')")
    edit('local cue=0','local cue=0\nlocal lifeCue=0')
    edit("assert(updates<1600 and s.yHigh<2 and s.lives==2 and(C.variant==0 or s.hp>0),'Bounded living first-block route')",
         "assert(updates<4800 and s.yHigh<2 and(s.lives==2 or(C.route=='life'and checks['3'].grant and s.lives==3))and(C.variant==0 or s.hp>0),'Bounded living natural Link continuation')")
    edit("assert(heads['0'],'Actual authored first block bump')", "assert(heads[tostring(a.kind)],'Actual authored block bump')")
    needle=' local complete=true'
    edit(needle,""" if checks['0'].after then LINK_FAMILY_CONTINUE=true end
 if LINK_FAMILY_CONTINUE and C.variant==0 and r('GuestLegacyHurt')==1 then
  finish(false,'Ordinary Link lost his earned tier during the continuation');return
 end
 local target=checks[tostring(C.target_kind)]
 if target.collect then
  LINK_FAMILY_TARGET_COLLECTED=true
  if not target.grant and C.target_kind~=3 and s.growth==0 and score()>=target.collect.score_before+1000 then
   if C.target_kind==1 then
    assert(C.variant==0 and s.status==2 or C.variant==1 and s.tech&16~=0,'Original Flower family reward persists')
   else assert(s.star>0,'Actually earned native Star persists')end
   target.grant=s
  end
 end
 if LINK_FAMILY_STOCK.missing and not target.collect then finish(false,'Actual target disappeared before collection');return end
"""+needle)
    edit("else assert(s.status==1 and s.growth==0 and(C.variant==0 or s.learned&2~=0),'Earned Link reward persists during movement')end",
         "else assert(s.growth==0 and(C.variant==0 and s.status==q.grant.status or C.variant==1 and s.learned&2~=0),'Earned Link reward persists during movement')end")
    edit("if kind==3 then assert(s.lives==q.grant.lives,'Earned life persists during movement')",
         "if kind==3 then assert(s.lives==q.grant.lives and lifeCue>q.collect.life_cue_before,'Native earned life and cue persist during movement')")
    edit("elseif kind==2 then assert(s.star>0,'Earned Star persists during movement')",
         "elseif kind==2 then assert(s.star>0 and score()>=q.collect.score_before+1000,'Native Star and credit persist during movement')")
    edit("Natural first Mushroom block, original reward and25 living movement returns", "Natural Link-family pickups, physical credit and25 living movement returns")
    edit('score_before=p.score}', 'score_before=p.score,life_cue_before=p.life_cue}')
    old_branch="""if C.variant==0 then
   assert(p.before.status==0 and s.growth~=0 and r('GuestPowerupTarget')==1,'Original Easy Link growth begins')
  else"""
    new_branch="""if a.kind==1 then
   if C.variant==0 then
    assert(p.before.status==1 and s.growth~=0 and r('GuestPowerupTarget')==2,'Original Easy Link Flower growth begins')
   else
    assert(a.owner==4 and a.stamp==0xc1 and p.before.tech&16==0 and s.tech&16~=0,
           'Actual next Z2 Flower food grants original Shield technology')
   end
  elseif C.variant==0 then
   assert(p.before.status==0 and s.growth~=0 and r('GuestPowerupTarget')==1,'Original Easy Link growth begins')
  else"""
    edit(old_branch,new_branch)
    edit('p.score=score();p.cue=cue','p.score=score();p.cue=cue;p.life_cue=lifeCue')
    edit('cue_count=cue,pending_returns=#pending,', 'continuation=LINK_FAMILY_STOCK,short_controller_SHA256=C.short_controller,life_cue_count=lifeCue,cue_count=cue,pending_returns=#pending,')
    edit("if entered and v==32 then cue=cue+1 end", "if entered and v==32 then cue=cue+1 elseif entered and v==64 then lifeCue=lifeCue+1 end")
    edit('physical<=6900','physical<=11000')
    restored=text
    for a,b in reversed(edits):assert restored.count(b)==1;restored=restored.replace(b,a,1)
    assert restored==original
    LuaRuntime().compile(text)
    assert not any(t in text for t in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    if historical_star:assert H(text.encode())==HISTORICAL_STAR[form]
    return text


def variant(program,form,route,*,star_guard=False,historical_flower_label=False):
    """Add separately pinned inputs/labels; baseline constructors stay exact."""
    assert not star_guard or(form=='zelda2'and route=='star')
    assert not historical_flower_label or(form=='zelda2'and route=='flower')
    text=program;edits=[]
    if star_guard:
        begin=text.index('local function defend(c,b)')
        old=text[begin:text.index('return function(c)',begin)]
        assert text.count(old)==1
        text=text.replace(old,STAR_GUARD,1);edits.append((old,STAR_GUARD))
    if form=='zelda2'and route=='flower'and not historical_flower_label:
        old='Actual next Z2 Flower food grants original Shield technology'
        new='Actual next Z2 Flower food grants original Downthrust'
        assert text.count(old)==1
        text=text.replace(old,new,1);edits.append((old,new))
    restored=text
    for old,new in reversed(edits):
        assert restored.count(new)==1;restored=restored.replace(new,old,1)
    assert restored==program
    LuaRuntime().compile(text)
    return text


def program_pin(form,route,*,star_guard=False,historical_flower_label=False):
    if star_guard:return GUARD_PIN
    if form=='zelda2'and route=='flower'and not historical_flower_label:return DOWNTHRUST_FLOWER_PIN
    return PINS[(form,route)]


def reference(raw):
    if H(raw)==PIN:return raw
    import compose_dkjr_side_epoch_fast_1123 as Fast
    assert H(raw)==CURRENT==Fast.CANDIDATE and Fast.PIN==PIN
    old=Fast.inverse(raw)
    assert H(old)==PIN
    return old


def native_program(raw,form,route,*,star_guard=False,historical_flower_label=False):
    """Authenticate the exact inverse and hooks, then change only ROM identity."""
    old=reference(raw);baseline=controller(old,form,route)
    assert H(baseline.encode())==PINS[(form,route)]
    program=variant(baseline,form,route,star_guard=star_guard,historical_flower_label=historical_flower_label).encode()
    assert H(program)==program_pin(form,route,star_guard=star_guard,historical_flower_label=historical_flower_label)
    hooks=LuaRuntime().execute(program.decode().split('\n',1)[0]+'\nreturn C.hooks')
    for name,hook in hooks.items():
        at=16+int(hook['offset']);expected=bytes.fromhex(hook['hex'])
        assert old[at:at+len(expected)]==raw[at:at+len(expected)]==expected,name
    if H(raw)==PIN:return program
    assert program.count(PIN.encode())==1
    rebound=program.replace(PIN.encode(),CURRENT.encode(),1)
    assert rebound.replace(CURRENT.encode(),PIN.encode(),1)==program
    LuaRuntime().compile(rebound.decode())
    return rebound


def source(raw,form,route,limit,*,star_guard=False):
    import inspect_rogue_missile_targets_cb95_1116 as Engine
    program=native_program(raw,form,route,star_guard=star_guard).decode();original_reference=First.reference
    def cold(image):
        assert image is raw
        def bind(value):return original_reference(reference(value))
        with patch.object(First,'reference',bind):return First.cold(image,form)
    with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',H(raw)):
        return Engine.run(raw,limit,text=program)


def native(raw,form,route,*,star_guard=False):
    program=native_program(raw,form,route,star_guard=star_guard);expected=H(raw)
    guard=check(ROM);candidate,script=OUT/'candidate.nes',OUT/'controller.lua';before=script.read_bytes()
    assert guard['ROM_sha256']==expected and not guard['matching_patch_files']
    assert set(OUT.iterdir())=={candidate,script} and candidate.read_bytes()==raw
    try:
        with preserve_script(script,candidate,raw)as stage:
            stage(program);q=run(script,ROM,OUT/'capture',expected,180)
        assert q['script_SHA256']==H(program)and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--form',choices=tuple(First.FORMS),default='link')
    p.add_argument('--route',choices=tuple(KINDS),default='life')
    p.add_argument('--star-guard',action='store_true',help='Separately pinned Zelda II Star floor-enemy crouched sword guard')
    mode=p.add_mutually_exclusive_group();mode.add_argument('--source',action='store_true');mode.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=4200);a=p.parse_args();assert 1600<=a.limit<=4800
    raw=ROM.read_bytes();reference(raw)
    assert not a.star_guard or(a.form=='zelda2'and a.route=='star')
    if a.run:q=native(raw,a.form,a.route,star_guard=a.star_guard)
    else:
        def deny(*args,**kwargs):raise AssertionError('Link continuation attempted files or emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.form,a.route,a.limit,star_guard=a.star_guard)
            else:
                program=native_program(raw,a.form,a.route,star_guard=a.star_guard);q=dict(passed=True,ROM_SHA256=H(raw),reference_SHA256=PIN,controller_SHA256=H(program),reference_controller_SHA256=program_pin(a.form,a.route,star_guard=a.star_guard),baseline_controller_SHA256=PINS[(a.form,a.route)],route_executed=False,files=0)
    print('LINK_FAMILY_STOCK '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
