"""Actual current source-backed changed body-helper seams under IRQ/FF NMI."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_body_cold_1103_v181 as C
import check_prince_live_policy_final_1103_v170 as OLD
import check_prince_lag_nested_irq_1102_v92 as NEST
V,N,I,O=C.V,C.N,C.I,C.O


def setup():
    base,q=C.M.image();V.M.image=lambda:(base,q);V.loaded=lambda:C.loaded(base)
    e,text=OLD.environment()
    rows=json.loads((O/'measurement.json').read_text())['patches']
    runtime_call=rows[0]['CPU'];public_call=rows[1]['CPU']
    marker="  if interrupt is not None and not injected and cut==interrupt[1]:"
    assert text.count(marker)==1
    extra=f"  if N.get(m,'NmiDisable')==255 and (bank==3 and (0xbdc3<=c.pc<0xbde1 or {runtime_call}<=c.pc<{runtime_call+4}) or bank==2 and {public_call}<=c.pc<{public_call+4}):cuts.add(cut)\n"
    text=text.replace(marker,extra+marker);exec(compile(text,str(Path(__file__)),'exec'),e)
    run=e['run']
    def filtered(m,target,lab,interrupt=None):
        result=run(m,target,lab,interrupt)
        result['cuts']={c for c in result['cuts']if 0xbdc3<=c[0]<0xbde1 or runtime_call<=c[0]<runtime_call+4 or public_call<=c[0]<public_call+4}
        return result
    e['run']=filtered
    _,seed,lab=C.first8(base);N.put(seed,ObjectMetasprite=0x91)
    cases=[('genuine-first8-stale-descriptor',seed,'GameLoop')]
    warm=N.fork(seed);run(warm,'GameLoop',lab)
    art=json.loads((V.O/'source-art.json').read_text())
    pose=next(p for p in art['poses']if any(x['pattern_pair']//32==30 for x in p['parts_8x16']))
    warm.ram[2][0x617]=pose['source_frame'];warm.ram[2][0x615]=pose['source_facing'];warm.ram[2][0xa6]=1
    cases.append(('typed-original-high-page-pose',warm,'GameLoop'))
    return base,q,e,lab,cases,text


def main():
    base,q,e,lab,cases,text=setup();counts={};rows=[];minimum=255
    normalize=V.A.U.C.V.normalized_state;fold=V.A.U.V.fold
    for name,seed,target in cases:
        m=N.fork(seed);ref=e['run'](m,target,lab);want=normalize(m);cuts=fold(ref['cuts']);assert cuts
        one={}
        for kind in ['IRQ','lagNMI']:
            for cut in cuts:
                if kind=='IRQ'and cut[3]:continue
                now=N.fork(seed);out=e['run'](now,target,lab,(kind,cut))
                assert out['regs']==ref['regs']and normalize(now)==want,(name,kind,cut)
                minimum=min(minimum,out['minSP']);counts[kind]=counts.get(kind,0)+1;one[kind]=one.get(kind,0)+1
        rows.append(dict(name=name,cuts=len(cuts),I1_cuts=sum(bool(c[3])for c in cuts),counts=one,foreground_minimum_SP=ref['minSP']))
        print('Actual new body helper IRQ/FF',rows[-1],flush=True)
    # Reuse the verified genuine FF handler/nested-IRQ machine assertions;
    # only the foreground finite scenarios/cuts are changed here.
    source=inspect.getsource(NEST.main)
    a=source.index(' e=environment();b,m,lab=V.loaded()');z=source.index(' actual=N.NesMPU;',a)
    source=source[:a]+' e=FINAL_ENV;lab=FINAL_LAB;scenarios=FINAL_CASES\n'+source[z:]
    source=source.replace('key=(cut[0],cut[2],cut[3])','key=cut[0]').replace("cuts=V.fold_cuts(ref['cuts'])","cuts=FINAL_FOLD(ref['cuts'])")
    source=source.replace("counts['lag_NMI_gather']==1846","counts['lag_NMI_gather']==sum(len(FINAL_FOLD(row[0]['cuts']))for row in references)")
    source=source.replace('audio=m[0x7da];wr=','audio=m[0x7da];smack=m[0x7d8];wr=').replace('and audio==m[0x7da]and','and audio==m[0x7da]and smack==m[0x7d8]and')
    a=source.index(' files=[Path(__file__)');source=source[:a]+" return dict(counts=dict(counts),minimum_nested_IRQ_SP=minimum,handler_PC_winners=len(winners))\n"
    env=dict(NEST.__dict__,O=O,__file__=str(Path(__file__)),FINAL_ENV=e,FINAL_LAB=lab,FINAL_CASES=cases,FINAL_FOLD=fold)
    exec(compile(source,str(Path(NEST.__file__)),'exec'),env);nested=env['main']()
    result=dict(passed=True,CPU_only=True,source_code_injected=False,ROM_written=False,memory_SHA256=q['expected_memory_only_SHA256'],
                scenarios=rows,real_IRQ_genuine_FF_NMI=counts,minimum_SP=minimum,nested=nested,
                scope='Exact180 over granted116/83, real source-backed fullcold before each first8 fixture. Only changed private callsites/helper PCs are added/replayed; every actual I0 supports hardwareIRQ and every I0/I1 supports genuineFFNMI. Existing harness asserts actualFF lag branch/INC and no regular branch. One genuine initialstage/Main stale-descriptor fixture plus an explicit legal original high-page pose retained in phase1 test upper=2. Deepest actual reached laghandlerPC gets IRQ with full SMC/private/R0..7/maps/AXYP/SP equality. Unchanged historical/source/native/full83 paths retain prior grants, not recounted as new coverage. No native hardware/geometry/fullstage/armed/audio claim.',
                bindings={str(p.relative_to(R)):C.M.B.sha(p)for p in [Path(__file__),Path(C.__file__),Path(OLD.__file__),Path(NEST.__file__),O/'body-manifest-v180.json',O/'body-owner.s',R/'docs/qa/allocations/combined-owner-auth-1103-v116.json',R/'src/reset.s']})
    (O/'body-ISR-v183.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k!='bindings'}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'body-ISR-negative-v183.json').write_text(json.dumps(dict(passed=False,error=repr(error)),indent=2)+'\n');raise
