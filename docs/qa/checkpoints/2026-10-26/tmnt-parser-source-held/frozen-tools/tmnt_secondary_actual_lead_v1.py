"""Bound the remaining first secondary loss to real core/control costs, no fix."""
from pathlib import Path
from collections import Counter
import argparse
import csv
import gzip
import json
from py65.disassembler import Disassembler
from tmnt_native_storage_driver import ROOT,OB,sha
from tmnt_native_storage_multiply_cpu import Linked

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')


def read(p):
    with p.open()as f:return list(csv.DictReader(f))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;native=D/'tmnt-sweep-live-math-native-ready-v1/candidate-easy';rom=D/'tmnt-sweep-live-math-v1/candidate.nes'
    assert not out.exists()and not out.resolve().is_relative_to(ROOT)
    audio=read(native/'audio-components.csv');requests=read(native/'source-apu.csv');states=read(native/'source-state.csv')
    top=next(r for r in audio if r['name']=='AudioUpdate'and r['phase']=='secondary'and r['update']=='531')
    call=next(r for r in audio if r['name']=='TnNativePlay'and int(r['startCPU'])>=int(top['startCPU'])and int(r['endCPU'])<=int(top['endCPU']))
    tick=int(next(r for r in requests if int(call['startCPU'])<=int(r['cpu'])<=int(call['endCPU']))['sourceTick'])
    gold=json.loads(gzip.decompress((OB/'probe-v2/song-02.json.gz').read_bytes()))
    runner=Linked(rom,True);trace=[];own=Counter();counts=Counter();instructions=Counter();targets=Counter();stack=[]
    for i in range(tick+1):
        if i!=tick:
            runner.call(gold[i],2)
        else:
            assert runner.state()==bytes.fromhex(states[i-1]['ZP14_RAM174_hex'])
            c,m=runner.c,runner.m;dis=Disassembler(c);step=c.step
            def profile():
                pc,cy=c.pc,c.processorCycles;_,text=dis.instruction_at(pc);op,mode=c.disassemble[m[pc]]
                owner=stack[-1]if stack else 0xa644;target=m[pc+1]+256*m[pc+2]if op=='JSR'else None
                step();delta=c.processorCycles-cy;own[owner]+=delta;counts[pc]+=1;instructions[pc,text]+=delta
                trace.append(dict(PC=pc,instruction=text,cycles=delta,owner=owner))
                if op=='JSR':targets[target]+=1;stack.append(target)
                elif op=='RTS'and stack:stack.pop()
            c.step=profile;cycles=runner.call(gold[i],2);c.step=step
            assert not stack
        assert runner.state()==bytes.fromhex(states[i]['ZP14_RAM174_hex'])
    assert sum(own.values())==cycles
    spans=read(native/'tmnt-performance-calls.csv');main=[r for r in spans if r['name']=='GameLoop']
    assert len(main)==600
    measured={name:dict(calls=len(v),cycles=sum(int(r['cpuCycles'])for r in v))
        for name in sorted({r['name']for r in spans if r['startFrame']=='860'})
        if(v:=[r for r in spans if r['startFrame']=='860'and r['name']==name])}
    core=dict(actual_sourceTick=tick,actual_full_native_core=call,paired_isolated_full_core_cycles=cycles,
        native_minus_isolated_cycles=int(call['CPUcycles'])-cycles,
        source_APU_count=len(gold[tick]['writes']),
        exclusive_cycles_by_direct_call_owner={hex(k):v for k,v in own.most_common()},
        actual_direct_calls={hex(k):v for k,v in targets.most_common()},
        top_instructions=[dict(PC=pc,instruction=t,cycles=n,count=counts[pc])for(pc,t),n in instructions.most_common(24)])
    out.mkdir(parents=True);(out/'source-trace.json.gz').write_bytes(gzip.compress(json.dumps(trace).encode()))
    proof=dict(measurement_valid=True,implementation=False,native_run=False,ROM_sha256=sha(rom),
        actual_frozen_native_negative='5373 Easy600:4extra secondary lost draws; no retry',
        source_state_stream_sha256=sha(native/'source-state.csv'),audio_costs_sha256=sha(native/'audio-components.csv'),
        source_full_before_after188B_state_and_original_APU_exact=True,
        first_loss_preceding_actual_AudioUpdate=top,actual_source_core_profile=core,
        actual_first_loss_foreground=main[531],actual_first_loss_caller_components=measured,
        source_trace_sha256=sha(out/'source-trace.json.gz'),checker_sha256=sha(Path(__file__)),
        limits='Source CPU profile reproduces real captured188B source states and every ordered request. No full native mixer/Main snapshot or physical DMC/NMI timing replay is claimed. Direct-call exclusive owners are a cost lead, not proof of removable work; preserve complete parser/voice/stream/ABI behavior in any future optimization. No production or native change.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(tick=tick,actual_native_core_cycles=int(call['CPUcycles']),isolated_core_cycles=cycles,
        owners=core['exclusive_cycles_by_direct_call_owner'],foreground=main[531],components=measured)))


if __name__=='__main__':main()
