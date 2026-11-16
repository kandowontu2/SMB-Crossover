"""Depart the fourth rising helper only on its actual downward half-cycle."""
from hashlib import sha256
import json
from pathlib import Path

import replay_dkjr_earlier_fourth_cap_root_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

C = Previous.C
PARENT_SHA = '4eb854c58cd1f8271c52e8040584f4fa83b4c348bb64d4e94c031ea3331a9640'
H = lambda data: sha256(data).hexdigest()


def controller(raw, *, source=False):
    assert H(Path(Previous.__file__).read_bytes()) == PARENT_SHA
    base = Previous.controller(raw, source=source)
    old = '   if player>=edge and grounded and up-32==y and up>=cap-6 and up<=cap then'
    new = '   if player>=edge and grounded and up-32==y and up>=cap-6 and up<=cap and(index~=4 or priorTop[u]and up>priorTop[u])then'
    assert base.count(old) == 1
    text = base.replace(old, new, 1)
    assert text.replace(new, old, 1) == base
    LuaRuntime().compile(text)
    assert not any(x in text for x in ('emu.write', 'emu.setState', 'io.open', 'takeScreenshot', 'saveState', 'loadState'))
    return text


if __name__ == '__main__':
    raw, _ = C.proposal(C.BT.ROM.read_bytes())
    text = controller(raw)
    print(json.dumps(dict(factory_SHA256=H(Path(__file__).read_bytes()), Lua_SHA256=H(text.encode()),
                          candidate_SHA256=H(raw), exact_parent_control_restoration=True,
                          game_bytes_changed=0, helpers_changed=0, outputs=0)))
