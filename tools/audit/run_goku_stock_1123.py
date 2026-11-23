"""Exactbcc26 Goku Easy hidden1-UP/Star by ordinary menu and controller.

Additive to the frozen native first-Mushroom and Flower/wave tests. Source
declares linked real menu/Select/Start entry; no gameplay state is seeded.
Root alone owns --run and the existing shared native slot.
"""
import argparse
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import run_goku_flower_1123 as Flower

First,H,W,N,Stock,ROM,Engine=Flower.First,Flower.H,Flower.W,Flower.N,Flower.Stock,Flower.ROM,Flower.Engine
PIN=Flower.PIN
OWNED=Stock.R/'build/goku-stock-source-1123'
FLOWER_SHA='bde40829b2a0f6883eb263278a30cd2ffd6514bcf46ee50444e0506393dfa9f9'
PINS={'life':None,'star':'de358dde10f1b67f9f8b88d00052f86ba52f79f20218d43365870906900cf630'}
KINDS={'life':3,'star':2}
SOURCE_PROOFS={'star':{
    'receipt_SHA256':'0a5133fae6d739f08635ca4b999efa95e76af5023088a352c2234c56d68c9ece',
    'receipt_inner_SHA256':'f1fe998377963893f2cb55f6603368c5e2f7d3cfa93615ada4e70069a1838b83',
    'linked_source_passes':1792,'Main_returns':1792,'Dp_returns':1792,
    'authored_birth':[1616,136,2],'collector_player':[1630,126],
    'native_contact_state':6,'positive_overlap':[1,13],
    'Star_before_after':[0,35],'music_before_after':[0,64],
    'score_before_after':[1740,2740],'post_credit_returns':25,
    'terminal':[1630,132,79,2,33],
    'scope':'Linked real menu/Select/Start; native Star accepts kind2 during emergence; actual CPU and ordinary pads, no native cadence claim',
}}

DRIVE=r'''
local function drive()
 if not(food.pickups[1]and food.pickups[1].resumed)then firstDrive();return end
 if not menuDone or not active()then buttons={};return end;identity();observe()
 local c=context();c.stageFrame=guestReturns;c.lastA=r('DpPrevious')&128~=0
 if c.x>(F.farthest or 0)then F.farthest=c.x;F.progress=guestReturns end
 assert(not F.progress or guestReturns-F.progress<650,'Bounded Goku stock route progress')
 if pendingCollect or pendingScore or food.pickups[2]then buttons={};return end
 local a=target()
 if a and a.kind==C.itemKind then
  F.actor=F.actor or a;F.latest={state=state(),actor=a}
  if F.phase~='catch'and F.phase~='wait-item'then fp(c,'wait-item')end
  if a.state<128 then buttons=steer(c,C.goal+36,2);return end
  if C.itemKind==3 then
   local x=math.max(c.camera+2,math.min(1100,a.x-8))
   buttons=steer(c,x,2)
   if ready(c)and c.y-a.y>12 and math.abs(c.x-a.x)<28 then
    F.jump=guestReturns;F.catch_request=state();fp(c,'catch');buttons.a=true
   elseif not c.grounded and F.jump then buttons.a=guestReturns-F.jump<32 end
   return
  end
  -- Stay ahead of the bouncing native Star and meet its descending arc.
  local x=math.max(c.camera+2,a.x-6)
  buttons=steer(c,x,2)
  if ready(c)and c.y-a.y>12 and math.abs(c.x-a.x)<32 then
   F.jump=guestReturns;F.catch_request=state();fp(c,'catch');buttons.a=true
  elseif not c.grounded and F.jump then buttons.a=guestReturns-F.jump<32 end
  return
 end
 if F.actor then F.missing=F.missing or state();buttons={};return end
 if F.phase=='travel'then
  if c.x<C.goal-76 then
   local lift=fourthLift(c);if lift then buttons=lift;return end
   if C.itemKind==2 and c.x>=1320 and c.x<1440 then
    F.gap=F.gap or{phase='approach',started=state()};local g=F.gap
    if g.phase=='approach'and c.x>=1360 and ready(c)then g.phase='press';g.request=state();buttons={right=true,a=true};return end
    if g.phase=='press'then
     if r('DpAction')==2 or r('DpAction')==3 and r('DpJumping')~=0 then g.phase='moving';g.accepted=state()
     elseif c.lastA then g.phase='approach';buttons={};return end
    end
    if g.phase=='moving'then
     if c.x>=1424 and ready(c)then g.landing=g.landing or state()end
     buttons={right=true,a=true};return
    end
    buttons={right=true};return
   end
   buttons=travel(c)
   local retry,failed=secondPipeRetry(c);assert(not failed,'Retained released second-pipe retry bound')
   if retry then buttons=retry end
   -- Do not reveal the other open block while approaching this test's item.
   if c.x>=950 and c.x<1080 or c.x>=1172 and c.x<1300 then buttons={right=true}end
   return
  end
  fp(c,'align')
 end
 if F.phase=='head'then
  assert(guestReturns-F.at<140,'Actual authored stock head bound')
  if ready(c)and guestReturns-F.at>5 then fp(c,'align');buttons={};return end
  buttons={a=guestReturns-F.at<32};return
 end
 if not ready(c)or c.y~=176 then buttons={};return end
 if math.abs(c.x-(C.goal-6))>1 or c.vx~=0 then buttons=steer(c,C.goal-6,1);return end
 F.attempts=(F.attempts or 0)+1;assert(F.attempts<=5,'Bounded actual hidden1-UP/Star head requests')
 F.head_request=state();fp(c,'head');buttons={a=true}
end
'''

ENDPOINT=r'''
local function endpoint()
 if pendingMain or pendingGuest then return end
 local q=food.pickups[#food.pickups];if not q or not q.credit or q.resumed then return end
 local n=guestReturns-q.credit.guest;q.resume_count=n;assert(n<=25,'Exactly25 returned Goku movements')
 if n~=25 then return end
 identity();assert(q.birth and(q.mature or q.native_contact_ready)and q.erase and q.setup and q.collected and q.score_credit,'Complete authored native-admitted item lifecycle')
 assert(r('DpHP')>0 and r('DpPole')==1 and r('DpPower')==1 and r('DpWaves')==0 and r('PlayerStatus')==1 and r('GuestPowerupActive')==0,'Natural Pole/tier and original owner survive stock reward')
 q.resumed={state=state(),pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']}
 if q.actor.kind==0 then food.phase='stock-travel';return end
 assert(q.actor.kind==C.itemKind and guestEntries==guestReturns and mainEntries==mainReturns,'Actual stock and balanced complete Main/owner returns')
 assert(not pendingCollect and not pendingScore,'Native stock/credit transaction returned')
 for _,list in pairs(dynamic)do assert(#list==0,'Every observed mapped caller returned')end
 if C.itemKind==3 then
  assert(q.life_writer and r('NumberofLives')==3 and q.credit.state.lives==3 and q.credit.cue==64 and q.score_credit.after==q.score_credit.before,'Real delayed extra life and cue; no invented score')
 else assert(r('StarInvincibleTimer')>0 and q.after.star==35 and q.after.music==64 and q.score_credit.after==q.score_credit.before+1000,'Real Star timer/music/score survive25 movements')end
 finish(true,'Natural Goku Mushroom then '..C.route..', actual native effect and25 completed original workers')
end
'''

COLLECT=r'''
hook('HandlePowerUpCollision',function()
 local i=emu.getState()['cpu.x'];local a=actor(i)
 if a.id~=46 or a.flag~=1 or a.kind==0 and a.state<128 then return end
 assert(a.kind==0 or a.kind==C.itemKind,'Only first Mushroom and selected authored stock are collected')
 observe();local n=#food.pickups+1;assert(n<=2 and food.births[n]and(food.births[n].mature or a.kind>=2),'Actual authored native-admitted stock before collection')
 assert(not pendingCollect,'One physical Goku collector')
 local pb,ib=box('BoundingBox_UL_Corner'),box('EnemyBoundingBoxCoord',i)
 local width=math.min(pb[3],ib[3])-math.max(pb[1],ib[1])+1;local height=math.min(pb[4],ib[4])-math.max(pb[2],ib[2])+1
 assert(width>0 and height>0,'Native inclusive positive physical stock overlap')
 local q={before=state(),actor=a,birth=food.births[n],mature=food.births[n].mature,native_contact_ready=a.kind>=2 and{state=a.state,kind=a.kind}or nil,player_box=pb,item_box=ib,overlap={width,height},pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']}
 food.pickups[n]=q;pendingCollect=q
 returning(function(t)
  q.after=state();q.return_pc=t.pc;q.return_sp=t.sp
  assert(q.erase and q.setup and r('Enemy_Flag',i)==0 and r('Square2SoundQueue')==32,'Actual erase, initial popup6 and grab cue32')
  if a.kind==0 then
   assert(q.source_reward and q.after.HP==q.source_reward.after.HP and q.after.pole==1 and q.after.tier==1,'Authentic source food/Pole reward returned')
  else
   assert(q.after.HP==q.before.HP and q.after.pole==q.before.pole and q.after.waves==q.before.waves and q.after.tier==q.before.tier and q.after.hunger==q.before.hunger,'Stock item preserves original Goku health/equipment/hunger')
   if a.kind==3 then assert(r('FloateyNum_Control',i)==11 and q.after.lives==q.before.lives,'Actual life popup11 defers extra-life credit')
   else assert(r('FloateyNum_Control',i)==6 and q.after.star==35 and q.after.music==64,'Native Star timer35 and music64 writer returned')end
  end
  q.collected=state();pendingCollect=nil;buttons={}
 end)
end)
'''

SCORE=r'''
hook('StockTimerDEC',function()
 local q=food.pickups[#food.pickups];if not q or not q.collected or q.score_credit or pendingScore then return end
 local i=emu.getState()['cpu.x'];local control=q.actor.kind==3 and 11 or 6
 if i~=q.actor.slot or r('FloateyNum_Control',i)~=control or r('FloateyNum_Timer',i)~=43 then return end
 local cpu=emu.getState();assert(cpu['cpu.a']==43 and cpu['cpu.y']==control,'Actual timer43/control branch')
 q.credit_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],timer=43,control=control}
 local before=score();pendingScore=returning(function(t)
  assert(score()==before+(q.actor.kind==3 and 0 or 1000),'Actual delayed native stock score writer')
  if q.actor.kind==3 then assert(q.life_writer and r('NumberofLives')==q.before.lives+1 and r('Square2SoundQueue')==64,'Actual INC lives and extra-life cue64')end
  q.score_credit={before=before,after=score(),state=state(),pc=t.pc,sp=t.sp};q.credit={guest=guestReturns,state=state(),cue=r('Square2SoundQueue')};pendingScore=nil
 end)
end)
hook('LifeCredit',function()
 local q=food.pickups[#food.pickups];if not q or q.actor.kind~=3 then return end
 local cpu=emu.getState();assert(pendingScore and cpu['cpu.x']==q.actor.slot and cpu['cpu.y']==11 and r('NumberofLives')==q.before.lives,'Actual native extra-life INC before state')
 q.life_writer={before=state(),pc=cpu['cpu.pc'],sp=cpu['cpu.sp']}
end)
hook('LifeCreditAfter',function()
 local q=food.pickups[#food.pickups];if not q or q.actor.kind~=3 then return end
 assert(q.life_writer and r('NumberofLives')==q.before.lives+1,'Actual native extra-life INC after state');q.life_writer.after=state()
end)
'''


@lru_cache(maxsize=1)
def reference(raw):
    assert H(raw)==PIN and H(Path(Flower.__file__).read_bytes())==FLOWER_SHA
    with patch.object(Flower,'OWNED',OWNED):return Flower.reference(raw)


@lru_cache(maxsize=2)
def controller(raw,route):
    assert route in KINDS;parent=reference(raw)
    old=Flower.controller(raw);assert H(old)==Flower.LUA;text=old.decode()
    cfg=deepcopy(First.bindings(parent));cfg.update(sha=PIN,kind='stock',route=route,itemKind=KINDS[route],goal=1024 if route=='life'else 1616)
    b=dict(W.Symbols.bundle(),raw=raw)
    for name in('HpActorSlot','HpActorOwner','PlatformCollisionFlag','AreaMusicQueue'):
        cfg['ram'][name]=W.address(b,name)
    at=W.location(b,'DecNumTimer');needle=b'\xee'+cfg['ram']['NumberofLives'].to_bytes(2,'little');body=raw[at:at+48]
    assert body.count(needle)==1;delta=body.index(needle);assert raw[at:at+48]==parent[at:at+48]
    for name,advance in(('LifeCredit',0),('LifeCreditAfter',3)):
        pc=W.address(b,'DecNumTimer')+delta+advance;location=at+delta+advance
        cfg['hooks'][name]=dict(pc=pc,offset=location-16,bytes=list(raw[location:location+12]),work=False)
    if route=='life':
        pc,location=W.address(b,'DpHostTileQuery'),W.location(b,'DpHostTileQuery')
        assert raw[location:location+12]==parent[location:location+12]
        cfg['hooks']['TileQuery']=dict(pc=pc,offset=location-16,bytes=list(raw[location:location+12]),work=False)
    # The exact original Flower chain supplies only the verified travel code;
    # its collection/use driver is replaced by this separately pinned route.
    once=First.once
    text=once(text,text.split('\n',1)[0],'local C='+Stock.value(cfg))
    text=once(text,"star=r('StarInvincibleTimer'),score=score()","star=r('StarInvincibleTimer'),music=r('AreaMusicQueue'),score=score()")
    text=once(text,"r('NumberofLives')==2,'Authored living1-1'","(r('NumberofLives')==2 or C.itemKind==3 and food.pickups[2]and food.pickups[2].life_writer and r('NumberofLives')==3),'Authored living1-1'")
    text=once(text,"a.kind<2 then return a","(a.kind==0 or a.kind==C.itemKind)then return a")
    text=once(text,"h.after.kind==n-1 and h.after.x==a.x","h.after.kind==(n==1 and 0 or C.itemKind)and h.after.x==a.x")
    text=once(text,"a.x==(n==1 and 336 or 1248)","a.x==(n==1 and 336 or C.goal)")
    # Reuse the same bound actual second-lift function without altering it.
    pre=Flower.DRIVE[:Flower.DRIVE.index('local function drive()')]
    text=once(text,Flower.DRIVE,pre+DRIVE)
    start=text.index('local function endpoint()');end=text.index("hook('GameLoop'",start)
    text=text[:start]+ENDPOINT+'\n'+text[end:]
    if route=='life':
        text=once(text,"hook('GameLoop',function()",r'''hook('TileQuery',function()
 local cpu=emu.getState();local y=cpu['cpu.a'];local x=pos('ScreenLeft_X_Pos','ScreenLeft_PageLoc')+cpu['cpu.y']
 if guestReturns<1100 or x<1024 or x>=1040 or y<112 or y>=160 then return end
 local c=context();local tile=c.block(x,y);F.tile_queries=F.tile_queries or{}
 if #F.tile_queries>=24 then return end
 local q={player=state(),probe={x,y},tile=tile,pc=cpu['cpu.pc']};F.tile_queries[#F.tile_queries+1]=q
 returning(function(t)q.property=emu.getState()['cpu.a'];q.return_pc=t.pc;q.return_sp=t.sp end)
end)
hook('GameLoop',function()''')
    # Original Mushroom reward remains; the native Star/life branch declines
    # DpPickup, so observe its returned decline without treating it as food.
    text=once(text," local q=pendingCollect;local before=state();assert", " local q=pendingCollect;if q.actor.kind>=2 then return end;local before=state();assert")
    start=text.index("hook('HandlePowerUpCollision',function()");end=text.index("hook('EraseEnemyObject'",start)
    text=text[:start]+COLLECT+'\n'+text[end:]
    start=text.index("hook('StockTimerDEC',function()");end=text.index("hook('UnionPwrUpCore'",start)
    text=text[:start]+SCORE+'\n'+text[end:]
    # No wave is earned or fired in these routes. Keep the common exact Dp
    # movement return observer but remove the unrelated allocation callback.
    start=text.index("hook('WaveAllocated',function()");end=text.index("hook('DpPickup'",start)
    text=text[:start]+text[end:]
    text=once(text,'Bounded natural Goku first-food policy','Bounded natural Goku hidden stock policy')
    program=text.encode();assert not any(s in program for s in(b'emu.write',b'emu.setState',b'io.open',b'dofile',b'saveState',b'loadState',b'takeScreenshot'))
    Stock.LuaRuntime().compile(text);return program


def source(raw,route,limit):
    program=controller(raw,route);assert H(program)==PINS[route]
    with patch.object(Engine.J,'cold',Flower.cold),patch.object(Engine.J,'PIN',PIN):return Engine.run(raw,limit,text=program.decode())


def native(raw,route):
    program=controller(raw,route);assert H(program)==PINS[route]
    out=Stock.OUT;candidate,script=out/'candidate.nes',out/'controller.lua';before=script.read_bytes();guard=Stock.check(ROM)
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(out.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Stock.preserve_script(script,candidate,raw)as stage:stage(program);q=Stock.run(script,ROM,out/'capture',PIN,230)
        assert q['script_SHA256']==PINS[route]and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and Stock.check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--route',choices=KINDS,default='life')
    mode=p.add_mutually_exclusive_group();mode.add_argument('--source',action='store_true');mode.add_argument('--run',action='store_true');p.add_argument('--limit',type=int,default=3500)
    a=p.parse_args();assert 1500<=a.limit<=4000;raw=ROM.read_bytes();reference(raw)
    if a.run:q=native(raw,a.route)
    else:
        def deny(*a,**k):raise AssertionError('Source attempted output/emulator after bounded transient inverse')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.route,a.limit)
            else:
                program=controller(raw,a.route);assert H(program)==PINS[a.route];q=dict(passed=True,ROM_SHA256=PIN,controller_SHA256=H(program),route_executed=False,outputs=0)
    print('GOKU_STOCK '+json.dumps(q,separators=(',',':')),flush=True);return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
