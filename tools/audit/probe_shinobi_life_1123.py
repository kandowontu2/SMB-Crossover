"""Separate ordinary-input Shinobi hidden 1-UP probe; stdout and memory only.

Retains the native first Mushroom and original four pipe inputs. Observe the
real rising upper probes before considering any hidden-material change.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import probe_shinobi_star_1123 as Star

Flower=Star.Flower
H,W,Stock,ROM=Star.H,Star.W,Star.Stock,Star.ROM
PIN=Star.Mega.CANDIDATE
FLOWER_SOURCE=Star.SOURCE
STAR_SOURCE='4bdf1957a2351f8175fafbdc07260cc283ae12f925a17d1469bfd64cfca178f6'
LUA='8d1e713247f4d6576ef036787399d323eb15a4bfeca4aaad813b2861fd42fa0e'

POLICY=r'''
local function lifePhase(p)
 if L.phase==p then return end
 L.phase=p;L.at=steps;assert(#L.events<20,'Bounded hidden life phases')
 L.events[#L.events+1]={phase=p,player=state()}
end
local function policy()
 if not F.first_ready then return firstPolicy()end
 local s=state();local a=item();latest={player=s,item=a,life=L.phase}
 assert(s.ready==167 and r('SelectedCharacter')==36 and s.high==1 and s.engine==8,
  'Living authenticated original Shinobi')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and s.power==0,'Ordinary1-1 with first food only')
 assert(updates<2600,'Bounded natural hidden1-UP route')
 assert(s.lives==(L.credit and 3 or 2),'Only the genuine native popup changes lives')
 if L.consumed then
  assert(s.health==L.pickup.after.health and s.power==L.pickup.after.power,'Life preserves donor inventory')
  assert(steps-L.consumed.steps<120,'Bounded delayed native life credit')
  if L.credit and L.cues>0 then L.grant=L.grant or s end
  if L.grant and steps-L.grant.steps>=25 and moves-L.grant.moves>=25 and r('Player_State')==0 then
   L.retained=state();finish(true,'Natural hidden1-UP earned life3 and retained25 original moves');return{}
  end
  return{}
 end
 if L.birth then
  lifePhase('collect');assert(a and a.kind==3,'Authored native1-UP remains')
  assert(steps-L.at<440,'Bounded moving native life acquisition')
  L.latest={player=s,actor=a};return steer(a.x-3,2)
 end
 if L.phase=='travel'then
  if s.x>=984 and r('Player_State')==0 then
   lifePhase('align');F.jumping=false
   L.cell={tile=r('Block_Buffer_1',((1024//256)%2)*208+((128-32)//16)*16),world_x=1024,world_y=128}
   assert(L.cell.tile==0x60,'Genuine authored hidden1-UP metatile')
  else return travel()end
 end
 if L.phase=='align'then
  if r('Player_State')~=0 or s.source_state==16 or s.source_state==5 then return{}end
  if math.abs(s.x-1017)<=2 and r('Player_X_Speed')==0 and released()then
   if L.attempts==2 then
    L.blocked=state();finish(false,'Two original jumps completed without a hidden1-UP birth');return{}
   end
   L.attempts=L.attempts+1;L.jump=steps;lifePhase('head');return{a=true}
  end
  return steer(1017,2)
 end
 if L.phase=='head'then
  L.min_y=math.min(L.min_y,s.y)
  if steps-L.jump>100 and r('Player_State')==0 then lifePhase('align');return{}end
  return{a=steps-L.jump<24}
 end
 return{}
end
'''

OBSERVE=r'''
local seenBirth={}
local function observe()
 local a=item();if not a then return end
 local key=a.slot..':'..a.kind
 if not seenBirth[key]then
  if a.kind==0 then assert(not mushroom and #heads==1 and a.x==336,'First authored food')
  else
   assert(a.kind==3 and F.first_ready and a.x==1024,'Authored hidden1-UP birth')
   local h=heads[#heads];L.transaction=h
   assert(h and h.tile==0x60 and h.pointer==0x300 and h.row==0x60,
    'Exact hidden rising native transaction')
   L.birth={actor=a,player=state()}
  end
  seenBirth[key]=true;births[#births+1]={actor=a,player=state()}
 end
 if a.state&128~=0 then
  if a.kind==0 and not mature then mature={actor=a,player=state()}
  elseif a.kind==3 and not L.mature then L.mature={actor=a,player=state()}end
 end
end
'''


@lru_cache(maxsize=1)
def controller(raw):
    assert H(raw)==PIN
    assert H(Path(Flower.__file__).read_bytes())==FLOWER_SOURCE
    assert H(Path(Star.__file__).read_bytes())==STAR_SOURCE
    base=Star.baseline(raw);text=Flower.controller(base).decode();once=Flower.Prior.once
    text=once(text,Flower.PIN,PIN)
    text=once(text,"local F={phase='first'",
              "local L={phase='travel',events={},probes={},attempts=0,min_y=255,cues=0}\nlocal F={phase='first'")
    start,stop=text.index('local function policy()'),text.index('local function returned(p)')
    text=text[:start]+POLICY+'\n'+text[stop:]
    start,stop=text.index('local seenBirth={}'),text.index('local function pulse(key)')
    text=text[:start]+OBSERVE+'\n'+text[stop:]
    text=once(text,"if p.name=='Movement'then moves=moves+1",'''if p.name=='UpperProbe'then
  if L.phase=='head'and #L.probes<48 then
   L.probes[#L.probes+1]={before=p.before,after=s,query=p.query,result=cpu['cpu.a'],
    tile=r('ShTile'),attribute=r('MTileAttribute',r('ShTile')),column=r('R6'),row=r('ShBlockRow'),pending=r('ShPendingTile')}
  end
 elseif p.name=='Movement'then moves=moves+1''')
    text=once(text,"elseif p.name=='SourcePickup'then",'''elseif p.name=='SourcePickup'and p.kind==3 then
  assert(L.birth and L.mature and p.actor.flag>0 and p.actor.state&128~=0,'Genuine mature native life')
  assert(s.lives==p.before.lives and s.lives==2 and r('FloateyNum_Control',p.slot)==11,
   'Native collector queues1-UP popup before delayed life credit')
  assert(s.power==p.before.power and s.health==p.before.health,'Life preserves source health/weapon')
  L.pickup={before=p.before,after=s,actor=p.actor};pickup=L.pickup
 elseif p.name=='NativePickup'and p.kind==3 then
  assert(L.pickup and r('Enemy_Flag',p.slot)==0 and r('FloateyNum_Control',p.slot)==11,
   'Native life erase and1-UP popup')
  L.consumed=s;lifePhase('retain')
 elseif p.name=='SourcePickup'then''')
    text=once(text,"if name=='SourcePickup'or name=='NativePickup'then",'''if name=='UpperProbe'then
  p.query={canvas_x=r('R0')+256*r('R1'),world_x=r('R0')+256*r('R1')+pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc'),
   y=r('R2')+256*r('R3'),motion=r('ShDir')}
 end
 if name=='SourcePickup'or name=='NativePickup'then''')
    text=once(text,"if name=='GameLoop'then updates=updates+1;return end",'''if name=='GameLoop'then updates=updates+1;return end
 if name=='LifeCredit'then
  assert(L.consumed and r('NumberofLives')==2,'Actual delayed earned life credit')
  L.credit_before=state();return
 elseif name=='LifeAfter'then
  assert(L.credit_before and r('NumberofLives')==3,'Actual native life INC executed')
  L.credit={before=L.credit_before,after=state()};return
 end''')
    code=Flower.P.Head.carrier(raw)
    assert code[0x1301]==code[0x1312]==0x20
    pc=code[0x1302]+256*code[0x1303]
    assert pc==code[0x1313]+256*code[0x1314] and 0xbb00<pc<0xbbf8
    hook=dict(name='ShUpperProbe',pc=pc,tag=3,offset=3*8192+(pc&8191),bytes=list(code[pc-0xa000:pc-0xa000+12]))
    bundle=W.Symbols.bundle()
    extra='C.hooks.UpperProbe='+Stock.value(hook)+'\nC.ram.MTileAttribute='+str(W.address(bundle,'MTileAttribute'))
    extra+='\nC.work.ShBlockRow=4\nC.work.ShPendingTile=2065'
    pc,at=W.address(bundle,'DecNumTimer'),W.location(bundle,'DecNumTimer')
    needle=b'\xee'+W.address(bundle,'NumberofLives').to_bytes(2,'little')
    assert raw[at:at+48].count(needle)==1
    delta=raw[at:at+48].index(needle)
    for name,d in (('LifeCredit',delta),('LifeAfter',delta+3)):
        h=dict(name='DecNumTimer+'+str(d),pc=pc+d,tag=((at-16)//8192)|128,
               offset=at-16+d,bytes=list(raw[at+d:at+d+12]))
        extra+='\nC.hooks.'+name+'='+Stock.value(h)
    text=once(text,'C.hooks.QueryReturn=nil','C.hooks.QueryReturn=nil\n'+extra)
    marker='emu.addEventCallback(function()emu.setInput(input,0)end,emu.eventType.inputPolled)'
    text=once(text,marker,'''emu.addMemoryCallback(guarded(function(_,v)
 if initial and v==64 then L.cues=L.cues+1 end
end),emu.callbackType.write,C.ram.Square2SoundQueue)
'''+marker)
    text=once(text,'headmotion=headmotion,flower=F,head_blocked=head_blocked',
        'headmotion=headmotion,flower=F,life=L,head_blocked=head_blocked')
    assert not any(word in text for word in('emu.write','emu.setState','io.open','dofile','takeScreenshot','saveState','loadState'))
    Stock.LuaRuntime().compile(text);program=text.encode()
    assert LUA is None or H(program)==LUA,'Frozen hidden1-UP probe'
    return program


def source(raw,limit):
    with patch.object(Star,'controller',controller):return Star.source(raw,limit)


def native(raw):
    assert LUA and H(controller(raw))==LUA,'Source-qualified frozen1-UP probe required'
    with patch.object(Star,'controller',controller),patch.object(Star,'PINS',{PIN:LUA}):return Star.native(raw)


def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group()
    g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=2500);a=p.parse_args();assert 1300<=a.limit<=3000
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:q=native(raw)
    else:
        def deny(*args,**kwargs):raise AssertionError('Source life probe attempted output/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            q=source(raw,a.limit)if a.source else dict(passed=True,controller_SHA256=H(controller(raw)),outputs=0)
    print('SHINOBI_LIFE '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
