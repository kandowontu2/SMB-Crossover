"""Conditional v50 callback/ISR evidence, without accepting its lifetime premise."""
import collections,json
from pathlib import Path
import measure_bub_landing_1102_v21 as L
import check_bubble_bobble_common_cold_1102_v4 as C

N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address;O=L.O


def load():
    _,old,layout,route=L.bundle();old['raw']=(O/'combined-current-landing.nes').read_bytes()
    q=json.loads((O/'scoped-auth-v50-measurement.json').read_text())
    assert P.sha(old['raw'])==q['base_ROM_SHA256'] and q['qualified'] is False
    for path,digest in q['bindings'].items():assert P.sha((R/path).read_bytes())==digest,path
    raw=bytearray(old['raw'])
    for patch in q['patches']:
        at=patch['offset'];before=bytes.fromhex(patch['old']);after=bytes.fromhex(patch['new'])
        assert raw[at:at+len(before)]==before and len(before)==len(after)
        raw[at:at+len(after)]=after
    new=dict(old);new['raw']=bytes(raw);assert P.sha(new['raw'])==q['in_memory_prototype_SHA256']
    return old,new,layout,route,q


def run(m,route,*,collect=False,inject=None,kind=None):
    native=N.NesMPU;events=[];private=[];returns=[];pending=[];cuts=set();ordinal=0;injected=False;isr=None
    dispatch=(O/'auth-scope-v50-routes.bin').read_bytes()
    offset=dispatch.index(bytes.fromhex('adff5fc981f0'));gate=0xa740+offset
    source_labels=P.P.labels(O/'auth-scope-v50-owner.lbl')
    mark=source_labels['CoMarkLease'];clear=(O/'auth-scope-v50-owner.bin').read_bytes().index(bytes.fromhex('adff5f1005297f8dff5f'))+0xae00
    ranges=[(gate,gate+15),(mark,mark+13),(clear,clear+10)]
    class Trace(native):
        def step(self):
            nonlocal ordinal,injected,isr
            mem=self.memory;pc=self.pc;tag=mem.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
            if pending and (pc,self.sp,tag)==pending[-1]['return']:
                z=pending.pop()
                returns.append(dict(row=z['row'],AXYP_SP=[self.a,self.x,self.y,self.p,self.sp],
                    SMC=list(mem[0x15a:0x17b]),R0_7=list(mem[3:11]),maps=list(mem.rawtags)))
            if tag==193 and pc==route['ExDispatch']:
                ordinal+=1;target=mem[address(mem.bundle,'FarcallJmpTarget_SMC')+1]+256*mem[address(mem.bundle,'FarcallJmpTarget_SMC')+2]
                row=(target-0xb08c)//3
                events.append(dict(row=row,AXYP_SP=[self.a,self.x,self.y,self.p,self.sp],
                    SMC=list(mem[0x15a:0x17b]),R0_7=list(mem[3:11]),maps=list(mem.rawtags)))
                ret=(mem[0x100+((self.sp+1)&255)]+256*mem[0x100+((self.sp+2)&255)]+1)&65535
                rt=mem.rawtags[(ret-0x8000)//8192] if ret>=0x8000 else -1
                pending.append(dict(row=row,return_ignored=None,**{'return':(ret,(self.sp+2)&255,rt)}))
            if collect and tag==193 and any(a<=pc<z for a,z in ranges):cuts.add((pc,self.sp,ordinal))
            if inject==(pc,self.sp,ordinal) and not injected and tag==193:
                injected=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc)
                maps=list(mem.rawtags);scratch=bytes(mem[3:11]);smc=bytes(mem[0x15a:0x17b])
                headers=[bytes(mem.ram[k][0x1fe0:0x1ff0]) for k in [2,3]]
                selected=N.get(mem,'SelectedCharacter');before=N.get(mem,'FamilyMainCommit')
                self.irq() if kind=='IRQ' else self.nmi()
                for steps in range(200000):
                    if (self.pc,self.sp)==(regs[-1],regs[-2]):break
                    assert mem[self.pc]!=0,(kind,inject,'ISR BRK',hex(self.pc));native.step(self)
                else:raise AssertionError(('ISR bound',kind,inject))
                assert regs==(self.a,self.x,self.y,self.p,self.sp,self.pc),(kind,inject,'AXYP/SP')
                assert maps==mem.rawtags and scratch==bytes(mem[3:11]) and smc==bytes(mem[0x15a:0x17b])
                assert headers==[bytes(mem.ram[k][0x1fe0:0x1ff0]) for k in [2,3]] and selected==N.get(mem,'SelectedCharacter')
                after=N.get(mem,'FamilyMainCommit')
                assert after==(before if kind=='IRQ' else before&1),(kind,inject,before,after)
                isr=dict(kind=kind,PC=pc,SP=self.sp,service_ordinal=ordinal,
                    protocol_before=before,protocol_after=after,ISR_instructions=steps,
                    AXYP_SP_SMC_R0_7_maps_owner_both_headers_exact=True)
            if tag==3 and 0xa000<=pc<0xbfe0 or tag==2 and 0xd320<=pc<0xd400:
                private.append((tag,pc,self.a,self.x,self.y,self.p,self.sp))
            return native.step(self)
    N.NesMPU=Trace
    try:
        N.put(m,FamilyMainCommit=0,NmiDisable=255,VRAM_Buffer1_Offset=0)
        N.invoke(m,'PauseRoutine',a=255,x=7,y=91,p=0x31)
        z=N.invoke(m,'GameCoreRoutine',x=0,y=0)
        main_smc=bytes(m[0x15a:0x17b]);main_scratch=bytes(m[3:11])
        N.invoke(m,'RdsMainGate',a=0,x=7,y=91,p=0x31)
        assert N.get(m,'FamilyMainCommit')==0 and not pending
    finally:N.NesMPU=native
    assert len(events)==len(returns)==13,(len(events),len(returns))
    if inject:assert injected
    return dict(result=z,entry=events,leave=returns,private=private,cuts=cuts,isr=isr,
        Main_SMC=main_smc.hex(),Main_R0_7=main_scratch.hex())


def main():
    old,new,layout,route,proposal=load();seeds=[]
    for b in [old,new]:
        m=Q.fresh(b,route,0);L.E.main_fields(m)
        N.put(m,FrameCounter=23,SavedJoypadBits=1,SavedJoypad1Bits=1)
        seeds.append(m)
    outputs=[];final=[]
    for m in seeds:
        n=N.fork(m);outputs.append(run(n,route,collect=m is seeds[1]));final.append(n)
    a,z=outputs
    for name in ['entry','leave','private','Main_SMC','Main_R0_7']:assert a[name]==z[name],('Current/prototype exact callback trace',name)
    assert final[0].ram==final[1].ram and final[0].rawtags==final[1].rawtags
    points=sorted(z['cuts']);assert points
    counts=collections.Counter();cutresults=[]
    for kind in ['IRQ','lagNMI']:
        for cut in points:
            m=N.fork(seeds[1]);got=run(m,route,inject=cut,kind=kind)
            for name in ['entry','leave','private','Main_SMC','Main_R0_7']:
                assert got[name]==z[name],('Exact resumed callback/private trace',kind,cut,name)
            assert m.ram==final[1].ram and m.rawtags==final[1].rawtags
            cutresults.append(got['isr']);counts[kind]+=1
    out=dict(passed=True,qualified=False,ROM_written=False,native=False,lease_bit_granted=False,
        base_ROM_SHA256=proposal['base_ROM_SHA256'],in_memory_prototype_SHA256=proposal['in_memory_prototype_SHA256'],
        compared_callbacks=13,complete_callback_entry_exit_AXYP_SP_SMC_R0_7_maps_exact=True,
        original_private_instruction_trace_entries=len(z['private']),
        original_private_instruction_trace_SHA256=P.sha(json.dumps(z['private']).encode()),
        actual_proposed_gate_and_mark_ISR_cuts=dict(counts),actual_ISR_results=cutresults,
        baseline_Main_CPU=a['result']['CPU'],conditional_prototype_Main_CPU=z['result']['CPU'],
        scope='Both real NMI and IRQ execute at every reached gate/mark instruction/SP/service occurrence in one actual empty walking Main. Each return retains exact registers, scratch, SMC, mappings, owner and32headerbytes; NMI clears the proposed bit and source/native callback traces resume identically. No callback/header writer invariant is inferred from these cuts.',
        remaining=proposal['missing_before_qualification'],
        rejected_unannounced_writer_control=proposal['rejected_unannounced_writer_control'],
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes()) for p in [Path(__file__),
            O/'scoped-auth-v50-measurement.json',O/'auth-scope-v50-owner.bin',O/'auth-scope-v50-routes.bin',
            O/'combined-current-landing.nes']})
    dst=O/'scoped-auth-v51-ISR.json';assert not dst.exists();dst.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,qualified=False,ROM_written=False,callbacks=13,
        exact_callback_entry_exit_AXYP_SP_SMC_R0_7_maps=True,actual_ISR_cuts=dict(counts),receipt=str(dst.relative_to(R)))))


if __name__=='__main__':main()
