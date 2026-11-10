"""Replace only the unqualified, task-owned WWF candidate with its source fix."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import stage_wwf_powerups_1110 as Previous
import check_wwf_role_palette_1110 as Fix

R,NIGHTLY=Previous.R,Previous.NIGHTLY
PARENT=Previous.PARENT
PIN='d76e070ef5923e05e61088fc7e91e05a637e0c4184c6ccf29feea23637252486'


def reconstruct():
    parent,_=Previous.reconstruct()
    image,record=Fix.proposal(parent)
    assert sha256(image).hexdigest()==PIN and len(image)==2_097_168
    return image,record


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();out=args.output.resolve()
    assert out==R/'build/wwf-powerups-native-1110'
    assert sorted(q.name for q in out.iterdir())==['candidate.nes']
    target=out/'candidate.nes'
    assert sha256(target.read_bytes()).hexdigest()==Previous.PIN
    assert Previous.check(NIGHTLY)['ROM_sha256']==PARENT
    image,record=reconstruct()
    target.write_bytes(image)
    assert target.read_bytes()==image
    print(json.dumps(dict(passed=True,native_pending=True,ROM_written=True,
        output_files=1,output_bytes=len(image),ROM_SHA256=PIN,
        replaced_only_own_unqualified_candidate=Previous.PIN,source_record=record),sort_keys=True))


if __name__=='__main__':main()
