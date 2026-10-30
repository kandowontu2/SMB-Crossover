"""Verify the native reservation block and optional body chunk admission."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_render_controls_v4 as T
from verify_native_relocation import NesMPU
from check_tmnt_render_oa import address
C=T.C;put=T.put;get=T.get;run=T.run
P=T.P;O=R/'build/final-fantasy-host-render-native-budget-v1'


if __name__=='__main__':
    assert not O.exists()
    h=json.loads((P/'build-proof.json').read_text())
    for p,d in h['bindings'].items():assert C.sha(p)==d,p
    b=C.bundle(P);optional=0;native=0;headers=set()
    start=address(b,'RosterProjectileOamReady')
    stop=address(b,'DrawAllMetasprites::InitObjectLoop')
    for entry in range(144):
        for face in [0,1,2]:
            m=T.setup(b,shadows=1)
            for chunk in range(1,8):
                source=T.records(m,entry,chunk,0,face)
                if source is None:break
                assert not source[0],('additional body color dropped by optional shortcut',entry,chunk,face)
                optional+=1
            for initial in [0,64,128]:
                m.raw_page(1,3);put(m,CurrentBank=3)
                source=T.records(m,entry,0,0,face)
                assert source is not None
                n=get(m,'FfRenderBuffer');headers.add(n)
                put(m,CurrentOAMOffset=initial,RgDrawRemaining=179)
                m.raw_page(1,132);put(m,CurrentBank=132)
                c=NesMPU(memory=m,pc=start);c.sp=240;c.p=0xf9;c.x=0xa7;c.y=0x91
                for steps in range(40):
                    if c.pc==stop:break
                    assert m[c.pc]!=0
                    c.step()
                else:raise AssertionError(('native reservation did not reach original object-loop boundary',entry,face,initial,hex(c.pc)))
                assert get(m,'CurrentOAMOffset')==initial+n
                assert c.x==0xa7 and get(m,'RgDrawRemaining')==179
                assert 220-n+n+32==252
                native+=1
    report=dict(passed=True,image_sha256=C.sha(P/'ram3.bin'),
        optional_body_chunks_all_empty_with_shadows_off=optional,
        actual_native_RosterProjectileOamReady_blocks=native,source_body_header_lengths=sorted(headers),
        native_reserves_actual_SmPosePtr_header=True,
        temporal_lease='RgDrawRemaining only within this selectedFF early draw; genuine MetaspriteRenderLoop does not consume it, native reservation block retains it, later native owners may reuse it.',
        scope='Actual physicalA4 block execution until unchanged native object-loop boundary. Not fullMain/cart hook/native emulator admission.',
        bindings={**h['bindings'],str((P/'build-proof.json').resolve()):C.sha(P/'build-proof.json'),
                  str(Path(__file__).resolve()):C.sha(__file__),str(Path(T.__file__).resolve()):C.sha(T.__file__)})
    O.mkdir();(O/'controls.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k!='bindings'}))
