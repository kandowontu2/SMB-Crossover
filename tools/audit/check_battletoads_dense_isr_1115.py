"""Reached detached resolver cuts using actual cold/Main caller stack frames."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import plan_battletoads_dense_resolver_1115 as D

P,C,N,W=D.Previous,D.C,D.N,D.W


def run(parent,image):
    cpu=N.NesMPU;entries={};phase='rash-cold'
    class Capture(cpu):
        def step(self):
            m=self.memory;pc=self.pc;tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
            if m.bundle['raw']is image and(tag,pc)==(215,0xb08e):
                owner=N.get(m,'SelectedCharacter');offset=m[0x16c]-0x20
                if owner in(29,33):
                    assert 0<=offset<=105 and offset%3==0
                    key=owner,offset//3
                    if key not in entries or self.sp<entries[key][1]['sp']:
                        entries[key]=(N.fork(m),{n:getattr(self,n)for n in('pc','sp','a','x','y','p')},phase)
            return super().step()
    with patch.object(N,'NesMPU',Capture),patch.object(W.UI.F,'NesMPU',Capture):
        m=P.Base.cold(image)
        for phase,pad in(('rash-idle',0),('rash-right',1)):
            m.controller_pad=pad;P.Base.Frames.frame(m,whole_pass=True)
        phase='hogan-cold'
        with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(P.Base.symbols(image),0)
        for pad in([4]*3+[1]*4):W.UI.key(m,pad)
        assert W.UI.menu_name(m)[0]=='HULK HOGAN'
        start=W.UI.key(m,16)
        N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
        N.invoke(m,'PauseRoutine',a=0)
        for _ in range(700):
            if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
            m.controller_pad=0;P.Base.Frames.frame(m,cold=True)
        else:raise AssertionError('Actual Hogan cold bound')
        for phase,pad in(('hogan-idle',0),('hogan-right',1)):
            m.controller_pad=pad;P.Base.Frames.frame(m,whole_pass=True)
    assert{29,33}<={k[0]for k in entries}
    actual_entry_count=len(entries)
    # Corrupt header and foreign aliases are declared query components using
    # an actual owning caller frame, never actor/health/terrain fixtures.
    seed,regs,origin=entries[33,0]
    for owner in(27,31):
        z=N.fork(seed);N.put(z,SelectedCharacter=owner)
        entries[owner,0]=(z,dict(regs),'foreign-owner'+str(owner)+'-component')
    z=N.fork(seed);z.ram[3][0x1fe0]^=1
    entries[33,-1]=(z,dict(regs),'corrupt-BT-header-component')
    cuts={};minimum=255;endpoints={}
    def finish(m,r,entry_sp,endpoint,collect=False,kind=''):
        nonlocal minimum
        c=cpu(memory=m,pc=r['pc'])
        for n,v in r.items():setattr(c,n,v)
        for _ in range(100000):
            if(c.pc,c.sp)==endpoint:break
            if(c.pc,c.sp)==(0x15d,entry_sp):
                word=m[0x16c]+256*m[0x16d]
                if not(m[0x162]==224 and word in(0xb2cb,0xb2cd)):break
            tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
            in_code=0x408e<=c.pc<0x4100 or 0x5099<=c.pc<0x50d8 or(tag==224 and 0xb639<=c.pc<0xb646)
            if collect and in_code:
                key=(tag,c.pc,c.p&0xef)
                if key not in cuts or c.sp<cuts[key][1]['sp']:
                    cuts[key]=(N.fork(m),{n:getattr(c,n)for n in('pc','sp','a','x','y','p')},entry_sp,endpoint,kind)
            minimum=min(minimum,c.sp);assert m[c.pc],('Detached continuation BRK',kind,c.pc);c.step()
        else:raise AssertionError(('Detached continuation bound',kind,c.pc,c.sp))
        return m,(c.pc,c.sp,c.a,c.x,c.y,c.p&0xef)
    with patch.object(P,'router',D.router),patch.object(P,'helper',D.helper):
        for key,(seed,r,origin)in entries.items():
            m,labels=D.detached_seed(seed,True);m.flat_visible=labels['Visible'];r=dict(r,pc=0x408e)
            sp=r['sp'];ret=(m[0x100+sp+4]+256*m[0x100+sp+5]+1)&65535;endpoint=ret,sp+5
            kind=str(key[0])+':'+str(key[1])+':'+origin
            endpoints[kind]=finish(m,r,sp,endpoint,True,kind)[1]
    assert cuts and len(cuts)<=300,('Bounded reached instruction cuts',len(cuts))
    print('PROGRESS '+json.dumps(dict(actual_caller_entries=len(entries),reached_detached_cuts=len(cuts))),flush=True)
    counts=Counter();contexts=Counter();rows=[]
    for index,(key,(seed,r,entry_sp,endpoint,context))in enumerate(sorted(cuts.items())):
        assert N.get(seed,'NmiDisable')&128,('Nonbusy NMI arm requires separate reachable contract',key)
        expected=finish(N.fork(seed),r,entry_sp,endpoint)[1]
        for kind in(('NMI',)if r['p']&4 else('IRQ','NMI')):
            z=N.fork(seed);original_type=type(z)
            class NoUnitReads(original_type):
                def __getitem__(self,at):
                    if isinstance(at,int):assert not(0x4020<=at<0x4100 or 0x5099<=at<0x5148),('Native ISR read detached array',at)
                    return super().__getitem__(at)
            z.__class__=NoUnitReads;c=cpu(memory=z,pc=r['pc'])
            for n,v in r.items():setattr(c,n,v)
            original=tuple(getattr(c,n)for n in('pc','sp','a','x','y','p'));skipped=N.get(z,'NmiSkipped')
            c.irq()if kind=='IRQ'else c.nmi()
            for _ in range(200000):
                minimum=min(minimum,c.sp)
                if(c.pc,c.sp)==original[:2]:break
                assert not(0x4020<=c.pc<0x4100 or 0x5099<=c.pc<0x5148),'Actual ISR executed detached unit code'
                assert z[c.pc],('Actual vector BRK',key,kind,c.pc);c.step()
            else:raise AssertionError(('Actual vector return bound',key,kind))
            result=tuple(getattr(c,n)for n in('pc','sp','a','x','y','p'))
            assert result[:5]==original[:5]and result[5]&0xef==original[5]&0xef
            assert z.rawtags==seed.rawtags and bytes(z[0x15a:0x17b])==bytes(seed[0x15a:0x17b])
            assert bytes(z[0x101+r['sp']:0x200])==bytes(seed[0x101+r['sp']:0x200])
            assert(N.get(z,'NmiSkipped')-skipped)&255==int(kind=='NMI')
            z.__class__=original_type
            _,actual=finish(z,{n:getattr(c,n)for n in r},entry_sp,endpoint)
            assert actual==expected,('Post-ISR public continuation differs',key,kind,expected,actual)
            counts[kind]+=1;contexts[context,kind]+=1
        if index%32==31:print('PROGRESS '+json.dumps(dict(cuts=index+1,interrupts=dict(counts),minimum_SP=minimum)),flush=True)
        if len(rows)<24:rows.append(dict(context=context,tag=key[0],PC=key[1],P=r['p'],SP=r['sp']))
    return dict(actual_compiled_Rash_and_Hogan_cold_and_Main_entries=actual_entry_count,
        declared_foreign_and_corrupt_query_component_entries=len(entries)-actual_entry_count,
        total_reached_caller_frames=len(entries),reached_detached_instruction_cuts=len(cuts),
        actual_vector_counts=dict(counts),contexts=[dict(context=k,kind=t,cuts=n)for(k,t),n in sorted(contexts.items())],
        sparse_examples=rows,minimum_SP=minimum,exact_ISR_AXYP_SP_live_stack_SMC_maps=True,
        restored_public_continuation_endpoints_exact=True,regular_NMI_arms_forced=0,
        actual_IRQ_busy_NMI_handlers_unchanged=True,separate_vector_entries_not_nested_schedule_claim=True,
        declared_corrupt_header_and_foreign_owner_query_components=True,
        no_mounted_overlay=True,no_new_whole_image=True,whole_Main_or_native_cadence_claim=False)


if __name__=='__main__':
    parent,image,info=D.Input.load()
    def deny(*a,**kw):raise AssertionError('Detached ISR audit attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Packet.Frozen.Cold.Runner.Native,'run',deny):q=run(parent,image)
    q.update(info,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
