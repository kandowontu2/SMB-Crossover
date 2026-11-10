"""AlignedD100 effects qualification; RAM/stdout only, explicit audio negative."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_sonic_native_effects_1110 as T
import sonic_sms_native_effects_aligned_1110 as B

E,C,O,N,R=T.E,T.C,T.O,T.N,T.R


def proposal():
    old=C.ROM.read_bytes();current=E.FF.proposal(old)[0];p=B.build(C.Current.W.bundle(current))
    with patch.object(E.Payload,'build',return_value=p['packet']):image,program,_,_,_=E.proposal(old,current)
    return image,program,p


def cold(trial,p,program):
    packet=p['packet'];seeds={}
    for owner in range(37,43):
        m=O.blank(trial);C.cold(m,owner,program['new']);seeds[owner]=(m,m)
    counts,result=E.eighth(trial,program,packet,seeds)
    for at in(0x1040,0x10ef,0x1100,0x1171,0x1172,0x1259):
        m=O.blank(trial);m.corrupt_at=(2,at)
        C.cold(m,43,program['new'],expect_success=False)
        assert O.headers(m)==(bytes(16),bytes(16))
    return dict(existing_eighth_contract=dict(counts),cold=result,actual_executable_metadata_readback_faults=6)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--expect-unmapped-audio',action='store_true');ap.add_argument('--native-audio',action='store_true');args=ap.parse_args()
    assert args.output.resolve().is_relative_to(R/'build')and not args.output.exists()
    image,program,p=proposal();audio=None
    if args.native_audio:
        import check_sonic_shared_audio_1110 as Audio
        image,audio=Audio.proposal(image)
    trial=C.Current.W.bundle(image);seed=T.install(trial,p,program)
    assert p['service']['symbols']['SonicServices']==0xd100
    original=p['service']['packet']['core']['image']
    assert p['packet']['kernel'][:len(original)]==original
    packet=p['packet'];assert packet['metadata'][62:64]==b'\xff\xff'
    assert packet['metadata'][0x25e:0x2e9]==p['service']['packet']['metadata'][0x25e:0x2e9]
    result=dict(passed=True,source_only=True,outputs_written=0,ROM_written=False,parent_SHA256=E.PIN,
        in_memory_SHA256=E.digest(image),source_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        private_code=p['service']['code_half_open'],metadata_segments=p['metadata_segments'],
        remaining_private=p['remaining_private_bytes'],remaining_metadata=p['remaining_metadata_bytes'],
        ordinary=T.episodes(seed,p),native_getters=T.getters(seed,p),bounds_head=T.bounds_and_head_contact(seed,p),
        render=T.render(seed,p),cold=cold(trial,p,program),public_raw43_still_rejected=True)
    if audio:result['native_audio']=audio
    if args.expect_unmapped_audio:
        try:T.world_edges(seed,p)
        except AssertionError as error:
            assert error.args==(('Native death audio queue not consumed',1,0),),error.args
            result.update(known_audio_negative=dict(expected=True,queue=1,buffer=0,actual_full_NMIs=1),
                native_ready=False,world_edge_motion_reaches_native_death_music=True)
        else:raise AssertionError('Pinned parent unexpectedly acquired a raw43 audio policy')
    else:result.update(world_edges=T.world_edges(seed,p))
    print(json.dumps(result,sort_keys=True),flush=True);assert not args.output.exists()


if __name__=='__main__':main()
