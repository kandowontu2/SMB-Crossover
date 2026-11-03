"""Bounded per-identity FF gather, then deepest-handler nested IRQ replay.

Only compact code-address/context aggregates are persisted, never RAM fixtures.
"""
import argparse,json
from collections import Counter
from pathlib import Path
import check_bub_head_pending_map_1102_v63 as K
H=K.H;O,N,R,sha=H.O,H.N,H.R,H.sha
SOUND=['Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue','AreaMusicQueue','EventMusicQueue','Square1SoundBuffer','Square2SoundBuffer','NoiseSoundBuffer','Squ1_SfxLenCounter','Squ2_SfxLenCounter','Sfx_SecondaryCounter']

def sounds(m):return {n:N.get(m,n)for n in SOUND}

def inputs():
    _,b,route,q,p,_=H.P.H.bundle();run,_=K.patched_run();proof=O/'head-projection-v60-NMI-I1.json'
    x=json.loads(proof.read_text());assert x['passed']and x['memory_ROM_SHA256']==p['memory_ROM_SHA256']
    for name,digest in x['bindings'].items():assert sha(R/name)==digest,name
    return b,route,q,p,run

def bindings():
    return {str(f.relative_to(R)):sha(f)for f in[Path(__file__),Path(K.__file__),Path(H.__file__),O/'head-projection-v60-NMI-I1.json',O/'head-projection-v63-pending-map.json',O/'head-projection-v55.json',O/'head-projection-v55-image.bin']}

def gather(identity):
    destination=O/f'head-projection-v64-gather-{identity}.json';assert not destination.exists()
    b,route,q,p,run=inputs();seed,_=H.seeds(b,route)[identity];z=N.fork(seed);ref=run(z,p,q);expected=H.state(z)
    actual=N.NesMPU;winners={};sound_profiles={};context=None;minimum=224;count=0
    class Trace(actual):
        def nmi(self):
            self.lag_return=(self.pc,self.sp);sound_profiles[context]=sounds(self.memory)
            return super().nmi()
        def step(self):
            ret=getattr(self,'lag_return',None)
            if ret is not None and(self.pc,self.sp)==ret:self.lag_return=None;ret=None
            if ret is not None and not self.p&4:
                m=self.memory;cut=(self.pc,self.sp,m.rawtags[1],m.rawtags[2]);key=(cut[0],cut[2],cut[3])
                if key not in winners or self.sp<winners[key][0][1]:winners[key]=(cut,context)
            return super().step()
    N.NesMPU=Trace
    try:
        print('Head phased gather',identity,'contexts',len(ref['cuts']),flush=True)
        for index,fore in enumerate(ref['cuts']):
            context=tuple(fore);z=N.fork(seed);out=run(z,p,q,('lagNMI',context));minimum=min(minimum,out['minimum_SP'])
            assert out['regs']==ref['regs']and H.state(z)==expected,(identity,context)
            count+=1
            if count%250==0:print('Head phased gather progress',identity,count,flush=True)
    except Exception as error:
        (O/f'head-projection-v64-gather-negative-{identity}.json').write_text(json.dumps(dict(passed=False,identity=identity,context=context,exception=repr(error),completed=count,memory_ROM_SHA256=p['memory_ROM_SHA256']),indent=2)+'\n');raise
    finally:N.NesMPU=actual
    chosen=sorted(set(fore for cut,fore in winners.values()))
    out=dict(passed=True,nested_qualified=False,CPU_only=True,ROM_written=False,memory_ROM_SHA256=p['memory_ROM_SHA256'],identity=identity,actual_FF_NMIs=count,minimum_FF_SP=minimum,
        winners=[dict(handler_cut=cut,foreground_cut=fore)for cut,fore in winners.values()],
        chosen_sound=[dict(foreground_cut=fore,live_sound=sound_profiles[fore])for fore in chosen],
        source_bound_pending_maps=dict(K.PENDING),scope='All watched head FF contexts plus every actual post-head instruction through GameCore return; deepest I0 lag-handler SP retained per PC/A/C. No RAM fixture stored; replay reconstructs the exact declared source/native arena.',bindings=bindings())
    destination.write_text(json.dumps(out,separators=(',',':'))+'\n')
    print(json.dumps({k:out[k]for k in['passed','identity','actual_FF_NMIs','minimum_FF_SP','source_bound_pending_maps']}));print('Handler keys',len(winners),'chosen contexts',len(chosen),flush=True)

def replay():
    destination=O/'head-projection-v64-nested.json';assert not destination.exists()
    b,route,q,p,run=inputs();winners={};profiles={};proofs=[];total=0
    for identity in[0,1]:
        proof=O/f'head-projection-v64-gather-{identity}.json';proofs.append(proof);x=json.loads(proof.read_text())
        assert x['passed']and x['identity']==identity and x['memory_ROM_SHA256']==p['memory_ROM_SHA256']
        for name,digest in x['bindings'].items():assert sha(R/name)==digest,name
        total+=x['actual_FF_NMIs']
        for row in x['chosen_sound']:profiles[identity,tuple(row['foreground_cut'])]=row['live_sound']
        for row in x['winners']:
            cut=tuple(row['handler_cut']);key=(cut[0],cut[2],cut[3]);fore=tuple(row['foreground_cut'])
            if key not in winners or cut[1]<winners[key][0][1]:winners[key]=(cut,identity,fore)
    seeds=[]
    for identity,(seed,cell)in enumerate(H.seeds(b,route)):
        z=N.fork(seed);reference=run(z,p,q);seeds.append((seed,reference,H.state(z)))
    actual=N.NesMPU;wanted=None;context=None;minimum=224;count=0;confirmed=False;checked_sound=None
    class Trace(actual):
        def nmi(self):
            nonlocal checked_sound
            self.lag_return=(self.pc,self.sp);checked_sound=sounds(self.memory)
            assert checked_sound==profiles[context],('Winning live audio profile changed',context)
            return super().nmi()
        def step(self):
            nonlocal minimum,confirmed
            ret=getattr(self,'lag_return',None)
            if ret is not None and(self.pc,self.sp)==ret:self.lag_return=None;ret=None
            m=self.memory
            cut=(self.pc,self.sp,m.rawtags[1],m.rawtags[2])
            if ret is not None and not self.p&4 and cut==wanted and not confirmed:
                confirmed=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);before=H.state(m);audio=H.audio(m)
                self.irq()
                for _ in range(20000):
                    minimum=min(minimum,self.sp)
                    if(self.pc,self.sp)==(regs[5],regs[4]):break
                    assert m[self.pc]!=0,('Nested BRK',context,cut,hex(self.pc),self.sp);super().step()
                else:raise AssertionError(('Nested IRQ bound',context,cut))
                assert(self.a,self.x,self.y,self.p&0xef,self.sp,self.pc)==(*regs[:3],regs[3]&0xef,*regs[4:])
                after=H.state(m)
                if after!=before or H.audio(m)!=audio:
                    diagnostic=dict(passed=False,context=context,wanted=wanted,minimum_SP=minimum,
                        maps=[before[3],after[3]],scratch=[list(before[1]),list(after[1])],SMC=[list(before[2]),list(after[2])],
                        RAM_differences=[dict(bank=k,offset=i,old=a,new=v)for k,(aa,bb)in enumerate(zip(before[0],after[0]))for i,(a,v)in enumerate(zip(aa,bb))if a!=v][:16],
                        native_differences=[dict(address=i+0x200,old=a,new=v)for i,(a,v)in enumerate(zip(before[4],after[4]))if a!=v][:16],audio=[audio,H.audio(m)],live_sound=checked_sound)
                    (O/'head-projection-v64-nested-negative.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
                    raise AssertionError(('Nested IRQ state',context,wanted,minimum))
            return super().step()
    N.NesMPU=Trace
    try:
        print('Head phased nested keys',len(winners),'gathered FF',total,flush=True)
        for index,(cut,identity,fore)in enumerate(sorted(winners.values(),key=lambda x:x[0][1])):
            wanted=cut;context=(identity,fore);confirmed=False;seed,ref,expected=seeds[identity];z=N.fork(seed)
            out=run(z,p,q,('lagNMI',fore))
            assert confirmed and out['regs']==ref['regs']and H.state(z)==expected,(context,wanted)
            count+=1
            if count%250==0:print('Head phased nested progress',count,flush=True)
    finally:N.NesMPU=actual
    chosen=sorted(set((identity,fore)for cut,identity,fore in winners.values()))
    out=dict(passed=True,CPU_only=True,ROM_written=False,installed=False,memory_ROM_SHA256=p['memory_ROM_SHA256'],all_post_head_foreground_instructions_included=True,
        counts=dict(all_foreground_lag=total,nested_IRQ=count),minimum_nested_IRQ_SP=minimum,
        winning_foreground_contexts=[dict(identity=identity,foreground_cut=fore,live_sound=profiles[identity,fore])for identity,fore in chosen],
        source_bound_pending_maps=dict(K.PENDING),scope='Source-bound57 I0 pass and60 whole-foreground zero-I1 measurement retained. Both per-identity gathers cover every watched contact/bump cut plus every post-head instruction through return. Every actual I0 lag-audio PC/A/C receives IRQ at the deepest measured foreground/handler context, including active bump/grow queues and renderer minimum. Native IRQ preserves all three audio clocks; native/private/scratch/SMC/maps/AXYP/SP strict. Exact63 pending C-bank macro bus consume, not arbitrary mapper normalization.',
        bindings={**bindings(),**{str(f.relative_to(R)):sha(f)for f in proofs}})
    destination.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['gather','replay'],required=True);parser.add_argument('--identity',type=int,choices=[0,1]);args=parser.parse_args()
    if args.phase=='gather':assert args.identity is not None;gather(args.identity)
    else:replay()
