"""Ordinary pipe5-depart enemy hop over frozen backward-stair current route."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_dkjr_backward_stairs_current_root_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

C=Previous.Previous.C
ABILITY_SHA=Previous.ABILITY_SHA
PARENT_FACTORY_SHA='ad2cbcb51948b73d7ef5068a3308aa02c6e98d240edb1662186b911b6fd060dd'
H=lambda value:sha256(value).hexdigest()
OLD=" if phase=='pipe5-depart'then\n  right=true\n"
NEW=""" if phase=='pipe5-depart'then
  right=true
  local priorHold=hold
  if ram(2,0x14)&128==0 then hopPastEnemy(2704)end
  if hold~=priorHold then
   events[#events].defense='pipe5-depart'
   events[#events].actors=approachActors()
   events[#events].source_y=ram(2,0x210)
   events[#events].origin=ram(2,0x76);events[#events].limit=ram(2,0x7b)
  end
"""


@lru_cache(maxsize=2)
def controller(raw,*,source=False):
    assert H(raw)==C.CANDIDATE
    assert H(Path(Previous.__file__).read_bytes())==PARENT_FACTORY_SHA
    base=Previous.controller(raw,source=source)
    assert base.count(OLD)==1
    text=base.replace(OLD,NEW,1)
    assert text.count(NEW)==1 and text.replace(NEW,OLD,1)==base
    LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text


def restore(text):
    assert text.count(NEW)==1
    return text.replace(NEW,OLD,1)
