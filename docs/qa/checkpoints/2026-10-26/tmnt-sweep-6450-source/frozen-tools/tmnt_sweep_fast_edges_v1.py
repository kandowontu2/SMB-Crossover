"""Source-only literal out-of-bound fallback and complete queue-entry controls."""
from pathlib import Path
import argparse
import itertools
import json
from check_tmnt_render_oa import load,Memory,address
from tmnt_sweep_fast_cpu_v2 import run,snapshot
from tmnt_native_storage_driver import ROOT,sha
from verify_native_relocation import NesMPU


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    old,new=load(a.baseline),load(a.candidate);flags=[32|(i&15)|((i&16)<<2)|((i&32)<<2)for i in range(64)]
    edge=0
    for period,pin in [(v,p)for v,p in itertools.product(range(18),flags)]+[(256*h+l,p)for h,l,p in itertools.product(range(8,256),[0,1,127,128,255],[32,255])]:
        c,m=run(old,'GuestExpansionFlush',period,pin);d,n=run(new,'TnExpansionSweepGate',period,pin)
        assert snapshot(c,m)==snapshot(d,n),('Literal outside bounded domain',period,pin);edge+=1
    cases=0;cycles=set()
    for char,marker,owner,pin in itertools.product(range(20),[0,9,19,255],[0,1,2,3,4,255],flags):
        def begin(b):
            m=Memory(b);m.page(1,29);m.page(2,38);at=lambda n:address(b,n)
            for name in['BassAudioInit','BassAudioPreviousMask','BassAudioLastDeath','BassAudioLastGround','BassSourceId',
                        'Cv3DmcPriority','Cv3DmcPending','MmRushLandActive','MmRushLandPreviousMask','MmRushLandRequest']:
                m[at(name)]=0xa5
            for name,value in dict(SelectedCharacter=char,GuestAudioCharacter=marker,BassDmcActive=owner,
                                   CurrentBank=157,CurrentBankC=166,Square1SoundQueue=0xff,Square2SoundQueue=0xff,NoiseSoundQueue=0xff).items():m[at(name)]=value
            m[0x5115],m[0x5116]=157,166;m[510],m[511]=255,126;m.writes=[]
            c=NesMPU(memory=m,pc=at('GuestAudioBegin'));c.a,c.x,c.y,c.p,c.sp=85,7,3,pin,253
            for _ in range(5000):
                if c.pc==0x7f00:break
                c.step()
            else:raise AssertionError('Queue entry timeout')
            return c,m
        c,m=begin(old);d,n=begin(new)
        assert snapshot(c,m)==snapshot(d,n),('Queue entry outcome',char,marker,owner,pin)
        cycles.add(d.processorCycles-c.processorCycles);cases+=1
    proof=dict(passed=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
               bounded_domain_outside_edge_cases=edge,all_periods0_through17_all64flags=True,
               all_upper_bytes8_through255_with5_low_boundaries=True,GuestAudioBegin_complete_cases=cases,
               all20_character_ids_all64physicalflags_four_cached_characters_six_DMCowners=True,
               queue_entry_all_scratch_APU_SMC_banks_AXYP_SP_exact=True,
               queue_entry_cycle_deltas=sorted(cycles),checker_sha256=sha(Path(__file__)))
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
