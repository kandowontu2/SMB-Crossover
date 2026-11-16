"""Actual SuperMaaa genuine M prefix for the missing F/S/L suites."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import current_supermaaa_stock_91dc_1116 as Current
import replay_kamikaze_mario_mushroom_91dc_1116 as Reference
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,digest=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.digest
BASE_SHA='0ade4e8d2e2ce7c96f956dc3e7c250760c0d0be2da56c2912e4041f8bb02f0f7'


@lru_cache(maxsize=1)
def controller(raw,key='supermaaa'):
    assert key=='supermaaa'and digest(Path(Reference.__file__).read_bytes())==BASE_SHA
    c=dict(Current.bindings(raw));h=c['hooks']['MarioSourceMovement'];c['movement_hex']=raw[16+h['offset']:16+h['offset']+64].hex()
    _,body=Reference.controller(raw,'kamikaze').split('\n',1)
    assert body.count("r('MarioVariant')==3")==2 and body.count('variant=3')==1 and body.count('for _=1,5 do press({select=true})end')==1
    body=body.replace("r('MarioVariant')==3","r('MarioVariant')==2").replace('variant=3','variant=2')
    assert body.count("r('X5ChrMode')==132")==2;body=body.replace("r('X5ChrMode')==132","r('X5ChrMode')==131")
    body=body.replace('for _=1,5 do press({select=true})end','for _=1,4 do press({select=true})end')
    body=body.replace('Kamikaze Mario','SuperMaaa Mario').replace('Kamikaze Select5','SuperMaaa Select4')
    old="variant=r('MarioVariant'),chr_mode=r('X5ChrMode')";assert body.count(old)==1
    body=body.replace(old,old+",neck=r('MaaaLength')",1)
    old='local function identity()\n';assert body.count(old)==1
    body=body.replace(old,old+" assert(r('MaaaLength')<=160,'Actual original maximum neck length')\n",1)
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='supermaaa'):
    return dict(ROM_SHA256=PIN,controller_SHA256=digest(controller(raw,key).encode()),factory_SHA256=digest(Path(__file__).read_bytes()),
        foundation=Current.foundation(raw),readonly_control_reference=BASE_SHA,actual_return_owner='MarioSourceMovement',
        scope='Source-qualified real M/60/1000/+25 prefix for F/S/L; historical nativeM retained, no extra standalone nativeM requested',
        outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def family():return SimpleNamespace(W=W,N=N,controller=controller,metadata=metadata)
