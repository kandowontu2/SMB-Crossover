"""Root provenance/cost review of the frozen private Bill V9 correctness control."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'agent49-bill-body-hot-v'


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda: f.read(4*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    out = V / 'root49-bill-v9-review-gf.json'
    assert not out.exists()
    frozen = H / 'freeze-final-v9.json'
    assert sha(frozen) == '6c98843ac35b6cbdbbc099afef9c6b2ddc47a8ab93704b0996f476b00bbf7af7'
    d = json.loads(frozen.read_text())
    checked = {}

    def pin(p, digest=None, size=None):
        p = Path(p)
        actual = sha(p)
        if digest is not None:
            assert actual == digest, p
        if size is not None:
            assert p.stat().st_size == size, p
        checked[p.relative_to(R).as_posix()] = dict(sha256=actual, bytes=p.stat().st_size)

    pin(frozen)
    for key in ('source_catalog', 'overlay_catalog', 'native_receipts', 'reproduction', 'storage'):
        pin(R / d[key]['path'], d[key]['sha256'])
    sources = json.loads((R / d['source_catalog']['path']).read_text())
    assert len(sources) == d['raw_source_files'] == 443
    for n, h in sources.items():
        pin(H / 'source-v9' / n, h)
    overlay = json.loads((R / d['overlay_catalog']['path']).read_text())
    assert len(overlay) == d['overlay_files'] == 10
    for n, h in overlay.items():
        pin(H / 'overlay-final-v9' / n, h)
        assert sources[n] == h
    for mapper, artifacts in d['build_artifacts'].items():
        for a in artifacts.values():
            pin(R / a['path'], a['sha256'])
    for n, h in d['reports'].items():
        pin(H / n, h)
    receipts = json.loads((R / d['native_receipts']['path']).read_text())
    count = 0
    for group, files in receipts.items():
        for n, a in files.items():
            pin(H / 'native' / group / n, a['sha256'], a['bytes'])
            count += 1
    # Independently recompute the reported scoped performance regressions.
    cost = json.loads((H / 'cost-review-v9.json').read_text())
    costs = {}
    for mapper in ('mmc3', 'mmc5'):
        ordinary = cost['reports'][mapper + '/ordinary']['runs']
        seeded = cost['reports'][mapper + '/seeded']['runs']
        oc = {n: ordinary[n]['groups']['Foreground/empty']['cycles']['mean'] for n in ('EC', 'V9')}
        sc = {n: seeded[n]['groups']['Foreground/six']['cycles']['mean'] for n in ('EC', 'V9')}
        lag = {n: seeded[n]['groups']['Foreground/six']['NmiSkipped_increments_in_scope'] for n in ('EC', 'V9')}
        assert oc['V9'] > oc['EC'] and sc['V9'] > sc['EC'] and lag['V9'] > lag['EC']
        costs[mapper] = dict(ordinary=oc, ordinary_delta=round(oc['V9']-oc['EC'], 3),
            seeded_six=sc, seeded_six_delta=round(sc['V9']-sc['EC'], 3), seeded_six_skipped_NMI=lag)
    assert costs['mmc3']['ordinary_delta'] == 738.654
    assert costs['mmc5']['ordinary_delta'] == 766.025
    ordinary = json.loads((H / 'ordinary-review-v9.json').read_text())
    assert ordinary['status'] == 'PASS' and len(ordinary['records']) == 4
    for z in ordinary['records']:
        assert z['frames'] == 1780 and z['deaths'] == 0 and z['cancel_up_events'] == 0
        p = Path(z['output'])
        for name, key in [('result.json', 'result_sha256'), ('inputs.csv', 'inputs_sha256'),
                          ('trace.csv', 'trace_sha256')]:
            pin(p / name, z[key])
    compiled = {}
    for mapper in ('mmc3', 'mmc5'):
        abi = json.loads((H / f'abi-matrix-pointer3-v9-{mapper}.json').read_text())
        assert abi['status'] == 'PASS_COMPILED_ALL256_RAW_P_AND4STACK_MATRIX'
        compiled[mapper] = sum(z['cases'] for z in abi['groups'])
        assert compiled[mapper] == 41984
    interrupts = json.loads((H / 'capture-interrupt-v9.json').read_text())
    assert interrupts['status'] == 'PASS_COMPILED_PER_INSTRUCTION_NMI_LIFETIME'
    assert [z['cases'] for z in interrupts['maps']] == [5632, 5632]
    main = R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json'
    assert sha(main) == '7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4'
    current = json.loads(main.read_text())
    assert all(sha(R / n) == h for n, h in current['source_hashes'].items())
    for b in current['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in b['artifacts'].values())
    assert not (R / 'src/bill_source_body.s').exists()
    report = dict(status='FROZEN_PRIVATE_V9_PROVENANCE_CHECKED_PERFORMANCE_REJECTED',
        script_sha256=sha(__file__), raw_sources_checked=443, overlay_files_checked=10,
        native_receipt_files_checked=count, compiled_ABI_cases=compiled,
        compiled_NMI_lifetime_cases_per_mapper=5632, scoped_costs=costs,
        source_body_axis_and_native_closure_reviews='Specialist reports retained and rehashed; root has not rerun the compiled matrices or native arenas in this review.',
        explicit_qualifications=d['qualifications'],
        native_short_capture_window_interrupt_attained=False,
        main_EL_unchanged=True, runtime_installed=False,
        correctness_control_only=True, performance_accepted=False,
        final_full_routes_or_movies=False, accepted_release=False, goal_complete=False,
        references=checked)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], count, sha(out), costs)


if __name__ == '__main__':
    main()
