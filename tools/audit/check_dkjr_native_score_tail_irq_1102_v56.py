"""Direct and nested native interrupts after local score tail repair."""
import argparse, collections, json
from pathlib import Path
import check_dkjr_native_service_nested_1102_v53 as I
import check_dkjr_native_score_tail_1102_v55 as S
A, R, O, W, N = I.A, I.R, I.O, I.W, I.N
timers, state, branches, audio_sites, AUDIO = I.timers, I.state, I.branches, I.audio_sites, I.AUDIO
fixture = S.fixture
text = I.text.replace("service_names = ['DkjrNativeAwardSourcePoints', 'DkjrNativeFruitCollision']",
                      "service_names = ['DkjrNativeAwardSourcePoints', 'DkjrNativeFruitCollision', 'DkScoreFlush']")
assert text != I.text
exec(compile(text, str(Path(__file__)), 'exec'), globals())


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--phase',choices=['deep','direct','nested'],default='deep')
    args=ap.parse_args()
    b,m,L,q=fixture()
    assert json.loads((O/'native-scoretail-v55-CPU.json').read_text())['passed']
    cohorts,shapes={},{}
    for epoch in range(1,63):
        N.put(m,FrameCounter=epoch,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0,NmiDisable=255)
        timers(m);seed=N.fork(m);out=run(m,L)
        if out['cuts']:
            cohorts[epoch]=(seed,out,state(m))
            for cut in out['cuts']:
                key=(cut[0],cut[2],cut[3],cut[4])
                if key not in shapes or cut[1]<shapes[key][1][1]:shapes[key]=(epoch,cut)
    cuts=sorted(shapes.values(),key=lambda z:(z[1][1],z[0],z[1][0]))
    minimum=255;counts=collections.Counter();writers=collections.Counter();transitions=collections.Counter();rows=[]
    try:
        if args.phase in ['deep','direct']:
            for kind in ['IRQ','lagNMI']:
                available=[z for z in cuts if kind!='IRQ' or not z[1][4]]
                selected=available[:1] if args.phase=='deep' else available
                print('DK scoretail direct',kind,len(selected),'of',len(available),flush=True)
                for index,(epoch,cut)in enumerate(selected):
                    seed,ref,expected=cohorts[epoch];z=N.fork(seed);out=run(z,L,(kind,cut));minimum=min(minimum,out['minimum_SP'])
                    assert out['regs']==ref['regs'] and state(z)==expected,('direct continuation',epoch,kind,cut)
                    counts[kind]+=1;writers.update(out['audio_writers']);transitions.update(out['audio_transitions'])
                    if index and index%200==0:print('DK scoretail direct progress',kind,index,flush=True)
        if args.phase in ['deep','nested']:
            for epoch,(seed,ref,expected)in cohorts.items():
                cut=min(ref['cuts'],key=lambda z:(z[1],z[0]));z=N.fork(seed);lag=run(z,L,('lagNMI',cut))
                assert lag['regs']==ref['regs']and state(z)==expected
                shapes=sorted(lag['nested_shapes'],key=lambda z:(z[1],z[0]))
                chosen=shapes[:1]if args.phase=='deep'else shapes
                print('DK scoretail nested',epoch,len(chosen),'of',len(shapes),flush=True)
                for index,nested in enumerate(chosen):
                    z=N.fork(seed);out=run(z,L,('lagNMI',cut),nested=nested);minimum=min(minimum,out['minimum_SP'])
                    assert out['regs']==lag['regs']and state(z)==expected,('nested continuation',epoch,cut,nested)
                    counts['nestedIRQ']+=1;writers.update(out['audio_writers']);transitions.update(out['audio_transitions'])
                    if index and index%200==0:print('DK scoretail nested progress',epoch,index,flush=True)
                rows.append(dict(epoch=epoch,foreground_cut=cut,unmasked_lag_shapes=len(shapes),independent_nested_IRQ=len(chosen)))
    except AssertionError as error:
        out=dict(passed=False,ROM_written=False,native_owner_admitted=False,phase=args.phase,epoch=epoch,
                 error=repr(error),actual_interrupts=dict(counts),minimum_SP=minimum)
        (O/f'native-scoretail-v56-{args.phase}-negative.json').write_text(json.dumps(out,indent=2)+'\n');raise
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,historical_v65_matching_header_fixture=True,
        phase=args.phase,genuine_NmiDisable=255,distinct_service_PC_A_C_I_shapes=len(cuts),I1_shapes=sum(bool(z[1][4])for z in cuts),
        actual_interrupts=dict(counts),minimum_ISR_SP=minimum,source_bound_audio_writers=dict(writers),audio_transitions=dict(transitions),nested_cohorts=rows,
        scope='Original score publication/type/epoch and native Main boundary parity bound by55. GenuineFF NMI includes all reached I states; IRQ only unmasked. Selected direct or independent nested nativeIRQ cuts preserve complete original/private/R0..7/SMC/native state and full foreground continuation; only source-bound outer audio clocks advance. No latestowner/cold/native/menu/admission claim.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),Path(I.__file__),Path(S.__file__),O/'native-scoretail-v54.s',O/'native-scoretail-v54.bin',O/'native-scoretail-v55-CPU.json',R/'src/reset.s',R/'src/music_drivers/vanilla_sfx.s']})
    (O/f'native-scoretail-v56-{args.phase}.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in['passed','phase','actual_interrupts','minimum_ISR_SP']}))


if __name__=='__main__':main()
