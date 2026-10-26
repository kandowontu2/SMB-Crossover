"""Prove ACE8 replacement ABI, all byte axes, real callers/IRQ/native source states."""
from pathlib import Path
from collections import Counter
import argparse
import csv
import gzip
import itertools
import json
from check_tmnt_render_oa import load, address
from tmnt_native_storage_multiply import MathMemory
from tmnt_native_storage_irq_cpu import ordinary, registers
from verify_native_relocation import NesMPU
from tmnt_parser_math_next_cpu_v1 import FLAGS, Linked, outcome
from tmnt_native_storage_driver import ROOT, OB, sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['baseline','candidate','native','output']: p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(); assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True); old,new=load(a.baseline),load(a.candidate)
    helper=address(new,'TnSourceChannelOwner'); machines=[]
    for b in [old,new]:
        m=MathMemory(b);m.page(1,63);m.page(2,99);machines.append((b,NesMPU(memory=m),m))
    def pair(aval,x,y,pin,gate,saved,sp=253,site=None):
        results=[];costs=[]
        for k,(b,c,m)in enumerate(machines):
            m[address(b,'TnAudioRam')+0x0e]=gate;m[address(b,'TnAudioRam')+0x93]=saved
            m[sp+0x100]=255;m[(sp+1)%256+0x100]=126
            c.pc=site if site else 0xace8 if k==0 else helper
            c.a,c.x,c.y,c.p,c.sp=aval,x,y,pin,sp if site else sp-1
            m.writes=[];m.math_events=[];start=c.processorCycles
            for _ in range(40):
                if c.pc==(site+3 if site else 0x7f00):break
                m.executing_PC=c.pc;c.step()
            else:raise AssertionError(('Channel owner domain timeout',site,aval,x,y,pin,hex(c.pc)))
            stores=[(at,v)for at,v in m.writes if not 0x100<=at<0x200]
            assert not stores and not m.math_events and m.banks==[126,63,99,127]
            results.append((c.a,c.x,c.y,c.p&207,c.sp));costs.append(c.processorCycles-start)
        assert results[0]==results[1],('Full channel owner ABI',site,aval,x,y,pin,gate,saved,results)
        assert costs[1]-costs[0]==(-5 if x else 0),(site,x,costs)
        return costs[1]-costs[0]
    domains=Counter();count=0
    for aval,x,pin,gate,saved in itertools.product(range(256),range(6),FLAGS,[0,255],[0,255]):
        domains[pair(aval,x,(aval+x)%256,pin,gate,saved)]+=1;count+=1
    for x,pin,aval,gate,saved in itertools.product(range(256),FLAGS,[0,1,128,255],[0,255],[0,255]):
        domains[pair(aval,x,(x*73)%256,pin,gate,saved)]+=1;count+=1
    for aval,x,y,gate,saved,pin,sp in itertools.product([0,255],[0,1,5,255],[0,47,255],[0,255],[0,255],[0x20,0xe9],[223,247,253,255]):
        domains[pair(aval,x,y,pin,gate,saved,sp)]+=1;count+=1
    prep=json.loads((a.candidate.parent/'channel-owner-preparation.json').read_text())
    for row in prep['replaced_real_direct_calls']:
        for aval,x,pin,gate,saved in itertools.product([0,1,128,255],[0,1,2,5,255],FLAGS,[0,255],[0,255]):
            domains[pair(aval,x,47,pin,gate,saved,253,row['runtime_PC'])]+=1;count+=1
    def setup(x,gate,aval,pin):
        m=MathMemory(new);m.page(1,63);m.page(2,99);m[address(new,'TnAudioRam')+0x0e]=gate;m[address(new,'TnAudioRam')+0x93]=255
        m[510],m[511]=255,126;m[0x5204]=128;m.writes=[];m.math_events=[]
        c=NesMPU(memory=m);c.pc,c.a,c.x,c.y,c.p,c.sp=helper,aval,x,47,pin,253
        return c,m
    def final(c,m):
        return(registers(c),ordinary(m),tuple(m.banks),tuple(m.operands),tuple(map(tuple,m.math_events)),
               [(at,v)for at,v in m.writes if not 0x100<=at<0x200 and at not in [0x2005,0x2006,0x5128,0x5204]])
    irq=0;maximum=0;irq_rows=[]
    for x,gate,aval,pin in itertools.product([0,1,5,255],[0,255],[0,255],[0x20,0xe9]):
        c,m=setup(x,gate,aval,pin);trace=[]
        while c.pc!=0x7f00:trace.append(c.pc);m.executing_PC=c.pc;c.step()
        expected=final(c,m)
        for position,pc in enumerate(trace):
            d,n=setup(x,gate,aval,pin)
            for i in range(40):
                if d.pc==0x7f00:break
                if i==position:
                    before=registers(d),ordinary(n),tuple(n.banks),tuple(n.operands),tuple(map(tuple,n.math_events));first=len(n.writes)
                    assert not d.p&4;d.irq();assert d.pc==0x8000;minimum=d.sp
                    for _ in range(300):
                        if d.pc==before[0][0]and d.sp==before[0][-1]:break
                        minimum=min(minimum,d.sp);n.executing_PC=d.pc;d.step()
                    else:raise AssertionError('Actual IRQ return timeout')
                    assert(registers(d),ordinary(n),tuple(n.banks),tuple(n.operands),tuple(map(tuple,n.math_events)))==before
                    stores=[(at,v)for at,v in n.writes[first:]if not 0x100<=at<0x200]
                    assert stores==[(0x2006,0),(0x5128,0),(0x2005,32),(0x2005,0),(0x2006,128)]
                    maximum=max(maximum,255-minimum)
                n.executing_PC=d.pc;d.step()
            assert final(d,n)==expected;irq+=1
        irq_rows.append(dict(X=x,gate=gate,A=aval,P=pin,boundaries=trace))
    gold=json.loads(gzip.decompress((OB/'probe-v2/song-02.json.gz').read_bytes()))
    states={int(r['sourceTick']):bytes.fromhex(r['ZP14_RAM174_hex'])for r in csv.DictReader((a.native/'source-state.csv').open())}
    parent,child=Linked(a.baseline,True),Linked(a.candidate,True);stream=[]
    for tick in range(602):
        costs=[];hits=[]
        for k,runner in enumerate([parent,child]):
            entries=Counter();step=runner.c.step
            def intercept():
                if runner.c.pc==(0xace8 if k==0 else helper)and runner.m.banks[1]==63:entries['nonzero'if runner.c.x else'zero']+=1
                step()
            runner.c.step=intercept;costs.append(runner.call(gold[tick],2));runner.c.step=step;hits.append(entries)
            assert runner.state()==states[tick]
        assert outcome(parent.c,parent.m)==outcome(child.c,child.m)
        writes=lambda m:[(at,v)for at,v in m.writes if not 0x100<=at<0x200]
        assert writes(parent.m)==writes(child.m)and parent.m.math_events==child.m.math_events and parent.m.operands==child.m.operands
        assert hits[0]==hits[1]and costs[1]-costs[0]==-5*hits[0]['nonzero']
        stream.append(dict(sourceTick=tick,baseline_cycles=costs[0],candidate_cycles=costs[1],delta=costs[1]-costs[0],original_entry_calls=dict(hits[0])))
    (a.output/'actual-source-stream.json').write_text(json.dumps(stream,indent=2)+'\n')
    (a.output/'IRQ-cases.json').write_text(json.dumps(irq_rows,indent=2)+'\n')
    q=dict(passed=True,source_only=True,native_run=False,accepted=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
           complete_domain_and_real_callers=count,all64P_all256A_actual_X0_to5=True,all256X_with_A_edges=True,Y_and_stack_edges=True,
           exact_AXYP_SP_banks_and_no_nonstack_writes=True,cycle_delta_histogram=dict(domains),
           actual_compiled_IRQ_injections=irq,maximum_total_stack_depth=maximum,all_five_IRQ_stores_exact=True,
           IRQ_cases_sha256=sha(a.output/'IRQ-cases.json'),native188byte_source_stream_calls=602,native_state_binding_sha256=sha(a.native/'source-state.csv'),
           every_original_ordered_nonstack_write_math_and_source_endpoint_exact=True,stream_sha256=sha(a.output/'actual-source-stream.json'),
           hot_source_rows=[r for r in stream if r['sourceTick']in[407,505,533,535]],checker_sha256=sha(Path(__file__)),
           limits='Arranged CPU leaf/caller axes and actual compiled IRQ. Native188-byte music inputs are real; no whole foreground RAM snapshot, physical DMC/NMI/PPU scheduling or recovered native display claim.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
