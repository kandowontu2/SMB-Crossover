"""Separate current Peach F/S/L bindings over frozen readonly control policies."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import current_smb1_peach_stock_91dc_1116 as Current
import replay_smb1_toad_flower_runup_91dc_1116 as Flower
import replay_smb1_toad_native_stock_91dc_1116 as Stock
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,digest=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.digest
KINDS={'flower':(1,1248,144),'star':(2,1616,144),'oneup':(3,1024,128)}
FLOWER_SHA='d18e2f63bccf343a3ff332a8d6f8ddaeb25cc7938c1ac3ed18a1f6094d1eeae6'
STOCK_SHA='1acaa08a55128dbf10d4cbfeb92d5d5611f183492c732b4dc060f19c5f8a7e1b'


@lru_cache(maxsize=3)
def controller(raw,key='flower'):
    assert key in KINDS
    base,sha=(Flower,FLOWER_SHA)if key=='flower'else(Stock,STOCK_SHA)
    assert digest(Path(base.__file__).read_bytes())==sha
    c=deepcopy(Current.bindings(raw));kind,x,y=KINDS[key];h=c['hooks']['BmNativeMovement']
    c.update(kind=key,stock_type=kind,target_x=x,target_y=y,movement_hex=raw[16+h['offset']:16+h['offset']+64].hex())
    b=Current.bundle(raw)
    for name in('ObjectOffset','Enemy_MovingDir','Enemy_Y_HighPos','Player_XSpeedAbsolute'):c['ram'][name]=W.address(b,name)
    name='MarioSourceInjuryStart';at,pc=W.location(b,name),W.address(b,name);bank=(at-16)//8192
    c['hooks'][name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    _,body=base.controller(raw,key).split('\n',1)
    assert body.count("r('MarioVariant')==5")==2 and body.count('variant=5')==1 and body.count('for _=1,2 do press({select=true})end')==1
    body=body.replace("r('MarioVariant')==5","r('MarioVariant')==6").replace('variant=5','variant=6')
    body=body.replace('for _=1,2 do press({select=true})end','for _=1,3 do press({select=true})end').replace('Toad','Peach').replace('Select2','Select3')
    marker="variant=r('MarioVariant'),chr_mode=r('X5ChrMode')"
    assert body.count(marker)==1
    body=body.replace(marker,marker+",BmOwner=r('BmOwner'),float_active=r('BmFloatActive'),float_timer=r('BmFloatTimer')",1)
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='flower'):
    return dict(ROM_SHA256=PIN,kind=key,controller_SHA256=digest(controller(raw,key).encode()),factory_SHA256=digest(Path(__file__).read_bytes()),
        foundation=Current.foundation(raw),readonly_control_reference=FLOWER_SHA if key=='flower'else STOCK_SHA,
        scope='Actual compiled Peach/genuineM+25 then real stock/credit/effect/25 returned BmNativeMovement; float state readonly',
        outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def family(kind='flower'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
