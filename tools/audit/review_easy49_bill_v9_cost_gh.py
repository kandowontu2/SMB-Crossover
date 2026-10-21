"""Independently reconstruct V9 foreground costs from original native entry/return events."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import statistics

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'agent49-bill-body-hot-v'
G = V / 'agent49-bill-head-axis-g'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-bill-v9-cost-gh.json'
    assert not out.exists()
    report_path = H / 'cost-review-v9.json'
    assert sha(report_path) == '24f1f5596f3527d6a1f0482893c3c9f7e175c7cbdceb12b3e10ca353f6bd79b0'
    claimed = json.loads(report_path.read_text())
    refs, results = {}, {}
    vector_fields = ('char', 'mode', 'variant', 'x', 'xf', 'y', 'yf', 'state', 'enemies', 'engine')
    for mapper in ('mmc3', 'mmc5'):
        for kind in ('ordinary', 'seeded'):
            vectors = {}
            for version in ('EC', 'G2', 'V9'):
                folder = (H if version == 'V9' else G) / 'native' / f'cost-q4-{kind}-{version}-{mapper}'
                expected = claimed['reports'][mapper + '/' + kind]['runs'][version]
                for name, key in [('binding.json', 'binding_sha256'), ('cost.jsonl', 'events_sha256')]:
                    p = folder / name
                    digest = sha(p)
                    assert digest == expected[key]
                    refs[p.relative_to(R).as_posix()] = dict(sha256=digest, bytes=p.stat().st_size)
                assert json.loads((folder / 'host-report.json').read_text())['exit'] == 0
                stacks, groups, lag = defaultdict(list), defaultdict(list), defaultdict(int)
                updates, paired = {}, 0
                for line in (folder / 'cost.jsonl').read_text().splitlines():
                    z = json.loads(line)
                    event = z['event']
                    if event.endswith('Entry'):
                        stacks[event[:-5]].append(z)
                    elif event.endswith('Return') and event != 'FinishedAfterActualReturn':
                        name = event[:-6]
                        e = stacks[name].pop()
                        assert z['sp'] == e['sp'] + 2
                        assert all(e[k] == z[k] for k in ('bank', 'bankc', 'hwa', 'hwc'))
                        paired += 1
                        if name == 'Update':
                            key = e['frame'] if kind == 'ordinary' else (e['case'], e['age'])
                            assert key not in updates
                            updates[key] = tuple(e[k] for k in vector_fields)
                        if name != 'Foreground':
                            continue
                        if kind == 'seeded' and (e['case'] != z['case'] or e['age'] >= 79):
                            continue
                        label = 'Foreground/' + ('empty' if e['enemies'] == 0 else 'six' if e['enemies'] == 6 else 'one')
                        groups[label].append(z['cycle'] - e['cycle'])
                        lag[label] += (z['lag'] - e['lag']) % 256
                assert all(not s for s in stacks.values())
                assert paired == expected['all_scopes_complete']
                assert len(updates) == expected['update_samples'] == (160 if kind == 'ordinary' else 640)
                vectors[version] = updates
                stats = {}
                for name, cycles in groups.items():
                    actual = dict(samples=len(cycles), min=min(cycles), max=max(cycles),
                        mean=round(statistics.mean(cycles), 3), median=statistics.median(cycles))
                    assert actual == expected['groups'][name]['cycles']
                    assert lag[name] == expected['groups'][name]['NmiSkipped_increments_in_scope']
                    stats[name] = dict(cycles=actual, skipped_NMI=lag[name])
                results[f'{mapper}/{kind}/{version}'] = stats
            assert vectors['EC'] == vectors['G2'] == vectors['V9']
    result = dict(status='ROOT_RECONSTRUCTED_NATIVE_V9_COST_REGRESSION_CONFIRMED',
        script_sha256=sha(__file__), original_report_sha256=sha(report_path),
        native_run_groups=12, all_complete_scopes_pair_and_restore_banks=True,
        matched_player_update_vectors=True, foreground_stats=results,
        scope='Ordinary fresh startup plus seeded flat/six-Goomba loads. Foreground includes interrupt/AI/render phase costs; no exact enemy-AI/render-phase equality or universal lag percentage is asserted.',
        V9_performance_accepted=False, main_changed=False,
        accepted_release=False, goal_complete=False, references=refs)
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], sha(out))


if __name__ == '__main__':
    main()
