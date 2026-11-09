"""Bind the signed-world successor to the existing DK Jr opening route."""
import argparse
import json
from pathlib import Path

import check_dkjr_world_span_1110_v1 as S

R = S.R


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, required=True)
    args = ap.parse_args()
    proof_path, vectors_path = (S.OUT / name for name in ['span-proof.json', 'span-vectors.json'])
    proof, vectors = [json.loads(path.read_text()) for path in [proof_path, vectors_path]]
    assert proof['passed'] and vectors['passed']
    pin = proof['memory_only_SHA256']
    assert pin == vectors['memory_only_SHA256'] == R.I.sha(args.rom.read_bytes())
    old, _, _, labels = R.pinned_inputs()
    assert R.I.sha(R.OAM.compose(old, proof['patches'])) == pin
    lua = R.controller(bytes.fromhex(proof['cookie']), labels)
    lua = R.OAM.replace_once(lua, R.PIN, pin)
    lua = R.OAM.replace_once(lua,
        ' local x,y=xpos(),read(0xbd)\n local ready=private(2,0x6b)==1',
        ''' local x,y=xpos(),read(0xbd)
 local relative=x-camera()
 local scrollInput=read(0x75a)
 local expectedScroll=math.max(0,math.min(255,relative))
 pipe.scroll=pipe.scroll or {samples=0,mismatches=0}
 local q=pipe.scroll
 q.samples=q.samples+1
 if scrollInput~=expectedScroll then
  q.mismatches=q.mismatches+1
  if not q.first_mismatch then q.first_mismatch={frame=frame,x=x,camera=camera(),value=scrollInput,expected=expectedScroll} end
 end
 q.last={frame=frame,x=x,camera=camera(),value=scrollInput,expected=expectedScroll}
 local ready=private(2,0x6b)==1''')
    lua = R.OAM.replace_once(lua,
        ' pipe.max_x=math.max(pipe.max_x,x)\n pipe.stationary=(x==lastX) and (pipe.stationary+1) or 0;lastX=x',
        ' pipe.stationary=(x<=pipe.max_x) and (pipe.stationary+1) or 0\n pipe.max_x=math.max(pipe.max_x,x)')
    R.V.prepare(S.OUT/'native', args.rom, lua,
                [Path(__file__), R.BASE, R.FRONTEND_PROOF, R.OAM_MANIFEST, R.ROUTE_SOURCE,
                 R.V.SOURCE, R.V.LAYOUT, proof_path, vectors_path, S.SOURCE],
                expected=pin, timeout=240, allow_interactive=True,
                scope='Private DK Jr native cold, real OAM DMA, idle and original hop followed by first natural pipe. Signed world scan and native scroll-input observations.')


if __name__ == '__main__':
    main()
