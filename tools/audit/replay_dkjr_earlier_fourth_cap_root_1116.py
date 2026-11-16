"""Ordinary fourth-pipe jump from an earlier edge and real source cap support."""
from hashlib import sha256
import json
from pathlib import Path

import replay_dkjr_pipe5_depart_defense_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

C = Previous.C
PARENT_SHA = '8716f225c58f2848f931d836c03798012fc29382e3fc5297ec2435c27d76ac58'
H = lambda data: sha256(data).hexdigest()


def controller(raw, *, source=False):
    assert H(raw) == C.CANDIDATE and H(Path(Previous.__file__).read_bytes()) == PARENT_SHA
    base = Previous.controller(raw, source=source)
    old_ground = ' local grounded=ram(2,0x6b)==1 and (read(0x1e)==0 or carried(u,up)or carried(d,down))'
    new_ground = ''' -- Donor source1 can stand on a real pipe while native state2 persists.
 -- Require the actual cap height and full-height static contact, not a
 -- helper plane or the sliver at the pipe's far edge.
 local rootCapCamera=ram(2,0x435)+256*ram(2,0x436)
 local rootCapLeft=ram(2,0x42)+rootCapCamera
 local rootCapRight=ram(2,0x44)+rootCapCamera
 local rootOnCap=index==4 and ram(2,0x6b)==1 and y==cap-32
   and ram(2,0x210)==cap-17 and player>=pipe+4 and player<=pipe+30
   and ram(2,0x43)==cap and ram(2,0x45)==cap+15
   and rootCapLeft>=pipe and rootCapLeft<pipe+32 and rootCapRight<=pipe+32
 if rootOnCap and not rootCapSeen then
  rootCapSeen=true;remember('earlier-fourth-real-cap')
  events[#events].contact={ram(2,0x42),ram(2,0x43),ram(2,0x44),ram(2,0x45)}
  events[#events].cached_camera=rootCapCamera
 end
 local grounded=ram(2,0x6b)==1 and (read(0x1e)==0 or carried(u,up)or carried(d,down)or rootOnCap)'''
    edits = [("local phase,index='approach',1", "local phase,index='approach',1\nlocal rootCapSeen=false"),
             ('   local edge=u+29', '   local edge=u+(index==4 and 17 or 29)'),
             (old_ground, new_ground)]
    text = base
    for old, new in edits:
        assert text.count(old) == 1, old
        text = text.replace(old, new, 1)
    restored = text
    for old, new in reversed(edits):
        assert restored.count(new) == 1
        restored = restored.replace(new, old, 1)
    assert restored == base
    LuaRuntime().compile(text)
    assert not any(x in text for x in ('emu.write', 'emu.setState', 'io.open', 'takeScreenshot', 'saveState', 'loadState'))
    return text


if __name__ == '__main__':
    parent = C.BT.ROM.read_bytes()
    raw, _ = C.proposal(parent)
    text = controller(raw)
    print(json.dumps(dict(factory_SHA256=H(Path(__file__).read_bytes()), Lua_SHA256=H(text.encode()),
                          candidate_SHA256=H(raw), exact_parent_control_restoration=True,
                          game_bytes_changed=0, helpers_changed=0, outputs=0)))
