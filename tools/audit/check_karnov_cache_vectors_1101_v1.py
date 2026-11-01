"""Interrupt the real linked Karnov resident using the actual host NMI/IRQ."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
import ff_host_pickups_vectors_v2 as V
from check_tmnt_render_oa import address
O=R/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    q=dict(passed=False,source_CPU=True,native=False,installed=False)
    try:
        proof=json.loads((O/'cache-CPU-controls.json').read_text());assert proof['passed']
        for p,h in proof['bindings'].items():assert sha(p)==h,p
        b=H.C.qualified(O/'candidate.nes')
        original_pending=V.pending_store
        def pending(m,c,slot,op):
            if original_pending(m,c,slot,op):return True
            reg={0x8d:c.a,0x8e:c.x,0x8c:c.y}.get(m[c.pc])
            target=0x5115 if slot==1 else 0x5116
            return reg is not None and bytes(m[c.pc+1:c.pc+3])==target.to_bytes(2,'little')and reg==H.get(m,'CurrentBank'if slot==1 else'CurrentBankC')
        V.pending_store=pending
        def make():
            m=L.make(b);H.put(m,SelectedCharacter=7,FmAlts=1);m.writes.clear();m.ram_writes.clear();return m
        def run(m,name,hook=None,y=0):
            c=H.start(m,name,a=85,x=7,y=y,p=0x70);trace=[];low=c.sp
            for i in range(500000):
                if c.pc==0x5b00:break
                if hook:hook(m,c,i)
                trace.append((c.pc,m.rawtags[1],m.rawtags[2]));low=min(low,c.sp)
                assert m[c.pc]!=0,('linked BRK',name,hex(c.pc));c.step()
            else:raise AssertionError(('bounded resident',name,hex(c.pc)))
            assert(c.a,c.x,c.y,c.sp)==(85,7,y,224)
            return c,trace,low
        def state(m):return([bytes(z)for z in m.ram],m.rawtags[:],H.get(m,'CurrentBank'),H.get(m,'CurrentBankC'),bytes(m[3:11]),bytes(m[0x15a:0x17b]))
        seed=make();c,_,_=run(seed,'KrLoad');assert c.p&1
        rows=[];masked=0;minimum=255
        for name in ['KrLoad','KrCheckCode','KrDispatch','KrRetire']:
            origin=make()if name=='KrLoad'else L.fork(seed)
            baseline=L.fork(origin);c,trace,_=run(baseline,name)
            first={}
            for i,(pc,a,c)in enumerate(trace):first.setdefault((pc,a,c),i)
            points=sorted(first.values());cuts={0,len(trace)-2,*points[::max(1,len(points)//20)]}
            # Every actually executed mapper publication, all cookie writes,
            # both entries/exits, plus a bounded sample of copy/readback sites.
            for key,i in first.items():
                pc=key[0]
                if pc in [address(b,n)for n in ['KrInvalidate','KrPublishByte','KrFailInvalidate','KrDispatchReturn','KrLoadReturn']]:cuts.add(i)
                if bytes(baseline[pc:pc+3])in [b'\x8d\x16\x51',b'\x8e\x16\x51',b'\x8d\x15\x51']:cuts.add(i)
            for cut in sorted(cuts):
                for kind in ['NMI','IRQ']:
                    m=L.fork(origin);events=[]
                    def hook(mem,c,i):
                        nonlocal masked
                        if i!=cut:return
                        if kind=='IRQ'and c.p&c.INTERRUPT:
                            before=V.cpu_state(c);c.irq();assert V.cpu_state(c)==before;masked+=1
                            events.append(dict(kind='IRQ-masked',minimum_SP=c.sp));return
                        prior=mem.chr_latches[:];event=V.interrupt(mem,c,kind)
                        event['native_CHR_changes']=[(i,a,z)for i,(a,z)in enumerate(zip(prior,mem.chr_latches))if a!=z]
                        events.append(event)
                    _,_,low=run(m,name,hook)
                    actual,want=state(m),state(baseline)
                    delta=[(i,a,z)for i,(a,z)in enumerate(zip(actual,want))if a!=z]
                    assert len(events)==1 and not delta,(name,kind,cut,'resumed state',[(i,a if i else 'RAM',z if i else 'RAM')for i,a,z in delta])
                    # The actual raster IRQ deliberately changes BG window0
                    # for the HUD split. Any final difference must be exactly
                    # an observed hardware write by that unchanged ISR.
                    native_chr={i:z for i,a,z in events[0].get('native_CHR_changes',[])}
                    assert all(a==z or a==native_chr.get(i)for i,(a,z)in enumerate(zip(m.chr_latches,baseline.chr_latches))),(name,kind,cut,'unexplained CHR change')
                    minimum=min(minimum,low,events[0]['minimum_SP']);rows.append(dict(operation=name,cut=cut,PC=f'{trace[cut][0]:04X}',**events[0]))
        # Auth/retire must also survive the real normal and paused NMI path.
        normal=0
        for name in ['KrCheckCode','KrRetire']:
            for paused in [0,1]:
                origin=L.fork(seed);H.put(origin,NmiDisable=0,GamePauseStatus=paused)
                base=L.fork(origin);_,trace,_=run(base,name)
                for cut in [0,len(trace)//2,len(trace)-2]:
                    m=L.fork(origin);events=[]
                    def hook(mem,c,i):
                        if i==cut:events.append(V.interrupt(mem,c,'NMI'))
                    _,_,low=run(m,name,hook);assert len(events)==1 and state(m)==state(base),(name,paused,cut)
                    minimum=min(minimum,low,events[0]['minimum_SP']);normal+=1
        q.update(passed=True,ROM_sha256=proof['ROM_sha256'],real_vector_cuts=len(rows),normal_paused_NMI=normal,masked_IRQ_requests=masked,minimum_SP=minimum,all_resumed_RAM_maps_SMC_scratch_exact=True,CHR_changes_only_observed_original_ISR=True,scope='Actual outer FarCallCommon and real host NMI/IRQ vectors; no vector/audio/map interception. Actual STA/STX pending shadow publication recognized by decoded operand and live register. Forced-blank lag NMI during loader; normal/pausedNMI on pure authentication/retirement. Original raster IRQ intentionally changes BG window0; remaining CHR changes must equal observed ISR writes. No native raster or gameplay admission.',rows=rows)
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),Path(L.__file__),Path(H.__file__),Path(V.__file__),O/'cache-CPU-controls.json',O/'candidate.nes',O/'candidate.dbg']}
    (O/'cache-vectors.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','rows','traceback']}));assert q['passed'],q.get('error')

if __name__=='__main__':main()
