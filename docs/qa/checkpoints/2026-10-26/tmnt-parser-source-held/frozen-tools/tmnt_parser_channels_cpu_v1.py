"""Joined full flags/state plus actual IRQ and entry closure for channel map."""
from pathlib import Path
import argparse
import itertools
import json
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
from tmnt_native_storage_multiply import MathMemory
from tmnt_native_storage_irq_cpu import ordinary,registers
from tmnt_native_storage_driver import ROOT,source_data,sha
from tmnt_parser_math_next_cpu_v1 import outcome,FLAGS


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    old,new=load(a.baseline),load(a.candidate);count=0;costs={}
    def setup(b,x,acc,y,flags):
        m=MathMemory(b);m.page(1,63);m.page(2,99)
        for n,v in dict(SelectedCharacter=19,OperMode=1,CurrentBank=191,CurrentBankC=227).items():m[address(b,n)]=v
        m[0x5204]=128;m[510],m[511]=255,1;m.writes=[];m.math_events=[]
        c=NesMPU(memory=m);c.pc,c.a,c.x,c.y,c.p,c.sp=0xa65e,acc,x,y,flags,253
        return c,m
    for x,acc,y,flags in itertools.product(range(6),[0,1,127,128,255],[0,1,127,128,255],FLAGS):
        machines=[]
        for b in[old,new]:
            c,m=setup(b,x,acc,y,flags)
            for _ in range(30):
                if c.pc==0xa64b:break
                m.executing_PC=c.pc;c.step()
            else:raise AssertionError('Channel join timeout')
            machines.append((c,m))
        (c,m),(d,n)=machines;assert outcome(c,m)==outcome(d,n)and m.operands==n.operands
        costs.setdefault(x,set()).add(d.processorCycles-c.processorCycles);count+=1
    injections=maximum=0
    for x,flags in itertools.product(range(6),[0x20,0xe9]):
        c,m=setup(new,x,85,47,flags);trace=[]
        for i in range(30):
            if c.pc==0xa64b:break
            trace.append(i);m.executing_PC=c.pc;c.step()
        expected=registers(c),ordinary(m),list(m.banks),list(m.operands),list(m.math_events)
        for position in trace:
            d,n=setup(new,x,85,47,flags);injected=False
            for index in range(30):
                if d.pc==0xa64b:break
                if index==position:
                    before=registers(d),ordinary(n),list(n.banks),list(n.operands),list(n.math_events)
                    d.irq();assert d.pc==0x8000;minimum=d.sp
                    for _ in range(300):
                        if d.pc==before[0][0]and d.sp==before[0][-1]:break
                        minimum=min(minimum,d.sp);n.executing_PC=d.pc;d.step()
                    else:raise AssertionError('IRQ return timeout')
                    assert(registers(d),ordinary(n),list(n.banks),list(n.operands),list(n.math_events))==before
                    maximum=max(maximum,255-minimum);injected=True
                n.executing_PC=d.pc;d.step()
            assert injected and(registers(d),ordinary(n),list(n.banks),list(n.operands),list(n.math_events))==expected;injections+=1
    _,memory,cpu,dis,seen,words=source_data();incoming=[];roots=[];lo,hi=0x865e,0x866d
    for pc in seen:
        if lo<=pc<hi:continue
        width,_=dis.instruction_at(pc);op,mode=cpu.disassemble[memory[pc]];targets=[]
        if mode=='rel':
            off=memory[pc+1];targets=[pc+width,pc+width+(off-256 if off>=128 else off)]
        elif op in['JSR','JMP']and mode=='abs':targets=[memory[pc+1]+256*memory[pc+2]]
        elif op not in['RTS','RTI','JMP','BRK']:targets=[pc+width]
        incoming.extend([pc,to]for to in targets if lo<=to<hi)
    roots=[word for word in words if lo<=memory[word]+256*memory[word+1]<hi]
    assert incoming and all(to==lo for pc,to in incoming)and not roots
    # Genuine preceding CPX6/BEQ guards the six-channel source loop. No
    # malformed private driver state with out-of-range channel X is claimed.
    at=16+63*8192+0x65a;assert new['raw'][at:at+4]==bytes.fromhex('e006f012')
    at=location(new,'TnNativeChannelOffsets');assert new['raw'][at:at+6]==bytes([0,4,8,12,0,12])
    inherited={}
    for name in['TnFastProduct','TnTempoProduct','TnParserPointer','TnFastDuration']:
        a1,a2=location(old,name),location(new,name);size=int(old['syms'][name]['size'],0)
        assert old['raw'][a1:a1+size]==new['raw'][a2:a2+size]
        inherited[name]=dict(PC=address(new,name),bytes=size,compiled_body_exact=True)
    proof=dict(passed=True,source_only=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
        full_AXYP_SP_nonstackRAM_SMC_banks_products_APU_join_cases=count,all64physical_flags=True,reachable_loop_channels=list(range(6)),
        source_preceding_CPX6_BEQ_guard_exact=True,malformed_driver_X_outside0_5_not_claimed=True,
        exact_loop_delta_per_X={str(x):sorted(v)for x,v in costs.items()},actual_compiled_IRQ_injections=injections,maximum_stack_depth=maximum,
        original_span=[lo,hi],external_original_entries=incoming,interior_original_pointer_roots=roots,
        existing_math_helpers_unchanged=inherited,checker_sha256=sha(Path(__file__)),native_recovery_claim=False)
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
