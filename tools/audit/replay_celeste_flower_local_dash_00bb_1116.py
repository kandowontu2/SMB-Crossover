"""Current natural Flower, then a local ordinary descent and earned dash.

The frozen v8 travel negative reaches a real Goomba before finding a safe dash.
This successor changes only post-credit25 inputs: step left off the earned
Flower row, stop on the native floor, and fresh Right+B on the measured runway.
"""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_celeste_flower_00bb_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='84f7b18bf4d97d18d8f47bf024d8e3ef2f2757ca15f8c1b10ced88ca6a11b1b6'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower' and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    c=deepcopy(Previous.bindings(raw));_,body=Previous.controller(raw).split('\n',1)
    old=' local c=context();buttons=flowerPolicy(c)'
    new=""" local c=context()
 if not stock.flower_scope_passed then buttons=flowerPolicy(c)
 else
  assert(r('CmTier')==2 and r('PlayerStatus')==2,'Retain real earned Flower during local dash controls')
  if not dash.control_phase then dash.control_phase='drop-left';dash.descent={request=state(),camera=c.camera}end
  assert(moves-dash.since<220,'Bounded local ordinary descent/dash')
  if dash.control_phase=='drop-left'then
   if c.grounded and c.yHigh==1 and c.y>=176 then
    dash.descent.landed=state();dash.control_phase='brake';buttons={}
   else buttons={left=true}end
  elseif dash.control_phase=='brake'then
   buttons={}
   if c.grounded and c.vx==0 and r('CmPreviousAB')&64==0 and r('TimerControl')==0 then
    dash.descent.braked=state();dash.control_phase='dash';buttons={right=true,b=true}
   end
  else buttons={right=true}end
 end"""
    assert body.count(old)==1;body=body.replace(old,new,1)
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw)
    q.update(factory_SHA256=digest(Path(__file__).read_bytes()),controller_SHA256=digest(controller(raw).encode()),
        parent_flower_factory_SHA256=BASE_SHA,scope='Actual00bb unchanged genuine M/F/1000/25; local left drop, native-floor brake and original fresh Right+B dash with measured112px runway/no enemy96, real stock/State6/Timer12 and returned Dash motion16px',
        post_F_inputs_only_changed=True)
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
