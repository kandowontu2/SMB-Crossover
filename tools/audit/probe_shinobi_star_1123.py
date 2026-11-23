"""Separate ordinary Easy Shinobi Star replay after the frozen Flower route.

No captures, ROM writes or actor seeds. Root alone may run Mesen after the
controller is frozen. Supports only exact c691 and its exact Mega successor.
"""
import argparse
from functools import lru_cache
import inspect
import json
from pathlib import Path
from unittest.mock import patch

import probe_shinobi_flower_1123 as Flower
import install_mega_giant_item_semantics_1123 as Mega

H,W,N,Stock,ROM,Engine=Flower.H,Flower.W,Flower.N,Flower.Stock,Flower.ROM,Flower.Engine
SOURCE='85a9517ad40e78cd12898bede967d38a8f8de2bcfecc5cbb8ccb2b098505b113'
PINS={Flower.PIN:'74266a34fd017874e54899ad6a7f75f49b23fc97e8ecb87827becd2725b72441',
      Mega.CANDIDATE:'b1ed9b15249e1343e12254028fc6b71d6dc36e9e4a47ebeced70468066293547'}

DRIVE=r'''
local function starPhase(p)
 if S.phase==p then return end
 S.phase=p;S.at=steps;assert(#S.events<24,'Bounded ordinary Shinobi Star phases')
 S.events[#S.events+1]={phase=p,player=state()}
end
local function policy()
 if not S.ready then return flowerPolicy()end
 local s=state();local a=item();latest={player=s,item=a,star=S.phase}
 assert(s.ready==167 and r('SelectedCharacter')==36 and s.lives==2 and s.engine==8 and s.high==1,
  'Living authenticated Shinobi on the normal Star route')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0,'Ordinary1-1 Star')
 assert(updates<4400 and s.power==1,'Bounded original Star route retaining Flower weapon')
 if s.x>(S.max_x or 0)then S.max_x=s.x;S.progress=steps end
 if S.consumed then
  assert(r('StarInvincibleTimer')>0 and s.power==S.pickup.before.power,'Genuine Star and donor weapon persist')
  if steps-S.consumed.steps>=25 and moves-S.consumed.moves>=25 and r('Player_State')==0 then
   assert(score()>=S.pickup.before.score+1000 and #births==3,'Actual Star credit persists')
   S.retained=state();S.retained.star=r('StarInvincibleTimer')
   finish(true,'Natural Shinobi Star started native invincibility/music and retained25 original moves');return{}
  end
  return{}
 end
 if S.birth then
  if S.phase~='star-collect'then starPhase('star-collect')end
  assert(a and a.kind==2,'Genuine Star actor remains before collection')
  assert(steps-S.at<420,'Bounded actual Star acquisition')
  S.latest={player=s,actor=a}
  return steer(math.max(pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc')+2,a.x-2),2)
 end
 if S.phase=='travel'then
  assert(steps-S.progress<500,'Source travel toward Star keeps progressing')
  if s.x>=1568 and r('Player_State')==0 then starPhase('star-align');F.jumping=false
  else return travel()end
 end
 if S.phase=='star-align'then
  if r('Player_State')~=0 or s.source_state==16 or s.source_state==5 then return{}end
  if math.abs(s.x-1609)<=2 and r('Player_X_Speed')==0 and released()then
   S.attempts=(S.attempts or 0)+1;assert(S.attempts<=3,'Bounded actual authored Star brick attempts')
   S.jump=steps;starPhase('star-head');return{a=true}
  end
  return steer(1609,2)
 end
 if S.phase=='star-head'then
  if steps-S.jump>100 and r('Player_State')==0 then starPhase('star-align');return{}end
  return{a=steps-S.jump<24}
 end
 return{}
end
'''

OBSERVE=r'''
local function observe()
 if not S.ready then return observeUpgrades()end
 local a=item();if not a then return end
 assert(a.kind==2 and a.id==46 and a.flag>0,'Only the authored Star on this continuation')
 if not S.birth then
  assert(a.x==1616 and #births==2 and #heads>=3,'Natural Star from its original1616brick')
  local h=heads[#heads]
  assert(h.tile==0x57 and h.pointer==0x305 and h.row==0x70,'Exact native Star brick transaction')
  S.birth={actor=a,player=state()};births[#births+1]=S.birth
 end
 if a.state&128~=0 and not S.mature then S.mature={actor=a,player=state(),at='endFrame'}end
end
'''


def baseline(raw):
    pin=H(raw);assert pin in PINS
    base=raw if pin==Flower.PIN else Mega.recover_parent(raw)
    assert H(base)==Flower.PIN
    for page in set(Flower.P.Head.PAGES+(503,504,505,516,517)):
        at=1048592+page*1024;assert raw[at:at+1024]==base[at:at+1024]
    at=Flower.P.Head.COOKIE;assert raw[at:at+16]==base[at:at+16]
    return base


@lru_cache(maxsize=2)
def controller(raw):
    assert H(Path(Flower.__file__).read_bytes())==SOURCE,'Frozen native-passed Flower source'
    base=baseline(raw);text=Flower.controller(base).decode();once=Flower.Prior.once
    assert text.count(Flower.PIN)==1;text=text.replace(Flower.PIN,H(raw))
    text=once(text,"local F={phase='first'",
        "local S={phase='travel',events={}}\nlocal F={phase='first'")
    text=once(text,'local function policy()','local function flowerPolicy()')
    text=once(text,"w.after=state();finish(true,'Natural Shinobi Flower raised weapon0 to1, retained25 moves and moved its genuine upgraded shot');return{}",
        "w.after=state();S.ready=true;S.started=steps;S.progress=steps;return{}")
    at=text.index('local function returned(p)');text=text[:at]+DRIVE+'\n'+text[at:]
    text=once(text,'local function observe()','local function observeUpgrades()')
    at=text.index('local function pulse(key)');text=text[:at]+OBSERVE+'\n'+text[at:]
    text=text.replace("if x()<1400 and #heads<12 then","if x()<1900 and #heads<16 then")
    text=once(text,'headmotion=headmotion,flower=F,head_blocked=head_blocked',
        'headmotion=headmotion,flower=F,star=S,head_blocked=head_blocked')
    text=once(text,"elseif p.name=='SourcePickup'then",'''elseif p.name=='SourcePickup'and p.kind==2 then
  assert(S.ready and S.birth and S.mature and S.admission and S.admission.carry==1
   and S.admission.overlap and S.admission.actor.slot==p.slot,'Actual mature Star and native collision')
  assert(p.actor.flag>0 and p.actor.id==46 and p.actor.state&128~=0,'Genuine live Star collector actor')
  assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64,'Native Star timer35 and music64')
  assert(s.power==p.before.power and s.health==p.before.health,'Star preserves original weapon and health')
  S.pickup={before=p.before,after=s,actor=p.actor,timer=r('StarInvincibleTimer'),music=r('AreaMusicQueue')};pickup=S.pickup
 elseif p.name=='NativePickup'and p.kind==2 then
  assert(S.pickup and r('Enemy_Flag',p.slot)==0 and r('Square2SoundQueue')==32
   and r('FloateyNum_Control',p.slot)==6,'Actual Star erase,cue and1000-point popup')
  S.consumed=s;starPhase('star-retain')
 elseif p.name=='SourcePickup'then''')
    text=once(text,"if p.actor.kind==1 then\n    F.maturity",'''if p.actor.kind==2 then
    S.admission={carry=c,actor=p.actor,player=p.before,overlap=p.overlap,player_box=p.player_box,item_box=p.item_box}
    S.mature=S.mature or{actor=p.actor,player=p.before,at='actual-HuMature-return'}
   end
   if p.actor.kind==1 then
    F.maturity''')
    extra='\n'.join(f'C.ram.{n}={W.address(W.Symbols.bundle(),n)}'for n in('StarInvincibleTimer','AreaMusicQueue'))
    text=once(text,'C.hooks.QueryReturn=nil','C.hooks.QueryReturn=nil\n'+extra)
    text=text.replace("frame<16000,'Physical Shinobi Flower bound'","frame<20000,'Physical Shinobi Star bound'")
    assert not any(word in text for word in('emu.write','emu.setState','io.open','dofile','takeScreenshot','saveState','loadState'))
    Stock.LuaRuntime().compile(text);program=text.encode()
    assert PINS[H(raw)] is None or H(program)==PINS[H(raw)],'Frozen Star controller'
    return program


def cold(raw):
    baseline(raw)
    with patch.object(Flower,'PIN',H(raw)):
        return Flower.cold(raw)


def source(raw,limit):
    body=inspect.getsource(Engine.run)
    body=Flower.Prior.once(body,'for fn in tuple(callbacks[0].get(self.pc,())):fn()',
        'for fn in tuple(callbacks[0].get(self.pc,())):fn(self.pc)')
    scope=dict(Engine.__dict__);exec(compile(body,__file__,'exec'),scope)
    with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',H(raw)):
        return scope['run'](raw,limit,text=controller(raw).decode())


def native(raw):
    pin=H(raw);program=controller(raw);assert PINS[pin]and H(program)==PINS[pin],'Qualified frozen Star script'
    out=Stock.OUT;candidate,script=out/'candidate.nes',out/'controller.lua'
    guard=Stock.check(ROM);previous=script.read_bytes()
    assert guard['ROM_sha256']==pin and not guard['matching_patch_files']
    assert set(out.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Stock.preserve_script(script,candidate,raw)as stage:
            stage(program);q=Stock.run(script,ROM,out/'capture',pin,240)
        assert q['script_SHA256']==PINS[pin] and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==previous and candidate.read_bytes()==raw and ROM.read_bytes()==raw and Stock.check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group()
    g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=3600);a=p.parse_args();assert 1800<=a.limit<=4600
    raw=ROM.read_bytes();baseline(raw)
    if a.run:q=native(raw)
    else:
        def deny(*args,**kwargs):raise AssertionError('Source Star replay attempted output/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            q=source(raw,a.limit)if a.source else dict(passed=True,controller_SHA256=H(controller(raw)),outputs=0)
    print('SHINOBI_STAR '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
