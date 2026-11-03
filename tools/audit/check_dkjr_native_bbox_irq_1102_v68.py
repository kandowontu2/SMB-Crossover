"""Deepest actual native bbox FF/NMI plus nestedIRQ before shared admission."""
import collections,json
from pathlib import Path
import check_dkjr_native_bbox_1102_v66 as B
import check_dkjr_native_service_nested_1102_v53 as I
A,R,O,W,N=B.A,B.R,B.O,B.W,B.N
timers,state,branches,audio_sites,AUDIO=I.timers,I.state,I.branches,I.audio_sites,I.AUDIO
text=I.text.replace("service_names = ['DkjrNativeAwardSourcePoints', 'DkjrNativeFruitCollision']","service_names = ['DkFullBox']")
text=text.replace('if bank == 3 and c.pc in entries:','if bank in [2,3] and c.pc in entries:')
exec(compile(text,str(Path(__file__)),'exec'),globals())


def main():
    b,m,L,q=B.fixture(True)
    B.P.P.direct(m,L['DkjrNativeFruitReset'])
    for i in range(6):m[W.address(b,'Enemy_Flag')+i]=0
    N.put(m,FrameCounter=1,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0,NmiDisable=255)
    seed=N.fork(m);ref=run(m,L);expected=state(m);assert ref['cuts'];cut=min(ref['cuts'],key=lambda z:(z[1],z[0]))
    completed=[];minimum=255
    try:
        for kind in ['IRQ','lagNMI']:
            z=N.fork(seed);out=run(z,L,(kind,cut));minimum=min(minimum,out['minimum_SP'])
            assert out['regs']==ref['regs']and state(z)==expected
            completed.append(kind)
            if kind=='lagNMI':
                nested=min(out['nested_shapes'],key=lambda z:(z[1],z[0]));z=N.fork(seed)
                out=run(z,L,(kind,cut),nested=nested);minimum=min(minimum,out['minimum_SP'])
                assert out['regs']==ref['regs']and state(z)==expected;completed.append('nestedIRQ')
    except AssertionError as error:
        out=dict(passed=False,ROM_written=False,native_owner_admitted=False,shared_grant=False,
            genuine_NmiDisable=255,foreground_minimum_SP=ref['minimum_SP'],foreground_cut=cut,
            error=repr(error),completed=completed,minimum_completed_ISR_SP=minimum,
            body_SHA256=A.sha((O/'native-bbox-v65.bin').read_bytes()),metadata_SHA256=A.sha((O/'native-bbox-ports-v65.bin').read_bytes()))
        (O/'native-bbox-v68-IRQ-negative.json').write_text(json.dumps(out,indent=2)+'\n');raise
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,shared_grant=False,
        genuine_NmiDisable=255,foreground_minimum_SP=ref['minimum_SP'],foreground_cut=cut,
        minimum_ISR_SP=minimum,completed=completed,cut_shapes=len(ref['cuts']),
        scope='Deepest actual new bbox context in complete normalGameCore, genuineFF lag and nestednativeIRQ with complete resumedMain equality. Isolated proposedgate/header fixture only; allcuts/currentpositiveforeign/source lifetime remain required before sharedgrant.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),Path(B.__file__),Path(I.__file__),O/'native-bbox-v65.bin',O/'native-bbox-ports-v65.bin',O/'native-bbox-v65-layout.json']})
    (O/'native-bbox-v68-IRQ.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))


if __name__=='__main__':main()
