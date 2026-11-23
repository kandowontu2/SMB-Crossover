"""Exactffd708 Roll Easy natural hidden1-UP and Star, normal inputs only.

Retained Mushroom and full-stage native results keep their own versions.
Source mode declares genuine linked menu/Select/Start entry. Root alone may
--run in the existing shared slot after the exact controller is qualified.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import run_grant_stock_1123 as Host
from current_ice_stock_binding_1122 import RAM_FIELDS
import inspect_rogue_missile_targets_cb95_1116 as Engine

Stock,W,N,H,ROM=Host.Stock,Host.W,Host.N,Host.H,Host.ROM
PIN='ffd7081036bca9cb165d9f4c5527e909126df70f993b4ebec75b7dd7ac83a6b1'
KINDS={'life':3,'star':2}
PINS={'life':'752cf35508766728f424afde64ab02565b85db605e2ffcff1901e3dbd92dbeaf',
      'star':'abc0dae0eafc11d05c0a619547cd3510ae7ff7fb50dfa0a742087b8593959249'}
TRAVEL=Stock.R/'tools/playthroughs/full_roster_policy_og.lua'
CONSUMED=Stock.R/'tools/playthroughs/current_roster_roll_consumed_jump_v1.lua'

POLICY=r'''
local T={kind=C.itemKind,phase='travel',events={}}
ROBOT_STOCK_STATE=T
local holdUntil=0
local function sample(c,a)return{x=c.x,y=c.y,update=c.update,state=c.state,hp=c.hp,energy=c.energy,food=c.food,item=a}end
local function phase(c,p,a)
 T.phase=p;T.at=c.update;assert(#T.events<50,'Bounded natural Roll phases')
 T.events[#T.events+1]={phase=p,player=sample(c,a)}
end
local function steer(c,x,n)return{right=c.x<x-n,left=c.x>x+n}end
local function released(c)return c.r('A_B_Buttons')&128==0 and c.r('PreviousA_B_Buttons')&128==0 end
local function item(c)
 for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==T.kind then
  return{slot=i,x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
 end end
end
local function jump(c,b,p,a)
 phase(c,p,a);holdUntil=c.update+34;T.request=sample(c,a);b.a=true;return b
end
return function(c)
 if C.route=='life'and c.lives>=3 or C.route=='star'and c.star>0 then phase(c,'credited');return{}end
 local goal=T.kind==3 and 1024 or 1616
 local a=item(c)
 if a and not T.actor then T.actor=a;phase(c,'emerge',a)end
 if T.actor and not a then T.missing=T.missing or sample(c);return{}end
 if a then
  T.latest=sample(c,a)
  if a.state&128==0 then return steer(c,goal+(T.kind==3 and 36 or 51),2)end
  if T.phase=='catch'then
   if not c.grounded or c.update-T.at<5 then
    local b=steer(c,math.max(c.camera+2,a.x-3),2);b.a=c.update<holdUntil;return b
   end
   phase(c,'collect',a)
  end
  if T.kind==2 and a.x<goal+80 then
   if math.abs(c.x-(goal+51))>2 then return steer(c,goal+51,2)end
   if c.grounded and released(c)and a.y>=110 and math.abs(a.x-c.x-6)<=13 then
    return jump(c,{right=true},'catch',a)
   end
   return{}
  end
  local x=math.max(c.camera+2,a.x-3);if T.kind==3 then x=math.min(x,1090)end
  if c.grounded and released(c)and math.abs(a.x-c.x)<32 and c.y-a.y>12 then
   return jump(c,steer(c,x,2),'catch',a)
  end
  return steer(c,x,2)
 end
 if T.phase=='travel'then
  if c.x<goal-76 then return travel(c)end
  phase(c,'align')
 end
 if T.phase=='head'then
  if c.grounded and c.update-T.at>60 then phase(c,'align')end
  return{a=c.update<holdUntil}
 end
 if not c.grounded or c.y<160 then return steer(c,goal-64,2)end
 if math.abs(c.x-(goal-6))<=2 and c.vx==0 and released(c)then
  T.attempts=(T.attempts or 0)+1;assert(T.attempts<=6,'Bounded real Roll authored bump')
  return jump(c,{},'head')
 end
 return steer(c,goal-6,2)
end
'''


def once(text,a,b):
    assert text.count(a)==1,(a,text.count(a));return text.replace(a,b,1)


@lru_cache(maxsize=2)
def bindings(raw,route):
    assert H(raw)==PIN and route in KINDS
    b=dict(W.Symbols.bundle(),raw=raw)
    names=set(n for n in RAM_FIELDS if not n.startswith('Ic'))
    names.update('GuestPowerupActive GuestPowerupTarget GuestLegacyHurt PlayerScoreDisplay RlVariant RlReady RlHealth RlEnergy RlLife RlFoodKind RlPrevious RlHurt RlInvul RlAttack RlCharge GamePauseStatus'.split())
    ram={n:W.address(b,n)for n in names};hooks={}
    def hook(name,symbol,delta=0):
        pc,at=W.address(b,symbol)+delta,W.location(b,symbol)+delta;bank=(at-16)//8192
        assert at-16==bank*8192+(pc&8191)
        hooks[name]=dict(pc=pc,tag=bank|128,offset=at-16,hex=raw[at:at+12].hex())
    for name,symbol in (('GameLoop','GameLoop'),('Movement','RlMovement'),
                        ('HandlePowerUpCollision','HandlePowerUpCollision'),('PlayerHeadCollision','PlayerHeadCollision')):
        hook(name,symbol)
    if route=='life':
        at=W.location(b,'DecNumTimer');needle=b'\xee'+ram['NumberofLives'].to_bytes(2,'little');body=raw[at:at+48]
        assert body.count(needle)==1;hook('LifeCredit','DecNumTimer',body.index(needle))
    nav=[]
    for i in range(32):
        row,col=divmod(i,8);nav.append('down'if row==0 else'up'if row>1 else'right'if col<1 else'left'if col>1 else'')
    return dict(sha=PIN,form='roll',name='ROLL',char=9,slot=9,variant=1,variant_field='RlVariant',variant_mask=255,
                route=route,itemKind=KINDS[route],expected=[KINDS[route]],mode_value=0,ram=ram,hooks=hooks,navigation=nav)


@lru_cache(maxsize=2)
def controller(raw,route):
    cfg=bindings(raw,route);parent=Host.Family.reference(Host.origin(raw))
    original=Stock.controller(parent,'simon',route).decode();marker="assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha"
    assert original.count(marker)==1;text=original[original.index(marker):];baseline=text;edits=[]
    def edit(a,b):
        nonlocal text
        text=once(text,a,b);edits.append((a,b))
    edit(marker,"assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha")
    edit("assert(r(C.variant_field)&C.variant_mask==0,'Original identity in menu')","if r(C.variant_field)~=C.variant then return pulse('select')end")
    edit('r(C.variant_field)&C.variant_mask==0','r(C.variant_field)==C.variant')
    edit("power=r('PlayerStatus'),growth=r('GuestPowerupActive')","power=r('PlayerStatus'),growth=r('GuestPowerupActive'),hp=r('RlHealth'),energy=r('RlEnergy'),food=r('RlFoodKind'),savedLife=r('RlLife')")
    edit('c.poll=updates;c.char=C.char;c.update=updates;','c.poll=motor;c.char=C.char;c.update=motor;c.frame=motor;')
    edit("assert(updates<5100 and s.yHigh<2,'Bounded living pickup route')","assert(updates<4000 and s.yHigh<2 and s.hp>0 and(s.lives==2 or(C.route=='life'and checks['3'].grant and s.lives==3)),'Bounded living natural Roll route')\n assert(r('RlReady')==82,'Native Roll owner is initialized')")
    edit("s.lives==q.grant.lives and (cues[64]or 0)>q.collect.life_cue,'Earned life and cue persist'","s.lives==q.grant.lives and (cues[64]or 0)>q.collect.life_cue and s.savedLife==s.lives and s.hp==q.grant.hp and s.energy==q.grant.energy and s.food==q.grant.food,'Real life, cue and original Roll records persist'")
    edit("s.star>0 and score()>=q.collect.score_before+1000,'Earned Star and score persist'","s.star>0 and score()>=q.collect.score_before+1000 and s.hp==q.grant.hp and s.energy==q.grant.energy and s.food==q.grant.food,'Native Star, score and original Roll records persist'")
    edit("if complete then finish(true,","if complete then assert(#pending==0 and not lifePending,'Actual owning workers returned');finish(true,")
    edit('phase=ROBOT_STOCK_STATE or {},sound_cues=cues,controller_only=true,files=0,images=0','phase=ROBOT_STOCK_STATE or {},sound_cues=cues,pending_returns=#pending,controller_only=true,game_state_writes=false,files=0,images=0')
    restored=text
    for a,b in reversed(edits):assert restored.count(b)==1;restored=restored.replace(b,a,1)
    assert restored==baseline
    assert H(TRAVEL.read_bytes())=='17d3a38d53fe09b930048f081938bf707028f765577207bce41777ea4f5edb7b'
    travel=once(TRAVEL.read_text(),"local phase='approach';local clock=0;","local phase='route';local clock=0;")
    consume=once(CONSUMED.read_text(),"local root = ROSTER_CONFIG.root\nlocal base = dofile(root..'/tools/playthroughs/full_roster_policy_og.lua')",'local base=(function()\n'+travel+'\nend)()')
    program='local C='+Stock.value(cfg)+"\nlocal ROSTER_CONFIG={name='roll'}\nlocal travel=(function()\n"+consume+'\nend)()\nlocal choose=(function()\n'+POLICY+'\nend)()\n'+text
    assert not any(s in program for s in('emu.write','emu.setState','saveState','loadState','io.open','dofile','takeScreenshot'))
    Stock.LuaRuntime().compile(program);return program.encode()


def cold(raw,route):
    bindings(raw,route);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in (4,1,32):W.UI.key(m,pad)
    assert W.UI.menu_name(m)[0]=='ROLL'and N.get(m,'SelectedCharacter')==9 and N.get(m,'RlVariant')==1
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Host.Family.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'RlReady')==82 and N.get(m,'RlHealth')==N.get(m,'RlEnergy')==28
            assert N.get(m,'NumberofLives')==2 and N.get(m,'CrossoverBehaviorVersion')==0
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Engine.Frames.frame(m,cold=True)
    raise AssertionError('Genuine linked Roll menu/Select/Start entry bound')


def source(raw,route,limit):
    program=controller(raw,route);assert H(program)==PINS[route]
    with patch.object(Engine.J,'cold',lambda image:cold(image,route)),patch.object(Engine.J,'PIN',PIN):return Engine.run(raw,limit,text=program.decode())


def native(raw,route):
    program=controller(raw,route);assert H(program)==PINS[route]
    out=Stock.OUT;candidate,script=out/'candidate.nes',out/'controller.lua';before=script.read_bytes();guard=Stock.check(ROM)
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(out.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Stock.preserve_script(script,candidate,raw)as stage:stage(program);q=Stock.run(script,ROM,out/'capture',PIN,210)
        assert q['script_SHA256']==PINS[route]and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and Stock.check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--route',choices=KINDS,default='life')
    mode=p.add_mutually_exclusive_group();mode.add_argument('--source',action='store_true');mode.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=3500);a=p.parse_args();assert 1200<=a.limit<=4200
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:q=native(raw,a.route)
    else:
        def deny(*a,**k):raise AssertionError('Roll source attempted outputs/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.route,a.limit)
            else:
                program=controller(raw,a.route);assert H(program)==PINS[a.route]
                q=dict(passed=True,ROM_SHA256=PIN,controller_SHA256=H(program),route_executed=False,outputs=0)
    print('ROLL_STOCK '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
