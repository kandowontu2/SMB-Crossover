"""Pure full-stage controller binding for the private native flag candidate."""
from hashlib import sha256
import argparse
import json

import compose_smb2_flag_handoff_1113 as C
import replay_smb2_stage_current_1113 as Root

BASE='6371ab8df461a9a347ad6baf5f7f3d84de78fa1472af4a49d73b98574958231e'
CANDIDATE='0e9e9254927236bcc651e79da36a77924eea5481421858a05f869b15298412e1'


def controller(raw,variant=4):
    assert 0<=variant<8 and sha256(raw).hexdigest()==CANDIDATE
    parent=C.inverse(raw)
    flags=dict(jump_hold=24,enemy_gap=48,source_edges=True,injury_trace=True,last_pit_settle=True,runup=True)
    text=Root.controller(parent,4,**flags);assert sha256(text.encode()).hexdigest()==BASE
    point='local identity,expectedRom,gameOffset,attrs=4,';assert text.count(point)==1
    text=text.replace(point,f'local identity,expectedRom,gameOffset,attrs={variant},')
    assert text==Root.controller(parent,variant,**flags)
    assert text.count(C.PIN)==1
    text=text.replace(C.PIN,CANDIDATE)
    Root.Base.LuaRuntime().compile(text)
    assert all(word not in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--variant',type=int,choices=range(8),default=4);args=p.parse_args()
    image,_=C.proposal(C.Check.load_input());text=controller(image,args.variant)
    print(json.dumps(dict(ROM_SHA256=CANDIDATE,variant=args.variant,identity=Root.NAMES[args.variant],
        controller_SHA256=sha256(text.encode()).hexdigest(),base_control_SHA256=BASE,
        controls_unchanged=True,Lua_compile=True,outputs=0,Mesen_run=False)),flush=True)
