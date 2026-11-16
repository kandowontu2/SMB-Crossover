"""Strict current Excitebike natural stock successors; no game changes."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import re
import replay_excitebike_mushroom_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
CONTROL=R/'tools/playthroughs/excitebike_stock_91dc_1116.lua'
ROUTE=R/'tools/reference/excitebike_full11_1102_v1.lua'
ROUTE_SHA='ca5d281ce2b60ef27dc20120a909e4591749c116fd4d6fed29213634da6da6b8'
M_FACTORY_SHA='178c61b38984525da4a5f7dee76f0dde29bf369b46efafeb23580ba6a22141c3'
KINDS={'flower':(1,1248,144),'star':(2,1616,144),'oneup':(3,1024,128)}

def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)

@lru_cache(maxsize=3)
def bindings(raw,key='flower'):
    assert key in KINDS and digest(Path(Previous.__file__).read_bytes())==M_FACTORY_SHA
    q=deepcopy(Previous.bindings(raw));kind,x,y=KINDS[key];q.update(key='excitebike',kind=key,stock_type=kind,target_x=x,target_y=y)
    b=Current.bundle(raw)
    for name in('FrameCounter','Block_Buffer_1','Block_Buffer_2','MTileAttribute','SavedJoypadBits'):
        q['ram'][name]=W.address(b,name)
    at,pc=W.location(b,'FloateyNumbersCore'),W.address(b,'FloateyNumbersCore');life=W.address(b,'NumberofLives');cue=W.address(b,'Square2SoundQueue')
    inc=bytes((0xe6,life))if life<256 else bytes((0xee,life&255,life>>8))
    store=bytes((0x85,cue))if cue<256 else bytes((0x8d,cue&255,cue>>8));needle=inc+b'\xa9\x40'+store
    hits=[i for i in range(160-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1
    for name,delta in(('LifeBefore',hits[0]),('LifeAfter',hits[0]+len(needle))):
        bank=(at-16)//8192;q['hooks'][name]=dict(pc=pc+delta,offset=at+delta-16,work=False,bytes=list(raw[at+delta:at+delta+8]),bank=bank,
            bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    return q

@lru_cache(maxsize=3)
def controller(raw,key='flower'):
    config=bindings(raw,key);text=Previous.controller(raw);prefix='local C='+Previous.Text.lua(Previous.bindings(raw))+'\n';assert text.startswith(prefix)
    text='local C='+Previous.Text.lua(config)+'\n'+text[len(prefix):]
    text=once(text,"local dynamic,food,readback={},{births={},pickups={}},{}", "local stock={phase='travel'}\nlocal dynamic,food,readback={},{births={},pickups={}},{};food.stock=stock")
    text=once(text,"and r('NumberofLives')==2,'Living no-cheat route'", "and r('NumberofLives')==(stock.life_credit and 3 or 2),'Living no-cheat route'")
    text=once(text,'local function endpoint()','local function foodEndpoint()')
    text=once(text,'local function foodEndpoint()\n','local function foodEndpoint()\n if food.M_scope_passed then return end\n')
    text=once(text,'local function drive()','local function foodDrive()')
    text=once(text,"  finish(true,'Natural Excitebike M/60 native ticks/1000 and25 returned original motor+movement at completed Main')",
        "  food.M_scope_passed=true;stock.since=movementReturns;phase='stock-travel';buttons=0")
    text=once(text,"hook('HandlePowerUpCollision',function()\n", "hook('HandlePowerUpCollision',function()\n if food.M_scope_passed then return end\n")
    text=once(text,"hook('GuestPowerupUpdate',function()\n", "hook('GuestPowerupUpdate',function()\n if food.M_scope_passed then return end\n")
    assert digest(ROUTE.read_bytes())==ROUTE_SHA
    route=ROUTE.read_text();route=route[route.index('local function block('):route.index('emu.addMemoryCallback(')]
    route=re.sub(r'\bjump\b','travelJump',route).replace('jumpSequences=jumpSequences+1','stock.jumpSequences=(stock.jumpSequences or 0)+1')
    route=once(route,'local function travel()','local function travel()\n local cached=state()')
    helper="local L=C.ram\nlocal travelJump\nlocal function wx()return pos('Player_X_Position','Player_PageLoc')end\n"+route+'\n'+CONTROL.read_text()+'\n'
    text=once(text,"hook('GameLoop',function()",helper+"hook('GameLoop',function()")
    text=once(text,"frame<5000 and mainEntries<3000,'Bounded physical/Main first-M'", "frame<12000 and mainEntries<5000,'Bounded physical/Main natural stock'")
    Previous.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','takeScreenshot','saveState','loadState'))
    return text

def metadata(raw,key='flower'):
    text=controller(raw,key)
    return dict(ROM_SHA256=PIN,kind=key,controller_SHA256=digest(text.encode()),factory_SHA256=digest(Path(__file__).read_bytes()),
        controls_SHA256=digest(CONTROL.read_bytes()),M_factory_preserved_SHA256=M_FACTORY_SHA,original_route_reference_SHA256=ROUTE_SHA,
        scope='Genuine M+25 then actual authored stock/cue/credit/effect+25 returned original motor and accepted movement at completed Main',
        preservation=Current.preservation(raw),gameplay_seeds=0,outputs=0,Mesen=False)

def family(kind='flower'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
