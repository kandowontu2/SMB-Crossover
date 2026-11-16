"""Current Kamikaze genuine firstM, actual Source movement return counter."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import current_kamikaze_mario_stock_91dc_1116 as Current
import replay_smb1_toad_native_mushroom_91dc_1116 as Reference
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,digest=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.digest
BASE_SHA='8932fddf3f9f0605988a83ee6b8aedcd7d235763d316030d0b742f61f5e10ed7'


@lru_cache(maxsize=1)
def controller(raw,key='kamikaze'):
    assert key=='kamikaze'and digest(Path(Reference.__file__).read_bytes())==BASE_SHA
    c=dict(Current.bindings(raw));h=c['hooks']['MarioSourceMovement'];c['movement_hex']=raw[16+h['offset']:16+h['offset']+64].hex()
    _,body=Reference.controller(raw).split('\n',1)
    assert body.count("r('MarioVariant')==5")==2 and body.count('variant=5')==1 and body.count('for _=1,2 do press({select=true})end')==1
    body=body.replace("r('MarioVariant')==5","r('MarioVariant')==3").replace('variant=5','variant=3')
    assert body.count("r('X5ChrMode')==131")==2;body=body.replace("r('X5ChrMode')==131","r('X5ChrMode')==132")
    body=body.replace('for _=1,2 do press({select=true})end','for _=1,5 do press({select=true})end')
    assert body.count("hook('BmNativeMovement',function()")==1 and body.count('C.hooks.BmNativeMovement')==2
    body=body.replace("hook('BmNativeMovement',function()","hook('MarioSourceMovement',function()",1).replace('C.hooks.BmNativeMovement','C.hooks.MarioSourceMovement')
    body=body.replace('ToadNative_entries','MarioSource_entries').replace('ToadNative_returns','MarioSource_returns')
    body=body.replace('SMB1 Toad','Kamikaze Mario').replace('native Toad movements','MarioSourceMovement updates').replace('Toad Select2','Kamikaze Select5')
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='kamikaze'):
    return dict(ROM_SHA256=PIN,controller_SHA256=digest(controller(raw,key).encode()),factory_SHA256=digest(Path(__file__).read_bytes()),
        foundation=Current.foundation(raw),readonly_control_reference=BASE_SHA,
        actual_return_owner='MarioSourceMovement, not BmNativeMovement',ordinary_M_policy_unchanged=True,
        scope='Compiled Kamikaze/genuineM/60tick tier1/1000 and25 actual returned Source movements at actualMain',
        outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def family():return SimpleNamespace(W=W,N=N,controller=controller,metadata=metadata)
