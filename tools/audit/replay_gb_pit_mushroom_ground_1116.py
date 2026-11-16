"""Separate ordinary ground-return successor; frozen first policy retained."""
from pathlib import Path
from functools import lru_cache
from types import SimpleNamespace
from copy import deepcopy
import replay_gb_pit_mushroom_1116 as Previous

R,ROM,W,N,H,Current=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='99e599f96ea955ac6b6ae3d2a23bc11b0c31e9dd0124898bf5aa23a7f7184e01'
CONTROL=R/'tools/playthroughs/gb_pit_mushroom_ground_controls_1116.lua'
OBSERVER=r'''
local gbHeadPending
hook('PlayerHeadCollision',function()
 if not menuDone or food.born then return end
 local s=state();if s.x<304 or s.x>352 or s.y>=176 then return end
 assert(not gbHeadPending,'Actual head call is synchronous')
 local z=emu.getState();local q={PC=z['cpu.pc'],SP=z['cpu.sp'],A=z['cpu.a'],X=z['cpu.x'],Y=z['cpu.y'],state=s,saved=r('SavedJoypadBits')}
 food.actual_head=q;gbHeadPending=returning(function(t)q.returned={PC=t.pc,SP=t.sp,state=state()};gbHeadPending=nil end)
end)
hook('SetupPowerUp',function()
 if not gbHeadPending or food.born then return end
 local z=emu.getState();food.actual_head_setup={PC=z['cpu.pc'],SP=z['cpu.sp'],A=z['cpu.a'],X=z['cpu.x'],Y=z['cpu.y'],state=state(),inside_actual_head=true}
end)
'''

@lru_cache(maxsize=1)
def bindings(raw):
    q=deepcopy(Previous.bindings(raw));b=Current.bindings(raw)['bundle']
    for name in('PlayerHeadCollision','SetupPowerUp'):q['hooks'][name]=Current.hook(b,name,8)
    return q

@lru_cache(maxsize=1)
def controller(raw,key='mushroom'):
    assert key=='mushroom'and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    _,body=Previous.controller(raw,key).split('\n',1);old=Previous.CONTROL.read_text();assert body.count(old)==1
    body=body.replace(old,CONTROL.read_text(),1)
    old="if stopped then return end;stopped=true;buttons={}"
    new="if stopped then return end;if ok then assert(food.actual_head_setup and food.actual_head and food.actual_head.returned,'Actual native head→M setup, not an arrow substitute')end;stopped=true;buttons={}"
    assert body.count(old)==1;body=body.replace(old,new,1)
    text='local C='+Previous.Text.lua(bindings(raw))+'\n'+body+'\n'+OBSERVER;Previous.LuaRuntime().compile(text)
    assert not any(v in text for v in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text

def metadata(raw,key='mushroom'):
    q=Previous.metadata(raw,key);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,key).encode()),
        control_SHA256=H(CONTROL.read_bytes()),parent_factory_SHA256=BASE_SHA,hooks=bindings(raw)['hooks'],all_original_item_and_return_assertions_preserved=True,
        retained_first_policy_negative='a7bf8e007d895f75bc44dc69c7cadc22b6dccf7c3e3ad64f4c45f2dcd3485783',
        retained_clearX_guard_negative='5f71fb22b18a5683196e0a492c28406bd2f3d36ff721248c0758745cf8d92931',
        control_delta='Retained Pit bow/travel, actual ground/support takes priority over obsolete clearX threshold, camera readback and freshA; actual native head→SetupPowerUp witness; no gameplay seeds');return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
