"""Actual IRQ/lag-NMI cuts through the restored private source phases."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from check_excitebike_heat_1102_v2 import machine,tick,M
from prepare_excitebike_heat_1102_v2 import memory_image
from prepare_excitebike_dispatch_1101_v1 import O,labels,sha,save
from check_tmnt_render_oa import address


def main():
    raw,_=memory_image();lab=labels(O/'heat-host.lbl');snapshots=[]
    # Reach actual overheat, completion-lane and released states with inputs;
    # keep only four in-memory snapshots, never a frame/state dump.
    m=machine(raw);seen=set()
    for frame in range(850):
        tick(m,frame,65)
        state=(m.ram[2][0x3e0],m.ram[2][0x9c],m.ram[2][0x3c])
        key='normal'if frame==1 else 'cooling'if state[0]and state[2]==20 else 'release'if state[0]and state[2]==9 and m.ram[2][0x20]==0 else 'recovery5'if state[1]==5 else None
        if key and key not in seen:
            seen.add(key);snapshots.append((key,M.fork(m),frame+1))
    assert len(snapshots)==4,seen
    native=M.NesMPU;total=0;by={};pcs=set()
    lo,hi=lab['ExHeatRelease'],lab['ExRecoveryEnd']
    for key,seed,epoch in snapshots:
        M.put(seed,NmiDisable=1)
        cuts=set()
        class Trace(native):
            def step(self):
                if self.memory.rawtags[1]==3 and lo<=self.pc<hi:cuts.add((self.pc,self.sp))
                return native.step(self)
        M.NesMPU=Trace
        try:expected=tick(M.fork(seed),epoch,65)
        finally:M.NesMPU=native
        for kind in ['IRQ','lagNMI']:
          for cut in sorted(cuts):
            n=M.fork(seed);injected=False
            class Interrupt(native):
                def step(self):
                    nonlocal injected
                    mem=self.memory
                    if not injected and mem.rawtags[1]==3 and(self.pc,self.sp)==cut:
                        injected=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc)
                        maps=list(mem.rawtags);private=[bytes(mem.ram[k])for k in [2,3]]
                        scratch=bytes(mem[address(mem.bundle,'R0'):address(mem.bundle,'R7')+1]);smc=bytes(mem[0x15a:0x17b])
                        if kind=='IRQ':self.irq()
                        else:self.nmi()
                        for _ in range(200000):
                            if self.pc==regs[5]and self.sp==regs[4]:break
                            assert mem[self.pc]!=0,(key,kind,cut,'BRK',hex(self.pc))
                            native.step(self)
                        else:raise AssertionError((key,kind,cut,'RTI bound'))
                        assert regs==(self.a,self.x,self.y,self.p,self.sp,self.pc),(key,kind,cut,'registers')
                        assert maps==mem.rawtags and mem.upper==0,(key,kind,cut,'mapper')
                        assert private==[bytes(mem.ram[k])for k in [2,3]],(key,kind,cut,'private state')
                        assert scratch==bytes(mem[address(mem.bundle,'R0'):address(mem.bundle,'R7')+1])and smc==bytes(mem[0x15a:0x17b]),(key,kind,cut,'scratch/SMC')
                    return native.step(self)
            M.NesMPU=Interrupt
            try:actual=tick(n,epoch,65)
            finally:M.NesMPU=native
            assert injected and [actual[k]for k in ['A','X','Y','P']]==[expected[k]for k in ['A','X','Y','P']]
            total+=1;by[kind]=by.get(kind,0)+1;pcs.add(cut[0])
    q=dict(passed=True,memory_candidate_SHA256=hashlib.sha256(raw).hexdigest(),actual_ISR_cuts=total,by_kind=by,
           actual_source_contexts=sorted(seen),private_phase_instruction_PCs=len(pcs),
           exact_AXYP_SP_PC_R0_7_SMC_PRG_maps_private_state=True,native=False,installed=False,
           scope='Actual native IRQ and real Main-busy NMI at every distinct reached instruction/SP in restored timer/cooling/post-air phases, from four genuine source journeys. No normal rendering NMI is invented inside the Main-busy interval.',
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),O/'heat-assembly.json',O/'heat-kernel.bin',O/'heat-host.lbl']})
    save('heat-ISR-CPU.json',q);print(json.dumps(q))


if __name__=='__main__':main()
