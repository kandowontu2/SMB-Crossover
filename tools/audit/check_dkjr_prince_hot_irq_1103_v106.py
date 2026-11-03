"""Combined101 full-auth/hot source continuations under real IRQ/FF/audio."""
import argparse
import collections
import inspect
import json
from pathlib import Path
import measure_dkjr_prince_owner_1103_v101 as P
import check_dkjr_anchored_lifetime_1103_v95 as F
import check_dkjr_native_service_nested_1102_v53 as I

A,R,O,N,W=P.A,P.R,P.O,F.N,F.W
timers,state,branches,audio_sites,AUDIO=I.timers,I.state,I.branches,I.audio_sites,I.AUDIO
text=I.text.replace("service_names = ['DkjrNativeAwardSourcePoints', 'DkjrNativeFruitCollision']",
    "service_names = ['CoCheckCode','DkNativeAnchorReady','DkFullBox','DkScoreFlush']")
assert text!=I.text;text=text.replace('if bank == 3 and c.pc in entries:','if bank in [2,3,193] and c.pc in entries:')
exec(compile(text,__file__,'exec'),globals())


def fixture():
    code=inspect.getsource(F.fixture);assert code.count('b,q=P.image()')==1
    code=code.replace('b,q=P.image()','b,q=CURRENT_IMAGE()')
    env=dict(F.__dict__,CURRENT_IMAGE=P.image);exec(compile(code,__file__,'exec'),env)
    b,m,L,q=env['fixture']();return b,m,dict(L,**q['manager_labels']),q


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['direct','nested'],default='direct');args=ap.parse_args()
    b,m,L,q=fixture();cohorts={};shapes={}
    for index in range(1,63):
        N.put(m,FrameCounter=index,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0,NmiDisable=255)
        timers(m);seed=N.fork(m);ref=run(m,L)
        if index in [1,2,61,62]:cohorts[index]=(seed,ref,state(m))
    for index,(seed,ref,expected)in cohorts.items():
        for cut in ref['cuts']:
            key=(cut[0],cut[2],cut[3],cut[4])
            if key not in shapes or cut[1]<shapes[key][1][1]:shapes[key]=(index,cut)
    cuts=sorted(shapes.values(),key=lambda z:(z[1][1],z[0],z[1][0]))
    counts=collections.Counter();minimum=255;writers=collections.Counter();rows=[]
    print('DK combinedhot',args.phase,len(cuts),'foregroundshapes',flush=True)
    if args.phase=='direct':
        for kind in ['IRQ','lagNMI']:
            chosen=[z for z in cuts if kind!='IRQ'or not z[1][4]]
            for index,(epoch,cut)in enumerate(chosen):
                seed,ref,expected=cohorts[epoch];z=N.fork(seed);out=run(z,L,(kind,cut))
                minimum=min(minimum,out['minimum_SP'])
                assert out['regs']==ref['regs']and state(z)==expected,('combinedhotcontinuation',kind,epoch,cut)
                counts[kind]+=1;writers.update(out['audio_writers'])
                if index and index%300==0:print('DK combinedhot',kind,index,'/',len(chosen),flush=True)
    else:
        for epoch,(seed,ref,expected)in cohorts.items():
            cut=min(ref['cuts'],key=lambda z:(z[1],z[0]));z=N.fork(seed);lag=run(z,L,('lagNMI',cut))
            nested=sorted(lag['nested_shapes'],key=lambda z:(z[1],z[0]))
            assert lag['regs']==ref['regs']and state(z)==expected
            print('DK combinedhot nested',epoch,len(nested),flush=True)
            for index,inner in enumerate(nested):
                z=N.fork(seed);out=run(z,L,('lagNMI',cut),nested=inner);minimum=min(minimum,out['minimum_SP'])
                assert out['regs']==ref['regs']and state(z)==expected,('combinedhotnested',epoch,cut,inner)
                counts['nestedIRQ']+=1;writers.update(out['audio_writers'])
                if index and index%300==0:print('DK combinedhot nested progress',epoch,index,flush=True)
            rows.append(dict(epoch=epoch,foreground_cut=cut,actual_nested_IRQ=len(nested)))
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        memory_only_SHA256=A.sha(b['raw']),phase=args.phase,genuine_NmiDisable=255,
        full_auth_and_source_foreground_shapes=len(cuts),I1_foreground_shapes=sum(bool(z[1][4])for z in cuts),
        actual_interrupts=dict(counts),minimum_ISR_SP=minimum,source_bound_audio_writers=dict(writers),nested_cohorts=rows,
        scope='Actualcombined101 realcold→nativeentrance/Ready2→earnedcapture1/firstD1AE2/terminal61/thaw62. Tracks completebusyMainCoCheckCode/selection/headercompare plus privateAnchor/FullBox/ScoreFlush envelopes. IRQonlyI0, actualhardwareFFNMIallreachedIstates; NmiSkippedonce andregularNMIexcluded. Fullprivate/R0..7/SMC/native/maps/AXYP/SP/foreground exact except sourcebound outeraudio clocks. Nestedphase everyreachedunmaskedaudio at deepestcohort. Coldcopy/readback/lateheadercommit/PrCopyLiveIRQ and finalPrincecanonical/menu/native admission remain separate.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),Path(F.__file__),Path(I.__file__),O/'native-combined-owner-v101-measurement.json',O/'native-combined-cold-v104-CPU.json',O/'native-combined-foreign-v105-CPU.json',R/'src/reset.s']})
    (O/f'native-combined-hot-v106-{args.phase}.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','phase','full_auth_and_source_foreground_shapes','I1_foreground_shapes','actual_interrupts','minimum_ISR_SP']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'native-combined-hot-v106-negative.json').write_text(json.dumps(dict(passed=False,error=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
