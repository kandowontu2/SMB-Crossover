"""Actual Easy Shinobi first-Mushroom ownership diagnostic; stdout only.

No fallback reward counts as a Shinobi pass. Root alone may run the frozen
read-only native controller. Existing component and stage packets stay frozen.
"""
import argparse
from functools import lru_cache
import inspect
import json
from pathlib import Path
from unittest.mock import patch

import run_arthur_mushroom_1123 as A

R,W,N,H,Stock,Engine,ROM=A.R,A.W,A.N,A.H,A.Stock,A.Engine,A.ROM
PIN='bcc26bb5f6d11bbd38e46d5a5025eb30d2bc146e1bd293a44ca104eec5f40a0e'
LUA='5ec31aacb6f24c64ee897f05520075f0fde7cde98b6232b2c86dc7f18463d3ec'
CODE_PAGES=(506,507,508,509,510,513,515)
KERNEL='b7da3c10463953722594eaeef25050c270230e3ef8b59416bebaee307c786dfb'

POLICY=r'''
local function policy()
 local s=state();local a=item();latest={player=s,item=a,actors={}}
 if phase=='head'then
  headmotion.minY=math.min(headmotion.minY,s.y)
  if #headmotion.states<8 and(steps-jumpStep)%3==0 then headmotion.states[#headmotion.states+1]=s end
 end
 for i=0,5 do latest.actors[#latest.actors+1]=actor(i)end
 assert(s.lives==2 and s.high==1 and s.engine~=11,'Living original Shinobi')
 assert(s.ready==167 and r('SelectedCharacter')==36,'Actual Shinobi owner, no fallback')
 assert(updates<1800,'Bounded first Shinobi Mushroom')
 if phase=='align'then
  if r('Player_State')~=0 then return{}end
  if math.abs(x()-329)<=2 and r('Player_X_Speed')==0 and released()then
   if attempts==2 then
    assert(headmotion.upper_hits>=2 and headmotion.minSourceExportY<176 and #heads==0 and #births==0,
     'Original upper collisions without native authored head transaction')
    head_blocked=true;finish(false,'Original Shinobi upper block collision has no native head/effect ingress');return{}
   end
   attempts=attempts+1;assert(attempts<=2,'Bounded real Shinobi head attempts')
   jumpStep=steps;mark('head');return{a=true}
  end
  return steer(329,2)
 end
 if phase=='head'then
  if a then mark('collect')end
  if phase=='head'then
   local t=steps-jumpStep
   if t>100 and r('Player_State')==0 then mark('align');return{}end
   return{a=t<24}
  end
 end
 if phase=='collect'then
  assert(a,'Natural Mushroom remains while rejected')
  if mature and maturity.overlap>=20 then
   assert(maturity.set==0 and maturity.clear>=20 and maturity.owned_reject>=20 and not pickup,
    'Actual owning row23 rejects mature overlap before collector')
   blocked=true;finish(false,'Shinobi authenticated maturity row23 returns C0 on mature Mushroom overlap');return{}
  end
  assert(steps-at<420,'Bounded actual Mushroom overlap observation')
  if a.y<148 then return steer(396,2)end
  return steer(a.x-3,3)
 end
 return{}
end
'''

RETURNED=r'''
local function returned(p)
 local s=state();local cpu=emu.getState()
 if p.name=='Movement'then
  moves=moves+1
  if phase=='head'then headmotion.minSourceExportY=math.min(headmotion.minSourceExportY,s.y)end
 elseif p.name=='TakeHit'or p.name=='SourceHit'then
  if s.health<p.before.health then
   assert(not damage and p.target.flag==1 and p.target.id==6,'One actual first-Goomba injury')
   damage={before=p.before,after=s,target=p.target}
  end
 elseif p.name=='Maturity'then
  local c=(cpu['cpu.ps']or cpu['cpu.p'])&1
  if p.actor and p.actor.kind==0 and p.actor.state&128~=0 then
   maturity.queries=maturity.queries+1
   if c==0 then maturity.clear=maturity.clear+1 else maturity.set=maturity.set+1 end
   if p.overlap then
    maturity.overlap=maturity.overlap+1
    if #maturity.samples<8 then maturity.samples[#maturity.samples+1]={before=p.before,after=s,actor=p.actor,player_box=p.player_box,item_box=p.item_box,carry=c}end
   end
  end
 elseif p.name=='SourcePickup'or p.name=='NativePickup'then
  pickup={entry=p.name,before=p.before,after=s};finish(false,'Unexpected collector ingress; qualify actual Shinobi reward separately')
 end
end
'''


def once(s,a,b):
    assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)


def payload(raw):
    assert H(raw)==PIN
    read=lambda pages:b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in pages)
    code=read(CODE_PAGES);assert H(code)==KERNEL
    meta=read((516,517));art=read((503,504,505))
    assert code[69:72]==code[72:75]==bytes.fromhex('4c6fa0')and code[0x6f:0x71]==bytes.fromhex('1860')
    return code,meta,art


@lru_cache(maxsize=1)
def controller(raw):
    code,meta,art=payload(raw)
    b=dict(W.Symbols.bundle(),raw=raw);text=A.BODY.read_text()
    fields=('SelectedCharacter Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos Player_X_Speed '
      'Player_State PlayerStatus ScreenLeft_X_Pos ScreenLeft_PageLoc NumberofLives Enemy_Flag Enemy_ID Enemy_State '
      'Enemy_X_Position Enemy_PageLoc Enemy_Y_Position PowerUpType ObjectOffset GameEngineSubroutine OperMode OperMode_Task '
      'CrossoverBehaviorVersion CrossoverMenuState CrossoverMenuIndex CrossoverTitleDrawn DisableScreenFlag '
      'A_B_Buttons PreviousA_B_Buttons PlayerScoreDisplay InjuryTimer WorldNumber LevelNumber R0 R1 R2 R3 R6 R7 '
      'BoundingBox_UL_Corner FmAlts').split()
    cheats=[n for n in('CheatInvincible','CheatStartLevel','CheatInfiniteTime','CheatInfiniteLives','CheatAlwaysBig','CheatAllItems','CheatNoEnemies')if n in b['syms']]
    ram={n:W.address(b,n)for n in set(fields+cheats)}
    work={'ShReady':0x800,'ShHealth':0x539,'ShPower':0x42,'ShActorState':0x413,'ShPose':0x300,'ShFlags':0x460,'ShEpoch':0x553,
          'ShFeet':0x38f,'ShFeetHi':0x39a,'ShDir':0x3fd,'ShTile':0x804}
    hooks={}
    for event,name in [('GameLoop','GameLoop'),('TakeHit','InjurePlayer'),('SourcePickup','HuPickup'),
                       ('NativePickup','HandlePowerUpCollision'),('Maturity','HuMature'),('Head','PlayerHeadCollision')]:
        pc,at=W.address(b,name),W.location(b,name)
        hooks[event]=dict(name=name,pc=pc,tag=((at-16)//8192)|128,offset=at-16,bytes=list(raw[at:at+12]))
    for event,pc in [('Movement',0xb74f),('Step',0xb8a7),('Reject',0xa06f),('QueryReturn',0xb571)]:
        offset=pc-0xa000;hooks[event]=dict(name='Sh'+event,pc=pc,tag=3,offset=3*8192+(pc&8191),bytes=list(code[offset:offset+12]))
    at=16+65*8192+0xc79
    assert raw[at:at+8]==bytes.fromhex('08488a489848a200')
    hooks['SourceHit']=dict(name='ShInjury',pc=0xac79,tag=193,offset=at-16,bytes=list(raw[at:at+12]))
    assert code[1]+256*code[2]==0xb74f
    # The shipped Sh recipe authenticates page517 twice: metadata then its
    # shared fourth art carrier. Keep that source-declared ordered input.
    cookie=bytes([167,36,1])+bytes.fromhex(H(code+meta+art+meta[1024:]))[:13]
    assert raw[16+65*8192+0xa78:16+65*8192+0xa88]==cookie
    cfg=dict(sha=PIN,ram=ram,work=work,hooks=hooks,cheats=cheats,cookie=list(cookie))
    text=once(text,"local phase,at='wound',0","local phase,at='align',0\nlocal blocked,head_blocked=false,false\nlocal maturity={queries=0,clear=0,set=0,owned_reject=0,overlap=0,samples={}}\nlocal headmotion={minY=255,minSourceExportY=255,upper_hits=0,states={},queries={}}")
    text=once(text,"local function r(n,i)return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)end",'''local function r(n,i)
 if C.work[n]then return emu.read(2*8192+C.work[n]+(i or 0),emu.memType.nesWorkRam)end
 return emu.read(assert(C.ram[n],n)+(i or 0),emu.memType.nesDebug)
end''')
    start,stop=text.index('local function state()'),text.index('local function actor(i)')
    text=text[:start]+'''local function state()
 return{x=x(),y=r('Player_Y_Position'),high=r('Player_Y_HighPos'),engine=r('GameEngineSubroutine'),lives=r('NumberofLives'),status=r('PlayerStatus'),
 ready=r('ShReady'),health=r('ShHealth'),power=r('ShPower'),source_state=r('ShActorState'),pose=r('ShPose'),flags=r('ShFlags'),epoch=r('ShEpoch'),
 source_feet=r('ShFeet')+256*r('ShFeetHi'),motion=r('ShDir'),
 update=updates,moves=moves,steps=steps,frame=frame,score=score(),injury=r('InjuryTimer')}
end
'''+text[stop:]
    text=text.replace("r('SelectedCharacter')~=32","r('SelectedCharacter')~=36").replace("r('SelectedCharacter')==32","r('SelectedCharacter')==36")
    text=once(text,'collections=collections,mature=mature,latest=latest','collections=collections,mature=mature,maturity=maturity,headmotion=headmotion,head_blocked=head_blocked,blocked=blocked,actual_pickup_passed=false,latest=latest')
    start,stop=text.index('local function policy()'),text.index('local function returned(p)')
    text=text[:start]+POLICY+'\n'+text[stop:]
    start,stop=text.index('local function returned(p)'),text.index('local function settle()')
    text=text[:start]+RETURNED+'\n'+text[stop:]
    text=once(text,"if name=='GameLoop'then updates=updates+1;return end",'''if name=='GameLoop'then updates=updates+1;return end
 if name=='Reject'then
  local p=pending[#pending];if p and p.name=='Maturity'then maturity.owned_reject=maturity.owned_reject+1 end
  return
 end
 if name=='QueryReturn'then
  if phase=='head'then
   local c=emu.getState();local sp=c['cpu.sp']
   local caller=emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+3)&255),emu.memType.nesDebug)
   if(caller==0xb303 or caller==0xb314)and c['cpu.a']==1 and(r('ShTile')==0xc1 or r('ShTile')==0x51)then
    headmotion.upper_hits=headmotion.upper_hits+1
   end
   if #headmotion.queries<8 then
    headmotion.queries[#headmotion.queries+1]={step=steps,state=state(),result=c['cpu.a'],tile=r('ShTile'),caller=caller,
     queryX=r('R0')+256*r('R1'),queryY=r('R2')+256*r('R3')}
   end
  end
  return
 end''')
    text=once(text,"if name=='TakeHit'then p.target=actor(r('ObjectOffset'))","if name=='TakeHit'or name=='SourceHit'then p.target=actor(r('ObjectOffset'))")
    text=once(text,"elseif name=='SourcePickup'then p.value=cpu['cpu.a']",'''elseif name=='Maturity'then
  p.actor=actor(r('ObjectOffset'));p.player_box={};p.item_box={}
  for k=0,3 do p.player_box[k+1]=r('BoundingBox_UL_Corner',k);p.item_box[k+1]=r('BoundingBox_UL_Corner',(p.actor.slot+1)*4+k)end
  local b,e=p.player_box,p.item_box
  p.overlap=b[1]~=255 and e[1]~=255 and b[1]<=e[3]and b[3]>=e[1]and b[2]<=e[4]and b[4]>=e[2]
 elseif name=='SourcePickup'then p.value=cpu['cpu.a']''')
    text=once(text,"assert(a.kind==0 and damage and #heads>0,'Authored first naked Mushroom birth')","assert(a.kind==0 and #heads>0,'Actual Shinobi authored first Mushroom birth')")
    text=once(text,"if index~=31 then pulse(index<24 and 'up' or 'left');return end",'''if index~=10 then
   if index//8>1 then pulse('up')elseif index//8<1 then pulse('down')elseif index%8<2 then pulse('right')else pulse('left')end;return
  end
  if r('SelectedCharacter')~=36 then pulse('select');return end''')
    text=once(text,"if r('ArHostReady')~=167 then","if r('ShReady')~=167 then")
    text=once(text,"assert(initial.lives==2 and initial.flags&32==0 and initial.weapon==64,'Normal armored Arthur first spawn')",'''assert(initial.lives==2 and initial.ready==167 and initial.health==6 and initial.power==0,'Actual initialized Shinobi donor actor')
  for i,v in ipairs(C.cookie)do
   assert(emu.read(2*8192+0x1fe0+i-1,emu.memType.nesWorkRam)==v and emu.read(3*8192+0x1fe0+i-1,emu.memType.nesWorkRam)==v,'Both full payload-derived Shinobi headers')
  end''')
    text=text.replace('Arthur','Shinobi')
    program='local C='+Stock.value(cfg)+'\n'+text
    assert not any(v in program for v in('emu.write','emu.setState','saveState','loadState','io.open','dofile','takeScreenshot'))
    assert H(program.encode())==LUA,'Frozen diagnostic controller'
    Stock.LuaRuntime().compile(program);return program.encode()


def cold(raw):
    payload(raw);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in (1,1,4,32):W.UI.key(m,pad)
    assert W.UI.menu_name(m)[0]=='SHINOBI'and N.get(m,'SelectedCharacter')==36 and N.get(m,'FmAlts')&68==4
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(A.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert m.ram[2][0x800]==167 and m.ram[2][0x539]==6
            assert bytes(m.ram[3][:7168])==payload(raw)[0]
            return m
        m.controller_pad=0;Engine.Frames.frame(m,cold=True)
    raise AssertionError('Actual Shinobi menu/cold bound')


def source(raw,limit):
    text=inspect.getsource(Engine.run)
    text=once(text,'for fn in tuple(callbacks[0].get(self.pc,())):fn()','for fn in tuple(callbacks[0].get(self.pc,())):fn(self.pc)')
    space=dict(Engine.__dict__);exec(compile(text,__file__,'exec'),space)
    with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',PIN):q=space['run'](raw,limit,text=controller(raw).decode())
    receipt=q['receipt'];expected=diagnostic(receipt)
    return dict(passed=expected,source_diagnostic_qualified=expected,actual_pickup_passed=False,execution=q,outputs=0,
                observer_source_SHA256=H(Path(__file__).read_bytes()),
                scope='Controller-only actual current menu/cold/Main instructions. Expected negative head or maturity witness; no native-video or pickup success claim.')


def diagnostic(q):
    return bool(q.get('head_blocked')and q.get('headmotion',{}).get('upper_hits',0)>=2 or
                q.get('blocked')and q.get('maturity',{}).get('overlap',0)>=20)


def native(raw):
    program=controller(raw);assert LUA and H(program)==LUA,'Run only source-qualified frozen controller'
    out=Stock.OUT;candidate,script=out/'candidate.nes',out/'controller.lua'
    before=script.read_bytes();guard=Stock.check(ROM)
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(out.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Stock.preserve_script(script,candidate,raw)as stage:
            stage(program);q=Stock.run(script,ROM,out/'capture',PIN,210)
        assert q['script_SHA256']==LUA and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and Stock.check(ROM)==guard
    return dict(passed=diagnostic(q['receipt']),native_diagnostic_observed=diagnostic(q['receipt']),
                actual_pickup_passed=False,execution=q,outputs=0)


def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group()
    g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=600);args=p.parse_args()
    assert 200<=args.limit<=2000;raw=ROM.read_bytes();assert H(raw)==PIN
    def deny(*a,**k):raise AssertionError('Shinobi source probe attempted output/emulator')
    if args.run:q=native(raw)
    else:
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            q=source(raw,args.limit)if args.source else dict(passed=True,controller_SHA256=H(controller(raw)),outputs=0)
    print('SHINOBI_MUSHROOM '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
