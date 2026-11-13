"""Exact unchanged flag/stage controls for the all-mirror private candidate."""
from hashlib import sha256
import json

import compose_smb2_foot_mirror_1113 as C
import replay_smb2_flag_handoff_1113 as Flag


def controller(raw,variant=4):
    assert sha256(raw).hexdigest()==C.ALL_IMAGES[C.PARENTS[1]]
    parent=C.all_mirrors_inverse(raw)
    assert sha256(parent).hexdigest()==Flag.CANDIDATE
    text=Flag.controller(parent,variant)
    if variant==4:assert sha256(text.encode()).hexdigest()=='09c0f838b1c8f592d7a470f51892cafe03227dbd898e5c1b61d317fc1873c453'
    assert text.count(Flag.CANDIDATE)==1
    text=text.replace(Flag.CANDIDATE,C.ALL_IMAGES[C.PARENTS[1]])
    Flag.Root.Base.LuaRuntime().compile(text)
    return text


if __name__=='__main__':
    parent=C.Flag.proposal(C.Flag.Check.ROM.read_bytes())[0]
    image,_=C.all_mirrors_proposal(parent);text=controller(image)
    print(json.dumps(dict(ROM_SHA256=sha256(image).hexdigest(),controller_SHA256=sha256(text.encode()).hexdigest(),
        ordinary_controls_and_exit_assertions_unchanged=True,outputs=0,Mesen_run=False)),flush=True)
