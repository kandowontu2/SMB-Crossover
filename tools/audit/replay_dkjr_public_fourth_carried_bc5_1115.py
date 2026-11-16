"""Adopt an actual fourth-helper ride before the old special roof jump wait."""
from hashlib import sha256
import replay_dkjr_public_early_depart_bc5_1115 as Prior

BASE = 'b09c91e99c79b0889305c74cfb4f175cc3adb1c10198e35d64463be14d72ff83'
OLD = ''' if phase=='roof'and index==4 then
  right=player<d-4
  if player>=d-4 and grounded and down and priorTop[d] and down>=101 and down<=114 and down>priorTop[d]then
   hold=updates+8;right=true;setPhase('jump-down',down)
  end
 elseif phase=='roof'and carried(d,down)then
  setPhase('lower',down)
'''
NEW = ''' if phase=='roof'and carried(d,down)then
  setPhase('lower',down)
  if index==4 then
   remember('fourth-actual-ride-adopted',down)
   events[#events].last_actual_carry=carries[tostring(d)].last
   events[#events].source_y=ram(2,0x210);events[#events].origin=ram(2,0x76);events[#events].limit=ram(2,0x7b)
  end
 elseif phase=='roof'and index==4 then
  right=player<d-4
  if player>=d-4 and grounded and down and priorTop[d] and down>=101 and down<=114 and down>priorTop[d]then
   hold=updates+8;right=true;setPhase('jump-down',down)
  end
'''


def controller(raw):
    base = Prior.controller(raw, grounded12=True)
    assert sha256(base.encode()).hexdigest() == BASE
    assert base.count(OLD) == 1
    text = base.replace(OLD, NEW, 1)
    assert text.replace(NEW, OLD, 1) == base
    Prior.Ground.LuaRuntime().compile(text)
    return text
