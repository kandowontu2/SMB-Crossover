"""Karnov natural Easy hidden 1-UP and Star, exactffd708, ordinary inputs.

Source-only by default. Root owns native --run and its two-file staging root.
Uses the verified five-item route's crouch fire and ordinary pipe controls.
"""
import argparse,json
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import run_sypha_stock_1123 as Previous

A=Previous.A
W,N,H,ROM,Stock,Engine=A.W,A.N,A.H,A.ROM,A.Stock,A.Engine
PIN=Previous.CURRENT
PINS={'life':'8bd3de07328ada4a7eeee57c9ce19b78c8bee0b6ab43627fa91e5e99abfff991',
      'star':'bd8a43052eebf3fc74a8c559545d66fc9b8767c664ed66d1ebca9797ad09a664'}
POLICY=r'''
local T={kind=C.itemKind,phase='travel',events={},support={}}
ROBOT_STOCK_STATE=T
local jumpAge,release,passedLift=0,0,false
local untilA,launchDirection=0,0
local goal=C.itemKind==3 and 1024 or 1616
local function buttons(n)
 local b={};for k,v in pairs({right=1,left=2,down=4,up=8,start=16,select=32,b=64,a=128})do b[k]=n&v~=0 end;return b
end
local function sample(c,a)return{x=c.x,y=c.y,state=c.state,update=c.update,health=c.health,shot=c.shot,item=a}end
local function phase(c,p,a)
 if T.phase==p then return end
 assert(#T.events<40,'Bounded Karnov pickup phases')
 T.phase=p;T.since=c.update;T.events[#T.events+1]={phase=p,player=sample(c,a)}
end
local function steer(c,x,band)return{right=c.x<x-band,left=c.x>x+band}end
local function solid(c,x,y)local t=c.block(x,y);return t~=0 and t~=35 and t~=38 and t~=194 end
local function actor(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46 and c.r('PowerUpType',i)==T.kind then
   return{x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),slot=i}
  end
 end
end
local function defend(c,b)
 local e=c.enemy()
 if e and e.id<21 and e.dx>0 and e.dx<100 and math.abs(e.y-c.y)<48 and c.grounded then
  if c.r('PlayerFacingDir')~=1 then return{right=true}end
  return{down=true,b=c.update%12<6}
 end
 return b
end
local function ordinary(c)
 local x,y,ground=c.x,c.y,c.grounded
 local pad=1
 local wait=x>=600 and x<636 and y<=128 or x>=1000 and x<1090 or x>=1290 and x<1362 or x>=2350 and x<2434
 if x>=1140 then wait=solid(c,x+16,216)and not solid(c,x+20,y+16)end
 if x>=2420 and x<2434 and y<=112 then wait=true end
 if ground and jumpAge==0 and release==0 and not wait then jumpAge=36 end
 if jumpAge>0 then pad=pad|128;jumpAge=jumpAge-1;if jumpAge==0 then release=8 end elseif release>0 then release=release-1 end
 if x<530 and c.update%12<6 then pad=pad|64 end
 if x>750 then passedLift=true end
 if not passedLift and x>=688 and x<724 then
  if y>108 then pad=x<700 and 1 or 0;jumpAge=0;release=0 else pad=129 end
 end
 return defend(c,buttons(pad))
end
local function launch(c,d,p)
 launchDirection=d;untilA=c.update+28;phase(c,p)
 return{right=d==1,left=d==-1,a=true}
end
local function drive(c)
 if C.itemKind==3 and c.lives>=3 or C.itemKind==2 and c.star>0 then phase(c,'credited');return{}end
 local a=actor(c)
 if a and not T.actor then T.actor=sample(c,a);phase(c,'emerge',a)end
 if T.actor and not a then T.missing=T.missing or sample(c);return{}end
 if a then
  T.latest=sample(c,a)
  local waitX=goal+(T.kind==3 and 52 or 51)
  -- The 1-UP leaves its block and falls through this safe floor intercept;
  -- a late airborne reversal loses ground against the moving native actor.
  if T.kind==3 then return defend(c,steer(c,waitX,2))end
  if a.state&128==0 then return defend(c,steer(c,waitX,2))end
  if T.phase=='catch-jump'then
   if c.grounded and c.update-T.since>4 then phase(c,'catch',a)
   else return{right=launchDirection==1,left=launchDirection==-1,a=c.update<untilA}end
  end
  phase(c,'catch',a)
  if T.kind==2 and a.x<goal+80 then
   if math.abs(c.x-waitX)>2 then return defend(c,steer(c,waitX,2))end
   if c.grounded and not c.lastA and a.y>=130 and math.abs(a.x-c.x-6)<=13 then return launch(c,1,'catch-jump')end
   return{}
  end
  if c.grounded and not c.lastA and math.abs(a.x-c.x)<24 and c.y-a.y>12 then return launch(c,a.x<c.x and -1 or 1,'catch-jump')end
  return defend(c,steer(c,a.x-4,3))
 end
 if T.phase=='travel'then
  if c.x>=goal-64 then phase(c,'align')else return ordinary(c)end
 end
 if T.phase=='bump'then
  if c.grounded and c.update-T.since>55 then phase(c,'align')end
  return{a=c.update<untilA}
 end
 if not c.grounded or c.y<160 then return defend(c,steer(c,goal-64,2))end
 if math.abs(c.x-(goal-5))<=2 and not c.lastA then
  T.attempts=(T.attempts or 0)+1;assert(T.attempts<=6,'Bounded authored Karnov head bump')
  return launch(c,0,'bump')
 end
 return defend(c,steer(c,goal-5,2))
end
return function(c)
 if T.clock==c.update then return T.pad end
 T.clock=c.update;T.pad=drive(c);return T.pad
end
'''


def star_policy():
    text=Stock.once(POLICY,"local T={kind=C.itemKind,phase='travel',events={},support={}}",
        "local T={kind=0,phase='travel',events={},support={}}")
    text=Stock.once(text,'local goal=C.itemKind==3 and 1024 or 1616','local goal=336')
    text=Stock.once(text,'local function drive(c)\n',"""local function drive(c)
 if T.kind==0 and T.mushroom then
  if c.update-T.mushroom.sourceSteps<40 then return{}end
  T.kind=2;goal=1616;T.actor=nil;T.missing=nil;T.attempts=0;phase(c,'travel')
 end
""")
    return Stock.once(text,'  T.latest=sample(c,a)',"""  T.latest=sample(c,a)
  if T.kind==0 then return defend(c,steer(c,math.min(a.x-8,414),1))end""")


def controller(raw,item):
    assert H(raw)==PIN and item in('life','star')
    parent=A.reference(Previous.reference(raw))
    cfg=deepcopy(Stock.bindings(parent,'simon',item))
    cfg.update(sha=PIN,form='karnov',name='KARNOV',char=34,slot=7,variant=1,variant_field='FmAlts',variant_mask=1,
               expected=[3]if item=='life'else[0,2],itemKind=3 if item=='life'else 2,navigation=['right']*7+['']*25)
    b=dict(W.Symbols.bundle(),raw=raw)
    for name in('FmAlts','PlatformCollisionFlag','CurrentBankC','InvPickup','InvPickupOwner'):
        cfg['ram'][name]=W.address(b,name)
    name='KrMovement';pc=W.address(b,name)
    segment=b['segs'][b['syms'][name]['seg']]
    assert segment['name']=='"KR_KERNEL"'and int(segment['start'],0)==0xa000 and int(segment['size'],0)==8192
    # This imported external .bin segment has ooffs0 in the combined debug;
    # its existing loader packet is CHR399, not file offset zero.
    at=1048592+399*1024+pc-0xa000
    cfg['hooks']['Movement']=dict(pc=pc,tag=3,offset=3*8192+(pc&8191),hex=raw[at:at+12].hex())
    for name,h in cfg['hooks'].items():
        if name!='Movement':
            at=16+h['offset'];assert raw[at:at+12].hex()==h['hex'],name
    old=Stock.controller(parent,'simon',item).decode();marker="assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha"
    body=old[old.index(marker):]
    changes=[("local function r(name,i)","local function kr(a)return emu.read(2*8192+a,emu.memType.nesWorkRam)end\nlocal function r(name,i)"),
        ('local physical,polls,updates,motor,mask=0,0,0,0,0','local physical,polls,updates,motor,mask=0,0,0,0,0\nlocal lastKarnovClock'),
        ("assert(r(C.variant_field)&C.variant_mask==0,'Original identity in menu')","if r(C.variant_field)&C.variant_mask~=C.variant then return pulse('select')end"),
        ('r(C.variant_field)&C.variant_mask==0','r(C.variant_field)&C.variant_mask==C.variant'),
        ("power=r('PlayerStatus'),growth=r('GuestPowerupActive')","power=r('PlayerStatus'),growth=r('GuestPowerupActive'),health=kr(0x68),shot=kr(0x65)&3,weapon=kr(0x65),option=kr(0x8e),owned=kr(0x8f),boots=kr(0xbd),bombs=kr(0xbb),cycle=kr(0x860),sourceClock=kr(0xe8),sourceSteps=motor"),
        ('c.update=updates;','c.update=motor;'),
        ("c.lastA=r('PreviousA_B_Buttons')&128~=0","c.lastA=kr(0x1b)&1~=0"),
        ("kind=r('PowerUpType',i),","kind=r('PowerUpType',i),stamp=r('InvPickup',i),owner=r('InvPickupOwner',i),"),
        ("assert(updates<5100 and s.yHigh<2,'Bounded living pickup route')","assert(updates<5000 and s.yHigh<2 and s.lives>=2,'Bounded living Karnov pickup route')"),
        ("  entered=physical;clockInput=choose(context())","  entered=physical;lastKarnovClock=kr(0xe8);clockInput=choose(context())"),
        ("if p.name=='Movement' then motor=motor+1", """if p.name=='Movement' then
   local clock=kr(0xe8)
   if clock~=lastKarnovClock then
    assert(clock==((lastKarnovClock+1)&255),'Exactly one accepted Karnov step')
    motor=motor+1;lastKarnovClock=clock
   end"""),
        (" local complete=true", """ local T=ROBOT_STOCK_STATE
 for i=0,5 do local a=actor(i)
  if a.flag==1 and a.id==37 and(a.state==64 or a.state==65)then
   local key=tostring(a.x)..':'..a.state
   local h=T.support[key]
   if not h then
    h={stage='1-1',slot=i,left=a.x,center=a.x+16,width=32,first_observed_top=a.y,
     source_initial_top=208,state=a.state,carries=0};T.support[key]=h
   end
   if r('PlatformCollisionFlag',i)==i and s.state==0 then h.carries=h.carries+1 end
  end
 end
 local complete=true"""),
        ("local s=state()\n q.collect=", """local s=state()
 assert(a.stamp==252 and a.owner==34,'Native Karnov stock preparation')
 assert(s.shot==p.before.shot and s.owned==p.before.owned and s.option==p.before.option and s.cycle==p.before.cycle,
  'Stock reward preserves Karnov equipment')
 q.collect="""),
        ('   q.after=s', """   assert(s.shot==q.grant.shot and s.owned==q.grant.owned and s.option==q.grant.option
    and s.boots==q.grant.boots and s.bombs==q.grant.bombs and s.cycle==q.grant.cycle,
    'Karnov equipment persists through25 accepted steps')
   q.after=s""")]
    for a,z in changes:body=Stock.once(body,a,z)
    if item=='star':
        body=Stock.once(body,
            "assert(s.shot==p.before.shot and s.owned==p.before.owned and s.option==p.before.option and s.cycle==p.before.cycle,\n  'Stock reward preserves Karnov equipment')",
            "assert(a.kind<2 or(s.shot==p.before.shot and s.owned==p.before.owned and s.option==p.before.option and s.cycle==p.before.cycle),\n  'Stock reward preserves Karnov equipment')")
        body=Stock.once(body,"assert(p.before.power==a.kind and s.growth~=0 and r('GuestPowerupTarget')==a.kind+1,'Actual source growth');return",
            """assert(a.kind==0,'Only the real first Mushroom precedes Star')
  if p.before.health&128~=0 then
   assert(s.health==p.before.health&127 and s.shot==p.before.shot,'Karnov Mushroom heals the first spent hit')
  else
   assert(s.health==p.before.health and s.shot==math.min(2,p.before.shot+1),'Karnov Mushroom earns a source shot')
  end
  ROBOT_STOCK_STATE.mushroom=s
  return""")
        body=Stock.once(body,'if q.collect and not q.grant and kind<2 and s.growth==0 and s.status==kind+1',
            'if q.collect and not q.grant and kind==0 and s.shot==q.collect.after.shot and s.status==q.collect.after.status')
    text='local C='+Stock.value(cfg)+'\nlocal choose=(function()\n'+(POLICY if item=='life'else star_policy())+'\nend)()\n'+body
    assert not any(t in text for t in('emu.write','emu.setState','saveState','loadState','io.open','dofile','takeScreenshot'))
    Stock.LuaRuntime().compile(text)
    if item in PINS:assert H(text.encode())==PINS[item]
    return text


def cold(raw):
    assert H(raw)==PIN
    b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for _ in range(7):W.UI.key(m,1)
    W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]=='KARNOV'and N.get(m,'SelectedCharacter')==34 and N.get(m,'FmAlts')&1
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(A.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert m.ram[2][0x65]==m.ram[2][0x68]==0
            return m
        m.controller_pad=0;Engine.Frames.frame(m,cold=True)
    raise AssertionError('Actual Karnov cold bound')


def source(raw,item,limit=4000):
    text=controller(raw,item).replace("assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha",
        "assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha",1)
    text+="\nemu.addEventCallback(guarded('Source bound',function()if physical>="+str(limit)+" then finish(false,'Bounded source diagnostic')end end),emu.eventType.endFrame)"
    with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',PIN):return Engine.run(raw,limit+1,text=text)


def native(raw,item,root):
    assert H(raw)==PIN and item in PINS
    program=controller(raw,item).encode();root=root.resolve()
    assert root.is_relative_to(Stock.R/'build')and root not in(Stock.R/'build',Stock.OUT)
    guard=Stock.check(ROM);assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    root.mkdir();candidate,script=root/'candidate.nes',root/'controller.lua'
    try:
        candidate.write_bytes(raw);script.write_bytes(program)
        q=Stock.run(script,ROM,root/'capture',PIN,210)
        print('KARNOV_STOCK_NATIVE '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['script_SHA256']==PINS[item]and q['outputs_written']==0 and not q['images']
        return q
    finally:
        script.unlink(missing_ok=True);candidate.unlink(missing_ok=True);root.rmdir()
        assert ROM.read_bytes()==raw and Stock.check(ROM)==guard


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--item',choices=('life','star'),default='life')
    g=p.add_mutually_exclusive_group();g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--native-root',type=Path);p.add_argument('--limit',type=int,default=4000);a=p.parse_args();assert 1000<=a.limit<=5000
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:
        assert a.native_root is not None
        return int(not native(raw,a.item,a.native_root)['passed'])
    def deny(*a,**k):raise AssertionError('Source attempted outputs/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        q=source(raw,a.item,a.limit)if a.source else dict(compiled=True,controller_SHA256=H(controller(raw,a.item).encode()),outputs=0,native=False)
    print('KARNOV_STOCK_SOURCE '+json.dumps(q,separators=(',',':')),flush=True)
    return int(a.source and not q['passed'])


if __name__=='__main__':raise SystemExit(main())
