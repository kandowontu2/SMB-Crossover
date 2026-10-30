"""Actual adversarial OAM capacity: every visible Bolt part must get a turn."""
from pathlib import Path
import argparse,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_render_controls_v3 as T
from check_tmnt_render_oa import address
C=T.C;put=T.put;get=T.get;setv=T.setv;run=T.run
P=R/'build/final-fantasy-host-render-v8'
O=R/'build/final-fantasy-host-render-overload-v1'


def exercise(b):
    m=T.setup(b,variant=2,tier=2,shadows=1,face=1,rotation=68)
    ref=T.setup(b,variant=2,tier=2,shadows=1,face=1)
    for index,value in [(0,2),(1,2),(2,0),(3,0),(4,128),(5,1),(7,125),(8,1)]:
        setv(m,'FfProjectile',value,index)
    expected=set()
    for chunk in range(8):
        source=T.records(ref,154,chunk,1,1)
        if source is None:break
        parts,off,page=source
        for p in parts:
            sy=p[2]-256 if p[2]&128 else p[2]
            sx=p[3]-256 if p[3]&128 else p[3]
            if 31<=125+off+sy<=239 and 0<=112+sx<=255:
                expected.add((chunk,*p))
    seen=set();draws=100;drawn=[]
    for frame in range(draws):
        # Deliberate pool pressure: another native owner already used all but
        # one available weapon record. No gameplay reachability is claimed.
        put(m,CurrentOAMOffset=220-get(m,'FfRenderBuffer')-4)
        def hook(m,c,step):
            if c.pc!=address(b,'MetaspriteRenderLoop')or m.rawtags[1]!=132:return
            ptr=get(m,'R0')+256*get(m,'R1');n=m[ptr]
            assert n==4,('exact one-record remaining budget',frame,n)
            part=tuple(m[ptr+i]for i in range(1,5))
            key=(get(m,'FfTargetPage'),*part)
            assert key in expected,('foreign source part emitted',frame,key)
            seen.add(key);drawn.append([frame,*key])
        run(m,'FfHostDrawShots',hook=hook)
    missing=sorted(expected-seen)
    return dict(passed=not missing,draws=draws,source_visible_parts=len(expected),
                observed_visible_parts=len(seen),never_seen_source_parts=missing,
                emitted_records=len(drawn),trace=drawn,
                scope='Synthetic one-slot pressure with frozen logical spell age. Tests renderer fairness; not a natural three-spell or full-Main cadence case.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,default=P);p.add_argument('--out',type=Path,default=O)
    args=p.parse_args();P=args.packet.resolve();O=args.out.resolve();assert not O.exists();O.mkdir()
    h=json.loads((P/'build-proof.json').read_text())
    for path,d in h['bindings'].items():assert C.sha(path)==d,path
    b=C.bundle(P)
    try:result=exercise(b)
    except Exception as e:result=dict(passed=False,error=repr(e),traceback=traceback.format_exc())
    bindings={**h['bindings'],str((P/'build-proof.json').resolve()):C.sha(P/'build-proof.json'),str(Path(__file__).resolve()):C.sha(__file__)}
    report=dict(**result,image_sha256=C.sha(P/'ram3.bin'),bindings=bindings)
    (O/'controls.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k not in ['bindings','trace']}),flush=True)
    if not result['passed']:raise SystemExit(1)
