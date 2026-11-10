"""Build the source-checked Sonic scene and palette fixes in the same slot."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_sonic_native_palette_1110 as Palette
import check_sonic_native_scene_1110 as Scene
import stage_sonic_portrait_1110 as Portrait

R, NIGHTLY, PARENT = Portrait.R, Portrait.NIGHTLY, Portrait.PARENT
CANDIDATE = R/'build/sonic-original-native-1110/candidate.nes'


def reconstruct():
    portrait, program, packet, record = Portrait.reconstruct()
    color, palette_record = Palette.proposal(portrait)
    image, packet, scene_record = Scene.proposal(color, packet)
    color_delta = Portrait.Original.differences(portrait,color)
    scene_delta = Portrait.Original.differences(color,image)
    assert not color_delta.keys() & scene_delta.keys()
    assert scene_record['exact_changed_bytes']==len(scene_delta)==71
    assert scene_record['cookie']=='a72b01c0f80210577f684adf9ea78ed5'
    return image, program, packet, dict(parent_SHA256=PARENT,
        ROM_SHA256=sha256(image).hexdigest(),rebase_and_portrait=record,
        palette=palette_record,scene=scene_record)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--pin',help='Exact image hash required to stage a candidate')
    parser.add_argument('--check-full-stage',action='store_true')
    args=parser.parse_args()
    output=args.output.resolve()
    assert output.is_relative_to(R/'build') and output!=R/'build'
    assert Portrait.Original.WWF.Previous.check(NIGHTLY)['ROM_sha256']==PARENT
    image,_,packet,record=reconstruct()
    if args.check_full_stage:
        import check_sonic_native_route_1110 as Route
        route,_=Route.run(image,packet,goal_x=3600,max_epochs=3300,full_stage=True)
        assert route['full_native_1_1'] and route['active_1_2']
        record['actual_CPU_fullstage']=route
    if args.pin:
        assert record['ROM_SHA256']==args.pin
        assert output==CANDIDATE.parent
        assert sorted(path.name for path in output.iterdir())==['candidate.nes']
        assert sha256(CANDIDATE.read_bytes()).hexdigest()==Portrait.PIN
        CANDIDATE.write_bytes(image)
        assert CANDIDATE.read_bytes()==image
    print(json.dumps(dict(passed=True,ROM_written=bool(args.pin),
        output_files=int(bool(args.pin)),native_Mesen=False,record=record),sort_keys=True),flush=True)


if __name__=='__main__':main()
