"""Add genuine FF NMI at I1 foreground contexts; retain the exact57 I0 pass."""
import inspect,json
from collections import Counter
from pathlib import Path
import check_bub_head_interrupts_1102_v57 as P
O,Q,N,address,R,sha=P.O,P.Q,P.N,P.address,P.R,P.sha

# Exact four control-domain changes, with no change to the actual ISR/state,
# audio writer, return-parity or foreground assertions already bound in57.
text=inspect.getsource(P.run)
changes={
    'cut=(c.pc,c.sp,m.rawtags[1],m.rawtags[2])':'cut=(c.pc,c.sp,m.rawtags[1],m.rawtags[2],int(bool(c.p&4)))',
    'if not c.p&4 and(active or bank==3 and newlo<=c.pc<newhi):':'if active or bank==3 and newlo<=c.pc<newhi:',
    'key=(c.pc,m.rawtags[1],m.rawtags[2])':'key=(c.pc,m.rawtags[1],m.rawtags[2],int(bool(c.p&4)))',
    'injected=True;assert not c.p&4':'injected=True;assert interrupt[0]==\'lagNMI\'or not c.p&4',
}
for before,after in changes.items():assert text.count(before)==1,before;text=text.replace(before,after)
before='cuts={};low=c.sp;';assert text.count(before)==1;text=text.replace(before,'cuts={};whole_I1={};whole_min=None;whole_steps=0;low=c.sp;')
before='        cut=(c.pc,c.sp,m.rawtags[1],m.rawtags[2],int(bool(c.p&4)))'
assert text.count(before)==1
text=text.replace(before,'''        whole_steps+=1
        whole_cut=(c.pc,c.sp,m.rawtags[1],m.rawtags[2],int(bool(c.p&4)))
        if whole_min is None or c.sp<whole_min[1]:whole_min=whole_cut
        if c.p&4:
            whole_key=(c.pc,m.rawtags[1],m.rawtags[2])
            if whole_key not in whole_I1 or c.sp<whole_I1[whole_key][1]:whole_I1[whole_key]=whole_cut
'''+before)
before='return dict(regs=';assert text.count(before)==1;text=text.replace(before,'return dict(whole_foreground_steps=whole_steps,whole_foreground_I1_cuts=sorted(whole_I1.values()),whole_foreground_min_context=whole_min,regs=')
env=dict(P.__dict__);exec(compile(text,str(Path(__file__)),'exec'),env);run=env['run']
state=P.state;audio=P.audio;I=P.I;seeds=P.seeds

def main():
    old,b,route,q,p,image=P.H.bundle();proof=O/'head-projection-v57-ISR.json';prior=json.loads(proof.read_text());assert prior['passed']and prior['memory_ROM_SHA256']==p['memory_ROM_SHA256']
    for name,digest in prior['bindings'].items():assert sha(R/name)==digest,name
    rows=[];minimum=224;count=0
    for identity,(m,cell)in enumerate(seeds(b,route)):
        z=N.fork(m);ref=run(z,p,q);expected=state(z);i0=[x for x in ref['cuts']if not x[4]];i1=[x for x in ref['cuts']if x[4]]
        assert len(i0)==prior['scenarios'][identity]['cuts']
        print('Head new I1 FF cohort',identity,len(i1),'wholeI1',len(ref['whole_foreground_I1_cuts']),'wholemin',ref['whole_foreground_min_context'],flush=True)
        for index,cut in enumerate(i1):
            z=N.fork(m);out=run(z,p,q,('lagNMI',cut));minimum=min(minimum,out['minimum_SP'])
            assert out['regs']==ref['regs']and state(z)==expected,(identity,cut)
            count+=1
            if index and index%100==0:print('Head I1 FF progress',identity,index,flush=True)
        rows.append(dict(identity=identity,all_NMI_contexts=len(ref['cuts']),reused_I0_contexts=len(i0),new_I1_contexts=len(i1),deepest_I1_foreground_SP=min((x[1]for x in i1),default=None),whole_foreground_steps=ref['whole_foreground_steps'],whole_foreground_I1_cuts=ref['whole_foreground_I1_cuts'],whole_foreground_min_context=ref['whole_foreground_min_context']))
    out=dict(passed=True,CPU_only=True,ROM_written=False,installed=False,memory_ROM_SHA256=p['memory_ROM_SHA256'],new_I1_FF_NMIs=count,minimum_new_I1_ISR_SP=minimum,scenarios=rows,reused_I0_IRQ_and_FF=prior['actual_interrupts'],
        scope='NMI ignores foreground I. Unconditional status collection covers every executed instruction in the whole actual FF foreground, not only the contact window. Any reached I1 watched context uses actual FF handler with all57 full-state/SMC/audio assertions. Zero I1 is a measured finite-domain result, not forced success: whole minimumSP150 is outside the watched window whose deepestSP156. Existing57 I0 IRQ/FF pass is hash-bound and reused without repeating it. IRQ itself remains I0; nested61 gathers every watched FF context including queued bump/grow paths.',
        bindings={str(f.relative_to(R)):sha(f)for f in[Path(__file__),Path(P.__file__),proof,O/'head-projection-v55.json',O/'head-projection-v55-image.bin']})
    (O/'head-projection-v60-NMI-I1.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

if __name__=='__main__':main()
