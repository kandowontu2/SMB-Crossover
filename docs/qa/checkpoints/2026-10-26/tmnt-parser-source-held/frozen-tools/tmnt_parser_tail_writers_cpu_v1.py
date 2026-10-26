"""Exact source STA tails: complete flags/stores, all source dirty edges and IRQ."""
from pathlib import Path
from collections import Counter
import argparse
import csv
import gzip
import itertools
import json
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT,OB,sha
from tmnt_native_storage_multiply import MathMemory
from tmnt_native_storage_irq_cpu import ordinary,registers
from tmnt_parser_math_next_cpu_v1 import FLAGS,Linked,outcome
from tmnt_parser_tail_writers_source_v2 import SITES


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['baseline','candidate','native','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    old,new=load(a.baseline),load(a.candidate);machines=[]
    for b in[old,new]:
        m=MathMemory(b);m.page(1,63);m.page(2,99);machines.append((b,NesMPU(memory=m),m))
    domains=Counter();cases=0;irq_count=depth=0
    def pair(site,aval,x,y,dirty,flags,sp=253):
        pc,helper,offset,indexed,_=site;results=[];costs=[]
        for b,c,m in machines:
            target=address(b,'GuestNativeApu')+offset+(x if indexed else 0)
            stamp=address(b,'GuestNativeDirty')+offset+(x if indexed else 0)
            m[target]=91;m[stamp]=dirty;m.writes=[];m.math_events=[]
            c.pc,c.a,c.x,c.y,c.p,c.sp=pc,aval,x,y,flags,sp;start=c.processorCycles
            for _ in range(20):
                if c.pc==pc+3:break
                m.executing_PC=c.pc;c.step()
            else:raise AssertionError(('Tail domain timeout',hex(pc)))
            stores=[(at,v)for at,v in m.writes if not 0x100<=at<0x200]
            assert stores==[(target,aval),(stamp,(dirty+1)&255)]
            assert m[target]==aval and m[stamp]==(dirty+1)&255
            assert not m.math_events and m.banks==[126,63,99,127]
            results.append((c.a,c.x,c.y,c.p&207,c.sp,stores));costs.append(c.processorCycles-start)
        assert results[0]==results[1]==(aval,x,y,flags&207,sp,results[0][-1])
        assert costs[1]-costs[0]==-6
        return -6
    for site in SITES:
        xs=[0,4,8,12]if site[3]else[0,3,255]
        for aval,x,y,dirty,flags in itertools.product([0,1,127,128,255],xs,[0,47,255],[0,1,127,128,254,255],FLAGS):
            domains[pair(site,aval,x,y,dirty,flags)]+=1;cases+=1
        for aval,x,dirty,flags in itertools.product(range(256),xs,[0,1,127,128,254,255],[0x20,0xe9]):
            domains[pair(site,aval,x,47,dirty,flags)]+=1;cases+=1
        # Legal cold stack depths plus near-page edge; no source stores omitted.
        for sp in[223,233,247,251,255]:
            domains[pair(site,255,xs[-1],255,255,0xe9,sp)]+=1;cases+=1
    def setup(site,aval,x,dirty,flags):
        b=new;m=MathMemory(b);m.page(1,63);m.page(2,99)
        pc,helper,offset,indexed,_=site
        m[address(b,'GuestNativeDirty')+offset+(x if indexed else 0)]=dirty
        m[0x5204]=128;m.writes=[];m.math_events=[]
        c=NesMPU(memory=m);c.pc,c.a,c.x,c.y,c.p,c.sp=pc,aval,x,47,flags,253
        return c,m
    def final(c,m):
        return(registers(c),ordinary(m),list(m.banks),list(m.operands),list(m.math_events),
            [(at,v)for at,v in m.writes if not 0x100<=at<0x200 and at!=0x5204])
    irq_rows=[]
    for site in SITES:
        for aval,x,dirty,flags in itertools.product([0,255],[0,12]if site[3]else[3],[0,255],[0x20,0xe9]):
            c,m=setup(site,aval,x,dirty,flags);pcs=[]
            while c.pc!=site[0]+3:
                pcs.append(c.pc);m.executing_PC=c.pc;c.step()
            expected=final(c,m)
            for position in range(len(pcs)):
                c,m=setup(site,aval,x,dirty,flags)
                for i in range(30):
                    if c.pc==site[0]+3:break
                    if i==position:
                        before=registers(c),ordinary(m),list(m.banks),list(m.operands),list(m.math_events)
                        c.irq();assert c.pc==0x8000;minimum=c.sp
                        for _ in range(300):
                            if c.pc==before[0][0]and c.sp==before[0][-1]:break
                            minimum=min(minimum,c.sp);m.executing_PC=c.pc;c.step()
                        else:raise AssertionError('Actual compiled IRQ return timeout')
                        assert(registers(c),ordinary(m),list(m.banks),list(m.operands),list(m.math_events))==before
                        depth=max(depth,255-minimum)
                    m.executing_PC=c.pc;c.step()
                assert final(c,m)==expected
                irq_count+=1
            irq_rows.append(dict(source_PC=site[0],A=aval,X=x,dirty=dirty,P=flags,boundaries=pcs))
    # Bind real188-byte native source stream and all source-endpoint requests.
    gold=json.loads(gzip.decompress((OB/'probe-v2/song-02.json.gz').read_bytes()))
    states={int(r['sourceTick']):bytes.fromhex(r['ZP14_RAM174_hex'])for r in csv.DictReader((a.native/'source-state.csv').open())}
    parent,child=Linked(a.baseline,True),Linked(a.candidate,True);stream=[]
    for tick in range(602):
        costs=[];site_hits=[]
        for runner in[parent,child]:
            hits=Counter();real=runner.c.step
            def step():
                if runner.c.pc in{row[0]for row in SITES}and runner.m.banks[1]==63:hits[runner.c.pc]+=1
                real()
            runner.c.step=step;costs.append(runner.call(gold[tick],2));runner.c.step=real;site_hits.append(hits)
            assert runner.state()==states[tick]
        assert outcome(parent.c,parent.m)==outcome(child.c,child.m)
        writes=lambda m:[(at,v)for at,v in m.writes if not 0x100<=at<0x200]
        assert writes(parent.m)==writes(child.m)and parent.m.math_events==child.m.math_events and parent.m.operands==child.m.operands
        assert site_hits[0]==site_hits[1]and costs[1]-costs[0]==-6*sum(site_hits[0].values())
        stream.append(dict(sourceTick=tick,parent_cycles=costs[0],candidate_cycles=costs[1],delta=costs[1]-costs[0],
            exact_source_endpoint_counts=dict(site_hits[0])))
    (a.output/'actual-source-stream.json').write_text(json.dumps(stream,indent=2)+'\n')
    proof=dict(passed=True,source_only=True,native_run=False,accepted=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
        complete_AXYP_SP_store_order_and_dirty_wrap_cases=cases,all64_meaningful_flags=True,all256_A_values=True,legal_indexed_X=[0,4,8,12],
        direct_X_edges=[0,3,255],Y_edges=[0,47,255],dirty_edges=[0,1,127,128,254,255],cycle_delta_histogram=dict(domains),
        unchanged_bytes_structural_leaf_copy_and_exact_two_write_footprint=True,actual_compiled_IRQ_injections=irq_count,maximum_total_stack_depth=depth,
        IRQ_rows=irq_rows,native188byte_source_stream_calls=602,native_state_binding_sha256=sha(a.native/'source-state.csv'),
        every_original_source_endpoint_request_and_ordered_nonstack_write_exact=True,stream_sha256=sha(a.output/'actual-source-stream.json'),
        hot_source_rows=[r for r in stream if r['sourceTick']in[407,505,533,535]],checker_sha256=sha(Path(__file__)),native_recovery_claim=False)
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='IRQ_rows'}))


if __name__=='__main__':main()
