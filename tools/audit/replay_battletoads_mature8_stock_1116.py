"""Actual91dc genuine M prefix then natural Star/hidden1UP; no game writes."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import replay_battletoads_mature8_food_credit_1116 as Previous

C,Current,R,ROM,PIN,W,N=Previous.C,Previous.Current,Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N
KINDS={'star':2,'oneup':3}
CONTROL=R/'tools/playthroughs/battletoads_mature8_stock_1116.lua'

def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)

@lru_cache(maxsize=4)
def bindings(raw,key='rash',kind='oneup'):
    assert kind in KINDS;q=deepcopy(Previous.bindings(raw,key));q.update(kind=kind,stock_kind=kind,stock_type=KINDS[kind]);b=Current.bundle(raw)
    for n in('AreaMusicQueue','BtLife'):q['ram'][n]=W.address(b,n)
    at,pc=W.location(b,'FloateyNumbersCore'),W.address(b,'FloateyNumbersCore');life=W.address(b,'NumberofLives');cue=W.address(b,'Square2SoundQueue')
    inc=bytes((0xe6,life))if life<256 else bytes((0xee,life&255,life>>8))
    store=bytes((0x85,cue))if cue<256 else bytes((0x8d,cue&255,cue>>8));pattern=inc+b'\xa9\x40'+store
    hits=[i for i in range(160-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    for n,delta in(('LifeBefore',hits[0]),('LifeAfter',hits[0]+len(pattern))):
        bank=(at-16)//8192;q['hooks'][n]=dict(pc=pc+delta,offset=at+delta-16,bytes=list(raw[at+delta:at+delta+8]),bank=bank,
            bank_SHA256=C.digest(raw[16+bank*8192:16+(bank+1)*8192]))
    return q

@lru_cache(maxsize=4)
def controller(raw,key='rash',kind='oneup'):
    text=Previous.controller(raw,key);prefix='local C='+Previous.Previous.Text.lua(Previous.bindings(raw,key))+'\n';assert text.startswith(prefix)
    text='local C='+Previous.Previous.Text.lua(bindings(raw,key,kind))+'\n'+text[len(prefix):]
    old="local food={phase='mushroom',pickups={},heads={},births={}}"
    text=once(text,old,old+"\nlocal stock={phase='M-prefix',samples={}};food.stock=stock")
    text=once(text,"and r('NumberofLives')==2,'Authored living1-1'","and r('NumberofLives')==(stock.life_credit and 3 or 2),'Authored living1-1'")
    text=once(text,'local function drive()','local function foodDrive()')
    marker="  if C.kind=='mushroom'or#food.pickups==2 then"
    text=once(text,marker,"""  if C.stock_kind then
   food.M_scope_passed=true;food.phase='stock-travel';stock.phase='travel';stock.since=guestReturns;buttons={};return
  end
"""+marker)
    marker="hook('GameLoop',function()";text=once(text,marker,CONTROL.read_text()+'\n'+marker)
    text=once(text,'endpoint();if not stopped then drive()end','endpoint();if not stopped then stockEndpoint()end;if not stopped then drive()end')
    text=once(text,'if mainReturns>2600 or frame>10000 then','if mainReturns>4200 or frame>14000 then')
    Previous.Previous.Previous.Previous.Previous.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text

def metadata(raw,key='rash',kind='oneup'):
    text=controller(raw,key,kind)
    return dict(ROM_SHA256=PIN,identity=key,kind=kind,controller_SHA256=C.digest(text.encode()),
        factory_SHA256=C.digest(Path(__file__).read_bytes()),controls_SHA256=C.digest(CONTROL.read_bytes()),
        actual_candidate_execution=True,real_M_prefix_and25_returns_retained=True,
        scope='Genuine authored stock birth/mature/physical collector/erase/cue/credit and25 completed original workers at Main return',
        gameplay_seeds=0,outputs=0,Mesen=False)

def family(kind='oneup'):
    from types import SimpleNamespace
    return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,key,kind),metadata=lambda raw,key:metadata(raw,key,kind))
