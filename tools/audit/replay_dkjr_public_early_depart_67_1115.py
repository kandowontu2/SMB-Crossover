"""Ordinary enemy hop during pipe3 departure; unchanged public67 game bytes."""
from hashlib import sha256
import replay_dkjr_public_cap_depart_67_1115 as Prior

Old = Prior.Old
BASE = '5c65a62251a0613e0c072087cc81f94716426e037c3ae9618d59e3415ddd9ffa'

LOWER_OLD = '''  elseif index~=4 and player>=leave and grounded and down-32==y and down>=192 and down<=208 and priorTop[d]and down>=priorTop[d]then
   setPhase('depart',down)
  end
'''
LOWER_NEW = '''  elseif index~=4 and player>=leave and grounded and down-32==y and down>=192 and down<=208 and priorTop[d]and down>=priorTop[d]then
   setPhase('depart',down)
  elseif index==3 and player>=leave and grounded and read(0x1e)==0 and y==176
    and ram(2,0x210)==191 and down>=212 then
   setPhase('depart',down);remember('third-static-ground-depart',down)
  end
'''
DEPART_OLD = " if phase=='depart'then\n  right=true\n"
DEPART_NEW = ''' if phase=='depart'then
  right=true
  if index==3 and grounded and y>=160 and y<=176 and updates>=rearm and nearEnemy(player)then
   hold=updates+8;rearm=updates+47;remember('third-depart-enemy-hop',down)
   events[#events].actors=approachActors();events[#events].source_y=ram(2,0x210)
   events[#events].origin=ram(2,0x76);events[#events].limit=ram(2,0x7b)
  end
'''


def controller(raw):
    base = Prior.controller(raw)
    assert sha256(base.encode()).hexdigest() == BASE
    assert base.count(LOWER_OLD) == base.count(DEPART_OLD) == 1
    text = base.replace(LOWER_OLD, LOWER_NEW, 1).replace(DEPART_OLD, DEPART_NEW, 1)
    assert text.replace(LOWER_NEW, LOWER_OLD, 1).replace(DEPART_NEW, DEPART_OLD, 1) == base
    Prior.Prior.LuaRuntime().compile(text)
    return text
