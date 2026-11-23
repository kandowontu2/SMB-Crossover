"""Join exact installed draw27e and qualified private Flower32bf in memory.

Default binds/compiles both controllers without files. Root --run serially
tests full1-1 and the natural Flower in the existing two-file slot, restoring
both original files. No Downloads writer, backup or game-asset copy exists.
"""
import argparse
from contextlib import ExitStack,contextmanager
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import run_dkjr_flower_native_1123 as Native
import run_dkjr_flower_pipe2_settle_native_1123 as Pickup
import run_dkjr_flower_full_native_1123 as Full
import probe_special_draw_routing_1123 as Draw
import replay_dkjr_early_riser_recovery_1123 as Stairs

S,H=Native.Source,Native.H
BASE=S.PIN
INSTALLED=Draw.CANDIDATE
FLOWER=S.CANDIDATE
CANDIDATE='d1a40df1a70768da51823f93e050141281603f09497d7c2193db4fa088db62b5'
SCRIPTS={
 'full':'c1e590343faecc49c901998bf72cf4a9059176e76c42934160a4058f807ab043',
 'flower':'f311e949029d89751f497a1324bbc7c814ba6532968f7bd8f7b4c2d80122423d',
}
PICKUP_QUALIFIED='57dab4f73213732a112ea5bcc0477c28003bd9d5424d48e3dc5ab2f3bef3310b'
PICKUP_RECEIPT='2ba47e97745e0aeed715f88da5911362e991b80afa5d5ca798149548184e3d29'
DRAW_FULL_QUALIFIED='ea28e38f447e91bae16eb389416e886c5a1e968ef87b48b92fa9409fcbe9bffc'
DRAW_FULL_RECEIPT='6193901229240e9ff9f98ec1bcb282c3763348f731b02be48a40482b16023108'
PINS={
 'run_dkjr_flower_native_1123.py':'adc1832d2c9fc9d4b44d1779d9f604a853e25585a53e9292e9a5aedbb4d2281a',
 'run_dkjr_flower_pipe2_native_1123.py':'725597fda0eccb87ca30789fd24e82d11f09aaca6ac51c4fee319aac044ece73',
 'run_dkjr_flower_pipe2_settle_native_1123.py':'974709d58a13d425eb09314bc2c763e2490099c75dcb7e310668277b20f5cda7',
 'run_dkjr_flower_full_native_1123.py':'ea3a2911af96086251046c800d6b372bfa100ed75b7a71305ced287b184f25d1',
 'probe_special_draw_routing_1123.py':'b51c47b4a116958d944222f0714410f65d83849d4b44c44777a93a5365decdb7',
 'replay_dkjr_early_riser_recovery_1123.py':'f41719e1f1a11243316b72bdadf47d22b3a8ab4f5d01ccdf3a2c634a33f492ee',
 'replay_dkjr_first_riser_recovery_1123.py':'f1c520e55b4dc42601d0a7180c17ef6d916958f76325b3d2abe63aa959d717f5',
}


def pins():
    for name,digest in PINS.items():assert H((Native.R/'tools/audit'/name).read_bytes())==digest,name
    assert H(Path(S.__file__).read_bytes())==Native.SOURCE_SHA
    assert BASE==Draw.PARENT and FLOWER==Full.CANDIDATE


@contextmanager
def cache():
    with Native.recipe_cache(),ExitStack() as stack:
        for name in ('proposal','inverse'):
            stack.enter_context(patch.object(Draw,name,lru_cache(maxsize=4)(getattr(Draw,name))))
        yield


def flower_regions():
    result=[]
    for name,(pc,size)in S.C.LAYOUT.items():
        for at,data in S.C.Old.chunks(pc,bytes(size)):
            result.append((at,at+len(data),'Flower '+name))
    at=S.C.Old.Head.COOKIE_AT;result.append((at,at+16,'Flower cookie'))
    return tuple(result)


def draw_regions():
    return ((Draw.offset(Draw.DRAW_BANK,Draw.ENTRY),Draw.offset(Draw.DRAW_BANK,Draw.ENTRY)+len(Draw.OLD_ENTRY),'draw entry'),
            (Draw.offset(Draw.SPECIAL_BANK,Draw.FAST),Draw.offset(Draw.SPECIAL_BANK,Draw.LIMIT),'draw padding'))


def indices(regions):return {i for lo,hi,_ in regions for i in range(lo,hi)}


def replace_regions(raw,reference,regions):
    result=bytearray(raw)
    for lo,hi,_ in regions:result[lo:hi]=reference[lo:hi]
    return bytes(result)


def proposal(installed):
    pins();assert isinstance(installed,bytes)and H(installed)==INSTALLED
    base=Draw.inverse(installed);assert H(base)==BASE and Draw.proposal(base)[0]==installed
    flower,layout=S.proposal(base);assert H(flower)==FLOWER
    assert S.C.inverse(S.inverse(flower))==base
    f,d=flower_regions(),draw_regions();fi,di=indices(f),indices(d)
    fd={i for i,(a,b)in enumerate(zip(base,flower,strict=True))if a!=b}
    dd={i for i,(a,b)in enumerate(zip(base,installed,strict=True))if a!=b}
    assert fd<=fi and dd<=di and not(fi&di)and not(fd&dd)
    combined=replace_regions(installed,flower,f)
    assert {i for i,(a,b)in enumerate(zip(base,combined,strict=True))if a!=b}==fd|dd
    assert replace_regions(combined,base,d)==flower and replace_regions(combined,base,f)==installed
    assert S.C.Old.Head.payload(combined)==S.C.Old.Head.payload(flower)
    if CANDIDATE is not None:assert H(combined)==CANDIDATE
    return combined,dict(base_SHA256=BASE,installed_draw_SHA256=INSTALLED,private_flower_SHA256=FLOWER,
        candidate_SHA256=H(combined),disjoint_ownership=True,draw_changed_bytes=len(dd),flower_changed_bytes=len(fd),
        combined_changed_bytes=len(fd|dd),draw_regions=d,flower_regions=f,
        removing_draw_is_exact32bf=True,removing_flower_is_exact27e=True,
        unchanged_Flower_carrier_and_cookie=True,helper=layout['helper'],outputs=0)


def without_draw(raw):
    pins();assert CANDIDATE is not None and H(raw)==CANDIDATE
    image=bytearray(raw)
    at=Draw.offset(Draw.DRAW_BANK,Draw.ENTRY);image[at:at+len(Draw.OLD_ENTRY)]=Draw.OLD_ENTRY
    lo,hi=Draw.offset(Draw.SPECIAL_BANK,Draw.FAST),Draw.offset(Draw.SPECIAL_BANK,Draw.LIMIT)
    image[lo:hi]=b'\xea'*(hi-lo)
    result=bytes(image);assert H(result)==FLOWER
    return result


def without_flower(raw):
    flower=without_draw(raw);base=S.C.inverse(S.inverse(flower))
    result=replace_regions(raw,base,flower_regions())
    assert H(result)==INSTALLED and Draw.inverse(result)==base and proposal(result)[0]==raw
    return result


def controllers(raw):
    flower=without_draw(raw);draw=without_flower(raw);base=Draw.inverse(draw)
    assert H(flower)==FLOWER and H(draw)==INSTALLED and H(base)==BASE
    before_cookie=base[S.C.Old.Head.COOKIE_AT:S.C.Old.Head.COOKIE_AT+16].hex()
    after_cookie=flower[S.C.Old.Head.COOKIE_AT:S.C.Old.Head.COOKIE_AT+16].hex()
    assert raw[S.C.Old.Head.COOKIE_AT:S.C.Old.Head.COOKIE_AT+16].hex()==after_cookie
    q=Native.bindings(flower)
    for name,hook in q['hooks'].items():
        lo=16+hook['offset'];pre=bytes.fromhex(hook['preimage16'])
        assert raw[lo:lo+len(pre)]==flower[lo:lo+len(pre)]==pre,name

    pickup=Pickup.controller(flower)
    assert H(pickup.encode())==PICKUP_QUALIFIED and pickup.count(FLOWER)==3
    bound_pickup=pickup.replace(FLOWER,CANDIDATE)
    assert bound_pickup.replace(CANDIDATE,FLOWER)==pickup

    full=Full.controller(flower);assert H(full.encode())==Full.FULL_SHA
    old='   if finalRiser>=3 and finalRiser<=6 then\n'
    shipped=Stairs.NEW
    assert shipped=='   if (finalRiser<=3 and finalRiserAttempts>0 or finalRiser>=4) and finalRiser<=6 then\n'
    recovered=S.Check.Replay.one(full,old,shipped)
    # A second view must recover the byte-exact shipped draw policy: helper
    # observation removed, old cookie restored, draw identity substituted.
    as_draw=S.Check.Replay.one(recovered,'local centers={[1264]=176,','local centers={')
    assert as_draw.count('ram(2,0x8fd)~=10')==2
    as_draw=as_draw.replace('ram(2,0x8fd)~=10','ram(2,0x8fd)~=9')
    as_draw=S.Check.Replay.one(as_draw,f"cookie=='{after_cookie}'",f"cookie=='{before_cookie}'")
    assert as_draw.count(FLOWER)==2
    as_draw=as_draw.replace(FLOWER,INSTALLED)
    assert H(as_draw.encode())==DRAW_FULL_QUALIFIED
    assert S.Check.Replay.one(recovered,shipped,old)==full
    bound_full=recovered.replace(FLOWER,CANDIDATE)
    assert bound_full.replace(CANDIDATE,FLOWER)==recovered
    programs=dict(full=bound_full.encode(),flower=bound_pickup.encode())
    for name,program in programs.items():
        Native.Check.LuaRuntime().compile(program.decode())
        assert not any(v in program for v in (b'emu.write',b'emu.setState',b'io.open',b'takeScreenshot',b'loadState',b'saveState'))
        if name in SCRIPTS:assert H(program)==SCRIPTS[name]
    return programs


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--compose-only',action='store_true');ap.add_argument('--run',action='store_true');args=ap.parse_args()
    assert not(args.compose_only and args.run)
    installed=Native.ROM.read_bytes();guard=Native.check(Native.ROM)
    assert guard['ROM_sha256']==INSTALLED and not guard['matching_patch_files']
    with cache():
        image,layout=proposal(installed)
        programs={}if args.compose_only else controllers(image)
    print('DK FLOWER DRAW BINDING '+json.dumps(dict(layout=layout,
        controllers={k:H(v)for k,v in programs.items()},qualified_pickup=PICKUP_QUALIFIED,
        qualified_pickup_receipt=PICKUP_RECEIPT,qualified_draw_full=DRAW_FULL_QUALIFIED,
        qualified_draw_full_receipt=DRAW_FULL_RECEIPT,factory_SHA256=H(Path(__file__).read_bytes()),outputs=0),separators=(',',':')),flush=True)
    if not args.run:return 0
    target,script=Native.OUT/'candidate.nes',Native.OUT/'controller.lua'
    assert set(Native.OUT.iterdir())=={target,script} and target.read_bytes()==installed
    original_target,original_script=target.read_bytes(),script.read_bytes()
    Native.require_free_workspace(Native.R,target,allow_interactive=True)
    success=True
    try:
        target.write_bytes(image);private=Native.check(target)
        assert private['ROM_sha256']==CANDIDATE and not private['matching_patch_files']
        for name in ('full','flower'):
            program=programs[name];script.write_bytes(program)
            result=Native.run(script,target,Native.OUT/'capture',CANDIDATE,360 if name=='full' else 320,long_no_capture=True)
            assert result['script_SHA256']==H(program) and result['outputs_written']==0 and not result['images']
            assert target.read_bytes()==image and script.read_bytes()==program and Native.check(target)==private
            print('DK FLOWER DRAW NATIVE '+json.dumps(dict(route=name,result=result),separators=(',',':')),flush=True)
            success=success and result['passed']
        return int(not success)
    finally:
        script.write_bytes(original_script);target.write_bytes(original_target)
        assert set(Native.OUT.iterdir())=={target,script} and target.read_bytes()==original_target and script.read_bytes()==original_script
        assert Native.ROM.read_bytes()==installed and Native.check(Native.ROM)==guard


if __name__=='__main__':raise SystemExit(main())
