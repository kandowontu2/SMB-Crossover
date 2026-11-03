"""Actual IRQ/FF and nested audio across new pending/anchored source lifetime.

Uses the private90 current-owner memory model, not a cartridge or emulator.
"""
import argparse
import collections
import inspect
import json
from pathlib import Path
import check_dkjr_anchored_lifetime_1103_v95 as F
import check_dkjr_native_service_nested_1102_v53 as I

A,R,O,W,N=F.A,F.R,F.O,F.W,F.N
timers,state,branches,audio_sites,AUDIO=I.timers,I.state,I.branches,I.audio_sites,I.AUDIO
text=I.text.replace("service_names = ['DkjrNativeAwardSourcePoints', 'DkjrNativeFruitCollision']",
    "service_names = ['DkNativeAnchorReady','DkFullBox','DkjrNativeAwardSourcePoints','DkjrNativeFruitCollision','DkScoreFlush']")
assert text!=I.text
text=text.replace('if bank == 3 and c.pc in entries:','if bank in [2,3] and c.pc in entries:')
exec(compile(text,__file__,'exec'),globals())


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['direct','nested'],default='direct');args=ap.parse_args()
    b,m,L,q=F.fixture();cohorts={};shapes={}
    # Preserve the exact genuine entrance setup but stop before its first
    # GameCore. The new INC Ready and import loops are therefore interrupted
    # as actually reached; Ready2 is never seeded into this cohort.
    enter=inspect.getsource(F.E.run)
    old="    N.invoke(m,'GameCoreRoutine',a=83,x=0,y=0,p=0x21)"
    assert enter.count(old)==1
    enter=enter.replace(old,'    # First GameCore is executed below with actual interrupts.')
    env=dict(F.E.__dict__);exec(compile(enter,__file__,'exec'),env)
    pending,_,_=env['run'](b);assert pending.ram[2][0x8fe]==1
    N.put(pending,NmiDisable=255)
    ref=run(pending,L);assert pending.ram[2][0x8fe]==2
    # Recreate its pre-call seed without a RAM-ready repair.
    seed,_,_=env['run'](b);N.put(seed,NmiDisable=255)
    cohorts[0]=(seed,ref,state(pending))
    for index in range(1,63):
        N.put(m,FrameCounter=index,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0,NmiDisable=255)
        timers(m);seed=N.fork(m);ref=run(m,L)
        if index in [1,2,61,62]:cohorts[index]=(seed,ref,state(m))
    for index,(seed,ref,expected)in cohorts.items():
        for cut in ref['cuts']:
            key=(cut[0],cut[2],cut[3],cut[4])
            if key not in shapes or cut[1]<shapes[key][1][1]:shapes[key]=(index,cut)
    cuts=sorted(shapes.values(),key=lambda z:(z[1][1],z[0],z[1][0]))
    counts=collections.Counter();minimum=255;writers=collections.Counter();nested_rows=[]
    print('DK anchored'+args.phase,'foreground shapes',len(cuts),'I1',sum(bool(z[1][4])for z in cuts),flush=True)
    if args.phase=='direct':
        for kind in ['IRQ','lagNMI']:
            chosen=[z for z in cuts if kind!='IRQ'or not z[1][4]]
            for index,(epoch,cut)in enumerate(chosen):
                seed,ref,expected=cohorts[epoch];z=N.fork(seed)
                result=run(z,L,(kind,cut));minimum=min(minimum,result['minimum_SP'])
                assert result['regs']==ref['regs']and state(z)==expected,('anchored native continuation',kind,epoch,cut)
                counts[kind]+=1;writers.update(result['audio_writers'])
                if index and index%250==0:print('DK anchored direct',kind,index,'/',len(chosen),flush=True)
    else:
        for epoch,(seed,ref,expected)in cohorts.items():
            cut=min(ref['cuts'],key=lambda z:(z[1],z[0]));z=N.fork(seed)
            lag=run(z,L,('lagNMI',cut));nested=sorted(lag['nested_shapes'],key=lambda z:(z[1],z[0]))
            assert lag['regs']==ref['regs']and state(z)==expected
            print('DK anchored nested',epoch,len(nested),flush=True)
            for index,inner in enumerate(nested):
                z=N.fork(seed);result=run(z,L,('lagNMI',cut),nested=inner)
                minimum=min(minimum,result['minimum_SP'])
                assert result['regs']==ref['regs']and state(z)==expected,('anchored nested continuation',epoch,cut,inner)
                counts['nestedIRQ']+=1;writers.update(result['audio_writers'])
                if index and index%300==0:print('DK anchored nested progress',epoch,index,flush=True)
            nested_rows.append(dict(epoch=epoch,foreground_cut=cut,actual_nested_IRQ=len(nested)))
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        memory_only_SHA256=A.sha(b['raw']),phase=args.phase,genuine_NmiDisable=255,
        foreground_shapes=len(cuts),I1_foreground_NMI_shapes=sum(bool(z[1][4])for z in cuts),
        actual_interrupts=dict(counts),minimum_ISR_SP=minimum,source_bound_audio_writers=dict(writers),nested_cohorts=nested_rows,
        scope='Privatecurrent90 actualcold/unchangednativeentrance plus capture1/firstD1AE2/terminal61/thaw62. FirstvalidReady1→2/import loops, D2BD/fullbox, sourcefruit and nativeScoreFlush run inside completeGameCore. IndependentIRQ onlyI0; hardwareFF NMI includes everyreachedI1 and incrementsNmiSkipped once/excludesregularNMI. Nestedphase covers everyreached unmasked nativeaudio cut at each deepest cohort. Full private/R0..7/SMC/native/foreground equality except source-bound outeraudio clocks. No finalPrince149 rebind/sharedrouting/menu/native admission.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),Path(F.__file__),Path(I.__file__),O/'native-owner-proposal-v90.json',O/'native-entrance-v89-layout.json',O/'native-ready-domains-v94-CPU.json',O/'native-anchored-lifetime-v97-CPU.json',R/'src/reset.s']})
    (O/f'native-anchored-v98-{args.phase}.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','phase','foreground_shapes','I1_foreground_NMI_shapes','actual_interrupts','minimum_ISR_SP']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'native-anchored-v98-negative.json').write_text(json.dumps(dict(passed=False,error=repr(error),ROM_written=False,native_owner_admitted=False),indent=2)+'\n');raise
