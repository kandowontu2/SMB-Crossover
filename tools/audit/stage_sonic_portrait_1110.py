"""Stage the qualified Sonic portrait fix in the owned candidate's file slot."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_sonic_static_portrait_1110 as Portrait
import stage_sonic_original_1110 as Original

R,NIGHTLY,PARENT=Original.R,Original.NIGHTLY,Original.PARENT
PIN='ccd2de04d1a2c00989a240943f7bbaf5ac1863bae34dce65e6c313558c7ba9ed'


def reconstruct():
    previous, program, packet, original = Original.reconstruct()
    image, portrait = Portrait.proposal(previous)
    assert sha256(image).hexdigest()==PIN
    return image, program, packet, dict(original=original,portrait=portrait)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    output=args.output.resolve()
    assert output==R/'build/sonic-original-native-1110'
    assert sorted(path.name for path in output.iterdir())==['candidate.nes']
    target=output/'candidate.nes'
    assert sha256(target.read_bytes()).hexdigest()==Portrait.PARENT
    assert Original.WWF.Previous.check(NIGHTLY)['ROM_sha256']==PARENT
    image,_,_,record=reconstruct()
    target.write_bytes(image)
    assert target.read_bytes()==image
    print(json.dumps(dict(passed=True,ROM_SHA256=PIN,native_Mesen=False,
        ROM_written=True,output_files=1,replaced_only_owned_candidate=Portrait.PARENT,
        record=record),sort_keys=True),flush=True)


if __name__=='__main__':main()
