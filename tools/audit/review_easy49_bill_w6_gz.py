"""Independently rehash the frozen private W6 packet; no union/main admission."""
from pathlib import Path
import csv
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'agent49-bill-body-hot-w'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


def main():
    out = V / 'root49-bill-w6-review-gz.json'
    assert not out.exists()
    freeze = H / 'freeze-final-w6.json'
    assert sha(freeze) == '1df55ea3bc787439a35fbbeb5b4c7018fc80f7ff746f805339ac60c10f210c1d'
    f = read(freeze)
    for field in ('source_only_freeze', 'source_catalog', 'native_receipts', 'reproduction', 'retained_negatives'):
        p = R / f[field]['path']
        assert sha(p) == f[field]['sha256'], p
    cat = read(R / f['source_catalog']['path'])
    assert len(cat) == 444
    assert all(sha(H / 'source-w6' / n) == h for n, h in cat.items())
    source = read(R / f['source_only_freeze']['path'])
    for group in source['artifacts'].values():
        for entry in group.values():
            assert sha(R / entry['path']) == entry['sha256']
    for n, value in source['generated'].items():
        assert sha(H / 'source-w6/build/generated' / n) == value
    for n, value in f['reports'].items():
        assert sha(H / n) == value
    receipts = read(R / f['native_receipts']['path'])
    assert len(receipts) == len(f['native_groups']) == 20
    total = 0
    native_results = {}
    for name, items in receipts.items():
        folder = R / f['native_groups'][name]['directory']
        for n, entry in items.items():
            p = folder / n
            assert sha(p) == entry['sha256'] and p.stat().st_size == entry['bytes'], p
            total += 1
        assert sha(folder / 'result.json') == f['native_groups'][name]['result_sha256']
        native_results[name] = read(folder / 'result.json')
    negatives = read(R / f['retained_negatives']['path'])
    for n, entry in negatives.items():
        assert sha(H / n) == entry['sha256'] and (H / n).stat().st_size == entry['bytes']
    incident = read(H / 'ordinary-incident-review-w6.json')
    assert incident['status'] == 'PASS' and len(incident['records']) == 4
    ordinary = []
    for row in incident['records']:
        folder = Path(row['output'])
        for filename, field in [('result.json', 'result_sha256'), ('inputs.csv', 'inputs_sha256'), ('trace.csv', 'trace_sha256')]:
            assert sha(folder / filename) == row[field]
        result = read(folder / 'result.json')
        assert result['frames'] == 1780 and result['failure'] == 'frame limit' and result['deaths'] == 0
        with (folder / 'trace.csv').open(newline='') as stream:
            trace = list(csv.DictReader(stream))
        assert len(trace) == 1780 and int(trace[-1]['x']) == row['final_x']
        assert min(int(x['y']) for x in trace if int(x['frame']) >= 541) == row['minimum_integer_y'] == 102
        ordinary.append(dict(mapper=row['mapper'], control=row['control'], frames=1780,
            deaths=0, final_x=row['final_x'], min_y=102, raw_head1650=row['raw_head_at1650'],
            admitted_head1650=row['admitted_head_at1650']))
    abi = read(H / 'abi-composed-w6.json')
    assert [(x['mapper'], x['cases']) for x in abi['maps']] == [('mmc3', 41984), ('mmc5', 41984)]
    envelope = read(H / 'envelope-source-w6.json')
    assert envelope['cases'] == 3489792 and len(envelope['profiles']) == 12
    live = read(H / 'temp-liveness-source-witness-review-w6.json')
    assert len(live['reports']) == 4 and all(x['actual_updates'] > 0 for x in live['reports'])
    for row in live['reports']:
        if row['kind'] == 'temp-fire2-liveness-w6':
            assert row['cases'] == 96 and row['actual_weapon_witness']
    main = read(R / 'build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json')
    assert len(main['source_hashes']) == 442
    assert all(sha(R / n) == h for n, h in main['source_hashes'].items())
    for build in main['builds']:
        assert all(sha(R / p['path']) == p['sha256'] for p in build['artifacts'].values())
    assert not (R / 'src/bill_source_body.s').exists()
    report = dict(status='PASS_REHASHED_PRIVATE_W6_PACKET_NOT_GQ_UNION_ADMISSION',
        script_sha256=sha(__file__), freeze_sha256=sha(freeze), sources=444,
        native_groups=20, native_receipt_files_rehashed=total, native_results=native_results,
        original_ordinary_contracts=ordinary, all_P_four_SP_cases_per_mapper=41984,
        conservative_source_enclosure_cases=3489792, actual_fire_liveness_report_sha256=sha(H / 'temp-liveness-source-witness-review-w6.json'),
        cost=f['cost'], qualifications=f['qualifications'],
        root_scope='Independent hash/identity and ordinary trace/result review. Agent native/compiled executors are not rerun by this root review. New union requires its own actual build and bound checks.',
        GQ_sources442_and_artifacts8_still_exact=True, runtime_changes=False,
        accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(out), total)


if __name__ == '__main__':
    main()
