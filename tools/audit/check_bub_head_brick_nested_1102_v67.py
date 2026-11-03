"""Actual FF and nested IRQ at additional plain-brick audio/profile minima."""
import argparse,json
from pathlib import Path
import check_bub_head_brick_profiles_1102_v66 as B
P,H,K,N,O,R,sha=B.P,B.H,B.K,B.N,B.O,B.R,B.sha


def inputs():
    b,route,q,p,run=P.inputs();proof=O/'head-projection-v66-brick-profiles.json'
    x=json.loads(proof.read_text());assert x['passed']and x['memory_ROM_SHA256']==p['memory_ROM_SHA256']
    for name,digest in x['bindings'].items():assert sha(R/name)==digest,name
    # A common callback PC/SP/map can occur both before and after the head
    # transaction. This followup targets the post-head occurrence explicitly,
    # rather than injecting at an earlier matching tuple with empty SFX.
    original=H.text
    before='if interrupt and not injected and cut==interrupt[1]:'
    assert original.count(before)==1
    H.text=original.replace(before,'if interrupt and not injected and headreturn is not None and not active and cut==interrupt[1]:')
    try:run,_=K.patched_run()
    finally:H.text=original
    return b,route,q,p,run,x


def bindings():
    return {**B.bindings(),**{str(f.relative_to(R)):sha(f)for f in[Path(__file__),O/'head-projection-v66-brick-profiles.json']}}


def gather():
    destination=O/'head-projection-v67-brick-gather.json';assert not destination.exists()
    b,route,q,p,run,profiles=inputs();actual=N.NesMPU;context=None;winners={};minimum=224;count=0
    seeds={(row['identity'],row['powered']):B.seed(b,route,row['identity'],row['powered'])[0]for row in profiles['scenarios']}
    class Trace(actual):
        def nmi(self):
            self.lag_return=(self.pc,self.sp)
            assert P.sounds(self.memory)==context[3],('Brick winning audio changed',context)
            return super().nmi()
        def step(self):
            ret=getattr(self,'lag_return',None)
            if ret is not None and(self.pc,self.sp)==ret:self.lag_return=None;ret=None
            if ret is not None and not self.p&4:
                m=self.memory;cut=(self.pc,self.sp,m.rawtags[1],m.rawtags[2])
                # Both forms retain independent witnesses, including shared
                # handler addresses with a distinct active bump/shatter SFX.
                key=(context[0],cut[0],cut[2],cut[3])
                if key not in winners or self.sp<winners[key][0][1]:winners[key]=(cut,context)
            return super().step()
    N.NesMPU=Trace
    try:
        for row in profiles['scenarios']:
            identity,powered=row['identity'],row['powered'];seed=seeds[identity,powered]
            z=N.fork(seed);ref=run(z,p,q);expected=H.state(z)
            for item in row['minima']:
                fore=tuple(item['foreground_cut']);assert not fore[4]
                context=(powered,identity,fore,item['live_sound']);z=N.fork(seed)
                out=run(z,p,q,('lagNMI',fore));minimum=min(minimum,out['minimum_SP'])
                assert out['regs']==ref['regs']and H.state(z)==expected,(powered,identity,fore)
                count+=1
            print('Brick FF minima complete',powered,identity,len(row['minima']),flush=True)
    finally:N.NesMPU=actual
    result=dict(passed=True,nested_qualified=False,CPU_only=True,ROM_written=False,
        memory_ROM_SHA256=p['memory_ROM_SHA256'],actual_FF_NMIs=count,minimum_FF_SP=minimum,
        winners=[dict(handler_cut=cut,powered=ctx[0],identity=ctx[1],foreground_cut=ctx[2],live_sound=ctx[3])for cut,ctx in winners.values()],
        source_bound_pending_maps=dict(K.PENDING),scope='Distinct measured plain-brick post-head minima only, both identities and native small/bump versus genuine mushroom-powered shatter. All actual post-head instructions were measured in66; each sound queue/buffer/clock and A/C-map profile retains its deepest foreground SP. No question-block cohort repeated. Every reached I0 handler PC/A/C retains a deepest witness separately per form.',bindings=bindings())
    destination.write_text(json.dumps(result,separators=(',',':'))+'\n')
    print('Brick FF count',count,'minimum',minimum,'handler witnesses',len(winners),flush=True)


def replay(powered):
    form='powered'if powered else'small';destination=O/f'head-projection-v67-brick-nested-{form}.json';assert not destination.exists()
    b,route,q,p,run,profiles=inputs();proof=O/'head-projection-v67-brick-gather.json';g=json.loads(proof.read_text())
    assert g['passed']and g['memory_ROM_SHA256']==p['memory_ROM_SHA256']
    for name,digest in g['bindings'].items():assert sha(R/name)==digest,name
    seeds={}
    for identity in[0,1]:
        seed,_,_=B.seed(b,route,identity,powered);z=N.fork(seed);ref=run(z,p,q)
        seeds[identity]=(seed,ref,H.state(z))
    actual=N.NesMPU;wanted=None;context=None;minimum=224;count=0;confirmed=False
    class Trace(actual):
        def nmi(self):
            self.lag_return=(self.pc,self.sp)
            assert P.sounds(self.memory)==context['live_sound']
            return super().nmi()
        def step(self):
            nonlocal minimum,confirmed
            ret=getattr(self,'lag_return',None)
            if ret is not None and(self.pc,self.sp)==ret:self.lag_return=None;ret=None
            m=self.memory;cut=(self.pc,self.sp,m.rawtags[1],m.rawtags[2])
            if ret is not None and not self.p&4 and cut==wanted and not confirmed:
                confirmed=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);before=H.state(m);audio=H.audio(m)
                self.irq()
                for _ in range(20000):
                    minimum=min(minimum,self.sp)
                    if(self.pc,self.sp)==(regs[5],regs[4]):break
                    assert m[self.pc]!=0,('Brick nested BRK',form,context,hex(self.pc),self.sp)
                    super().step()
                else:raise AssertionError(('Brick nested IRQ bound',form,context))
                assert(self.a,self.x,self.y,self.p&0xef,self.sp,self.pc)==(*regs[:3],regs[3]&0xef,*regs[4:])
                after=H.state(m)
                if after!=before or H.audio(m)!=audio:
                    diagnostic=dict(passed=False,form=form,context=context,minimum_SP=minimum,
                        maps=[before[3],after[3]],scratch=[list(before[1]),list(after[1])],SMC=[list(before[2]),list(after[2])],
                        RAM_differences=[dict(bank=k,offset=i,old=a,new=v)for k,(aa,bb)in enumerate(zip(before[0],after[0]))for i,(a,v)in enumerate(zip(aa,bb))if a!=v][:16],
                        native_differences=[dict(address=i+0x200,old=a,new=v)for i,(a,v)in enumerate(zip(before[4],after[4]))if a!=v][:16],audio=[audio,H.audio(m)])
                    (O/f'head-projection-v67-brick-negative-{form}.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
                    raise AssertionError(('Brick nested parity',form,context))
            return super().step()
    rows=sorted((r for r in g['winners']if r['powered']==powered),key=lambda r:r['handler_cut'][1]);assert rows
    N.NesMPU=Trace
    try:
        print('Brick nested keys',form,len(rows),flush=True)
        for context in rows:
            wanted=tuple(context['handler_cut']);confirmed=False;seed,ref,expected=seeds[context['identity']];z=N.fork(seed)
            out=run(z,p,q,('lagNMI',tuple(context['foreground_cut'])))
            assert confirmed and out['regs']==ref['regs']and H.state(z)==expected,(form,context)
            count+=1
            if count%250==0:print('Brick nested progress',form,count,flush=True)
    finally:N.NesMPU=actual
    result=dict(passed=True,CPU_only=True,ROM_written=False,installed=False,memory_ROM_SHA256=p['memory_ROM_SHA256'],
        form=form,nested_IRQ=count,minimum_nested_IRQ_SP=minimum,actual_FF_profile_minima=g['actual_FF_NMIs'],
        source_bound_pending_maps=dict(K.PENDING),scope='Additional actual plain-brick post-head audio path. Genuine small bump or mushroom-powered shatter; deepest per-form I0 handler PC/A/C receives real IRQ, full private/native/R0..7/SMC/maps/AXYP/SP strict and IRQ preserves all three actual native audio clocks. Question-block64 qualification reused without rerun. No ROM or emulator claim.',
        bindings={**bindings(),str(proof.relative_to(R)):sha(proof)})
    destination.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='bindings'}),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['gather','replay'],required=True)
    parser.add_argument('--form',choices=['small','powered']);args=parser.parse_args()
    if args.phase=='gather':gather()
    else:assert args.form;replay(args.form=='powered')
