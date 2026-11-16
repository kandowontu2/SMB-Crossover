"""Current-acquire IRQ/busy-NMI reader closure and compiled raw-word ownership."""
from collections import Counter
from unittest.mock import patch
import audit_contra_force_palette_acquire_root_1116 as Root

W,N=Root.W,Root.N

def supplement(actual,b,q,cut):
    last=W.address(b,'SmFreezeLastBlue');base=N.NesMPU
    def tag(m,pc):return m.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
    ownership=[]
    for row in Root.scan_words(actual,last):
        at=row['file'];owners=[]
        for name,sym in b['syms'].items():
            if 'seg' not in sym or 'val' not in sym:continue
            g=b['segs'][sym['seg']]
            if 'ooffs' not in g or int(g.get('size','0'),0)==0:continue
            file=int(g['ooffs'],0)+int(sym['val'],0)-int(g['start'],0)
            if 0<=at-file<256:
                owners.append(dict(symbol=name,file=file,PC=int(sym['val'],0),delta=at-file,segment=g['name']))
        row=dict(row);row['nearest_compiled_symbols']=sorted(owners,key=lambda r:r['delta'])[:4]
        ownership.append(row)
    m=N.fork(cut['seed']);cpu=base(memory=m,pc=cut['pc'])
    for key in ('sp','a','x','y','p'):setattr(cpu,key,cut[key])
    tested=[];reads=[];minimum=255;skip_irq=0;map_transients=[]
    def tail(z,d):
        for j in range(10000):
            if (d.pc,d.sp,tag(z,d.pc))==(cut['return_PC'],cut['return_SP'],cut['return_tag']):return
            assert z[d.pc]!=0,('Tail BRK',d.pc,tag(z,d.pc));d.step()
        raise AssertionError('Complete real acquisition continuation bound')
    for number in range(10000):
        if number and (cpu.pc,cpu.sp,tag(m,cpu.pc))==(cut['return_PC'],cut['return_SP'],cut['return_tag']):break
        assert N.get(m,'NmiDisable')&128,'Only real busy acquisition cuts; regular-NMI arms not invented'
        for kind in ('NMI','IRQ'):
            if kind=='IRQ' and cpu.p&4:skip_irq+=1;continue
            z=N.fork(m);d=base(memory=z,pc=cpu.pc)
            for key in ('sp','a','x','y','p'):setattr(d,key,getattr(cpu,key))
            before=(d.pc,d.sp,d.a,d.x,d.y,d.p);banks=z.rawtags[:]
            smc=bytes(z[0x15a:0x17b]);live=bytes(z[0x101+d.sp:0x200])
            private=[bytes(z.ram[i]) for i in (1,2,3)]
            read=type(z).__getitem__;active=False;seen=[]
            def observed(obj,at):
                if active and obj is z and isinstance(at,int) and at==last:
                    seen.append(dict(kind=kind,cut_PC=cpu.pc,cut_bank=tag(m,cpu.pc),observed_PC=d.pc,bank=tag(z,d.pc)))
                return read(obj,at)
            with patch.object(type(z),'__getitem__',observed):
                if kind=='IRQ':z[0x5204]=128
                active=True
                if kind=='NMI':d.nmi()
                else:d.irq()
                low=d.sp
                for steps in range(100000):
                    if (d.pc,d.sp)==before[:2]:break
                    assert z[d.pc]!=0,('Current-acquire ISR BRK',kind,cpu.pc,d.pc)
                    low=min(low,d.sp);d.step()
                else:raise AssertionError(('Current-acquire ISR return bound',kind,cpu.pc,d.pc))
                active=False
            assert (d.pc,d.sp,d.a,d.x,d.y,d.p)==before
            assert bytes(z[0x15a:0x17b])==smc,dict(kind=kind,cut_number=number,
                cut_PC=hex(cpu.pc),cut_bank=tag(m,cpu.pc),cut_SP=cpu.sp,minimum_SP=low,
                disable_screen=N.get(m,'DisableScreenFlag'),engine=N.get(m,'GameEngineSubroutine'),
                LastBlue_reads=seen,banks_before=banks,banks_after=z.rawtags,
                SMC_delta=[(hex(0x15a+i),a,c) for i,(a,c) in enumerate(zip(smc,bytes(z[0x15a:0x17b]))) if a!=c])
            assert bytes(z[0x101+d.sp:0x200])==live
            assert [bytes(z.ram[i]) for i in (1,2,3)]==private
            if z.rawtags!=banks:
                # The baseline can be interrupted between caller bank capture
                # and publishing the next bank. Prove the whole real continuation
                # converges instead of calling this dead intermediate map live.
                row=dict(kind=kind,PC=cpu.pc,bank=tag(m,cpu.pc),before=banks,after=z.rawtags[:])
                ref=N.fork(m);e=base(memory=ref,pc=cpu.pc)
                for key in ('sp','a','x','y','p'):setattr(e,key,getattr(cpu,key))
                tail(ref,e);tail(z,d)
                assert (d.pc,d.sp,d.a,d.x,d.y,d.p)==(e.pc,e.sp,e.a,e.x,e.y,e.p)
                assert z.rawtags==ref.rawtags and bytes(z[0x15a:0x17b])==bytes(ref[0x15a:0x17b])
                assert bytes(z[0x101+d.sp:0x200])==bytes(ref[0x101+e.sp:0x200])
                assert [bytes(z.ram[i]) for i in (1,2,3)]==[bytes(ref.ram[i]) for i in (1,2,3)]
                protocol=list(range(0x7e0,0x7e7))+[0x7ea,0x7ff7,0x7ff8,0x7ff9,0x7ffa]
                assert [z[i] for i in protocol]==[ref[i] for i in protocol]
                row['complete_public_return_converges_without_allowlist']=True;map_transients.append(row)
            reads.extend(seen);minimum=min(minimum,low)
            tested.append(dict(kind=kind,PC=cpu.pc,bank=tag(m,cpu.pc),steps=steps))
        cpu.step()
    else:raise AssertionError('Foreground acquisition traversal bound')
    assert not reads,reads
    return dict(native_LastBlue_word_owners=ownership,
        reached_current_acquire_ISR=dict(counts=dict(Counter(r['kind'] for r in tested)),
            instruction_cuts=number,IRQ_masked_arms_skipped=skip_irq,minimum_SP=minimum,
            LastBlue_reads=reads,all_AXYP_SP_live_stack_33SMC_private_RAM123_immediate_exact=True,
            all_complete_public_maps_exact=True,intermediate_maps_requiring_actual_continuation=map_transients),
        scope='Existing actual instructions/real busy cuts only. No proposed marker code; regular NMI palette path remains a separate static contract.',outputs=0)

if __name__=='__main__':Root.main(supplement)
