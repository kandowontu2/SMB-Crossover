"""New actual SuperMaaa F/S/L routes with a complete genuine M prefix."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import current_supermaaa_stock_91dc_1116 as Current
import replay_kamikaze_mario_flower_edge_91dc_1116 as Flower
import replay_kamikaze_mario_ground_stock_91dc_1116 as Stock
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,digest=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.digest
KINDS=Stock.KINDS
FLOWER_SHA='9663c035feff4544faeb2bf98dfdf006dc1df7c30f0b86d582cd014af04248f9'
STOCK_SHA='58e1680356c1a30ea16d8beba9dd5305362b28222bf38b71b2de35f6025fdf01'


@lru_cache(maxsize=3)
def controller(raw,key='flower'):
    assert key in KINDS;base,pin=(Flower,FLOWER_SHA)if key=='flower'else(Stock,STOCK_SHA)
    assert digest(Path(base.__file__).read_bytes())==pin
    c=deepcopy(Current.bindings(raw));b=Current.bundle(raw);kind,x,y=KINDS[key];h=c['hooks']['MarioSourceMovement']
    c.update(kind=key,stock_type=kind,target_x=x,target_y=y,movement_hex=raw[16+h['offset']:16+h['offset']+64].hex())
    for name in('ObjectOffset','Enemy_MovingDir','Enemy_Y_HighPos'):c['ram'][name]=W.address(b,name)
    name='MarioSourceInjuryStart';pc,at=W.address(b,name),W.location(b,name);bank=(at-16)//8192
    c['hooks'][name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    _,body=base.controller(raw,key).split('\n',1)
    assert body.count("r('MarioVariant')==3")==2 and body.count('variant=3')==1 and body.count('for _=1,5 do press({select=true})end')==1
    body=body.replace("r('MarioVariant')==3","r('MarioVariant')==2").replace('variant=3','variant=2')
    assert body.count("r('X5ChrMode')==132")==2;body=body.replace("r('X5ChrMode')==132","r('X5ChrMode')==131")
    body=body.replace('for _=1,5 do press({select=true})end','for _=1,4 do press({select=true})end')
    body=body.replace('Kamikaze Mario','SuperMaaa Mario').replace('Kamikaze Select5','SuperMaaa Select4')
    old="variant=r('MarioVariant'),chr_mode=r('X5ChrMode')";assert body.count(old)==1;body=body.replace(old,old+",neck=r('MaaaLength')",1)
    marker='local function identity()\n';assert body.count(marker)==1;body=body.replace(marker,marker+" assert(r('MaaaLength')<=160,'Original growing neck bound')\n",1)
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='flower'):
    return dict(ROM_SHA256=PIN,controller_SHA256=digest(controller(raw,key).encode()),factory_SHA256=digest(Path(__file__).read_bytes()),kind=key,
        foundation=Current.foundation(raw),readonly_control_reference=FLOWER_SHA if key=='flower'else STOCK_SHA,
        actual_return_owner='MarioSourceMovement; actual neck head/body/timer unchanged',
        scope='Current SuperMaaa genuine M+25 then actual F/S/L physical lifecycle/credit/effect and25 actual Source returns',
        outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def family(kind='flower'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
