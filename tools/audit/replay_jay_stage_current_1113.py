"""Bind the retained Jay full-stage controller to the private head successor."""

import argparse
from hashlib import sha256
import json

import compose_jay_head_bridge_1113 as P


def controller(raw):
    assert sha256(raw).hexdigest() == P.CANDIDATE_PIN
    source = P.B.Gun.controller()
    assert sha256(source.encode()).hexdigest() == 'e40a2a03ce87a0d28d5a2527d6c6613ba20395153b44101d250e6cf335a6d200'
    edits = (
        ("local cookie=assert(os.getenv('SMB_JAY_COOKIE'))",f"local cookie='{P.NEW_COOKIE.hex()}'"),
        ("local variant=tonumber(os.getenv('SMB_TEST_VARIANT') or '0')","local variant=2"),
        ("local donorFlags=tonumber(os.getenv('SMB_JAY_DONOR_FLAGS') or '0')","local donorFlags=49170"),
        ("cookie:sub(1,6)=='a71020'",f"cookie=='{P.NEW_COOKIE.hex()}'"),
    )
    for before,after in edits:
        assert source.count(before) == 1,before
        source = source.replace(before,after)
    return source


def cpu_route(raw):
    """Actual menu/Main route; no actor, position or source-state injection."""
    assert sha256(raw).hexdigest() == P.CANDIDATE_PIN
    B,Motion = P.B,P.B.Gun.T.Motion
    bundle = dict(B.Current.W.Symbols.bundle(),raw=raw)
    model = B.Gun.C.menu(bundle,1)
    for tick in range(220):
        if tuple(B.Current.N.get(model,n)for n in Motion.STATES) == (1,3,8):
            break
        model.controller_pad=0
        B.Current.Frames.frame(model)
    else:
        raise AssertionError('Current Jay stage ingress')
    assert B.Gun.C.Common.headers(model) == (P.NEW_COOKIE,)*2
    assert model.ram[2][0x33:0x35] == b'\0\0'
    import check_jay_silius_helpers_1111 as Helpers
    helper,_ = Helpers.assemble(bundle,origin=0xbd20)
    body=helper['images']['HELPERS']
    assert bytes(model.ram[3][0x1d20:0x1d20+len(body)]) == body
    work,fields = Motion.assemble_handoff(bundle,bytes(model.ram[3][0x88d:0x8c0]),origin=0xb800,
        control_tail=True,native_sync=True,native_helpers=(helper['symbols']['StepHelpers'],helper['symbols']['ResetHelpers']),
        pit_boundary=True)
    work.update(tile=B.Gun.C.Jay.build()['symbols']['JayHostTile'],status=0xc0f3)
    early=Motion.assisted_route(model,fields,work)
    assert early['lives']==2 and early['terminal']==(995,176,883)
    assert [v['pipe']for v in early['carry']]==[3,4]
    late=Motion.late_route(model,fields,middle_hold=2)
    assert late['lives']==2 and late['scene'][3]==1 and len(late['gap_landings'])==3,late
    assert any(v[1]=='scene' and v[3]==(1,3,4,0) for v in late['events'])
    assert any(v[1]=='scene' and v[3]==(1,3,5,0) for v in late['events'])
    for entrance in range(550):
        if tuple(B.Current.N.get(model,n)for n in Motion.STATES)==(1,3,8) and B.Current.N.get(model,'LevelNumber')==1:
            if B.Current.N.get(model,'Player_State')==0 and B.Current.N.get(model,'Player_Y_Position')==176:
                break
        model.controller_pad=0
        B.Current.Frames.frame(model)
    else:
        raise AssertionError(('Current Jay 1-2 entry',P.B.Current.state(model)))
    assert model.ram[2][0xbf]==3 and model.ram[2][0x20]==0 and model.ram[2][0xbe]==63
    return dict(actual_menu=True,actor_or_position_injection=False,early=early,late=late,entrance_wait=entrance,
                terminal=P.B.Current.state(model),scope='CPU route only; generated native controller is separately retained logic')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cpu-route',action='store_true')
    args=parser.parse_args()
    installed=P.B.Current.ROM.read_bytes()
    image=installed if sha256(installed).hexdigest()==P.CANDIDATE_PIN else P.proposal(installed)[0]
    text=controller(image)
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    print(json.dumps(dict(ROM_SHA256=P.CANDIDATE_PIN,script_SHA256=sha256(text.encode()).hexdigest(),
        compiles=True,output_files=0,native_pending=True)),flush=True)
    if args.cpu_route:
        print(json.dumps(cpu_route(image)),flush=True)
