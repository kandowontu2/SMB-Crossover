"""Bound first native miss against actual publication/flag-read instructions.

Read-only retained traces plus exact compiled IRQ/NMI/tail instructions. This
does not execute Mesen or claim counterfactual native cadence recovery.
"""
from pathlib import Path
import argparse
import csv
import json
from py65.disassembler import Disassembler
from check_tmnt_render_oa import load,Memory,address
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT,sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['storage','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();d,out=a.storage,a.output
    assert not out.exists() and not out.resolve().is_relative_to(ROOT)
    rom=d/'parser-ready-v1/candidate.nes'
    digest='9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd'
    assert sha(rom)==digest
    diagnosis=d/'parser-native-negative-ready-v1/diagnosis.json'
    assert sha(diagnosis)=='aeb77d02e160c5fc11b3126ab3276ab4560602d17de827c374b5acb26a460baa'
    j=json.loads(diagnosis.read_text());first=j['first_causal_deadline']
    native=d/'parser-native-pilot-v1/candidate-easy'
    audio=list(csv.DictReader((native/'audio-components.csv').open()))
    calls=list(csv.DictReader((native/'tmnt-performance-calls.csv').open()))
    main=[r for r in calls if r['name']=='GameLoop'][405]
    start=first['candidate']['draw']['stamp']['cpu'];finish=first['candidate']['complete']['stamp']['cpu']
    inside=[r for r in audio if r['name']=='AudioUpdate' and start<int(r['startCPU'])<finish]
    assert len(inside)==1 and inside[0]['IRQCycles']=='0'
    interrupted_audio=inside[0]
    b=load(rom);m=Memory(b)
    for name,value in dict(NmiDisable=255,DisableScreenFlag=0,SelectedCharacter=19,CurrentBank=215,CurrentBankC=216,Mirror_PPUCTRL=128).items():m[address(b,name)]=value
    c=NesMPU(memory=m);c.pc=address(b,'NonMaskableInterrupt');c.sp=240;c.p=0x24
    dis=Disassembler(c);trace=[];read=None
    for _ in range(300):
        if c.pc==address(b,'AudioUpdate'):break
        pc=c.pc;before=c.processorCycles;instruction=dis.instruction_at(pc)[1]
        c.step();trace.append(dict(pc=pc,instruction=instruction,start_CPU=before,end_CPU=c.processorCycles))
        if pc==address(b,'NonMaskableInterrupt')+9:
            pass
        if instruction==f'LDA ${address(b,"NmiDisable"):04x}':read=trace[-1]
    else:raise AssertionError('Lag NMI prelude timeout')
    assert read and read['start_CPU']==20 and read['end_CPU']==24 and c.processorCycles==85
    prelude=c.processorCycles
    # Return to the literal JSR continuation without replacing/emulating any
    # source audio body. Its actual measured duration comes from retained CSV.
    c.pc=(m[0x100+(c.sp+1)%256]+256*m[0x100+(c.sp+2)%256]+1)&65535
    c.sp=(c.sp+2)&255;c.processorCycles=0;post=[]
    for _ in range(100):
        pc=c.pc;instruction=dis.instruction_at(pc)[1];before=c.processorCycles
        c.step();post.append(dict(pc=pc,instruction=instruction,start_CPU=before,end_CPU=c.processorCycles))
        if instruction=='RTI':break
    else:raise AssertionError('Lag NMI postlude timeout')
    assert c.processorCycles==37
    prepost=7+prelude+c.processorCycles
    assert prepost==129
    nmi_duration=prepost+int(interrupted_audio['inclusiveCycles'])
    assert nmi_duration==int(main['isrCycles'])==2832
    q=qualified(rom);pause=q['GameLoop','PauseSkip']
    mem=Memory(b);cpu=NesMPU(memory=mem);cpu.pc=pause;cpu.sp=253;mem[510],mem[511]=255,126
    tail=[]
    for _ in range(3):
        pc=cpu.pc;instruction=Disassembler(cpu).instruction_at(pc)[1];before=cpu.processorCycles;cpu.step()
        tail.append(dict(pc=pc,instruction=instruction,start_CPU=before,end_CPU=cpu.processorCycles))
    assert cpu.pc==0x7f00 and [t['instruction'] for t in tail]==['LDA #$00',f'STA ${address(b,"NmiDisable"):04x}','RTS']
    assert tail[-1]['end_CPU']-tail[-1]['start_CPU']==6
    clear_without_intervening_nmi=finish-nmi_duration-6
    flag_read_complete=int(interrupted_audio['startCPU'])-(prelude-read['end_CPU'])
    baseline_clear=first['baseline']['complete']['stamp']['cpu']-6
    distance=clear_without_intervening_nmi-flag_read_complete
    assert distance==409 and flag_read_complete-baseline_clear==2556
    out.mkdir(parents=True)
    result=dict(valid=True,source_only=True,native_run=False,ROM_sha256=digest,first_missed_publication_update=406,
        actual_NMI_audio_span=interrupted_audio,main_span=main,exact_compiled_NMI_prelude_cycles=85,
        exact_compiled_NMI_postlude_cycles=37,hardware_NMI_entry_cycles=7,actual_lag_NMI_cycles=2832,
        exact_match_to_entire_observed_main_ISR_cycles=True,actual_NmiDisable_read_completion_CPU=flag_read_complete,
        clear_completion_without_intervening_lag_NMI_CPU=clear_without_intervening_nmi,
        publication_completion_lateness_CPU=distance,strict_before_same_flag_read_requires_saved_CPU_at_least=distance+1,
        baseline_publication_slack_to_actual_candidate_flag_read_CPU=2556,
        renderer_empty_scan_gate_saving_in_this_primary_case=0,
        limits='The409cycle distance is source reconstruction from completed native instruction spans, not a recorded bus access or a new native run. Completion boundaries use matching final-cycle read/write offsets.410 is the strict-before target for this existing flag-read alignment; a new candidate can alter instruction/IRQ/DMC alignment and requires new native qualification. This does not authorize changing workload, publication policy or cadence assertions.',
        NMI_prelude=trace,NMI_postlude=post,GameLoop_publication_tail=tail,
        bindings={str(p):sha(p) for p in [rom,diagnosis,native/'audio-components.csv',native/'tmnt-performance-calls.csv',Path(__file__)]})
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['valid','actual_NmiDisable_read_completion_CPU','clear_completion_without_intervening_lag_NMI_CPU','publication_completion_lateness_CPU','strict_before_same_flag_read_requires_saved_CPU_at_least','renderer_empty_scan_gate_saving_in_this_primary_case']}))


if __name__=='__main__':main()
