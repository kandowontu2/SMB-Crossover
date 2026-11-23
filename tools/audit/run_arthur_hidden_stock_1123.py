"""Exact restored Arthur Easy hidden 1-UP/Star, normal inputs and stdout only.

Root alone may --run after the per-route controller pins are source-qualified.
The existing Mushroom/Flower/stage sources are read-only inputs.
"""
import argparse
from functools import lru_cache
import inspect
import json
from pathlib import Path
import re
from unittest.mock import patch

import run_arthur_mushroom_1123 as A
import replay_arthur_restored_stage_1123 as Full

R,W,N,H,Stock,Engine,ROM=A.R,A.W,A.N,A.H,A.Stock,A.Engine,A.ROM
PIN='bcc26bb5f6d11bbd38e46d5a5025eb30d2bc146e1bd293a44ca104eec5f40a0e'
PINS={'life':'c5a4015c872ea65a4079bd60474184e84b38a303f9751694e2678843e8783299',
      'star':'a1c512a94f53d40a55ac8746087c2a9c5a12bc6a8a2d0603a5d1f29793c8cb64'}
KINDS={'life':3,'star':2}


POLICY=r'''
local jumpStart,jumpSecond,jumpReason,jumps=nil,true,'none',0
local combatStart,combatStops=nil,0
local L=C.ram
local function wx()return x()end
__TRAVEL__
local function policy()
 local s=state();local a=item();latest={player=s,item=a}
 assert(s.lives==2 or(C.kind==3 and lifeCredit and s.lives==3),'Living Arthur stock route')
 assert(s.high==1 and s.engine~=11 and s.ready==167 and r('SelectedCharacter')==32,'Active original Arthur')
 assert(updates<5000 and r('WorldNumber')==0 and r('LevelNumber')==0,'Bounded ordinary1-1 stock route')
 if grant then return{}end
 if phase=='travel'then
  if x()<C.goal-76 then return travel()end
  mark('align')
 end
 if phase=='align'then
  if s.mode~=0 or r('Player_State')~=0 then return steer(C.goal-64,2)end
  if s.y<160 then return{right=true}end
  if math.abs(x()-(C.goal-6))<=2 and r('Player_X_Speed')==0 and released()then
   attempts=attempts+1;assert(attempts<=2,'Bounded authored hidden-block attempts')
   jumpStep=steps;mark('head');return{a=true}
  end
  return steer(C.goal-6,2)
 end
 if phase=='head'then
  if steps%3==0 and #pursuit<24 and(not pursuit[#pursuit]or pursuit[#pursuit].player.steps~=steps)then
   pursuit[#pursuit+1]={phase='head',player=s,pad=r('ArHostPad'),nativeA=r('A_B_Buttons'),
    tile128=block(C.goal+8,128),tile144=block(C.goal+8,144),tile112=block(C.goal+8,112)}
  end
  if a then mark('collect')end
  if phase=='head'then
   local t=steps-jumpStep
   if t>60 and s.mode==0 then mark('align');return{}end
   return{a=t<4 or(t>=12 and t<18)}
  end
 end
 if phase=='collect'then
  assert(steps-at<420,'Bounded actual item interception')
  if collected then return{}end
  assert(a,'Real target remains until actual collection')
  if frame%9==0 and #pursuit<32 then pursuit[#pursuit+1]={player=s,item=a}end
  if C.kind==3 then
   if a.y<148 then return steer(C.goal+36,2)end
   return steer(math.min(C.goal+66,math.max(C.goal-16,a.x-3)),3)
  end
  if a.state&128==0 then return steer(C.goal+51,2)end
  if not jumpStep then jumpStep=steps end
  if s.mode==0 and released()and a.x>=x()-32 and a.x<=x()+24 then
   jumpStep=steps;return{right=x()<a.x,left=x()>a.x,a=true}
  end
  local t=steps-jumpStep
  return{right=x()<a.x,left=x()>a.x+8,a=s.mode~=0 and(t<4 or(t>=12 and t<18))}
 end
 return{}
end
'''


RETURNED=r'''
local function returned(p)
 local s=state()
 if p.name=='Movement'then
  moves=moves+1
  if collected and not grant then
   if C.kind==3 and lifeCredit and s.lives==3 and lifeCues>collected.life_cues then grant=s;mark('retain')
   elseif C.kind==2 and s.star>0 and starCues>collected.star_cues then grant=s;mark('retain')end
  end
  if grant and moves>=grant.moves+25 and s.mode==0 and r('Player_State')==0 then
   assert(s.flags&32==grant.flags&32 and s.weapon==grant.weapon,'Original Arthur armor/weapon persist')
   if C.kind==3 then assert(s.lives==3 and lifeCredit and lifeCues>collected.life_cues,'Earned life and native cue persist')
   else assert(s.lives==2 and s.star>0 and starCues>collected.star_cues and score()>=collected.before.score+1000,'Native Star, cue and1000points persist')end
   after=state();assert(#pending==0 and not lifePending,'Native stock and original movement workers unwound')
   finish(true,'Authored Arthur stock, native credit and25further movement returns')
  end
 elseif p.name=='NativePickup'then
  assert(not collected and p.actor.kind==C.kind and p.actor.state&128~=0 and #heads>0 and mature,'Natural mature target through actual native collector')
  assert(r('Enemy_Flag',p.actor.slot)==0,'Native target actor erased')
  collected={before=p.before,after=s,actor=p.actor,life_cues=p.life_cues,star_cues=p.star_cues};mark('credit')
 elseif p.name=='TakeHit'then
  assert(#hits<8,'Bounded genuine injury log');hits[#hits+1]={before=p.before,after=s,target=p.target}
 end
end
'''


def once(s,a,b):
    assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)


@lru_cache(maxsize=2)
def controller(raw,route):
    assert H(raw)==PIN and route in KINDS
    old=A.controller(raw).decode();assert H(old.encode())==A.LUA
    text=old;b=dict(W.Symbols.bundle(),raw=raw)
    extra='StarInvincibleTimer AreaMusicQueue Square2SoundQueue Block_Buffer_1 Block_Buffer_2 MTileAttribute ArHostPad'.split()
    ram={n:W.address(b,n)for n in extra};hooks={}
    def hook(name,symbol,delta=0):
        pc,at=W.address(b,symbol)+delta,W.location(b,symbol)+delta
        hooks[name]=dict(name=symbol,pc=pc,tag=((at-16)//8192)|128,offset=at-16,bytes=list(raw[at:at+12]))
    hook('NativePickup','HandlePowerUpCollision')
    at=W.location(b,'DecNumTimer');needle=b'\xee'+W.address(b,'NumberofLives').to_bytes(2,'little')
    assert raw[at:at+48].count(needle)==1;delta=raw[at:at+48].index(needle)
    hook('LifeCredit','DecNumTimer',delta);hook('LifeAfter','DecNumTimer',delta+3)
    additions='\n'.join('C.ram['+Stock.value(n)+']='+str(v)for n,v in sorted(ram.items()))
    additions+='\n'+ '\n'.join('C.hooks['+Stock.value(n)+']='+Stock.value(v)for n,v in sorted(hooks.items()))
    additions+='\nC.kind='+str(KINDS[route])+'\nC.goal='+str(1024 if route=='life'else 1616)+'\nC.route='+Stock.value(route)+'\n'
    first=text.split('\n',1)[0];text=once(text,first,first+'\n'+additions)
    text=once(text,"local phase,at='wound',0","local phase,at='travel',0")
    text=once(text,'local damage,pickup,after,latest,initial,mature',
        'local damage,pickup,after,latest,initial,mature\nlocal collected,grant,lifePending,lifeCredit\nlocal lifeCues,starCues=0,0\nlocal hits,pursuit={},{}')
    text=once(text,"ready=r('ArHostReady'),mode=", "star=r('StarInvincibleTimer'),ready=r('ArHostReady'),mode=")
    text=once(text,"collections=collections,mature=mature,latest=latest",'collections=collections,mature=mature,collected=collected,grant=grant,life_credit=lifeCredit,life_cues=lifeCues,star_cues=starCues,hits=hits,pursuit=pursuit,route=C.route,latest=latest')
    text=once(text,"if q.flag>0 and q.id==46 then return q end",'if q.flag>0 and q.id==46 and q.kind==C.kind then return q end')
    full=Full.BASE.read_bytes();assert H(full)==Full.BASE_SHA
    travel=full.decode();travel=travel[travel.index('local function block('):travel.index('emu.addMemoryCallback')]
    travel=re.sub(r'\bage\b','frame',travel)
    start,stop=text.index('local function policy()'),text.index('local function returned(p)')
    text=text[:start]+POLICY.replace('__TRAVEL__',travel)+'\n'+text[stop:]
    start,stop=text.index('local function returned(p)'),text.index('local function settle()')
    text=text[:start]+RETURNED+'\n'+text[stop:]
    text=once(text,"if name=='GameLoop'then updates=updates+1;return end",'''if name=='GameLoop'then updates=updates+1;return end
 if name=='LifeCredit'then
  assert(C.kind==3 and collected and r('NumberofLives')==2,'Actual delayed earned life credit')
  lifePending=state();return
 elseif name=='LifeAfter'then
  assert(lifePending and r('NumberofLives')==3,'Native life INC executed')
  lifeCredit={before=lifePending,after=state()};lifePending=nil;return
 end''')
    text=once(text,"elseif name=='SourcePickup'then p.value=cpu['cpu.a']",'''elseif name=='SourcePickup'then return
 elseif name=='NativePickup'then
  p.actor=actor(r('ObjectOffset'))
  if p.actor.kind~=C.kind or p.actor.id~=46 or p.actor.flag==0 then return end
  p.life_cues=lifeCues;p.star_cues=starCues''')
    text=once(text,'if x()<400 and #heads<8 then', 'if math.abs(x()-C.goal)<32 and #heads<8 then')
    text=once(text,"assert(a.kind==0 and damage and #heads>0,'Authored first naked Mushroom birth')", "assert(a.kind==C.kind and #heads>0,'Authored Arthur target birth')")
    marker='emu.addEventCallback(function()emu.setInput(input,0)end,emu.eventType.inputPolled)'
    cues='''emu.addMemoryCallback(guarded(function(_,v)
 if initial and v==64 then lifeCues=lifeCues+1 end
end),emu.callbackType.write,C.ram.Square2SoundQueue)
emu.addMemoryCallback(guarded(function(_,v)
 if initial and v==64 then starCues=starCues+1 end
end),emu.callbackType.write,C.ram.AreaMusicQueue)
'''
    text=once(text,marker,cues+marker)
    text=once(text,"assert(frame<6500,'Physical Arthur pickup bound')", "assert(frame<9500,'Physical Arthur stock bound')")
    if route=='life':
        # The higher hidden block needs Arthur's original second jump near
        # the first apex. Twelve donor steps waits until almost landing.
        text=once(text,'return{a=t<4 or(t>=12 and t<18)}','return{a=t<2 or(t>=5 and t<9)}')
    assert not any(s in text for s in('emu.write','emu.setState','saveState','loadState','io.open','dofile','takeScreenshot'))
    Stock.LuaRuntime().compile(text);return text.encode()


def source(raw,route,limit):
    assert H(controller(raw,route))==PINS[route]
    text=inspect.getsource(Engine.run)
    before='for fn in tuple(callbacks[0].get(self.pc,())):fn()'
    text=once(text,before,'for fn in tuple(callbacks[0].get(self.pc,())):fn(self.pc)')
    space=dict(Engine.__dict__);exec(compile(text,__file__,'exec'),space)
    with patch.object(Engine.J,'cold',A.cold),patch.object(Engine.J,'PIN',PIN):
        q=space['run'](raw,limit,text=controller(raw,route).decode())
    q['source_exec_callback_argument']='Actual PC, matching Mesen; unrelated pending-return checks have no effects'
    return q


def native(raw,route):
    program=controller(raw,route);assert PINS[route]and H(program)==PINS[route]
    out=Stock.OUT;candidate,script=out/'candidate.nes',out/'controller.lua';before=script.read_bytes();guard=Stock.check(ROM)
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(out.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Stock.preserve_script(script,candidate,raw)as stage:
            stage(program);q=Stock.run(script,ROM,out/'capture',PIN,210)
        assert q['script_SHA256']==PINS[route]and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and Stock.check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--route',choices=KINDS,default='life')
    g=p.add_mutually_exclusive_group();g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=4500);args=p.parse_args();assert 1000<=args.limit<=5200
    raw=ROM.read_bytes();assert H(raw)==PIN
    if args.run:q=native(raw,args.route)
    else:
        def deny(*a,**k):raise AssertionError('Arthur hidden stock attempted outputs/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if args.source:q=source(raw,args.route,args.limit)
            else:
                digest=H(controller(raw,args.route));assert digest==PINS[args.route]
                q=dict(passed=True,controller_SHA256=digest,outputs=0)
    print('ARTHUR_HIDDEN_STOCK '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
