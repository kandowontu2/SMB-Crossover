"""Ordinary input successor: find each real fixed girder, not newest-slot cache."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_oneup_1327_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='12274f44fbc40de6a2f336627133d26977e49194dc2bf102bb8abc28f7c4fe16'


@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup'and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw)
    old=' local slot = ram(0xc30b)-1\n'
    new=""" local cached=ram(0xc30b)-1;local slot=-1
 for i=0,5 do
  if read(L.Enemy_Flag+i)==1 and read(L.Enemy_ID+i)==0x25 and read(L.Enemy_X_Position+i)+256*read(L.Enemy_PageLoc+i)==left then slot=i;break end
 end
 if slot>=0 and slot~=cached and not route.first_cache_difference then route.first_cache_difference={state=state(),expected_left=left,actual_slot=slot,cached_slot=cached,actual_actor=actor(slot),cached_actor=cached>=0 and cached<6 and actor(cached)or nil}end
"""
    assert text.count(old)==1;text=text.replace(old,new,1);LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text


def metadata(raw,key='oneup'):
    q=Previous.metadata(raw);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw).encode()),parent_L_factory_SHA256=BASE_SHA,
        scope='Same genuine M/hiddenL controls except real flagged native25 girder lookup by required world-left; actor cache mismatch recorded. Mature wholeC1/INC/cue64/+25 original+public returns unchanged')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
