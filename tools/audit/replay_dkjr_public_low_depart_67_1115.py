"""Ordinary first-pipe descending departure; public67 game bytes unchanged."""
from hashlib import sha256
import recover_dkjr_current_identity_67_1115 as Old
from check_ff_stdout_controller_source_1110 import LuaRuntime

BASE = '43b51e99c2e05c101a697f35bbf4a154deb6a3a3b4edf455f58bf586badb500d'

OLD_RISE = ''' if phase=='rise'and up then
  local edge=u+(index==1 and 23 or 29)
  right=player<edge
  if player>=edge and grounded and up-32==y and up>=cap-6 and up<=cap then
   hold=updates+8
   setPhase('cross',up)
  end
 end
'''

NEW_RISE = ''' if phase=='rise'and up then
  if index==1 then
   -- X446 remains inside the stock416..447 footprint, with poll margin.
   local edge=u+30
   right=player<edge
   local descending=priorTop[u]and up>priorTop[u]
   if player>=edge-1 and player<=edge+1 and carried(u,up)and grounded
     and up-32==y and descending and up>=154 and up<=160 then
    assert(cap-up<ram(2,0x7b),'First-pipe departure retains original safe fall distance')
    hold=updates;right=true
    setPhase('cross',up);remember('pipe1-low-depart',up)
    events[#events].source_y=ram(2,0x210);events[#events].origin=ram(2,0x76)
    events[#events].limit=ram(2,0x7b);events[#events].predicted_drop=cap-up
   end
  else
   local edge=u+29
   right=player<edge
   if player>=edge and grounded and up-32==y and up>=cap-6 and up<=cap then
    hold=updates+8
    setPhase('cross',up)
   end
  end
 end
'''


def controller(raw):
    text = Old.controller(raw, kind='delivered-public-67')
    assert sha256(text.encode()).hexdigest() == BASE
    assert text.count(OLD_RISE) == 1
    text = text.replace(OLD_RISE, NEW_RISE, 1)
    assert text.replace(NEW_RISE, OLD_RISE, 1) == Old.controller(raw, kind='delivered-public-67')
    LuaRuntime().compile(text)
    return text
