"""Strict82e8 facade for the frozen06336/656c DK Mushroom proposal.

Memory-only composition, linked controllers and compact stdout receipts.
Neither an emulator nor a ROM/output writer is available here.
"""
import argparse
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
import io
import json

import compose_scrooge_prepare_stack_1123 as Scrooge
import compose_dkjr_mushroom_helper_1123 as Old
import check_dkjr_mushroom_helper_1123 as Check

H=Old.H
PIN=Scrooge.CANDIDATE
CANDIDATE='3b7b36cad368c89165b37892c3fd9110a1362b6c2579c17a1cad8cf5115cf289'
OLD_COMPOSER='150b46ee9edc990ee20db876de3d30870814a479a943618ef7353e37bca69f56'
OLD_CHECKER='7e841eb418f77e7fcfbc0d9a6885825ae6110856293c2dd6d16de520b6b9f1cc'
old_controller=Check.controller


def pins():
    assert H(Path(Old.__file__).read_bytes())==OLD_COMPOSER
    assert H(Path(Check.__file__).read_bytes())==OLD_CHECKER


def proposal(parent):
    pins()
    assert isinstance(parent,bytes) and H(parent)==PIN and len(parent)==2097168
    original=Scrooge.inverse(parent)
    assert H(original)==Old.PIN and Scrooge.proposal(original)[0]==parent
    frozen,old_info=Old.proposal(original)
    dk_changed={i for i,(a,b) in enumerate(zip(original,frozen,strict=True)) if a!=b}
    scrooge_changed={i for i,(a,b) in enumerate(zip(original,parent,strict=True)) if a!=b}
    scrooge_owned=set(range(Scrooge.offset(0xba1d),Scrooge.offset(0xbaaa)))
    dk_owned=set(range(Old.Head.COOKIE_AT,Old.Head.COOKIE_AT+16))
    for name,(pc,_) in Old.LAYOUT.items():
        for at,data in Old.chunks(pc,Old.old_images()[name]):dk_owned.update(range(at,at+len(data)))
    assert len(dk_changed)==39 and not dk_owned&scrooge_owned and scrooge_changed<=scrooge_owned
    out=bytearray(parent)
    for i in dk_changed:out[i]=frozen[i]
    result=bytes(out)
    independent=bytearray(frozen)
    for i in scrooge_changed:independent[i]=parent[i]
    assert bytes(independent)==result and {i for i,(a,b) in enumerate(zip(parent,result,strict=True)) if a!=b}==dk_changed
    assert Old.Head.payload(result)==Old.Head.payload(frozen)
    if CANDIDATE is not None:assert H(result)==CANDIDATE
    return result,dict(parent_SHA256=PIN,candidate_SHA256=H(result),
        frozen_parent_SHA256=Old.PIN,frozen_candidate_SHA256=Old.CANDIDATE,
        changed_bytes=39,complete_owner_envelopes_disjoint=True,
        independent_composition_commutes=True,Scrooge_file_extent=[min(scrooge_owned),max(scrooge_owned)+1],
        inherited_helper=old_info['added_helper'],outputs=0,native_qualified=False)


def inverse(candidate):
    assert CANDIDATE is not None and H(candidate)==CANDIDATE
    out=bytearray(candidate)
    for name,(pc,_) in Old.LAYOUT.items():
        for at,data in Old.chunks(pc,Old.old_images()[name]):out[at:at+len(data)]=data
    out[Old.Head.COOKIE_AT:Old.Head.COOKIE_AT+16]=Old.PARENT_COOKIE
    parent=bytes(out)
    assert H(parent)==PIN and proposal(parent)[0]==candidate
    return parent


def controller(raw,*,cutoff=180,route=False):
    parent=inverse(raw)
    frozen,_=Old.proposal(Scrooge.inverse(parent))
    text=old_controller(frozen,cutoff=cutoff,route=route)
    assert text.count(Old.CANDIDATE)==1
    rebound=text.replace(Old.CANDIDATE,H(raw),1)
    assert rebound.replace(H(raw),Old.CANDIDATE,1)==text
    Check.LuaRuntime().compile(rebound)
    return rebound


def full_controller(raw):
    """The current qualified full-route factory, with only layout bindings."""
    import compose_dkjr_side_epoch_fast_1123 as Fast
    import compose_dkjr_public_side_forward_1123 as Side
    import compose_dkjr_sonic_dispatch_1123 as Combined
    import compose_sonic_current_auth_epoch_1122 as Sonic
    import repair_rogue_side_pipe_1123 as Pipe
    import run_dkjr_dispatch_native_1123 as Native
    base=Scrooge.inverse(inverse(raw))
    old=Combined.inverse(Side.inverse(Fast.inverse(Old.Head.inverse(base))))
    reference=Sonic.inverse(Pipe.restore_pipe_bytes(old))
    _,program=Native.prepare_full_stage(reference,raw)
    program=Native.time_final_cap_approach(program)
    program=Native.center_flag_takeoff(program)
    program=Native.backward_flag_takeoff(program)
    text=program.decode()
    once=Check.Replay.one
    if '[336]=128,' in text:text=once(text,'[336]=128,','[336]=188,')
    else:text=once(text,'local centers={','local centers={[336]=188,')
    assert text.count('ram(2,0x8fd)~=8')==2
    text=text.replace('ram(2,0x8fd)~=8','ram(2,0x8fd)~=9')
    text=once(text,"local rom=os.getenv('SMB_STDOUT_ROM_SHA')or''",f'local rom="{H(raw)}"')
    text=once(text,"os.getenv('SMB_TEST_VARIANT')=='0'",'true')
    assert text.count("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'")==2
    text=text.replace("os.getenv('SMB_DKJR_FAST_ROUTE')=='1'",'true')
    text=once(text,"emu.addEventCallback(guarded('input',function()",
        "if CPU_CONTROLLER_OPENING then frame=541;playing=true end\nemu.addEventCallback(guarded('input',function()")
    assert not any(q in text for q in ('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    Check.LuaRuntime().compile(text)
    return text


def baseline(raw):
    text=full_controller(raw)
    m,opening=Check.Head.cold(raw)
    with patch.object(Check.Route.Frames,'frame',Check.normal_frame):
        with redirect_stdout(io.StringIO()):
            result=Check.Route.route(m,raw,14000,controller_text=text)
    return dict(result,opening_Main=opening,ROM_SHA256=H(raw),scope='Existing full-route controls from ordinary menu/cold, with new336 birth and horizontal ordinal bindings. No Mushroom-controller overlay or gameplay RAM writes.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('compose','neighbors','route','baseline'),default='compose')
    args=p.parse_args()
    raw,q=proposal(Old.M.ROM.read_bytes())
    print('DK M SCROOGE COMPOSE '+json.dumps(q,separators=(',',':')),flush=True)
    if args.mode=='compose':return
    cases=(180,182,184) if args.mode=='neighbors' else (180,)
    for cutoff in cases:
        if args.mode=='baseline':result=baseline(raw)
        else:
            with patch.object(Check,'controller',controller):
                result,_=Check.first_mushroom(raw,cutoff=cutoff,route=args.mode=='route')
        result['facade_SHA256']=H(Path(__file__).read_bytes())
        receipt=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
        if args.mode!='baseline':result.pop('receipt',None)
        print('DK M SCROOGE RESULT '+json.dumps(result,separators=(',',':')),flush=True)
        print('RECEIPT '+receipt,flush=True)
        assert result['passed']


if __name__=='__main__':main()
