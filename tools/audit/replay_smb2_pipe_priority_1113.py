"""Pure unchanged ordinary Imajin route for the separately pinned successor."""
from hashlib import sha256
import json

import compose_smb2_pipe_priority_1113 as C
import replay_smb2_foot_mirror_1113 as Parent


def controller(raw,variant=4):
    assert sha256(raw).hexdigest()==C.CANDIDATE
    before=C.inverse(raw);text=Parent.controller(before,variant)
    if variant==4:assert sha256(text.encode()).hexdigest()=='a6e3fefaadbec7398f11b60fc10475414db57fbf534047e26d5670444fea9276'
    assert text.count(C.PIN)==1
    text=text.replace(C.PIN,C.CANDIDATE)
    Parent.Flag.Root.Base.LuaRuntime().compile(text)
    return text


if __name__=='__main__':
    parent7=C.Check.F.load_input();parent=C.Mirror.all_mirrors_proposal(C.Mirror.Flag.proposal(parent7)[0])[0]
    image,_=C.proposal(parent);text=controller(image)
    print(json.dumps(dict(ROM_SHA256=C.CANDIDATE,controller_SHA256=sha256(text.encode()).hexdigest(),
        ordinary_inputs_and_full_exit_assertions_unchanged=True,outputs=0,Mesen_run=False)),flush=True)
