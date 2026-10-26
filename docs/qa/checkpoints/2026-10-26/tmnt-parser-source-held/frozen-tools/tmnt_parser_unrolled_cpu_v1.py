"""Per-voice complete-state induction, ordered writes, actual IRQ and closure."""
from pathlib import Path
import argparse
import csv
import gzip
import json
from py65.disassembler import Disassembler
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT,OB,source_data,sha
from tmnt_parser_math_next_cpu_v1 import Linked,outcome
from tmnt_native_storage_irq_cpu import ordinary,registers


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['baseline','candidate','native','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    old,new=load(a.baseline),load(a.candidate);parent,child=Linked(a.baseline,True),Linked(a.candidate,True)
    lo=address(new,'TnNativeUnrolled');size=int(new['syms']['TnNativeUnrolled']['size'],0);off=location(new,'TnNativeUnrolled')
    body=new['raw'][off:off+size];store=bytes([0x8e,address(new,'TnAudioRam')+0x92&255,(address(new,'TnAudioRam')+0x92)>>8])
    headers=[lo+i for i in range(len(body)-2)if body[i:i+3]==store];assert len(headers)==6
    gold=json.loads(gzip.decompress((OB/'probe-v2/song-02.json.gz').read_bytes()))
    states={int(r['sourceTick']):bytes.fromhex(r['ZP14_RAM174_hex'])for r in csv.DictReader((a.native/'source-state.csv').open())}
    header_checks=calls=0;snapshot=None
    source_writes=lambda m:[(at,v)for at,v in m.writes if not 0x100<=at<0x200]
    for tick in range(602):
        if tick==533:
            snapshot=dict(memory=list(child.m),banks=list(child.m.banks),operands=list(child.m.operands),
                registers=[child.c.a,child.c.x,child.c.y,child.c.p&~4])
        captures=[]
        for runner,pcs in[(parent,{0xa64b}),(child,set(headers))]:
            rows=[];real=runner.c.step
            def step():
                if runner.c.pc in pcs and runner.m.banks[1]==63:
                    rows.append(outcome(runner.c,runner.m))
                real()
            runner.c.step=step;runner.call(gold[tick],2);runner.c.step=real;captures.append(rows)
            assert runner.state()==states[tick]
        expected=0 if gold[tick]['call']==-1 else 6
        assert len(captures[0])==len(captures[1])==expected
        assert captures[0]==captures[1],('Per-voice source register/state mismatch',tick)
        assert outcome(parent.c,parent.m)==outcome(child.c,child.m)
        assert source_writes(parent.m)==source_writes(child.m),('Ordered source writes changed',tick)
        assert parent.m.math_events==child.m.math_events and parent.m.operands==child.m.operands
        header_checks+=expected;calls+=1
    assert snapshot is not None
    def setup(empty):
        q=Linked(a.candidate,True);q.m[:]=snapshot['memory'];q.m.banks=list(snapshot['banks']);q.m.operands=list(snapshot['operands'])
        if empty:
            for i in range(6):q.m[address(new,'TnAudioRam')+0x0a+i]=0
        q.m[0x5204]=128;q.m[510],q.m[511]=255,1;q.m.writes=[];q.m.math_events=[]
        q.c.a,q.c.x,q.c.y,q.c.p=snapshot['registers'];q.c.pc,q.c.sp=address(new,'TnNativePlay'),253
        return q.c,q.m
    def final(c,m):return registers(c),ordinary(m),list(m.banks),list(m.operands),list(m.math_events),[(at,v)for at,v in m.writes if 0x4000<=at<=0x4017 or 0x5000<=at<=0x5015]
    injections=maximum=0;irq_rows=[]
    for empty in[False,True]:
        c,m=setup(empty);trace=[]
        for i in range(50000):
            if c.pc==512:break
            if lo<=c.pc<lo+size:trace.append(i)
            m.executing_PC=c.pc;c.step()
        else:raise AssertionError('Unrolled source timeout')
        expected=final(c,m)
        for position in trace:
            c,m=setup(empty);injected=False
            for i in range(50000):
                if c.pc==512:break
                if i==position:
                    before=registers(c),ordinary(m),list(m.banks),list(m.operands),list(m.math_events)
                    c.irq();assert c.pc==0x8000;minimum=c.sp
                    for _ in range(300):
                        if c.pc==before[0][0]and c.sp==before[0][-1]:break
                        minimum=min(minimum,c.sp);m.executing_PC=c.pc;c.step()
                    else:raise AssertionError('IRQ return timeout')
                    assert(registers(c),ordinary(m),list(m.banks),list(m.operands),list(m.math_events))==before
                    maximum=max(maximum,255-minimum);injected=True
                m.executing_PC=c.pc;c.step()
            else:raise AssertionError('Interrupted source timeout')
            assert injected and final(c,m)==expected
            injections+=1
        irq_rows.append(dict(before_source_tick533_state=True,all_six_private_active_flags_forced_zero=empty,boundaries=len(trace)))
    _,mem,cpu,dis,seen,words=source_data();refs=[]
    for pc in seen:
        if 0x8644<=pc<0x8647:continue
        width,_=dis.instruction_at(pc);op,mode=cpu.disassemble[mem[pc]];targets=[]
        if mode=='rel':
            off=mem[pc+1];targets=[pc+width,pc+width+(off-256 if off>=128 else off)]
        elif op in['JSR','JMP']and mode=='abs':targets=[mem[pc+1]+256*mem[pc+2]]
        elif op not in['RTS','RTI','JMP','BRK']:targets=[pc+width]
        refs.extend([pc,to]for to in targets if 0x8644<=to<0x8647)
    roots=[word for word in words if 0x8644<=mem[word]+256*mem[word+1]<0x8647]
    assert all(to==0x8644 for pc,to in refs)and all(mem[p]+256*mem[p+1]==0x8644 for p in roots)
    proof=dict(passed=True,source_only=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
        actual_native_188byte_state_stream_sha256=sha(a.native/'source-state.csv'),full_source_calls=calls,
        per_voice_full_AXYP_SP_sourceRAM_SMC_banks_orderedAPU_and_math_induction_checks=header_checks,
        every_ordered_nonstack_source_write_exact=True,no_source_parser_call_event_or_store_omission=True,
        actual_compiled_IRQ_injections=injections,maximum_total_stack_depth=maximum,IRQ_cases=irq_rows,
        no_nested_NMI_or_physical_hardware_claim=True,new_genuine_header_PCs=headers,old_numeric_play_entry_genuine_JMP=True,
        original_entry_external_refs=refs,original_entry_pointer_roots=roots,checker_sha256=sha(Path(__file__)),native_recovery_claim=False)
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
