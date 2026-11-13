"""Pure original route; only the exact foreground-successor ROM label differs."""
from hashlib import sha256
import json

import compose_smb2_pipe_foreground_1113 as C
import replay_smb2_pipe_priority_1113 as Parent


def controller(raw,variant=4):
    assert sha256(raw).hexdigest()==C.CANDIDATE
    before=C.inverse(raw);text=Parent.controller(before,variant)
    if variant==4:assert sha256(text.encode()).hexdigest()=='f4b9ebfaee4cd75245ecd3cb0e38b5d4ab6c00127fc2a9f125270448a5ddf5cc'
    assert text.count(C.PIN)==1
    text=text.replace(C.PIN,C.CANDIDATE)
    Parent.Parent.Flag.Root.Base.LuaRuntime().compile(text)
    return text


def visual_controller(raw,variant=4):
    """Same two passive root views, plus the visible normal attribute gate."""
    import replay_smb2_priority_visual_1113 as Visual
    assert sha256(raw).hexdigest()==C.CANDIDATE
    text=Visual.controller(C.inverse(raw),variant)
    assert text.count(C.PIN)==1
    text=text.replace(C.PIN,C.CANDIDATE)
    needle="local function priorityShot(tag)\n"
    assert text.count(needle)==1
    text=text.replace(needle,needle+" if tag=='underground_grounded'then assert(read(priorityAttributeAddress)==0,'Normal visible foreground priority cleared')end\n")
    Parent.Parent.Flag.Root.Base.LuaRuntime().compile(text)
    return text


if __name__=='__main__':
    before=C.Check.parent(C.Check.F.load_input());image,_=C.proposal(before);text=controller(image)
    print(json.dumps(dict(ROM_SHA256=C.CANDIDATE,controller_SHA256=sha256(text.encode()).hexdigest(),
        visual_controller_SHA256=sha256(visual_controller(image).encode()).hexdigest(),
        ordinary_inputs_and_all_full_exit_assertions_unchanged=True,outputs=0,Mesen_run=False)),flush=True)
