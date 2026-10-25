"""Compare equal-update native profiles, retaining controller sampling differences."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import statistics

ROOT = Path(__file__).resolve().parents[2]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(); p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); assert not a.output.exists()
    old = json.loads((a.baseline/'results.json').read_text()); new = json.loads((a.candidate/'results.json').read_text())
    assert old['passed'] and new['passed']
    for field, dep in [('driver_sha256','tests/tmnt-performance.lua'),('observer_sha256','tools/audit/tmnt_performance_observer.lua')]:
        assert old[field] == new[field] == sha(ROOT/dep)
    results = {}
    for name in ('leonardo','donatello'):
        before, after = a.baseline/name, a.candidate/name
        states = [list(csv.DictReader((d/'gameplay.csv').open())) for d in (before, after)]
        assert len(states[0]) == len(states[1]) == 600
        differences = []
        for i, (x,y) in enumerate(zip(*states)):
            fields = {k:[x[k],y[k]] for k in x if x[k] != y[k]}
            assert all(k == 'input' for k in fields), (name,i,fields)
            if fields: differences.append(dict(update=i,fields=fields))
        item = dict(gameplay_state_exact_excluding_input=True, complete_trace_byte_exact=not differences,
                    controller_sampling_differences=differences,
                    baseline_trace_sha256=sha(before/'gameplay.csv'), candidate_trace_sha256=sha(after/'gameplay.csv'), phases={})
        for phase in ('idle','walk','enemies','primary','secondary'):
            row = {}
            for tag, d, state in [('old',before,states[0]),('new',after,states[1])]:
                assert sum(q['phase']==phase for q in state) == 120
                calls = [q for q in csv.DictReader((d/'tmnt-performance-calls.csv').open()) if q['phase']==phase]
                frames = [q for q in csv.DictReader((d/'tmnt-performance-frames.csv').open()) if q['phase']==phase]
                row[tag] = dict(lag_NMIs=sum(int(q['lagNmis']) for q in frames), draws=sum(q['name']=='DrawAllMetasprites' for q in calls))
                for routine, key in [('DrawAllMetasprites','draw'),('GameLoop','loop'),('TnDrawEquipment','equipment')]:
                    values = [int(q['cpuCycles']) for q in calls if q['name']==routine]; assert values
                    row[tag][key+'_CPU_mean'] = statistics.mean(values)
            row['draw_CPU_saved_pct'] = 100*(row['old']['draw_CPU_mean']-row['new']['draw_CPU_mean'])/row['old']['draw_CPU_mean']
            if phase == 'secondary':
                assert row['new']['equipment_CPU_mean'] < row['old']['equipment_CPU_mean']
                assert row['new']['lag_NMIs'] < row['old']['lag_NMIs']
            else:
                # GameLoop is tagged at entry, before TnMovement changes phase.
                # Its last primary span therefore includes secondary setup.
                for key in ('lag_NMIs','draws','draw_CPU_mean','equipment_CPU_mean'):
                    assert row['new'][key] == row['old'][key], (name,phase,key)
            item['phases'][phase] = row
        assert all(sum(q['phase']=='enemies' and (int(q['enemy0'])>0 or int(q['enemy1'])>0) for q in s)==120 for s in states)
        results[name] = item
    proof = dict(passed=True, ROM_sha256=new['ROM_sha256'], baseline_ROM_sha256=old['ROM_sha256'],
                 driver_sha256=new['driver_sha256'], observer_sha256=new['observer_sha256'], runs=results,
                 baseline_results_sha256=sha(a.baseline/'results.json'), candidate_results_sha256=sha(a.candidate/'results.json'),
                 scope='Two arranged native600-update components. All recorded gameplay-state fields match; exact controller sample differences are retained, not silently masked. Same input policy, not a byte-identical controller trace claim. Routine spans exclude interrupts and nest. Heavy-shot lag remains; no60Hz claim.')
    a.output.write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps(dict(passed=True, ROM_sha256=proof['ROM_sha256'], runs=results), indent=2))


if __name__ == '__main__': main()
