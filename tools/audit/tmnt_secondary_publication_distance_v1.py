"""Reconstruct the first real secondary missed-publication distance, no retry."""
from pathlib import Path
import argparse
import csv
import json
from py65.disassembler import Disassembler
from check_tmnt_render_oa import load,Memory,address
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT,sha

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output;native=D/'tmnt-sweep-live-math-native-ready-v1/candidate-easy';rom=D/'tmnt-sweep-live-math-v1/candidate.nes'
    assert not out.exists()and not out.resolve().is_relative_to(ROOT)
    bus=[json.loads(x)for x in(native/'native-bus.jsonl').read_text().splitlines()]
    draw=next(r for r in bus if r['kind']=='draw-construction'and r['index']==532)
    done=next(r for r in bus if r['kind']=='completed-game-update'and r['index']==532)
    with(native/'audio-components.csv').open()as f:audio=list(csv.DictReader(f))
    inside=[r for r in audio if r['name']=='AudioUpdate'and draw['stamp']['cpu']<int(r['startCPU'])<done['stamp']['cpu']]
    assert len(inside)==1 and inside[0]['IRQCycles']=='0';span=inside[0]
    with(native/'tmnt-performance-calls.csv').open()as f:main=[r for r in csv.DictReader(f)if r['name']=='GameLoop'][531]
    b=load(rom);m=Memory(b)
    for n,v in dict(NmiDisable=255,DisableScreenFlag=0,SelectedCharacter=19,CurrentBank=215,CurrentBankC=216,Mirror_PPUCTRL=128).items():m[address(b,n)]=v
    c=NesMPU(memory=m);c.pc=address(b,'NonMaskableInterrupt');c.sp=240;c.p=0x24;dis=Disassembler(c);pre=[]
    for _ in range(300):
        if c.pc==address(b,'AudioUpdate'):break
        pc,cycle=c.pc,c.processorCycles;text=dis.instruction_at(pc)[1];c.step();pre.append(dict(PC=pc,instruction=text,cycles=c.processorCycles-cycle))
    else:raise AssertionError('Prelude timeout')
    assert c.processorCycles==85
    c.pc=(m[0x100+(c.sp+1)%256]+256*m[0x100+(c.sp+2)%256]+1)&65535;c.sp=(c.sp+2)&255;c.processorCycles=0;post=[]
    for _ in range(100):
        pc,cycle=c.pc,c.processorCycles;text=dis.instruction_at(pc)[1];c.step();post.append(dict(PC=pc,instruction=text,cycles=c.processorCycles-cycle))
        if text=='RTI':break
    else:raise AssertionError('Postlude timeout')
    assert c.processorCycles==37
    interruption=7+85+int(span['inclusiveCycles'])+37
    assert interruption==int(main['isrCycles'])==4228
    acceptance=int(span['startCPU'])-85-7
    clear=done['stamp']['cpu']-interruption-6
    assert acceptance==25638639 and clear==25639373 and clear-acceptance==734
    out.mkdir(parents=True)
    proof=dict(valid=True,source_only=True,native_run=False,ROM_sha256=sha(rom),publication_update=532,
        following_actual_missing_hardware_epoch=862,source_reconstructed_acceptance_CPU=acceptance,
        counterfactual_Main_clear_without_NMI_CPU=clear,strict_before_same_acceptance_saving_target=735,
        measured_intervening_audio=span,actual_main_span=main,compiled_prelude_cycles=85,compiled_postlude_cycles=37,
        hardware_entry_cycles=7,entire_Main_ISR4228_exactly_reproduced=True,prelude=pre,postlude=post,
        inputs={str(path):sha(path)for path in[rom,native/'native-bus.jsonl',native/'audio-components.csv',native/'tmnt-performance-calls.csv']},
        checker_sha256=sha(Path(__file__)),
        limits='734/735 are source reconstruction under the same interrupt/instruction/DMC alignment, not an actual recorded NMI-entry/stackedPC or a native recovery promise. Main cannot publish during the ISR. No state/workload/ROM/native changes; original strict negative remains.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k]for k in ['valid','source_reconstructed_acceptance_CPU','counterfactual_Main_clear_without_NMI_CPU','strict_before_same_acceptance_saving_target']}))


if __name__=='__main__':main()
