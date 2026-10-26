"""Actual compiled IRQ across every new helper/join boundary, no NMI fiction."""
from pathlib import Path
import argparse
import itertools
import json
from check_tmnt_render_oa import load,address
from verify_native_relocation import NesMPU
from tmnt_native_storage_multiply import MathMemory
from tmnt_native_storage_irq_cpu import ordinary,registers
from tmnt_native_storage_driver import ROOT,sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    b=load(a.candidate);cases=[]
    for e2,n,flags in itertools.product([0,1,3,16,128,255],[0,1,2,16],[0x20,0xe9]):cases.append(dict(kind='tempo',e2=e2,n=n,flags=flags))
    for timer,x,status,flags in itertools.product([0,1,2,255],[0,5],[0,255],[0x20,0xe9]):cases.append(dict(kind='pointer',e2=timer,n=x,status=status,flags=flags))
    count=maximum=0;rows=[]
    for case in cases:
        kind=case['kind'];ends=[0xaadd]if kind=='tempo'else[0xa67f,0xa91f]
        def setup():
            m=MathMemory(b);m.page(1,63);m.page(2,99)
            for n,v in dict(SelectedCharacter=19,OperMode=1,CurrentBank=191,CurrentBankC=227).items():m[address(b,n)]=v
            zp,ram=address(b,'TnAudioZp'),address(b,'TnAudioRam');x=case['n']
            m[zp+2]=case['e2'];m[ram+0x22+x]=37;m[ram+0x28+x]=219;m[ram+0x16+x]=case.get('status',91);m[ram+4+x]=case['e2']
            m[0x5204]=128;m.writes=[];m.math_events=[];m[510],m[511]=255,1
            c=NesMPU(memory=m);c.pc,c.a,c.x,c.y,c.p,c.sp=0xaacc if kind=='tempo' else 0xa671,case['e2'],x,47,case['flags'],253
            return c,m
        c,m=setup();trace=[]
        for i in range(4000):
            if c.pc in ends:break
            trace.append(i);m.executing_PC=c.pc;c.step()
        else:raise AssertionError(('Uninterrupted timeout',case))
        expected=registers(c),ordinary(m),list(m.banks),list(m.operands),list(m.math_events)
        for position in trace:
            d,n=setup();injected=False
            for index in range(4000):
                if d.pc in ends:break
                if index==position:
                    before=registers(d),ordinary(n),list(n.banks),list(n.operands),list(n.math_events)
                    d.irq();assert d.pc==0x8000;minimum=d.sp
                    for _ in range(300):
                        if d.pc==before[0][0]and d.sp==before[0][-1]:break
                        minimum=min(minimum,d.sp);n.executing_PC=d.pc;d.step()
                    else:raise AssertionError(('IRQ timeout',case,index))
                    assert(registers(d),ordinary(n),list(n.banks),list(n.operands),list(n.math_events))==before
                    maximum=max(maximum,255-minimum);injected=True
                n.executing_PC=d.pc;d.step()
            else:raise AssertionError(('Interrupted timeout',case,position))
            assert injected and(registers(d),ordinary(n),list(n.banks),list(n.operands),list(n.math_events))==expected
            count+=1
        rows.append(case|dict(actual_instruction_boundaries=len(trace)))
    proof=dict(passed=True,source_only=True,native_run=False,candidate_ROM_sha256=sha(a.candidate),actual_compiled_IRQ_injections=count,
        maximum_total_stack_depth=maximum,full_intermediate_and_final_registers_sourceRAM_SMC_banks_products_exact=True,
        actual_IRQ_has_no_product_access=True,no_nested_NMI_supported_claim=True,rows=rows,checker_sha256=sha(Path(__file__)))
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:proof[k]for k in['passed','actual_compiled_IRQ_injections','maximum_total_stack_depth']}))


if __name__=='__main__':main()
