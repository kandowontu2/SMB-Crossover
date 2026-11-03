"""Cold/readback/auth, moved helpers, foreign guards and actual ISR cuts."""
import json
from pathlib import Path
import measure_bub_landing_1102_v21 as L

E=L.E;N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address
O=L.O;B=E.O;C=E.C

def main():
    old,new,q,route=L.bundle();image=(O/'landing-v21-image.bin').read_bytes();art=(O/'landing-v21-helper.chr').read_bytes()
    owner=P.P.labels(B/'native-event-v9-owner.lbl');checks={};cold=[]
    for case,fault in[('cold',None),('code-readback',(3,2048)),('helper-readback',(2,0x1320)),('protected','protected')]:
        m=C.ready(new);N.put(m,SelectedCharacter=39)
        if fault=='protected':m.protection=[0,0]
        elif fault:m.corrupt_at=fault
        scratch=bytes(m[3:11]);maps=list(m.rawtags);z=C.call(m,owner['CoCold'])
        assert scratch==bytes(m[3:11])and maps==m.rawtags and(z['A'],z['X'],z['Y'])==(83,71,109)
        if fault:assert not z['P']&1 and m.ram[2][0x1fe0]!=167
        else:
            expect=bytearray(image);expect[0x1fe0:0x1ff0]=bytes.fromhex(q['cookie'])
            assert m.ram[3]==expect and bytes(m.ram[2][4096:5120])==art and m.ppu_reads==18450
            assert m.ram_writes[-1]==(2,0x1fe0,167)
            count=len(m.ram_writes);reads=m.ppu_reads;assert C.call(m,owner['CoCold'])['P']&1
            assert len(m.ram_writes)==count and m.ppu_reads==reads
        cold.append(dict(case=case,accepted=bool(z['P']&1)))
    checks['complete9row_copy_verify_lastcommit_warm_and_faults']=cold
    seeds=[Q.fresh(b,route,0)for b in[old,new]];foreign=0
    for raw in range(256):
        results=[]
        for seed in seeds:
            m=N.fork(seed);N.put(m,SelectedCharacter=raw);maps=list(m.rawtags);private=[bytes(x)for x in m.ram];scratch=bytes(m[3:11])
            z=C.call(m,owner['CoCheckCode']);assert maps==m.rawtags and private==[bytes(x)for x in m.ram]and scratch==bytes(m[3:11]);results.append(z)
        assert results[0]==results[1],(raw,results)
        assert bool(results[1]['P']&1)==(raw==39);foreign+=1
    checks['all256_raw_auth_foreign_AXYP_maps_state_exact']=foreign
    poison=0
    for bank in[2,3]:
        for byte in range(16):
            m=N.fork(seeds[1]);m.ram[bank][0x1fe0+byte]^=1
            assert not C.call(m,owner['CoCheckCode'])['P']&1;poison+=1
    checks['both_full16B_header_poison_failclosed']=poison
    helper=[]
    for identity in[0,1]:
        m=Q.fresh(new,route,identity);E.main_fields(m)
        for name in['HuFullBox','HuColors','HuStatusName']:
            if name not in new['syms']:continue
            N.put(m,VRAM_Buffer1_Offset=0);N.invoke(m,name,a=0,x=0,y=0)
            helper.append(dict(identity=identity,service=name,completed=True))
        N.put(m,CurrentOAMOffset=0,GuestOamRotationActive=0,RgOamUsed=0)
        N.invoke(m,'HuDraw',a=0,x=0,y=0)
        assert any(m[512+i]<240 for i in range(0,256,4))
    checks['moved_fullbox_backdrop_status_and_draw_entries']=helper
    # These states represent native post-foot landing; the exact physical
    # predicate and original reset are additionally exercised by the complete
    # legal staircase in landing-v21-CPU, not invented velocity-only states.
    cuts=set();native=N.NesMPU;core=P.P.labels(B/'component.lbl')
    def selected(c):return c.memory.rawtags[1]==3 and(q['labels']['BbNativeLanding']<=c.pc<=q['labels']['BbNativeLandingDone']or core['BbOriginal_D41C']<=c.pc<core['BbOriginal_D422']+1)
    class Collect(native):
        def step(self):
            if selected(self):cuts.add((self.pc,self.sp))
            return native.step(self)
    seed=N.fork(seeds[1]);E.main_fields(seed);N.put(seed,NmiDisable=1,Player_State=0,Player_Y_Speed=0,FrameCounter=91,SavedJoypadBits=129,SavedJoypad1Bits=129)
    seed.ram[2][0x31]=3;reference=N.fork(seed);N.NesMPU=Collect
    try:expected=N.invoke(reference,'HuMovement',a=85,x=7,y=73,p=0x31)
    finally:N.NesMPU=native
    assert cuts
    counts={};low=255
    for kind in['IRQ','NMI']:
        for cut in sorted(cuts):
            m=N.fork(seed);injected=False
            class Interrupt(native):
                def step(self):
                    nonlocal injected,low
                    if not injected and self.memory.rawtags[1]==3 and(self.pc,self.sp)==cut:
                        injected=True;mem=self.memory;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc)
                        maps=list(mem.rawtags);private=[bytes(x)for x in mem.ram];scratch=bytes(mem[3:11]);smc=bytes(mem[0x15a:0x17b]);assert not self.p&4
                        self.irq()if kind=='IRQ'else self.nmi()
                        for _ in range(200000):
                            low=min(low,self.sp)
                            if self.pc==regs[5]and self.sp==regs[4]:break
                            assert mem[self.pc]!=0;native.step(self)
                        else:raise AssertionError('ISR bound')
                        assert regs==(self.a,self.x,self.y,self.p,self.sp,self.pc)
                        assert maps==mem.rawtags and private==[bytes(x)for x in mem.ram]and scratch==bytes(mem[3:11])and smc==bytes(mem[0x15a:0x17b])
                    return native.step(self)
            N.NesMPU=Interrupt
            try:z=N.invoke(m,'HuMovement',a=85,x=7,y=73,p=0x31)
            finally:N.NesMPU=native
            assert injected and all(z[k]==expected[k]for k in['A','X','Y','P'])and m.ram==reference.ram and m.rawtags==reference.rawtags,(kind,cut,injected,z,expected)
            counts[kind]=counts.get(kind,0)+1
    checks['actual_native_IRQ_busyNMI_landing_and_original_reset']=dict(cuts=counts,minimum_ISR_SP=low)
    out=dict(passed=True,ROM_written=False,native=False,base_ROM_sha256=L.PIN,checks=checks,
        scope='Exact source-only private successor: all9coldrows/readback/headercommit and warm/failure paths; all256raw auth parity; complete32header poison; moved helperentries; real IRQ/busyNMI at every reached addedpredicate and authentic originalreset instruction. No ROM/privatecandidate/nativequalification/install.',
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),R/'tools/audit/measure_bub_landing_1102_v21.py',O/'landing-v21-layout.json',O/'landing-v21-image.bin',O/'landing-v21-helper.chr',O/'landing-v21-CPU.json']})
    (O/'landing-v21-transport-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks)))

if __name__=='__main__':main()
