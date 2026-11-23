"""Separate exactffd708 natural Roll Mushroom->Flower restoration replay.

Normal controller input earns both actors, a live-enemy health deficit and
an actually paid automatic charge. The frozen hidden-life/Star file is read
only. Source declares linked native-menu entry; Root alone may --run.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import run_roll_stock_1123 as Base

H,W,N,ROM,Stock,Engine=Base.H,Base.W,Base.N,Base.ROM,Base.Stock,Base.Engine
PIN=Base.PIN
BASE_SHA='d95e4a4f91819fcc57c17721da78090fba6c647817535ed9f5647afb63a3ddb5'
LUA='76d48634820674d76580909296fda36d371d8e07a7d5fb50343d79999fc84298'

POLICY=r'''
local T={kind=0,phase='travel',events={}}
ROBOT_STOCK_STATE=T
local holdUntil=0
local function sample(c)return{x=c.x,y=c.y,update=c.update,state=c.state,hp=c.hp,energy=c.energy,food=c.food}end
local function phase(c,p)
 if T.phase==p then return end
 T.phase=p;T.at=c.update;assert(#T.events<60,'Bounded ordinary Roll food phases')
 T.events[#T.events+1]={kind=T.kind,phase=p,player=sample(c)}
end
local function steer(c,x,n)return{right=c.x<x-n,left=c.x>x+n}end
local function released(c)return c.r('A_B_Buttons')&128==0 and c.r('PreviousA_B_Buttons')&128==0 end
local function item(c)
 for i=0,5 do if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==T.kind then
  return{slot=i,x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i)}
 end end
end
local function woundedTravel(c)
 if T.damage and c.grounded and c.y==176 and c.x>=920 and c.x<1080 and c.block(c.x+32,208)~=0 and c.block(c.x+32,192)==0 then
  return{right=true}
 end
 if not T.damage and c.hp==28 and c.r('RlInvul')==0 and c.grounded and c.y==176 and c.x>=500 then
  for i=0,5 do
   local dx=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)-c.x
   local id,st=c.r('Enemy_ID',i),c.r('Enemy_State',i)
   if c.r('Enemy_Flag',i)==1 and(id==0 or id==3 or id==6)and st<2 and c.r('Enemy_Y_Position',i)>=168 and dx>8 and dx<70 then
    local clear=true;for x=c.x+8,c.x+dx+8,8 do if c.block(x,208)==0 or c.block(x,192)~=0 then clear=false end end
    if clear then
     if dx>=16 then return{right=true}end
     if not released(c)then return{}end
     T.woundRequest={player=sample(c),slot=i};T.woundUntil=c.update+5
     return{a=true}
    end
   end
  end
 end
 local b=travel(c)
 b.b=false
 if T.woundUntil and c.update<T.woundUntil then b.a=true end
 return b
end
return function(c)
 if ROLL_FLOWER_COLLECTED then return{}end
 if T.kind==0 and ROLL_FIRST_COLLECTED and not ROLL_FIRST_AFTER then return{}end
 if T.kind==0 and ROLL_FIRST_AFTER then T.kind=1;T.actor=nil;T.missing=nil;T.attempts=0;phase(c,'travel')end
 local goal=T.kind==0 and 336 or 1248
 local a=item(c)
 if a and not T.actor then T.actor=a;phase(c,'emerge')end
 if T.actor and not a then T.missing=T.missing or sample(c);return{}end
 if T.kind==0 and a then
  T.latest={player=sample(c),actor=a}
  return steer(c,c.y<160 and 404 or 396,2)
 end
 if T.phase=='travel'then
  if c.x<goal-76 then return T.kind==1 and woundedTravel(c)or travel(c)end
  phase(c,'align')
 end
 if T.phase=='align'then
  if not c.grounded or c.y<160 then return steer(c,goal-64,2)end
  if math.abs(c.x-(goal-6))<=2 and c.vx==0 and released(c)then
   T.attempts=(T.attempts or 0)+1;assert(T.attempts<=6,'Bounded real Roll power-block bumps')
   phase(c,'head');holdUntil=c.update+34;return{a=true}
  end
  return steer(c,goal-6,2)
 end
 if T.phase=='head'then
  if c.grounded and c.update-T.at>60 then phase(c,'align')end
  return{a=c.update<holdUntil}
 end
 if T.kind==1 and a then
  T.latest={player=sample(c),actor=a}
  if T.phase=='emerge'then phase(c,'charge-setup')end
  if T.phase=='charge-setup'then
   if math.abs(c.x-1284)>3 or not c.grounded or c.y~=176 then return steer(c,1284,3)end
   if c.vx~=0 or c.r('RlHurt')~=0 then return{}end
   if c.r('PlayerFacingDir')~=1 then return{right=true}end
   if a.state&128==0 then return{}end
   if T.charge and T.charge.paid then phase(c,'release');return{}end
   assert(c.energy==28 and c.r('RlCharge')==0,'Original full energy before an actually earned charge expense')
   T.charge={requested=sample(c),fired=c.r('RlChargeFired')};phase(c,'charge');return{b=true}
  end
  if T.phase=='charge'then
   assert(c.update-T.at<180,'Bounded actual automatic paid charge')
   if not T.charge.paid then return{b=true}end
   phase(c,'release');return{}
  end
  if T.phase=='release'then
   if not released(c)or c.r('RlPrevious')&64~=0 then return{}end
   T.launch=sample(c);T.mounts=(T.mounts or 0)+1;assert(T.mounts<=5,'Bounded normal right-hand Flower approach')
   phase(c,'mount');holdUntil=c.update+34;return{left=true,a=true}
  end
  if T.phase=='mount'then
   assert(c.update-T.at<150,'Ordinary Roll jump reaches the real Flower')
   if c.grounded and c.update-T.at>5 and c.y>=160 then phase(c,'charge-setup');return steer(c,1284,3)end
   local b=steer(c,a.x+10,2);b.a=c.update<holdUntil
   b.b=c.r('PlayerFacingDir')==2 and c.update%12<2
   return b
  end
 end
 return{}
end
'''

RETURNS=r'''
local function rollFlowerReturn(p)
 local s=state();local T=ROBOT_STOCK_STATE
 if p.rollCollect then
  local q=checks[tostring(p.rollCollect.kind)]
  assert(s.hp==28 and s.energy==28 and s.food==1 and s.status==1 and s.growth==0,'Actual immediate native Roll restores both health and energy')
  if p.rollCollect.kind==1 then
   assert(T.damage and T.charge and T.charge.paid and p.before.hp<28 and p.before.energy<28,
    'Real contact and paid original charge deficits precede the genuine Flower')
  end
  q.family={before=p.before,after=s,slot=p.rollCollect.slot,kind=p.rollCollect.kind,pc=p.entryPC,return_pc=p.pc,return_sp=p.sp}
 elseif p.weapon and T.charge and not T.charge.paid and s.energy<p.weapon.energy then
  assert(p.weapon.energy==28 and s.energy==24 and r('RlChargeFired')==T.charge.fired+1,
   'Actual native automatic charge spends4 only after a successful original Spawn')
  T.charge.paid={before=p.weapon,after=s,fired=r('RlChargeFired')}
 elseif p.damage and checks['0'].after and not T.damage and s.hp<p.damage.hp then
  assert(p.damage.hp==28 and s.hp==24 and p.victim.flag==1 and p.victim.state<32,'A live native actor causes original4HP injury after earned Mushroom')
  T.damage={before=p.damage,after=s,actor=p.victim,pc=p.entryPC,return_pc=p.pc,return_sp=p.sp}
 end
end
'''


@lru_cache(maxsize=1)
def controller(raw):
    assert H(raw)==PIN and H(Path(Base.__file__).read_bytes())==BASE_SHA
    old=Base.controller(raw,'star');assert H(old)==Base.PINS['star'];text=old.decode();changes=[]
    def edit(a,b):
        nonlocal text
        text=Base.once(text,a,b);changes.append((a,b))
    b=dict(W.Symbols.bundle(),raw=raw)
    fields=('RlChargeFired',)
    metadata=';'.join('C.ram.'+n+'='+str(W.address(b,n))for n in fields)
    hooks={}
    for event,symbol in (('RollCollect','RlCollect'),('RollWeapons','RlWeapons'),('RollInjury','RlInjury')):
        pc,at=W.address(b,symbol),W.location(b,symbol);hooks[event]=dict(pc=pc,tag=((at-16)//8192)|128,offset=at-16,hex=raw[at:at+12].hex())
    first=text.split('\n',1)[0]
    edit(first,first+"\nC.expected={0,1};C.itemKind=0;C.route='upgrades';C.form='roll-flower';"+metadata+';'+ ';'.join('C.hooks.'+event+'='+Stock.value(hook)for event,hook in hooks.items()))
    edit(Base.POLICY,POLICY)
    edit(' local complete=true',""" if checks['0'].collect then ROLL_FIRST_COLLECTED=true end
 if checks['0'].after then ROLL_FIRST_AFTER=true end
 if checks['1'].collect then ROLL_FLOWER_COLLECTED=true end
 local complete=true""")
    edit("assert(p.before.power==a.kind and s.growth~=0 and r('GuestPowerupTarget')==a.kind+1,'Actual source growth');return",
         "assert(q.family and s.hp==28 and s.energy==28 and s.food==1 and s.status==1 and s.growth==0,'Actual native Roll food collector restores resources');return")
    edit('if q.collect and not q.grant and kind<2 and s.growth==0 and s.status==kind+1',
         'if q.collect and not q.grant and kind<2 and s.growth==0 and s.status==1 and s.food==1')
    edit("else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end",
         "else assert(s.hp==28 and s.energy==28 and s.food==1 and s.status==1,'Actual full Roll resources persist after food')end")
    edit('local function settle()',RETURNS+'\nlocal function settle()')
    edit(' local p={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc)}',' local p={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc),entryPC=h.pc}')
    edit("  elseif p.name=='GameLoop' then afterMain()", "  elseif p.rollCollect or p.weapon or p.damage then rollFlowerReturn(p)\n  elseif p.name=='GameLoop' then afterMain()")
    edit(" if name=='HandlePowerUpCollision' then", """ if name=='RollCollect'then
  local i=cpu['cpu.x'];local kind=r('PowerUpType',i);local q=checks[tostring(kind)]
  if not(q and q.birth and q.birth.actor.slot==i and kind<2)then return end
  p.rollCollect={slot=i,kind=kind};p.before=state()
 elseif name=='RollWeapons'then p.weapon=state()
 elseif name=='RollInjury'then p.damage=state();p.victim=actor(r('ObjectOffset'))
 elseif name=='HandlePowerUpCollision' then""")
    restored=text
    for a,z in reversed(changes):assert restored.count(z)==1;restored=restored.replace(z,a,1)
    assert restored.encode()==old
    assert not any(t in text for t in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    Stock.LuaRuntime().compile(text);return text.encode()


def source(raw,limit):
    program=controller(raw);assert H(program)==LUA
    with patch.object(Engine.J,'cold',lambda image:Base.cold(image,'star')),patch.object(Engine.J,'PIN',PIN):return Engine.run(raw,limit,text=program.decode())


def native(raw):
    program=controller(raw);assert H(program)==LUA
    out=Stock.OUT;candidate,script=out/'candidate.nes',out/'controller.lua';before=script.read_bytes();guard=Stock.check(ROM)
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(out.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Stock.preserve_script(script,candidate,raw)as stage:stage(program);q=Stock.run(script,ROM,out/'capture',PIN,230)
        assert q['script_SHA256']==LUA and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and Stock.check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=3200);a=p.parse_args();assert 1000<=a.limit<=4200
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:q=native(raw)
    else:
        def deny(*a,**k):raise AssertionError('Roll Flower source attempted output/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.limit)
            else:
                program=controller(raw);assert H(program)==LUA;q=dict(passed=True,ROM_SHA256=PIN,controller_SHA256=H(program),route_executed=False,outputs=0)
    print('ROLL_FLOWER '+json.dumps(q,separators=(',',':')),flush=True);return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
