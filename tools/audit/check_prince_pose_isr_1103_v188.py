"""Bounded changed-private-path IRQ, actual FF-NMI and deepest nested IRQ."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit')]
import check_prince_pose_reservation_1103_v186 as A
import check_prince_live_policy_final_1103_v170 as OLD
import check_prince_lag_nested_irq_1102_v92 as NEST
M,V,N,I,O=A.M,A.V,A.N,A.I,A.O


def setup():
    base,q=M.image();source=json.loads((O/'pose-source.json').read_text())
    seed,_=A.C.C.cold(base,38)
    V.M.image=lambda:(base,q)
    V.loaded=lambda:A.loaded(base,seed)
    e,text=OLD.environment()
    call=source['upper_call_CPU'];store=source['count_store_CPU']
    runtime=(O/'pose-runtime.bin').read_bytes()
    # The live renderer no longer initializes the unused native input-A.
    # Trace its actual remaining setup and FarCallCommon, not a former PC.
    needle=bytes.fromhex('a900a9ba8d6c01a9a58d6d01a984205a01')
    sites=[i+0xa000 for i in range(len(runtime)) if runtime[i:i+len(needle)]==needle]
    assert len(sites)==1;native_setup=sites[0]
    public=json.loads((M.OLD.O/'measurement.json').read_text())['patches'][1]['CPU']
    ranges=[(3,store,store+4),(3,call,call+4),(3,0xbdc3,0xbde1),
            (3,native_setup,native_setup+len(needle)),(2,public,public+4)]
    condition=' or '.join(f'(bank=={bank} and {start}<=c.pc<{end})' for bank,start,end in ranges)
    marker="  if interrupt is not None and not injected and cut==interrupt[1]:"
    assert text.count(marker)==1
    text=text.replace(marker,f"  if N.get(m,'NmiDisable')==255 and ({condition}):cuts.add(cut)\n"+marker)
    exec(compile(text,str(Path(__file__)),'exec'),e)
    run=e['run']
    def filtered(m,target,lab,interrupt=None):
        result=run(m,target,lab,interrupt)
        result['cuts']={c for c in result['cuts'] if any(start<=c[0]<end for _,start,end in ranges)}
        return result
    e['run']=filtered
    _,first,lab=A.first8(base,seed)
    N.put(first,ObjectMetasprite=0x91)
    cases=[('actual-first8-five-part-pose',first,'GameLoop')]
    warm=N.fork(first);run(warm,'GameLoop',lab)
    art=json.loads((V.O/'source-art.json').read_text())
    pose=max(art['poses'],key=lambda p:(len(p['parts_8x16']),max(x['pattern_pair']//32 for x in p['parts_8x16'])))
    warm.ram[2][0x617]=pose['source_frame'];warm.ram[2][0x615]=pose['source_facing']
    warm.ram[2][0xa6]=1
    cases.append(('typed-original-thirteen-part-pose',warm,'GameLoop'))
    return base,q,e,lab,cases,ranges


def main():
    assert json.loads((O/'pose-CPU-v187.json').read_text())['passed']
    base,q,e,lab,cases,ranges=setup()
    counts={};rows=[];minimum=255
    normalize=V.A.U.C.V.normalized_state;fold=V.A.U.V.fold
    for name,seed,target in cases:
        m=N.fork(seed);ref=e['run'](m,target,lab);want=normalize(m)
        cuts=fold(ref['cuts']);assert cuts
        one={}
        for kind in ['IRQ','lagNMI']:
            for cut in cuts:
                if kind=='IRQ' and cut[3]:continue
                now=N.fork(seed);out=e['run'](now,target,lab,(kind,cut))
                assert out['regs']==ref['regs'] and normalize(now)==want,(name,kind,cut)
                minimum=min(minimum,out['minSP']);counts[kind]=counts.get(kind,0)+1
                one[kind]=one.get(kind,0)+1
        rows.append(dict(name=name,cuts=len(cuts),I1_cuts=sum(bool(c[3]) for c in cuts),
                         counts=one,foreground_minimum_SP=ref['minSP']))
        print('Current188 changed-private-path',rows[-1],flush=True)
    source=inspect.getsource(NEST.main)
    start=source.index(' e=environment();b,m,lab=V.loaded()')
    end=source.index(' actual=N.NesMPU;',start)
    source=source[:start]+' e=FINAL_ENV;lab=FINAL_LAB;scenarios=FINAL_CASES\n'+source[end:]
    source=source.replace('key=(cut[0],cut[2],cut[3])','key=cut[0]').replace("cuts=V.fold_cuts(ref['cuts'])","cuts=FINAL_FOLD(ref['cuts'])")
    source=source.replace("counts['lag_NMI_gather']==1846","counts['lag_NMI_gather']==sum(len(FINAL_FOLD(row[0]['cuts']))for row in references)")
    source=source.replace('audio=m[0x7da];wr=','audio=m[0x7da];smack=m[0x7d8];wr=').replace('and audio==m[0x7da]and','and audio==m[0x7da]and smack==m[0x7d8]and')
    start=source.index(' files=[Path(__file__)')
    source=source[:start]+" return dict(counts=dict(counts),minimum_nested_IRQ_SP=minimum,handler_PC_winners=len(winners))\n"
    env=dict(NEST.__dict__,O=O,__file__=str(Path(__file__)),FINAL_ENV=e,FINAL_LAB=lab,
             FINAL_CASES=cases,FINAL_FOLD=fold)
    exec(compile(source,str(Path(NEST.__file__)),'exec'),env)
    nested=env['main']()
    result=dict(passed=True,CPU_only=True,ROM_written=False,source_code_injected=False,
                memory_SHA256=q['expected_memory_only_SHA256'],current_parent_SHA256=q['parent_SHA256'],
                scenarios=rows,real_IRQ_genuine_FF_NMI=counts,minimum_SP=minimum,nested=nested,
                exact_changed_private_ranges=ranges,
                scope='Actualca90 five-owner sharedcold precedes both candidate fixtures. Original five-part first8 and explicit legal maximum13part pose replay only changed private count-store, shifted upper call, existing source-funded ownership helper, removed native-A setup and public graphics call. HardwareIRQ only at I0; genuineFF NMI at all reached I0/I1 cuts, with actual lagbranch/INC asserted. Deepest reached real FF handler PCs receive nestedIRQ with private/SMC/R0..7/maps/AXYP/SP exact. Unchanged shared/foreign/cold/retire/hot paths reuse their exact-source prior qualification; no expanded native/fullstage/audio claim.',
                bindings={p.relative_to(R).as_posix():M.sha(p) for p in [Path(__file__),Path(A.__file__),
                    Path(M.__file__),Path(OLD.__file__),Path(NEST.__file__),O/'pose-manifest.json',
                    O/'pose-CPU-v187.json',O/'pose-source.json',R/'src/reset.s']})
    (O/'pose-ISR-v188.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='bindings'}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        p=O/'pose-ISR-negative-v188.json'
        if not p.exists():p.write_text(json.dumps(dict(passed=False,error=repr(error)),indent=2)+'\n')
        raise
