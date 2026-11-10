"""Unchanged frozen eight FF earned-item routes on the frozen96e0 image.

Only the cartridge read facade/PIN are scoped before genuine menu startup.
No model/cache/actor/terrain/stat grant is inserted and no artifact is written.
"""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
from unittest.mock import patch

import check_ff_head_corner_1110_v2 as Fix
import check_ff_star_life_current_1110 as S

W = S.W
PIN='96e09ab1b67a7c75b89d49219e8e529582b9a05b7dd82dd3cd570fdb239212bd'
STAR_PIN='19650c8f19ad03c8eecf4652a91b6ecd33ce9676c5544206cbe4e4ce23d72ee2'
FIX_PIN='e508771dbac9dfb42c33ca41b3d3af4c07f98f81fd2f742205f6e4a3ce690665'
SOURCE_PIN='6e58b2460852e808031f64ce733545ca0bffc78da05e5b68860d929e98c7f0cd'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',type=int,choices=range(4))
    args=p.parse_args()
    for source,pin in ((Path(S.__file__),STAR_PIN),(Path(Fix.__file__),FIX_PIN),(Fix.SOURCE,SOURCE_PIN)):
        assert sha256(source.read_bytes()).hexdigest()==pin
    original=W.ROM.read_bytes()
    assert sha256(original).hexdigest()==W.PIN
    image,kernel,cookie,_,_,_=Fix.proposal(original)
    assert sha256(image).hexdigest()==PIN
    class MemoryImage:
        def read_bytes(self):return image
    results=[]
    with patch.object(W,'ROM',MemoryImage()),patch.object(W,'PIN',PIN):
        for variant in range(4) if args.variant is None else (args.variant,):
            for kind in ('life','star'):
                log=io.StringIO()
                try:
                    with redirect_stdout(log):result=S.route(variant,kind)
                except Exception:
                    print(log.getvalue(),flush=True)
                    raise
                assert result['passed'] and result['ROM_sha256']==PIN
                row=dict(variant=variant,class_name=result['class_name'],kind=kind,passed=True,
                    authored=result['authored'],birth_step=result['born']['player']['step'],
                    collected=result['collected'],life_award=result['life_award'],
                    protected_enemy=result['protected_enemy'],music_restored=result['music_restored'],
                    timer_transitions=len(result['timer_changes']),palette_phases=len(result['palettes']),
                    terminal=result['terminal'])
                results.append(row)
                print(json.dumps(dict(event='frozen_powerup_regression_pass',result=row)),flush=True)
    assert sha256(W.ROM.read_bytes()).hexdigest()==W.PIN==sha256(original).hexdigest()
    print(json.dumps(dict(passed=True,source_CPU_only=True,Mesen_run=False,ROM_written=False,
        output_files=0,candidate_SHA256=PIN,kernel_SHA256=sha256(kernel).hexdigest(),
        cookie=cookie.hex(),frozen_route_SHA256=STAR_PIN,source_SHA256=SOURCE_PIN,
        proposal_checker_SHA256=FIX_PIN,results=[dict(variant=r['variant'],class_name=r['class_name'],
        kind=r['kind'],passed=True,terminal=r['terminal']) for r in results],
        scope='Unchanged actual-menu/controller/native-parser first-mushroom/flower/Star or1UP routes on96e0; Star body protection/timer/palette/music and native deferred1UP preserved. Two independent routes per class; logical CPU only, no fullstage/Mesen claim.')),flush=True)


if __name__=='__main__':main()
