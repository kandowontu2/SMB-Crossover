"""Check full AudioUpdate compatibility for every non-Mac identity (CPU only)."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load
from robots_weapon_cpu_v1 import Arena
from cv3_dmc_cpu_v1 import diff, regs, apu
from final_item_matrix import ROSTER

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['baseline','candidate','output']:
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    a.output.mkdir(exist_ok=False)
    bundles=[load(a.baseline),load(a.candidate)]
    rows=[]
    for name, slot, character, variant, value, family in ROSTER:
        if family=='mac':
            continue
        count,costs=0,[]
        for mode,request in itertools.product([0,1],[(1,0),(2,0),(0,4),(1,8)]):
            qs=[Arena(b,character)for b in bundles]
            for q in qs:
                q.put(CrossoverBehaviorVersion=mode,AreaMusicQueue=request[0],EventMusicQueue=request[1])
                if variant:
                    q.set(variant,value)
            for tick in range(32):
                for q in qs:
                    q.put(GamePauseStatus=int(tick in (16,17)),
                          AvAudioRequest=21 if tick==8 else 22 if tick==12 else 0)
                    if tick==20:
                        q.m[0x4015]=15
                cs=[q.invoke('AudioUpdate')[0]for q in qs]
                assert apu(qs[0])==apu(qs[1]),(name,mode,request,tick)
                diff(qs)
                assert regs(cs[0])==regs(cs[1])and qs[0].m.banks==qs[1].m.banks,(name,mode,request,tick)
                costs.append(cs[1].processorCycles-cs[0].processorCycles)
                count+=1
        row=dict(identity=name,character=character,variant=variant,value=value,
                 cases=count,cycle_delta=[min(costs),max(costs)])
        rows.append(row)
        (a.output/'progress.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(row),flush=True)
    assert len(rows)==36
    proof=dict(passed=True,baseline_ROM_sha256=sha(a.baseline),ROM_sha256=sha(a.candidate),
               identities=36,CPU_mode_cells=72,full_AudioUpdate_calls=sum(row['cases']for row in rows),
               rows=rows,tool_sha256=sha(Path(__file__)),
               scope='All36 non-Mac identities; directly seeded CPU modes, area/event requests, typed effects, pause and ended-DMC controls. Exact ordered APU, application RAM, registers and mapper outcomes. Cycle costs disclosed separately; not a native mode selection, gameplay, interrupt, waveform, every-item or campaign pass.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in proof.items()if k!='rows'},indent=2))


if __name__=='__main__':
    main()
