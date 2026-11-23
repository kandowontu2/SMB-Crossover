"""Exactbcc26 Goku ordinary Mushroom->Flower and earned original wave.

Additive controller-only successor to the frozen27e first-food proof. Root
alone may --run. Source uses declared linked real menu entry, normal pads,
the existing Goku lifts and the original source latch/charge/shot behavior.
"""
import argparse
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import run_goku_first_food_1123 as First
import run_dkjr_flower_draw_native_1123 as Binding
import run_arthur_restored_cache_native_1123 as Arthur

H,W,N,Stock,ROM,Engine=First.H,First.W,First.N,First.Stock,First.ROM,First.Engine
PARENT=Binding.CANDIDATE
PIN=Arthur.CANDIDATE
OWNED=Stock.R/'build/goku-flower-source-1123'
FIRST_SHA='2857dc5b710063cf1fca175071af1b0d066e2fb6f57a665fcac360f485921a60'
LUA='a0bdda3f104d794f96ae0c1ba584ce1bee33224a1480c35cf89c12f1dc8a8aa0'
SOURCE_PROOF={
    'ROM_SHA256':PIN,
    'receipt_SHA256':'8178c4585d66940e85e7285cda67de5b93248a0f8fb2333aa5a76a5b673a94dc',
    'receipt_inner_SHA256':'c3de585b5a1852287313488228f304eed47403647504cdaffac9da6c4ad4dda8',
    'linked_source_passes':1558,'Main_returns':1558,'Dp_returns':1558,
    'Flower_birth':[1248,136,1],'Flower_mature':[1248,119,128],
    'collector_player':[1260,138],'positive_overlap':[3,3],
    'waves_before_after':[0,3],'tier_before_after':[1,2],
    'score_before_after':[1125,2125],'pickup_post_credit_returns':25,
    'wave_spend':[3,2],'wave_world_distance':119,'wave_post_use_returns':25,
    'terminal':[1260,112,83,2,2],
    'scope':'Declared linked real menu/Select/Start; actual current CPU; ordinary pads only; no native cadence claim',
}

DRIVE=r'''
local F={phase='travel',events={},mounts=0}
food.flower_route=F
local function fp(c,p)
 if F.phase==p then return end
 F.phase=p;F.at=guestReturns;assert(#F.events<55,'Bounded ordinary Goku Flower phases')
 local s=state();s.control=p;F.events[#F.events+1]=s
end
local function steer(c,x,n)return{right=c.x<x-n,left=c.x>x+n}end
local function ready(c)return c.grounded and r('DpAction')==1 and r('DpPrevious')&128==0 end
local function fourthLift(c)
 if c.x<850 or c.x>=945 then return end
 F.fourth=F.fourth or{phase='ride',started=guestReturns}
 local p=F.fourth;assert(guestReturns-p.started<500,'Bounded actual second Goku lift crossing')
 if p.phase=='press'then
  if r('DpAction')==2 or r('DpAction')==3 and r('DpJumping')~=0 then p.phase='moving';p.accepted=state();p.at=guestReturns
  elseif r('DpPrevious')&128~=0 then p.phase='ride';return{right=true}end
  return{right=true,a=true}
 end
 if p.phase=='moving'then
  if c.grounded and c.y==112 then p.landing=p.landing or state()end
  return{right=true,a=guestReturns-p.at<8}
 end
 for i=0,5 do local e=actor(i)
  if e.flag==1 and e.id==37 and e.state==64 and e.x==872 and r('HpActorOwner',i)==132
    and r('PlatformCollisionFlag',i)<128 and math.abs(e.y-c.y-32)<=1 and ready(c)and c.y<=144 then
   p.support={state=state(),actor=e,owner=132,collision=r('PlatformCollisionFlag',i)};p.phase='press'
   return{right=true,a=true}
  end
 end
 return steer(c,887,1)
end
local function drive()
 if not(food.pickups[1]and food.pickups[1].resumed)then firstDrive();return end
 if not menuDone or not active()then buttons={};return end;identity();observe()
 local c=context();c.stageFrame=guestReturns;c.lastA=r('DpPrevious')&128~=0
 if c.x>(F.farthest or 0)then F.farthest=c.x;F.progress=guestReturns end
 if c.x>=850 and c.x<945 and guestReturns%32==0 then
  F.support=F.support or{};local s={state=state(),slot=r('HpActorSlot'),actors={}}
  for i=0,5 do local e=actor(i);if e.flag>0 then e.owner=r('HpActorOwner',i);e.support=r('PlatformCollisionFlag',i);s.actors[#s.actors+1]=e end end
  if #F.support==12 then table.remove(F.support,1)end;F.support[#F.support+1]=s
 end
 assert(not F.progress or guestReturns-F.progress<500,'Bounded measured Goku Flower travel progress')
 local q=food.pickups[2]
 if q then
  if not q.resumed then buttons={};return end
  F.wave=F.wave or{phase='release',started=guestReturns,trace={}}
  local wave=F.wave;assert(guestReturns-wave.started<220,'Bounded original ground charge and fresh-A wave use')
  if wave.allocated then buttons={};return end
  if wave.phase=='release'then
   if not ready(c)or r('DpPrevious')&64~=0 then buttons={};return end
   if r('PlayerFacingDir')~=1 then buttons={right=true};return end
   wave.phase='charge';wave.request=state()
  end
  if r('DpAction')==8 and r('DpTimer')==0 then
   assert(r('DpPrevious')&128==0,'Actual released A before original ready charge')
   wave.freshA=wave.freshA or state();buttons={b=true,a=true};return
  end
  buttons={b=true};return
 end
 if pendingCollect or pendingScore then buttons={};return end
 local a=target()
 if a then
  F.actor=a;F.latest={state=state(),actor=a}
  if F.phase=='travel'or F.phase=='align'or F.phase=='head'then fp(c,'clear-right-brick')end
  if F.phase=='clear-right-brick'then
   if not F.tiles then
    F.tiles={};for y=80,208,16 do local row={y=y,tiles={}};for x=1168,1328,16 do row.tiles[#row.tiles+1]=c.block(x,y)end;F.tiles[#F.tiles+1]=row end
   end
   local tile=c.block(1264,144)
   if tile==0 or tile==35 or tile==194 or tile==195 then F.open={state=state(),tile=tile};fp(c,'run-up')
   else
    if not ready(c)or c.y~=176 then buttons={};return end
    if math.abs(c.x-1260)>2 or c.vx~=0 then buttons=steer(c,1260,2);return end
    F.brick_request=state();F.brick_before=tile;fp(c,'brick-jump');buttons={a=true};return
   end
  end
  if F.phase=='brick-jump'then
   assert(guestReturns-F.at<130,'Original powered head clears the adjacent authored brick')
   if c.block(1264,144)==0 or c.block(1264,144)==35 then
    F.open={state=state(),tile=c.block(1264,144)};fp(c,'run-up')
   else buttons={a=guestReturns-F.at<28};return end
  end
  if F.phase=='run-up'then
   if not ready(c)or c.y~=176 then buttons=steer(c,1260,1);return end
   if math.abs(c.x-1260)>1 or c.vx~=0 then buttons=steer(c,1260,1);return end
   if a.state<128 then buttons={};return end
   F.mounts=F.mounts+1;assert(F.mounts<=4,'Bounded genuine right-side Flower mounts')
   F.takeoff=state();F.mount_trace=F.mount_trace or{};F.mount_trace[F.mounts]={takeoff=state()}
   fp(c,'mount');buttons={a=true};return
  end
  if F.phase=='mount'then
   assert(guestReturns-F.at<120,'Ordinary Goku Flower mount bound')
   local trace=F.mount_trace[F.mounts]
   if not trace.apex or c.y<trace.apex.y then trace.apex=state();trace.player_box=box('BoundingBox_UL_Corner');trace.item_box=box('EnemyBoundingBoxCoord',a.slot)end
   if c.grounded and guestReturns-F.at>5 then fp(c,'run-up');buttons=steer(c,1260,1);return end
   buttons={a=guestReturns-F.at<35};return
  end
 end
 if F.phase=='travel'then
  if c.x<1172 then
   local lift=fourthLift(c);if lift then buttons=lift;return end
   buttons=travel(c)
   local retry,failed=secondPipeRetry(c);assert(not failed,'Bounded retained second-pipe latch retry')
   if retry then buttons=retry end
   if c.x>=950 and c.x<1080 then buttons.a=false end
   return
  end
  fp(c,'align')
 end
 if F.phase=='align'then
  if not ready(c)or c.y~=176 then buttons={};return end
  if math.abs(c.x-1242)>2 or c.vx~=0 then buttons=steer(c,1242,2);return end
  F.head_attempts=(F.head_attempts or 0)+1;assert(F.head_attempts<=5,'Bounded actual second-question head requests')
  F.head_request=state();fp(c,'head');buttons={a=true};return
 end
 if F.phase=='head'then
  assert(guestReturns-F.at<130,'Actual second question bump bound')
  if ready(c)and guestReturns-F.at>5 then fp(c,'align');buttons={};return end
  buttons={a=guestReturns-F.at<30};return
 end
 buttons={}
end
'''


def once(t,a,b):return First.once(t,a,b)


@lru_cache(maxsize=1)
def reference(raw):
    assert H(raw)in(PARENT,PIN)and H(Path(First.__file__).read_bytes())==FIRST_SHA
    origin=raw
    if H(raw)==PIN:
        existed=OWNED.exists()
        try:origin=Arthur.recover_parent(raw,OWNED)
        finally:
            if OWNED.exists():
                assert not any(OWNED.iterdir()),'Only transient assembler files, already removed'
                if not existed:OWNED.rmdir()
        assert H(origin)==PARENT
    with Binding.cache():parent=Binding.without_flower(origin)
    assert H(parent)==First.PIN
    for h in First.bindings(parent)['hooks'].values():
        lo=16+h['offset'];assert raw[lo:lo+len(h['bytes'])]==origin[lo:lo+len(h['bytes'])]==parent[lo:lo+len(h['bytes'])]==bytes(h['bytes'])
    return parent


@lru_cache(maxsize=1)
def controller(raw):
    parent=reference(raw);old=First.controller(parent);assert H(old)==First.LUA;text=old.decode()
    cfg=deepcopy(First.bindings(parent));cfg.update(sha=H(raw),kind='upgrades')
    b=dict(W.Symbols.bundle(),raw=raw)
    for n in('HpActorSlot','HpActorOwner','PlatformCollisionFlag','DpTimer','DpShotState','DpShotX','DpShotY','DpShotYPage','DpShotCamera'):
        cfg['ram'][n]=W.address(b,n)
    pc,at=W.address(b,'DpNEACA'),W.location(b,'DpNEACA')
    debit=W.location(b,'DpNEAC6');expected=b'\xce'+cfg['ram']['DpWaves'].to_bytes(2,'little')+b'\xee'+cfg['ram']['DpShotState'].to_bytes(2,'little')
    assert at==debit+len(expected)and raw[debit:at]==parent[debit:at]==expected
    cfg['hooks']['WaveAllocated']=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+12]),work=False)
    line=text.split('\n',1)[0];text=once(text,line,'local C='+Stock.value(cfg))
    # Inline the exact retained ordinary travel chain; the first item already
    # completed, so its original generic first-block phase is bypassed.
    route=(Stock.R/'tools/playthroughs/full_roster_policy_og.lua').read_text()
    assert H((Stock.R/'tools/playthroughs/full_roster_policy_og.lua').read_bytes())=='17d3a38d53fe09b930048f081938bf707028f765577207bce41777ea4f5edb7b'
    route=once(route,"local phase='approach';local clock=0;","local phase='route';local clock=0;")
    prior='full_roster_policy_og.lua'
    for v in range(3,8):
        piece=(Stock.R/f'tools/playthroughs/dragon_power_11_v{v}.lua').read_text()
        piece=once(piece,"local root=assert(ROSTER_CONFIG.out:match('^(.*)/build/'))", "local root=''")
        piece=once(piece,"local route=assert(dofile(root..'/tools/playthroughs/"+prior+"'))",'local route=(function()\n'+route+'\nend)()')
        route=piece;prior=f'dragon_power_11_v{v}.lua'
    retry=(Stock.R/'tools/reference/goku_pipe_retry_1110.lua').read_text()
    start=retry.index('local function writePipeRetry()');end=retry.index('local function secondPipeRetry(c)',start)
    retry=retry[:start]+retry[end:]+"\nfood.pipe_retry=pipe\n"
    text=once(text,'local function drive()','local function firstDrive()')
    text=once(text,'local function endpoint()',"local ROSTER_CONFIG={name='goku'}\nlocal travel=(function()\n"+route+'\nend)()\n'+retry+'\n'+DRIVE+'\nlocal function endpoint()')
    text=once(text,"assert(n==1 and h and h.after and h.after.flag==1 and h.after.kind==0 and h.after.x==a.x", "assert(n<=2 and h and h.after and h.after.flag==1 and h.after.kind==n-1 and h.after.x==a.x")
    text=once(text,"r('DpWaves')==0,'Living original Dragon Power owner'", "r('DpWaves')<=3,'Living original Dragon Power owner'")
    text=once(text,"  assert(r('PlayerStatus')==1 and r('DpPower')==1 and r('DpPole')==1 and r('DpWaves')==0 and r('GuestPowerupActive')==0,'Actual earned Pole/tier survives25 original movements')", "  assert(r('PlayerStatus')==#food.pickups and r('DpPower')==#food.pickups and r('DpPole')==1 and r('DpWaves')==(#food.pickups==1 and 0 or 3)and r('GuestPowerupActive')==0,'Actual earned Pole/Flower tier survives25 original movements')")
    text=once(text," if pendingMain or pendingGuest then return end", """ if pendingMain or pendingGuest then return end
 local w=F.wave
 if w and w.allocated and guestReturns-w.allocated.guest>=25 and r('DpAction')==1 then
  identity();assert(w.moved and w.moved>=28 and r('DpWaves')==2 and r('DpPower')==2 and r('PlayerStatus')==2 and r('DpPole')==1,
   'One actually allocated earned wave spends3to2 and moves at least28 world pixels')
  assert(not pendingCollect and not pendingScore and mainEntries==mainReturns and guestEntries==guestReturns,'Balanced live use and completed Main')
  for _,list in pairs(dynamic)do assert(#list==0,'All mapped calls returned after earned wave use')end
  finish(true,'Natural Goku Mushroom/Flower, Waves3, actual charged wave and25 post-use returns');return
 end""")
    text=once(text,"   finish(true,'Natural Goku Mushroom, actual health/Pole reward and25 completed original workers')", "   food.flower_pickup_complete=state()")
    text=once(text,"assert(a.kind==0,'Only the real first Mushroom is accepted')", "assert(a.kind==#food.pickups,'Authored Mushroom then actual Flower accepted')")
    old_reward=""" local q=pendingCollect;local before=state();assert(emu.getState()['cpu.a']==0 and q.actor.kind==0,'Actual first Mushroom kind at source collector')
 local pc=emu.getState()['cpu.pc']
 returning(function(t)
  local after=state();assert(after.HP==math.min(150,before.HP+20)and before.HP<150 and after.HP>before.HP,
   'Immediate original food20/cap150 produces a real health increase')
  assert(before.pole==0 and before.tier==0 and after.pole==1 and after.tier==1 and after.waves==before.waves and after.hunger==0,
   'Actual native Pole/tier1 and original hunger reset, not Mario growth')
  q.source_reward={before=before,after=after,pc=pc,return_pc=t.pc,return_sp=t.sp}
 end)"""
    new_reward=""" local q=pendingCollect;local before=state();assert(emu.getState()['cpu.a']==q.actor.kind,'Actual authored kind at original source collector')
 local pc=emu.getState()['cpu.pc']
 returning(function(t)
  local after=state()
  if q.actor.kind==0 then
   assert(before.pole==0 and before.tier==0 and after.pole==1 and after.tier==1 and after.waves==before.waves and after.hunger==0,
    'Actual first native Pole/tier1 and original hunger reset')
   assert(after.HP==math.min(150,before.HP+20)and before.HP<150 and after.HP>before.HP,'Actual first food20/cap150 health increase')
  else
   assert(q.actor.kind==1 and before.waves==0 and after.waves==3 and before.tier==1 and after.tier==2,
    'Actual native Flower grants three plain original waves and tier2')
   assert(before.pole==1 and after.pole==1 and after.HP==before.HP and after.hunger==before.hunger,'Flower preserves original Pole, health and hunger')
  end
  q.source_reward={before=before,after=after,pc=pc,return_pc=t.pc,return_sp=t.sp}
 end)"""
    text=once(text,old_reward,new_reward)
    text=once(text,"q.after.pole==1 and q.after.tier==1,'Source award returned", "q.after.pole==1 and q.after.tier==q.actor.kind+1,'Source award returned")
    text=once(text,'pendingGuest=returning(function(t)pendingGuest=nil;guestReturns=guestReturns+1 end)',"""pendingGuest=returning(function(t)
  pendingGuest=nil;guestReturns=guestReturns+1
  local w=F.wave
  if w and w.allocated and r('DpShotState')&15~=0 then
   local x=r('DpShotX')+r('DpShotCamera')+256*r('DpShotCamera',1)
   local s={guest=guestReturns,x=x,y=r('DpShotY'),shot=r('DpShotState'),waves=r('DpWaves'),action=r('DpAction')}
   w.first=w.first or s;w.moved=math.max(w.moved or 0,math.abs(x-w.first.x))
   if #w.trace<12 then w.trace[#w.trace+1]=s end
  end
 end)""")
    text=once(text,"hook('DpPickup',function()", """hook('WaveAllocated',function()
 local w=F.wave;assert(food.pickups[2]and food.pickups[2].resumed and w and not w.allocated,'Earned Flower and25 returns precede use')
 assert(r('DpWaves')==2 and r('DpShotState')&15==1,'Actual original DEC Waves and INC ShotState completed')
 w.allocated={state=state(),guest=guestReturns,pc=emu.getState()['cpu.pc']}
end)
hook('DpPickup',function()""")
    program=text.encode();assert not any(v in program for v in (b'emu.write',b'emu.setState',b'io.open',b'dofile',b'takeScreenshot',b'saveState',b'loadState'))
    Stock.LuaRuntime().compile(text);return program


def cold(raw):
    reference(raw);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in(8,2,32):W.UI.key(m,pad)
    assert W.UI.menu_name(m)[0]=='GOKU'and N.get(m,'SelectedCharacter')==24 and N.get(m,'FmAlts')&128
    start=W.UI.key(m,16);N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(First.Base.Host.Family.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'DpReady')==68 and N.get(m,'DpHP')==100 and N.get(m,'DpPole')==N.get(m,'DpWaves')==N.get(m,'DpPower')==0
            assert N.get(m,'NumberofLives')==2 and N.get(m,'CrossoverBehaviorVersion')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Engine.Frames.frame(m,cold=True)
    raise AssertionError('Bounded genuine current Goku linked-menu/Select/Start entry')


def source(raw,limit):
    program=controller(raw);assert H(program)==LUA
    with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',H(raw)):return Engine.run(raw,limit,text=program.decode())


def native(raw):
    program=controller(raw);assert H(program)==LUA
    out=Stock.OUT;candidate,script=out/'candidate.nes',out/'controller.lua';before=script.read_bytes();guard=Stock.check(ROM)
    assert guard['ROM_sha256']==H(raw)and not guard['matching_patch_files']
    assert set(out.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Stock.preserve_script(script,candidate,raw)as stage:stage(program);q=Stock.run(script,ROM,out/'capture',H(raw),230)
        assert q['script_SHA256']==LUA and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and Stock.check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true');p.add_argument('--limit',type=int,default=3500)
    a=p.parse_args();assert 1200<=a.limit<=5000;raw=ROM.read_bytes();assert H(raw)in(PARENT,PIN)
    reference(raw)  # Five transient assembler files only under this bounded OWNED root.
    if a.run:q=native(raw)
    else:
        def deny(*a,**k):raise AssertionError('Goku Flower source attempted outputs/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.limit)
            else:
                program=controller(raw);assert H(program)==LUA;q=dict(passed=True,ROM_SHA256=PIN,controller_SHA256=H(program),route_executed=False,outputs=0)
    print('GOKU_FLOWER '+json.dumps(q,separators=(',',':')),flush=True);return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
