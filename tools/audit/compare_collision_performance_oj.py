"""Require matched native work before crediting collision-router savings."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import statistics


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert not a.output.exists();old=json.loads((a.baseline/'results.json').read_text());new=json.loads((a.candidate/'results.json').read_text())
    assert old['passed']and new['passed']
    assert all(old[k]==new[k]for k in ['fixture_sha256','observer_source_sha256','bound_observer_sha256'])
    exact=True;no_added=True;runs={}
    for name in ['sophia','chip']:
        folders=[a.baseline/name,a.candidate/name]
        states=[list(csv.DictReader((f/'gameplay.csv').open()))for f in folders]
        assert all(len(s)==600 for s in states)
        differences=[]
        for i,(x,y)in enumerate(zip(*states)):
            fields={k:[x[k],y[k]]for k in x if x[k]!=y[k]}
            if fields:differences.append(dict(update=i,fields=fields))
        exact&=not differences
        phases={}
        for phase in ['idle','walk','enemies','primary','jump']:
            row={}
            for tag,folder,state in zip(['old','new'],folders,states):
                assert sum(r['phase']==phase for r in state)==120
                if phase=='enemies':assert sum(r['phase']==phase and(int(r['enemy0'])or int(r['enemy1']))for r in state)==120
                calls=[r for r in csv.DictReader((folder/'collision-performance-calls.csv').open())if r['phase']==phase]
                frames=[r for r in csv.DictReader((folder/'collision-performance-frames.csv').open())if r['phase']==phase]
                data=dict(lag_NMIs=sum(int(r['lagNmis'])for r in frames),draws=sum(r['name']=='DrawAllMetasprites'for r in calls))
                for routine,field in [('GameLoop','loop'),('ExpandedCollisionAdder','adder'),('ExpandedCollisionBox','box')]:
                    selected=[int(r['cpuCycles'])for r in calls if r['name']==routine]
                    assert len(selected)==120,(name,tag,phase,routine,len(selected))
                    data[field+'_CPU_mean']=statistics.mean(selected)
                row[tag]=data
            row['added_lag_NMIs']=row['new']['lag_NMIs']-row['old']['lag_NMIs'];no_added&=row['added_lag_NMIs']<=0
            row['loop_CPU_saved_mean']=row['old']['loop_CPU_mean']-row['new']['loop_CPU_mean']
            phases[phase]=row
        runs[name]=dict(exact_all_recorded_gameplay_fields=not differences,differences=differences,
            trace_sha256=[sha(f/'gameplay.csv')for f in folders],phases=phases)
    q=dict(passed=bool(exact and no_added),measurement_valid=bool(exact),no_added_lag=bool(no_added),
        ROM_sha256=new['ROM_sha256'],baseline_ROM_sha256=old['ROM_sha256'],runs=runs,
        fixture_sha256=new['fixture_sha256'],observer_sha256=new['bound_observer_sha256'],
        source_results_sha256=[sha(f/'results.json')for f in [a.baseline,a.candidate]],
        scope='Two matched native600-update components,120updates per scene, with exactly120live-actor updates. Every recorded input/position/state/pose/shot/actor field must match, with no exceptions. CPU spans exclude actual interrupt body cycles and retain DMC DMA stalls; spans nest. Lag must not increase in any scene. A seeded per-update joypad snapshot is an explicit component stimulus, separate from controller-only campaign and input-latency evidence. A mismatched workload is retained as a failed measurement, not credited as an optimization.')
    a.output.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=q['passed'],measurement_valid=q['measurement_valid'],ROM_sha256=q['ROM_sha256'],
        summary={n:dict(different_rows=len(r['differences']),phases={p:dict(saved_CPU=d['loop_CPU_saved_mean'],lag=[d['old']['lag_NMIs'],d['new']['lag_NMIs']])for p,d in r['phases'].items()})for n,r in runs.items()}),indent=2))
    return 0 if q['passed']else 2


if __name__=='__main__':raise SystemExit(main())
