"""Independently compare actual static menu pixels with NumPy, without a launch."""
from pathlib import Path
import hashlib
import json
import numpy as np
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT=D/'ROOT-clean731-menu-static-v1'
SHA='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rgb(p):
    a=np.frombuffer(Path(p).read_bytes(),dtype=np.uint8)
    assert a.size==245760
    return a.reshape(240,256,4)[:,:,[2,1,0]]


def main():
    assert not OUT.exists()
    review=D/'parodius-menu-clean731-background-v1'
    run=D/'parodius-menu-clean731-preparation-v1/menu/baseline-early'
    old=D/'parodius-menu3cee-preparation-v2/menu/baseline-early'
    bad=D/'parodius-menub0-preparation-v3/menu/baseline-early'
    assert sha(run/'candidate.nes')==SHA
    b=scoped_load(run/'candidate.nes');raw=b['raw']
    lo,hi=location(b,'X5MenuCursorLo'),location(b,'X5MenuCursorHi')
    assert hi-lo==19 and address(b,'X5MenuNameAddress')==0x2328
    rectangles=[]
    for at,count in [(0x2346,20),(0x2328,16)]+[(raw[lo+i]+256*raw[hi+i],1)for i in range(19)]:
        row,col=divmod(at-0x2000,32)
        assert 0<=row<30 and col+count<=32
        rectangles.append([8*col,8*row,8*(col+count)-1,8*row+7])
    rectangles.append([80,136,176,208])
    claimed=json.loads((review/'source-derived-mask.json').read_text(encoding='utf-8'))
    assert rectangles==[r['rectangle_inclusive']for r in claimed['rectangles']]
    mask=np.ones((240,256),dtype=bool)
    for x0,y0,x1,y1 in rectangles:
        mask[y0:y1+1,x0:x1+1]=False
    assert int(mask.sum())==51712
    reference=rgb(old/'frame-000185.argb')
    count=lambda frame:int(np.count_nonzero(np.any(reference!=rgb(frame),axis=2)&mask))
    assert count(old/'frame-000200.argb')==0
    negatives={n:count(bad/f'frame-{n:06d}.argb')for n in [194,206,218,230,242,254,266]}
    assert all(negatives.values())
    rows=json.loads((review/'all-owned-menu-static-pixels.json').read_text(encoding='utf-8'))
    assert len(rows)==164 and len({r['frame']for r in rows})==164
    owners=[json.loads(s)for s in (run/'menu-early-timing.jsonl').read_text(encoding='utf-8').splitlines()]
    ownerframes=[r['ppu']['frame']for r in owners if r['kind']=='early-menu-start-owner']
    assert [r['frame']for r in rows]==ownerframes
    results=[]
    for row in rows:
        frame=run/f"frame-{row['frame']:06d}.argb"
        assert sha(frame)==row['actual_frame_sha256']
        mismatch=count(frame)
        assert mismatch==row['static_mismatches']==0
        results.append(dict(frame=row['frame'],raw_sha256=sha(frame),static_mismatches=mismatch))
    proof=dict(passed=True,native_launched=False,ROM_sha256=SHA,owned_actual_frames=len(results),
               static_pixels_per_frame=int(mask.sum()),total_static_pixels=int(mask.sum())*len(results),
               independently_reconstructed_mask_rectangles=rectangles,
               rejected_known_b0_frames=negatives,frames=results,tool_sha256=sha(__file__),
               limits='Independent NumPy implementation on saved actual RGB pixels and linked cursor tables. Explicit9728dynamic/preview pixels excluded. This is no wholeBG, body-visibility, gameplay, waveform or adoption claim; manual wholeframe review is separate.')
    OUT.mkdir()
    (OUT/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in proof.items()if k not in ['frames','independently_reconstructed_mask_rectangles']}))


if __name__=='__main__':
    main()
