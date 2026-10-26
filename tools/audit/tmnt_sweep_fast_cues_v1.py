"""Disclosed source-only full-caller effect/retrigger costs; retain regressions."""
from pathlib import Path
from collections import Counter
import argparse
import json
from check_tmnt_render_oa import load,address
from tmnt_native_storage_driver import ROOT,sha
from tmnt_native_storage_multiply import MathMemory
from tmnt_sweep_fast_outer_v1 import outcome
from verify_native_relocation import NesMPU


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    old,new=load(a.baseline),load(a.candidate);rows=[];total=Counter();count=0
    scenarios=[('none',0,0,0)]+[(name,1<<i if ch==0 else 0,1<<i if ch==1 else 0,1<<i if ch==2 else 0)
              for ch,name in enumerate(['square1','square2','noise'])for i in range(8)]+[('all',255,255,255)]
    for name,q1,q2,qn in scenarios:
        machines=[]
        for b in[old,new]:
            m=MathMemory(b);m.page(2,38)
            for n,v in dict(SelectedCharacter=19,TnVariant=0,OperMode=1,CrossoverBehaviorVersion=0,AreaMusicQueue=1,
                           CurrentBank=215,CurrentBankC=166,XgAudioCharacter=255).items():m[address(b,n)]=v
            machines.append((b,m,NesMPU(memory=m)))
        costs=Counter();bad=[]
        for tick in range(80):
            cycles=[]
            for b,m,c in machines:
                # Test setup/status/queues are explicit BEFORE-call inputs,
                # never native acquisition or in-phase outcome modifications.
                m[0x4015]=m[0x4015]&15
                if tick>=20 and tick%3==2:
                    for n,v in [('Square1SoundQueue',q1),('Square2SoundQueue',q2),('NoiseSoundQueue',qn)]:m[address(b,n)]=v
                c.pc,c.a,c.x,c.y,c.p,c.sp=address(b,'AudioUpdate'),85,3,7,0x69,253
                m[510],m[511]=255,126;m.writes=[];m.math_events=[];start=c.processorCycles
                for _ in range(50000):
                    if c.pc==0x7f00:break
                    m.executing_PC=c.pc;c.step()
                else:raise AssertionError('Cue full-caller timeout')
                cycles.append(c.processorCycles-start)
            assert outcome(machines[0][2],machines[0][1])==outcome(machines[1][2],machines[1][1]),(name,q1,q2,qn,tick)
            assert machines[0][1].math_events==machines[1][1].math_events
            d=cycles[1]-cycles[0];costs[d]+=1;total[d]+=1;count+=1
            if d>0:bad.append(dict(tick=tick,parent=cycles[0],candidate=cycles[1],delta=d))
        rows.append(dict(kind=name,queues=[q1,q2,qn],calls=80,cycle_deltas=dict(sorted(costs.items())),regressions=bad))
    proof=dict(passed=True,source_only=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
               complete_paired_AudioUpdate_calls=count,final_AXYP_SP_RAM_SMC_banks_and_ordered_APU_exact=True,
               arranged_before_call_shared_queues_and4015_status=True,natural_acquisition_or_native_snapshot_claim=False,
               caller_cycle_deltas=dict(sorted(total.items())),regression_calls=sum(len(r['regressions'])for r in rows),rows=rows,
               checker_sha256=sha(Path(__file__)),native_recovery_claim=False)
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items()if k!='rows'}))


if __name__=='__main__':main()
