"""All actual bbox-port/header/source FF cuts plus independent nested IRQ."""
import argparse,collections,json
from pathlib import Path
import check_dkjr_native_bbox_irq_1102_v68 as P
A,R,O,W,N=P.A,P.R,P.O,P.W,P.N
timers,state,branches,audio_sites,AUDIO=P.timers,P.state,P.branches,P.audio_sites,P.AUDIO
text=P.text.replace("service_names = ['DkFullBox']","service_names = ['DkFullBox','DkProposedBBoxPort']")
text=text.replace('if bank in [2,3] and c.pc in entries:','if bank in [2,3,193] and c.pc in entries:')
exec(compile(text,str(Path(__file__)),'exec'),globals())


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['direct','nested'],default='direct');args=ap.parse_args()
    b,m,L,q=P.B.fixture(True);L=dict(L);L['DkProposedBBoxPort']=0xadd8
    P.B.P.P.direct(m,L['DkjrNativeFruitReset'])
    for i in range(6):m[W.address(b,'Enemy_Flag')+i]=0
    N.put(m,FrameCounter=1,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0,NmiDisable=255)
    seed=N.fork(m);ref=run(m,L);expected=state(m);cuts=sorted(ref['cuts'],key=lambda z:(z[1],z[0]))
    counts=collections.Counter();minimum=255;writers=collections.Counter()
    try:
        if args.phase=='direct':
            for kind in ['IRQ','lagNMI']:
                chosen=[z for z in cuts if kind!='IRQ'or not z[4]]
                print('DK bbox port direct',kind,len(chosen),flush=True)
                for i,cut in enumerate(chosen):
                    z=N.fork(seed);out=run(z,L,(kind,cut));minimum=min(minimum,out['minimum_SP'])
                    assert out['regs']==ref['regs']and state(z)==expected,('bboxportdirectcontinuation',kind,cut)
                    counts[kind]+=1;writers.update(out['audio_writers'])
        else:
            cut=cuts[0];z=N.fork(seed);lag=run(z,L,('lagNMI',cut));shapes=sorted(lag['nested_shapes'],key=lambda z:(z[1],z[0]))
            print('DK bbox port nested',len(shapes),flush=True)
            for i,nested in enumerate(shapes):
                z=N.fork(seed);out=run(z,L,('lagNMI',cut),nested=nested);minimum=min(minimum,out['minimum_SP'])
                assert out['regs']==ref['regs']and state(z)==expected,('bboxportnestedcontinuation',cut,nested)
                counts['nestedIRQ']+=1;writers.update(out['audio_writers'])
                if i and i%250==0:print('DK bbox port nested progress',i,flush=True)
    except AssertionError as error:
        out=dict(passed=False,ROM_written=False,native_owner_admitted=False,shared_grant=False,phase=args.phase,
            error=repr(error),actual_interrupts=dict(counts),minimum_completed_SP=minimum)
        (O/f'native-bbox-v69-{args.phase}-negative.json').write_text(json.dumps(out,indent=2)+'\n');raise
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,shared_grant=False,
        phase=args.phase,genuine_NmiDisable=255,source_envelope='Actual193:ADD8proposedport entry through its real native return, including sharedauth/header/frame and nested originalD2BD callback.',
        direct_cut_shapes=len(cuts),I1_NMI_cut_shapes=sum(bool(z[4])for z in cuts),actual_interrupts=dict(counts),minimum_ISR_SP=minimum,
        source_bound_audio_writers=dict(writers),
        scope='Independent fresh realGameCore continuation for every selected port/header/source PC/SP/A/C/I shape; IRQ onlyI0, hardwareNMI includesI1. GenuineFF lag incrementsNmiSkipped once/excludes regularNMI. Nestedphase tests every reached native unmasked audio position at the deepest port/source context. Full private/R0..7/33SMC/native/application and foreground exact, only bound outer sound clocks allowed. Positivecurrentforeign owners/latestcold and final currentbinding remain pending; no sharedgrant/ROM/nativeadmission.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),Path(P.B.__file__),O/'native-bbox-v65.bin',O/'native-bbox-ports-v65.bin',O/'native-bbox-gate-v65.bin']})
    (O/f'native-bbox-v69-{args.phase}.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['passed','phase','direct_cut_shapes','I1_NMI_cut_shapes','actual_interrupts','minimum_ISR_SP']}))


if __name__=='__main__':main()
