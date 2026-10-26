"""Full unchanged-roster caller check for the private Chip music route."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load
from check_tmnt_audio_fallback_oc import execute,result
from final_item_matrix import ROSTER

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists();a.output.mkdir(parents=True)
    baseline=ROOT/'build/smb-crossover-mmc5-expanded.nes'
    assert hashlib.sha256(baseline.read_bytes()).hexdigest()=='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
    old,new=load(baseline),load(a.rom)
    rows=[]
    for identity,slot,char,variant,value,family in ROSTER:
        if char==14:continue
        count=0;costs=set()
        for entry in ['ExpandedAudioUpdate','AudioUpdate']:
            if entry=='ExpandedAudioUpdate' and char<6:continue
            for mode,flags,phase in itertools.product([0,1],[0x20,0x21,0x60,0x61,0xe0,0xe1],range(6)):
                seed=dict(SelectedCharacter=char,OperMode=1,CrossoverBehaviorVersion=mode,
                          AreaMusicQueue=[1,0,4,128,0,64][phase],EventMusicQueue=[0,4,0,0,64,8][phase],
                          GamePauseStatus=int(phase==4),CurrentBank=215,CurrentBankC=166,XgAudioCharacter=255)
                if variant:seed[variant]=value
                c,m=execute(old,entry,seed,flags=flags);d,n=execute(new,entry,seed,flags=flags)
                assert result(c,m)==result(d,n),(identity,entry,mode,flags,phase)
                costs.add(d.processorCycles-c.processorCycles);count+=1
        row=dict(identity=identity,cases=count,cycle_deltas=sorted(costs));rows.append(row)
        print(json.dumps(row),flush=True)
    proof=dict(passed=True,accepted=False,native_run=False,
               candidate_ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),
               unchanged_identities=len(rows),calls=sum(r['cases']for r in rows),rows=rows,
               equality='Full AXYP/SP, physical banks, ordinary RAM/SMC, mapper shadows and ordered APU output; only discarded stack excluded.',
               checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               limits='Seeded whole audio callers in both modes, cold/pause/request states. No native timing or full gameplay qualification.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,identities=len(rows),calls=proof['calls'])))


if __name__=='__main__':main()
