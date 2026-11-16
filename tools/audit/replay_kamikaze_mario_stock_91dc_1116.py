"""Actual Kamikaze Source movement for separate genuine current F/S/L."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import current_kamikaze_mario_stock_91dc_1116 as Current
import replay_smb1_toad_flower_right_mount_91dc_1116 as Flower
import replay_smb1_toad_native_stock_91dc_1116 as Stock
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,digest=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.digest
KINDS={'flower':(1,1248,144),'star':(2,1616,144),'oneup':(3,1024,128)}
FLOWER_SHA='ae9c837befedc084f7844a14116eab6de14e6eddc707bcf9f570fee7cbc840cd'
STOCK_SHA='1acaa08a55128dbf10d4cbfeb92d5d5611f183492c732b4dc060f19c5f8a7e1b'


@lru_cache(maxsize=3)
def controller(raw,key='flower'):
    assert key in KINDS;base,sha=(Flower,FLOWER_SHA)if key=='flower'else(Stock,STOCK_SHA)
    assert digest(Path(base.__file__).read_bytes())==sha
    c=deepcopy(Current.bindings(raw));kind,x,y=KINDS[key];h=c['hooks']['MarioSourceMovement'];b=Current.bundle(raw)
    c.update(kind=key,stock_type=kind,target_x=x,target_y=y,movement_hex=raw[16+h['offset']:16+h['offset']+64].hex())
    for name in('ObjectOffset','Enemy_MovingDir','Enemy_Y_HighPos'):c['ram'][name]=W.address(b,name)
    name='MarioSourceInjuryStart';at,pc=W.location(b,name),W.address(b,name);bank=(at-16)//8192
    c['hooks'][name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    _,body=base.controller(raw,key).split('\n',1)
    assert body.count("r('MarioVariant')==5")==2 and body.count('variant=5')==1 and body.count("r('X5ChrMode')==131")==2
    body=body.replace("r('MarioVariant')==5","r('MarioVariant')==3").replace('variant=5','variant=3').replace("r('X5ChrMode')==131","r('X5ChrMode')==132")
    assert body.count('for _=1,2 do press({select=true})end')==1;body=body.replace('for _=1,2 do press({select=true})end','for _=1,5 do press({select=true})end')
    assert body.count("hook('BmNativeMovement',function()")==1 and body.count('C.hooks.BmNativeMovement')==2
    body=body.replace("hook('BmNativeMovement',function()","hook('MarioSourceMovement',function()",1).replace('C.hooks.BmNativeMovement','C.hooks.MarioSourceMovement')
    body=body.replace('ToadNative_entries','MarioSource_entries').replace('ToadNative_returns','MarioSource_returns')
    body=body.replace('SMB1 Toad','Kamikaze Mario').replace('native Toad movements','MarioSourceMovement updates').replace('Toad Select2','Kamikaze Select5').replace('native movements','Source movements')
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='flower'):
    return dict(ROM_SHA256=PIN,kind=key,controller_SHA256=digest(controller(raw,key).encode()),factory_SHA256=digest(Path(__file__).read_bytes()),
        foundation=Current.foundation(raw),readonly_control_reference=FLOWER_SHA if key=='flower'else STOCK_SHA,
        actual_return_owner='MarioSourceMovement',scope='Genuine M+25 then actual stock/credit/effect and25 returned Source moves; no native speed-class assumption',
        outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def family(kind='flower'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
