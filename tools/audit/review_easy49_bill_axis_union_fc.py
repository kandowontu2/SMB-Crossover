"""Verify G2/EU frozen correctness and preserve their explicit performance rejection."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
G = V / 'agent49-bill-head-axis-g'
EU = V / 'root49-bill-axis-link-eu'
L = V / 'agent-lsr-victory-repair-eu-checks-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-bill-axis-union-fc.json'
    assert not out.exists()
    pins = {
        G / 'freeze-u.json': '32db2a18b92534b0fab5f33394bd1ee059509ce8f119f74c575b8e7841242a7f',
        G / 'source-catalog-s.json': '36c25b745b9194ed667a2c6f6d07872d9623759caa0b24828878d755a1dc2c51',
        EU / 'report.json': 'b8d29b6afe7158ee11d1883aac6d103d247879a070c332fb2954365d43878100',
        L / 'freeze.json': 'b7e63e75a62920404e128a3173c1e90354e476a5732155010252e4507c0a62b2',
    }
    for p, h in pins.items():
        assert sha(p) == h, p
    g = json.loads((G / 'freeze-u.json').read_text())
    eu = json.loads((EU / 'report.json').read_text())
    sources = json.loads((G / 'source-catalog-s.json').read_text())
    assert sources == eu['g2_source_hashes'] and len(sources) == 442
    assert all(sha(G / 'source-g' / n) == h for n, h in sources.items())
    catalog = G / 'receipt-catalog-u.json'
    assert sha(catalog) == g['receipt_catalog_sha256']
    receipts = json.loads(catalog.read_text())
    assert len(receipts) == g['receipt_files'] == 1001
    for name, row in receipts.items():
        p = (G / name).resolve()
        assert p.is_relative_to(R) and sha(p) == row['sha256'], p
        assert p.stat().st_size == row['bytes'], p
    for mapper in ('mmc3', 'mmc5'):
        for artifact in g['build_artifacts'][mapper].values():
            assert sha(artifact['path']) == artifact['sha256']
    assert all(sha(EU / 'source' / n) == h for n, h in eu['source_hashes'].items())
    helper = 'src/guest_victory_control.s'
    assert [n for n, h in eu['source_hashes'].items() if sources.get(n) != h] == [helper]
    for row in eu['builds']:
        tag = row['mapper'] + ('-baseline' if row['baseline'] else '')
        for ext, h in row['artifacts'].items():
            assert sha(EU / 'source/build' / f'smb-crossover-{tag}.{ext}') == h
    lf = json.loads((L / 'freeze.json').read_text())
    for n, h in lf['files'].items():
        assert sha(L / n) == h, n
    assert sha(L / 'review.json') == lf['review_sha256']
    lr = json.loads((L / 'review.json').read_text())
    assert lr['native']['total_cases'] == 616 and lr['compiled']['actual_G2_vs_EU_calls'] == 1000
    main_path = R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json'
    assert sha(main_path) == '7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4'
    main_state = json.loads(main_path.read_text())
    assert all(sha(R / n) == h for n, h in main_state['source_hashes'].items())
    assert not (R / 'src/bill_source_body.s').exists()
    for b in main_state['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in b['artifacts'].values())
    report = dict(status='PASS_FROZEN_G2_EU_CORRECTNESS_NOT_PERFORMANCE_ADMISSION',
        script_sha256=sha(__file__), root_references={p.relative_to(R).as_posix(): h for p, h in pins.items()},
        source_files_G2_and_EU=442, G2_receipts_rehashed=1001,
        literal_old_cases=g['old_unchanged_cases'], new_cases=g['new_consumer_precision_activation_reset_cases'],
        matched_profile_vectors=g['matched_profile_vectors'], ordinary_controls=g['ordinary_controls'],
        cost_summary=g['cost_summary'], combined_Link_native_cases=616, combined_strict_controller_ABI_cases=1000,
        combined_scope_limits=lr['scope_limits'], main_EL_exact_unchanged=True,
        rejected_for_final_admission='Material ordinary walking/seeded six-Goomba cost; separate hot-path successor required.',
        G2_and_EU_remain_immutable=True, runtime_edits=False, main_changed=False,
        accepted_release=False, goal_complete=False)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(out))


if __name__ == '__main__':
    main()
