"""Execute the exact cartridge dispatch, all rows and full header rejection.

Kernel rows remain explicit rejections. A memory-only success leaf checks the
generic transport's output ABI; it is not an implemented gameplay service.
"""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
import check_hogan_current_bounded_v1 as M
from prepare_excitebike_dispatch_1101_v1 import labels,sha,save,O

def bundle():
    b=scoped_load(O/'candidate.nes')
    b['segs']['excitebike_resident']={'start':str(0xa000),'ooffs':str(16+65*8192)}
    for n,a in labels(O/'dispatch.lbl').items():
        if n.startswith('Ex'):b['syms'][n]={'val':str(a),'seg':'excitebike_resident'}
    for row in range(37):
        b['syms'][f'ExService{row}']={'val':str(0xb08c+row*3),'seg':'excitebike_resident'}
    return b

def main():
    b=bundle();q=json.loads((O/'dispatch-assembly.json').read_text())
    assert sha(O/'candidate.nes')==q['ROM_SHA256']
    m=M.fresh(b)
    M.put(m,SelectedCharacter=37,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,
          Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,ReloadCHRBank=1)
    cold=M.invoke(m,'ExLoad');assert cold['P']&1 and m.ppu_reads==16400
    assert bytes(m.ram[3][:6144])==(O/'dispatch-kernel.bin').read_bytes()
    cookie=(O/'dispatch-cookie.bin').read_bytes()
    assert all(bytes(m.ram[k][0x1fe0:0x1ff0])==cookie for k in [2,3])
    coldguards=0
    for fields in [dict(SelectedCharacter=36),dict(SelectedCharacter=38),dict(OperMode=0),dict(OperMode=2),
                   dict(FamilyMainCommit=0),dict(DisableScreenFlag=0),dict(Mirror_PPUMASK=24),dict(NmiDisable=0)]:
        n=M.fresh(b);M.put(n,SelectedCharacter=37,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,
            Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,ReloadCHRBank=1)
        M.put(n,**fields);before=[bytes(z)for z in n.ram];reads=n.ppu_reads
        z=M.invoke(n,'ExLoad');assert not z['P']&1 and n.ppu_reads==reads and before==[bytes(z)for z in n.ram]
        coldguards+=1
    rows=success=0;maxcycles=0
    for row in range(37):
        for a,x,y,p in [(0,0,0,0x30),(0x55,7,91,0x31),(0x80,255,255,0x71),(0xff,0x83,0x51,0xf1)]:
            for carry in [0,1]:
                n=M.fork(m)
                # Deliberate fixture mutation affects only the private return
                # leaf; the ROM's37 rows always execute CLC/RTS.
                if carry:n.ram[3][0x56f:0x577]=bytes([0xa9,0x80,0xa2,0x17,0xa0,0x33,0x38,0x60])
                before=[bytes(z) for z in n.ram]
                result=M.invoke(n,f'ExService{row}',a=a,x=x,y=y,p=p)
                returns=[0x80,0x17,0x33] if carry else [a,x,y]
                assert [result[z]for z in ['A','X','Y']]==returns,(row,carry,result,returns)
                assert result['P']&1==carry,(row,carry,result)
                physical=(p&0x4c)|(returns[0]&0x80)|(2 if returns[0]==0 else 0)|carry
                assert result['P']&0xcf==physical,(row,carry,result,physical)
                assert bytes(n.ram[2])==before[2] and bytes(n.ram[3])==before[3]
                maxcycles=max(maxcycles,result['CPU'])
                rows+=1;success+=carry
    corrupt=0
    for bank in [2,3]:
      for index in range(16):
        n=M.fork(m);n.ram[bank][0x1fe0+index]^=1;n.ram[3][0x56f]=0
        before=[bytes(z)for z in n.ram]
        result=M.invoke(n,'ExService0',a=0x55,x=7,y=91,p=0xf1)
        assert not result['P']&1 and [result[z]for z in ['A','X','Y']]==[0x55,7,91]
        assert before==[bytes(z)for z in n.ram]
        corrupt+=1
    identities=0
    for char in [0,1,10,34,35,36,38,255]:
        n=M.fork(m);M.put(n,SelectedCharacter=char);before=[bytes(z)for z in n.ram]
        result=M.invoke(n,'ExService0',a=0x55,x=7,y=91,p=0xf1)
        assert not result['P']&1 and [result[z]for z in ['A','X','Y']]==[0x55,7,91]
        assert before==[bytes(z)for z in n.ram];identities+=1
    # Native NMI at each instruction boundary in a valid row dispatch. This
    # exercises the actual ROM ISR and matches both continuation PC and SP.
    baseline=M.NesMPU;cuts=[]
    class Trace(baseline):
        def step(self):
            if self.memory.rawtags[1]==193 and 0xa740<=self.pc<0xa800:
                cuts.append((self.pc,self.sp))
            return super().step()
    M.NesMPU=Trace
    try:expected=M.invoke(M.fork(m),'ExService0',a=0x55,x=7,y=91,p=0xf1)
    finally:M.NesMPU=baseline
    unique=list(dict.fromkeys(cuts));interrupts=0
    for cut in unique:
        n=M.fork(m);injected=[False]
        class Interrupt(baseline):
            def step(self):
                if not injected[0] and self.memory.rawtags[1]==193 and (self.pc,self.sp)==cut:
                    injected[0]=True;pc,sp=self.pc,self.sp;self.nmi()
                    for _ in range(200000):
                        if self.pc==pc and self.sp==sp:break
                        assert self.memory[self.pc]!=0,('ISR BRK',cut,hex(self.pc))
                        super().step()
                    else:raise AssertionError(('ISR continuation bound',cut))
                return super().step()
        M.NesMPU=Interrupt
        try:result=M.invoke(n,'ExService0',a=0x55,x=7,y=91,p=0xf1)
        finally:M.NesMPU=baseline
        assert injected[0] and [result[z]for z in ['A','X','Y','P']]==[expected[z]for z in ['A','X','Y','P']],(cut,result,expected)
        interrupts+=1
    result=dict(passed=True,ROM_SHA256=sha(O/'candidate.nes'),cold_loader=cold,
                service_ABI_cases=rows,all_37_rows_executed=True,memory_only_success_cases=success,
                corrupted_header_cases=corrupt,foreign_identity_cases=identities,
                shortened_cold_guard_rejections=coldguards,
                actual_ISR_instruction_cuts=interrupts,max_dispatch_cycles=maxcycles,
                full_header_verification=True,conditional_RAM_unchanged=True,
                gameplay_rows_implemented=0,pending_menu_locked=True,native_emulator=False,installed=False,
                scope='Actual ROM FarCallCommon, loader, dispatch and ISR. Explicitly rejecting kernel rows; success leaf changed only in memory to test result transport. No owning gameplay ingress or native controller claim.',
                bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),O/'dispatch-assembly.json',O/'dispatch.lbl']})
    save('dispatch-CPU.json',result);print(json.dumps(result))

if __name__=='__main__':main()
