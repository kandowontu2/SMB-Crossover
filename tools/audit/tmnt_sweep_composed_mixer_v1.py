"""Fresh complete composed mixer controls for native-only MMC5 pulse owners."""
from pathlib import Path
import argparse
import itertools
import json
from check_tmnt_render_oa import load,Memory,address
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT,sha
from tmnt_sweep_fast_cpu_v2 import snapshot


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    old,new=load(a.baseline),load(a.candidate);flags=[32|(i&15)|((i&16)<<2)|((i&32)<<2)for i in range(64)]
    cases=0;deltas=set()
    for char,dirty,equal,pin in itertools.product([5,19],[0,65535]+[1<<i for i in range(16)],[0,1],flags):
        machines=[]
        for b in[old,new]:
            m=Memory(b);m.page(1,29);m.page(2,38);at=lambda n:address(b,n)
            seed=dict(SelectedCharacter=char,OperMode=1,GuestAudioCharacter=char,CurrentBank=157,CurrentBankC=166,
                      BassDmcActive=4 if char==19 else 0,GuestNativeEnable=15,GuestSweepControl=153,GuestSweepPeriod=70)
            for n,v in seed.items():m[at(n)]=v
            for i in range(16):
                v=(37*i+91)&255
                m[at('GuestNativeApu')+i]=v;m[at('GuestApuLast')+i]=v if equal else v^255
                m[at('GuestNativeDirty')+i]=(dirty>>i)&1;m[at('GuestFxDirty')+i]=(dirty>>(15-i))&1
            m[at('GuestWorldQueues')]=32;m[at('GuestWorldQueues')+2]=1
            m[0x5115],m[0x5116],m[0x4015]=157,166,31 if char==19 else 15
            machines.append((b,m,NesMPU(memory=m)))
        for tick in range(2):
            cycles=[]
            for b,m,c in machines:
                c.pc,c.a,c.x,c.y,c.p,c.sp=address(b,'GuestAudioFinish'),85,3,7,pin,253
                m[510],m[511]=255,126;m.writes=[];start=c.processorCycles
                for _ in range(12000):
                    if c.pc==0x7f00:break
                    c.step()
                else:raise AssertionError('Complete mixed controls timeout')
                cycles.append(c.processorCycles-start)
            c,m=machines[0][2],machines[0][1];d,n=machines[1][2],machines[1][1]
            assert snapshot(c,m)==snapshot(d,n),('Native pulse ownership/mixer',char,dirty,equal,pin,tick)
            deltas.add(cycles[1]-cycles[0]);cases+=1
    proof=dict(passed=True,source_only=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
               complete_mixer_calls=cases,numeric_characters=[5,19],all64physical_P=True,all16dirtybits_and_clear_full=True,
               held_and_changed_native_images=True,two_actual_effect_calls_with_noise_and_fireball=True,
               complete_AXYP_SP_allRAM_SMC_banks_ordered_APU_exact=True,component_cycle_deltas=sorted(deltas),
               cold_or_native_cadence_claim=False,checker_sha256=sha(Path(__file__)))
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
