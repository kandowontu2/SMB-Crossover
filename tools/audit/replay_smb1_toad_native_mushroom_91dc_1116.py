"""Corrected current native Toad counters and actual-row firstM controls."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import current_smb1_toad_native_stock_91dc_1116 as Current
import replay_smb1_toad_mushroom_91dc_1116 as Previous

R,ROM,PIN,W,N,digest=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.digest
BASE_SHA='5809a065450523676ac780c78ff5ab40f7a1a659d91d1d281540de479ba0c3da'
CONTROL=R/'tools/playthroughs/smb1_toad_native_mushroom_controls_91dc_1116.lua'


@lru_cache(maxsize=1)
def controller(raw,key='toad'):
    assert key=='toad'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    config=dict(Current.bindings(raw));h=config['hooks']['BmNativeMovement']
    config['movement_hex']=raw[16+h['offset']:16+h['offset']+64].hex()
    _,body=Previous.controller(raw,key).split('\n',1)
    assert body.count("hook('MarioSourceMovement',function()")==1
    body=body.replace("hook('MarioSourceMovement',function()","hook('BmNativeMovement',function()",1)
    assert body.count('C.hooks.MarioSourceMovement')==2
    body=body.replace('C.hooks.MarioSourceMovement','C.hooks.BmNativeMovement')
    marker='local function drive()\n';assert body.count(marker)==1
    body=body.replace(marker,'local firstM=(function()\n'+CONTROL.read_text()+'\nend)()\n'+marker,1)
    assert body.count('buttons=travel(context())')==1
    body=body.replace('buttons=travel(context())','buttons=firstM(context())',1)
    body=body.replace('Mario_entries=guestEntries,Mario_returns=guestReturns','ToadNative_entries=guestEntries,ToadNative_returns=guestReturns')
    body=body.replace('returned Mario movements','returned native Toad movements')
    text='local C='+Previous.Text.lua(config)+'\n'+body;Previous.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='toad'):
    return dict(ROM_SHA256=PIN,controller_SHA256=digest(controller(raw,key).encode()),factory_SHA256=digest(Path(__file__).read_bytes()),
        control_SHA256=digest(CONTROL.read_bytes()),foundation=Current.foundation(raw),
        retained_wrong_profile_control_negative='834bbe29dcdf05ffdee833bb583dad6ebb597f5b7662753a520c188b9a0b4cf3',
        original_60tick_score_and25_assertions_retained=True,outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def family():return SimpleNamespace(W=W,N=N,controller=controller,metadata=metadata)
