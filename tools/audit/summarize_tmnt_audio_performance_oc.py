"""Report native-music performance, retaining any added lag as an open gate."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import statistics

ROOT=Path(__file__).resolve().parents[2]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()
    old=json.loads((a.baseline/'results.json').read_text());new=json.loads((a.candidate/'results.json').read_text())
    assert old['passed']and new['passed']
    for field,name in [('driver_sha256','tests/tmnt-performance.lua'),('observer_sha256','tools/audit/tmnt_performance_observer.lua')]:
        assert old[field]==new[field]==sha(ROOT/name)
    runs={};no_added_lag=True
    for name in ['leonardo','donatello']:
        paths=[a.baseline/name,a.candidate/name]
        states=[list(csv.DictReader((q/'gameplay.csv').open()))for q in paths]
        assert all(len(s)==600 for s in states)
        changes=[]
        for i,(x,y)in enumerate(zip(*states)):
            diff={k:[x[k],y[k]]for k in x if x[k]!=y[k]}
            assert all(k=='input'for k in diff),(name,i,diff)
            if diff:changes.append(dict(update=i,fields=diff))
        phases={}
        for phase in ['idle','walk','enemies','primary','secondary']:
            row={}
            for tag,folder,state in zip(['old','new'],paths,states):
                assert sum(q['phase']==phase for q in state)==120
                if phase=='enemies':assert sum(q['phase']==phase and(int(q['enemy0'])>0 or int(q['enemy1'])>0)for q in state)==120
                calls=[q for q in csv.DictReader((folder/'tmnt-performance-calls.csv').open())if q['phase']==phase]
                frames=[q for q in csv.DictReader((folder/'tmnt-performance-frames.csv').open())if q['phase']==phase]
                value=dict(lag_NMIs=sum(int(q['lagNmis'])for q in frames),draws=sum(q['name']=='DrawAllMetasprites'for q in calls))
                for routine,key in [('DrawAllMetasprites','drawing'),('GameLoop','loop'),('TnDrawEquipment','equipment')]:
                    value[key+'_CPU_mean']=statistics.mean(int(q['cpuCycles'])for q in calls if q['name']==routine)
                row[tag]=value
            row['added_lag_NMIs']=row['new']['lag_NMIs']-row['old']['lag_NMIs']
            no_added_lag&=row['added_lag_NMIs']<=0;phases[phase]=row
        runs[name]=dict(recorded_gameplay_state_exact_excluding_input=True,controller_sample_differences=changes,
                        trace_hashes=[sha(q/'gameplay.csv')for q in paths],phases=phases)
    q=dict(passed=no_added_lag,measurement_valid=True,performance_gate_passed=no_added_lag,
           ROM_sha256=new['ROM_sha256'],baseline_ROM_sha256=old['ROM_sha256'],runs=runs,
           input_policy_sha256=new['driver_sha256'],observer_sha256=new['observer_sha256'],
           source_result_hashes=[sha(d/'results.json')for d in [a.baseline,a.candidate]],
           scope='Two arranged600-update native components,120updates per phase, both with live actors. Same input policy, with every controller-sampling difference retained. Cycle spans exclude NMI/IRQ body time but include real DMC DMA stalls; spans nest. Added lag is an explicit failed acceptance gate, not a successful optimization claim.')
    a.output.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));return 0 if no_added_lag else 2


if __name__=='__main__':raise SystemExit(main())
