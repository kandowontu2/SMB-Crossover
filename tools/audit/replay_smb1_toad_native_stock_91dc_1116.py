"""Current native Toad M prefix, then genuine separate F/Star/hidden1UP."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_smb1_toad_native_mushroom_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='8932fddf3f9f0605988a83ee6b8aedcd7d235763d316030d0b742f61f5e10ed7'
TEMPLATE=R/'tools/playthroughs/smb1_toad_native_stock_91dc_1116.lua'
KINDS={'flower':(1,1248,144),'star':(2,1616,144),'oneup':(3,1024,128)}


def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)


@lru_cache(maxsize=3)
def controller(raw,key='flower'):
    assert key in KINDS and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    c=dict(Current.bindings(raw));h=c['hooks']['BmNativeMovement'];kind,x,y=KINDS[key]
    c.update(kind=key,stock_type=kind,target_x=x,target_y=y,movement_hex=raw[16+h['offset']:16+h['offset']+64].hex())
    _,body=Previous.controller(raw).split('\n',1)
    body=once(body,'local function read(at)',"local stock={phase='travel'};food.stock=stock\nlocal function read(at)")
    body=once(body,"kind='mushroom'",'kind=C.kind')
    body=once(body,"and r('NumberofLives')==2 and", "and r('NumberofLives')==(stock.life_credit and 3 or 2)and")
    body=once(body,'local function drive()\n',"local stockDrive\nlocal function drive()\n if food.M_scope_passed then stockDrive();return end\n")
    body=once(body,'local function endpoint()\n','local function foodEndpoint()\n if food.M_scope_passed then return end\n')
    body=once(body,"  finish(true,'Natural SMB1 Toad M/1000/60tick tier1 and25 returned native Toad movements at completedMain')",
        "  food.M_scope_passed=true;stock.since=guestReturns;buttons={}")
    body=once(body,"hook('HandlePowerUpCollision',function()\n", "hook('HandlePowerUpCollision',function()\n if food.M_scope_passed then return end\n")
    body=once(body,"hook('MarioSourcePowerupUpdate',function()\n", "hook('MarioSourcePowerupUpdate',function()\n if food.M_scope_passed then return end\n")
    body=once(body,"hook('GameLoop',function()",TEMPLATE.read_text()+"\nhook('GameLoop',function()")
    body=once(body,"frame<5000 and mainEntries<3000,'Bounded firstM fixture'","frame<12000 and mainEntries<6500,'Bounded actual Toad natural stock'")
    text='local C='+Previous.Previous.Text.lua(c)+'\n'+body;Previous.Previous.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='flower'):
    return dict(ROM_SHA256=PIN,kind=key,controller_SHA256=digest(controller(raw,key).encode()),
        factory_SHA256=digest(Path(__file__).read_bytes()),template_SHA256=digest(TEMPLATE.read_bytes()),
        M_factory_preserved=BASE_SHA,foundation=Current.foundation(raw),
        scope='Genuine M+25, then separate natural stock/physical collector/effect/cue/credit and25 returned BmNativeMovement updates at actualMainreturn',
        outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def family(kind='flower'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
