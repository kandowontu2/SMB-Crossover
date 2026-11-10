"""Real-vector cuts in snapshots produced by the genuine FF loader execution."""
from pathlib import Path
import copy,hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_wram_host_controls_v3 as H
C=H.C;O=H.O
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def clone(m,c):
    n=list.__new__(type(m));list.extend(n,list.__iter__(m))
    for k,v in m.__dict__.items():setattr(n,k,v if k=='bundle'else copy.deepcopy(v))
    q=copy.copy(c);q.memory=n;return n,q


def reg(c):return(c.a,c.x,c.y,c.p,c.sp)


def main():
    out=O/'loader-isr-controls-v4.json';assert not out.exists()
    proof=dict(passed=False,native=False,RAM_preload=False,checks={})
    try:
        b=C.qualified(O/'candidate.nes');m=H.make(b);H.native_publish(m)
        c=H.start(m,'FwLoad');snapshots=[];seen=set();code_exec=[]
        names=['FwLoad','FwCheck','FwMapPage','FwCopy256','FwVerify256','FwPublishCookie',
               'FwRestorePPU','FwRestoreContext','X5PublishChr']
        entries={H.address(b,n):n for n in names}
        for step in range(500000):
            if c.pc==0x5b00:break
            pc=c.pc;op=bytes(m[pc:pc+3]);tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else -1
            assert not(pc>=0x8000 and tag==3),'Executing unverified RAM3 in loader'
            reason=None
            if pc in entries:
                key=(entries[pc],m[H.address(b,'R1')],c.x if entries[pc]=='FwPublishCookie'else 0)
                if key not in seen:reason=key
            elif op in [b'\x8d\x16\x51',b'\x8d\x30\x51',b'\x8d\x2b\x51',b'\x8d\x00\x20',
                         b'\x8d\x05\x20',b'\x8d\xe0\xdf',b'\x9d\xe0\xdf']:
                key=(pc,m[H.address(b,'R1')],c.x if op==b'\x9d\xe0\xdf'else c.a)
                if key not in seen:reason=key
            if reason is not None:
                seen.add(reason);snapshots.append((step,pc,reason,clone(m,c)))
            c.step()
        else:raise AssertionError('bounded loader discovery')
        H.exact(m);final=reg(c);expectedCHR=m.chr_latches[:];rows=[];irqmasked=0
        for step,pc,reason,(state,cpu) in snapshots:
            for kind in ['NMI','IRQ']:
                q,d=clone(state,cpu)
                if kind=='IRQ' and d.p&d.INTERRUPT:
                    before=C.cpu_state(d);d.irq();assert C.cpu_state(d)==before
                    irqmasked+=1;continue
                source=bytes(q[0x5c00:0x5c80])+bytes(q[0x5fc1:0x5fcf])+bytes([q[0x5fef]])
                prefix=len(q.ppu_log);upper=q.upper
                isr=C.interrupt(q,d,kind)
                irqlog=[(0x2006,(H.get(q,'IrqPPUCTRL')&1)<<2),(0x2005,32),(0x2005,H.get(q,'IrqNewScroll')),(0x2006,128|(H.get(q,'IrqNewScroll')>>3))] if kind=='IRQ' else []
                assert q.ppu_log[prefix:]==irqlog,('unexpected realISR PPU writes',step,kind,q.ppu_log[prefix:],irqlog)
                if kind=='IRQ':assert upper==0 and prefix in[0,len(m.ppu_log)],('unmasked IRQ inside owned copy',step,prefix,upper)
                assert source==bytes(q[0x5c00:0x5c80])+bytes(q[0x5fc1:0x5fcf])+bytes([q[0x5fef]])
                H.finish(q,d);H.exact(q)
                assert reg(d)==final and q.rawtags==m.rawtags
                reference=m
                if kind=='IRQ' and prefix==len(m.ppu_log):
                    reference,finalcpu=clone(m,c);C.interrupt(reference,finalcpu,'IRQ')
                assert q.chr_latches==reference.chr_latches and q.upper==0 and q.ppuctrl==reference.ppuctrl and q.toggle==0
                expectedlog=m.ppu_log[:prefix]+irqlog+m.ppu_log[prefix:]
                assert q.ppu_reads==m.ppu_reads and q.ppu_log==expectedlog,('ISR corrupted owned PPU transaction',step,hex(pc),kind,prefix)
                rows.append(dict(step=step,PC=pc,reason=list(reason),**isr))
        proof['checks']['cold_copy']=dict(real_interruptions=len(rows),masked_IRQ_requests=irqmasked,
            actual_snapshots=len(snapshots),rows=rows,source143bytes_unchanged=True,
            complete_copy_cookie_registers_rawmaps_PPU_equivalent=True,
            IRQ_rule='RealSEI masks requests through copy/verify; no fabricated IRQ entry inside a protected PPU transaction.')
        print('FF actual loader ISR PASS',len(rows),'maskedIRQ',irqmasked,flush=True)
        # Normal NMI is legal around active ready routing/checks, not inside a
        # loader whose required NmiDisable entry ownership is already negative.
        hot=H.make(b);H.invoke(hot,'FwLoad');hot_snap=[]
        for target in ['FwCheck','FwMovement','FwRenderChunk']:
            q,d=clone(hot,H.start(hot,target,a=0,x=0,y=0));H.put(q,FfSlot=1,NmiDisable=0)
            for step in range(10000):
                if d.pc==0x5b00:break
                pc=d.pc;op=bytes(q[pc:pc+3])
                if step<20 or op in [b'\x8d\x15\x51',b'\x8d\x16\x51']:
                    hot_snap.append((target,step,pc,clone(q,d)))
                d.step()
            else:raise AssertionError('hot dispatch bounded')
        hotrows=[]
        for name,step,pc,(state,cpu) in hot_snap:
            for lag in[0,255]:
                for kind in ['NMI','IRQ']:
                    q,d=clone(state,cpu);H.put(q,NmiDisable=lag)
                    if kind=='IRQ'and d.p&d.INTERRUPT:continue
                    isr=C.interrupt(q,d,kind);H.finish(q,d);H.exact(q)
                    assert q.rawtags[1]==215 and q.rawtags[2]==216
                    hotrows.append(dict(entry=name,step=step,PC=pc,lag=lag,**isr))
        proof['checks']['hot_routes']=dict(real_normal_lag_NMI_IRQ_cases=len(hotrows),rows=hotrows,
            all33SMC_AXYP_SP_R0_R1_R6_R7_rawmaps_code_exact=True)
        proof['passed']=True
    except Exception as e:proof.update(error=repr(e),traceback=traceback.format_exc())
    proof['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(H.__file__),Path(C.__file__),
        O/'candidate.nes',O/'candidate.dbg',O/'build-proof.json',O/'loader-controls-v3.json',O/'ram3.bin',O/'ff-cookie.bin']}
    path=out if proof['passed']else O/'loader-isr-negative-v4.json';assert not path.exists()
    path.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=proof['passed'],error=proof.get('error'),path=str(path))))
    assert proof['passed']


if __name__=='__main__':main()
