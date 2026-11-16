"""Frozen genuineM prefix, then ordinary authored GB Pit Flower and returns."""
from pathlib import Path
from functools import lru_cache
from types import SimpleNamespace
from copy import deepcopy
import replay_gb_pit_mushroom_ground_1116 as Previous

R,ROM,W,N,H,Current=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='39fc5b092fbf9da26da702f2c4351defac48aaec6f9c0790217f0d220299bd4c'
M_CONTROL_SHA='adbc164c7a7ceab3aaa936aefda4dcf794e9bb5107a952707b8ea7dea88d3102'
TEMPLATE=R/'tools/playthroughs/smb1_toad_native_stock_91dc_1116.lua'
TEMPLATE_SHA='5af8cb1b2aa3820b723c71e3612c0df2440098bfa4ea94159d6b8893520b507b'
CONTROL=R/'tools/playthroughs/gb_pit_flower_controls_1116.lua'

def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)

@lru_cache(maxsize=1)
def bindings(raw):
    c=deepcopy(Previous.bindings(raw));c.update(kind='flower',stock_type=1,target_x=1248,target_y=144)
    b=Current.bindings(raw)['bundle'];pc,at=W.address(b,'FloateyNumbersCore'),W.location(b,'FloateyNumbersCore')
    life,cue=c['ram']['NumberofLives'],c['ram']['Square2SoundQueue']
    inc=bytes((0xe6,life))if life<256 else bytes((0xee,life&255,life>>8))
    store=bytes((0x85,cue))if cue<256 else bytes((0x8d,cue&255,cue>>8))
    needle=inc+b'\xa9\x40'+store;hits=[i for i in range(160-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1
    for name,n in(('LifeBefore',hits[0]),('LifeAfter',hits[0]+len(needle))):
        bank=(at-16)//8192;c['hooks'][name]=dict(pc=pc+n,offset=at+n-16,bank=bank,bytes=list(raw[at+n:at+n+8]),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))
    return c

@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    assert H(Previous.CONTROL.read_bytes())==M_CONTROL_SHA and H(TEMPLATE.read_bytes())==TEMPLATE_SHA
    _,body=Previous.controller(raw,'mushroom').split('\n',1)
    body=once(body,'local function read(at)',"local stock={phase='travel'};food.stock=stock\nlocal function read(at)")
    body=once(body,"kind='mushroom'",'kind=C.kind')
    body=once(body,'local function drive()\n','local stockDrive\nlocal function drive()\n if food.M_scope_passed then stockDrive();return end\n')
    body=once(body,'local function endpoint()\n','local function foodEndpoint()\n if food.M_scope_passed then return end\n')
    body=once(body,"  finish(true,'Natural GB Pit M/1000/60tick tier1 and25 returned Pit movements at completedMain')",
        "  assert(food.actual_head_setup and food.actual_head and food.actual_head.returned,'Frozen genuineM head proof');food.M_scope_passed=true;stock.since=guestReturns;stock.pitSince=pitReturns;buttons={}")
    body=once(body,"hook('HandlePowerUpCollision',function()\n","hook('HandlePowerUpCollision',function()\n if food.M_scope_passed then return end\n")
    body=once(body,"hook('GuestPowerupUpdate',function()\n","hook('GuestPowerupUpdate',function()\n if food.M_scope_passed then return end\n")
    body=once(body,"frame<5000 and mainEntries<3000,'Bounded firstM fixture'","frame<14000 and mainEntries<6500,'Bounded ordinary GB Pit M then Flower'")
    stock=TEMPLATE.read_text().replace("hook('MarioSourcePowerupUpdate'","hook('GuestPowerupUpdate'")
    stock=stock.replace('SMB1 Toad','GB Pit')
    start=stock.index('local function chooseStock(c)');end=stock.index('\nstockDrive=function()',start)
    stock=stock[:start]+CONTROL.read_text()+stock[end:]
    stock=once(stock,'or pendingMain or pendingGuest or pendingStock then return end','or pendingMain or pendingGuest or pendingStock or pendingPit then return end')
    stock=once(stock,'if not stock.resumeBase then stock.resumeBase=guestReturns end','if not stock.resumeBase then stock.resumeBase=guestReturns;stock.pitBase=pitReturns end')
    stock=once(stock,"assert(stock.sound.writes20>0 and mainEntries==mainReturns and guestEntries==guestReturns,'Actual cue and balanced Main/native movement')",
        "assert(stock.sound.writes20>0 and mainEntries==mainReturns and guestEntries==guestReturns and pitEntries==pitReturns and pitReturns-stock.pitBase>=25,'Actual cue,25 returned movement/ability and completedMain');assert(stock.actual_head and stock.actual_head.returned and stock.actual_head_setup,'Actual head→Flower setup, not arrow replacement')")
    head=r'''local stockHeadPending
hook('PlayerHeadCollision',function()
 if not food.M_scope_passed or stock.born then return end
 local s=state();if s.x<C.target_x-24 or s.x>C.target_x+16 or s.y>=176 then return end
 assert(not stockHeadPending);local z=emu.getState()
 local q={PC=z['cpu.pc'],SP=z['cpu.sp'],A=z['cpu.a'],X=z['cpu.x'],Y=z['cpu.y'],state=s,saved=r('SavedJoypadBits')};stock.actual_head=q
 stockHeadPending=returning(function(t)q.returned={PC=t.pc,SP=t.sp,state=state()};stockHeadPending=nil end)
end)
hook('SetupPowerUp',function()
 if not stockHeadPending or stock.born then return end
 local z=emu.getState();stock.actual_head_setup={PC=z['cpu.pc'],SP=z['cpu.sp'],A=z['cpu.a'],X=z['cpu.x'],Y=z['cpu.y'],state=state(),inside_actual_head=true}
end)
hook('InjurePlayer',function()
 if not food.M_scope_passed or stock.injury then return end
 local z=emu.getState();local i=r('ObjectOffset');stock.injury={PC=z['cpu.pc'],SP=z['cpu.sp'],state=state(),actor=actor(i),player_box=box('BoundingBox_UL_Corner'),enemy_box=box('EnemyBoundingBoxCoord',i)}
end)
'''
    body=once(body,"hook('GameLoop',function()",stock+'\n'+head+"hook('GameLoop',function()")
    text='local C='+Previous.Previous.Text.lua(bindings(raw))+'\n'+body
    Previous.Previous.LuaRuntime().compile(text)
    assert not any(v in text for v in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text

def metadata(raw,key='flower'):
    return dict(ROM_SHA256=H(raw),owner_role=Current.OWNERS[H(raw)],factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,key).encode()),
        M_factory_SHA256=BASE_SHA,M_control_SHA256=M_CONTROL_SHA,stock_template_SHA256=TEMPLATE_SHA,control_SHA256=H(CONTROL.read_bytes()),
        hooks=bindings(raw)['hooks'],scope='Frozen genuineGBPit M+25 then actual1248Flower head/birth/maturity/physicalcollector/credit/60tier2/+25returned ExpandedMovement+PitFlight atactualMain',
        old_APIs_unchanged=True,gameplay_seeds=0,game_bytes_changed=0,outputs=0,Mesen=False)

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
