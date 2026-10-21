"""Validate actual-DQ frozen native receipts before working checkpoint install."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    output = V / 'root49-union-admission-dv.json'
    assert not output.exists()
    dp = V / 'root49-body-victory-union-dq/report.json'
    assert sha(dp) == '40b361bb28db5f1e923c8079d1256bddfd622714ddd46ec44f9110f3039536a7'
    d = json.loads(dp.read_text())
    assert d['status'] == 'PASS_PRIVATE_DQ_FOUR_BUILDS_EXACT_COMPONENT_BYTE_UNION_ADMISSION_PENDING'
    assert len(d['builds']) == 4 and all(x['exit'] == 0 for x in d['builds'])
    source = dp.parent / 'source'
    assert len(d['source_hashes']) == 442 and all(sha(source / n) == h for n, h in d['source_hashes'].items())
    for row in d['builds']:
        stem = source / 'build' / ('smb-crossover-' + row['mapper'] + ('-baseline' if row['baseline'] else ''))
        assert all(sha(stem.with_suffix('.' + ext)) == h for ext, h in row['artifacts'].items())
    bf = V / 'agent49-bill-body-dq-rebind-r/freeze-r.json'
    assert sha(bf) == 'e7d9338d3f8eb7ca3d452a4445d79a8ebc5c533a5e9469dcd64aad88d4ae7126'
    b = json.loads(bf.read_text())
    assert b['DQ_build_report_sha256'] == sha(dp)
    assert b['source_cases'] == sum(x['cases'] for x in b['native_groups']) == 9978
    assert b['matched_profile_vectors'] == 5568
    bc = bf.parent / b['DQ_source_catalog']['path']
    assert sha(bc) == b['DQ_source_catalog']['sha256']
    assert json.loads(bc.read_text()) == d['source_hashes']
    for mapper, entries in b['artifacts'].items():
        expected = next(x for x in d['builds'] if x['mapper'] == mapper and not x['baseline'])
        for ext, rec in entries.items():
            assert sha(Path(rec['path'])) == rec['sha256'] == expected['artifacts'][ext]
    # Freeze R pins the original unchanged cores, independent source inputs,
    # all actual native outputs, and paired hardware/cost receipts.
    receipts_path = bf.parent / 'receipt-catalog-r.json'
    assert sha(receipts_path) == '2a1a84329ea50d8627f9559c64519f7dd6685dcf2a549c3e28ca540f9bcf6569'
    receipts = json.loads(receipts_path.read_text())
    assert len(receipts) == 144
    for n, rec in receipts.items():
        p = bf.parent / n
        assert sha(p) == rec['sha256'] and p.stat().st_size == rec['bytes'], p
    for row in b['native_groups']:
        p = Path(row['output'])
        assert sha(p / 'binding.json') == row['binding_sha256']
        assert sha(p / 'core.lua') == row['unchanged_core_sha256']
        for n, h in row['reviews'].items():
            assert sha(p / n) == h
    profile = bf.parent / 'optimization-profile-p.json'
    assert sha(profile) == b['profile_review_sha256'] == 'fe7ae1cf53b66d2be9b8a9f8d9b002ace130f62ad25ab4facde5b24160b30ce3'
    cf = V / 'agent-lsr-victory-repair-c/dq-native-a/freeze.json'
    assert sha(cf) == 'fe359f570f0b4c7088e2cae7019903a59975fdb50a1d55ada959a7cce1279a4d'
    c = json.loads(cf.read_text())
    assert c['DQ_report_sha256'] == sha(dp) and c['cores_literal']
    for n, h in c['files'].items():
        assert sha(cf.parent / n) == h, n
    cr = cf.parent / 'report.json'
    assert sha(cr) == c['actual_report_sha256'] == '1f651c1feb0e56e80c755b76c17ac44113bfde396fb78aefda6ef9992a761000'
    runs = json.loads(cr.read_text())['runs']
    assert sum(x['result']['cases'] for x in runs) == 132
    assert all(x['exit'] == 0 and x['result']['failure_count'] == 0 for x in runs)
    cp = V / 'root49-union-native-dr.json'
    assert sha(cp) == '2a5410c864e02aae2a0670b7e77462a670c5209fa805b94a7185b9e9c6495abb'
    native = json.loads(cp.read_text())
    assert sum(x['cases'] for x in native['mappers']) == 120
    result = dict(status='PASS_ACTUAL_DQ_COMPONENT_ADMISSION_WORKING_CHECKPOINT_ONLY',
        script_sha256=sha(__file__), DQ_report_sha256=sha(dp), body_union_freeze_sha256=sha(bf),
        body_receipt_files_verified=144, victory_union_freeze_sha256=sha(cf),
        victory_receipt_files_verified=len(c['files']), native_fallback_review_sha256=sha(cp),
        body_source_cases=9978, matched_profile_vectors=5568, victory_native_cases=132,
        native_fallback_cases=120, total_component_cases=10230, actual_raw_source_files=442,
        source_body_scope='Exact source body endpoints versus native integer enemy proxies; source enemy fractions, bitmap firebars, terrain resolution, and platform paths remain separately qualified. No assertion that the two original Bill contacts are fixed.',
        performance='231..298 fewer cycles per matched body publication than F correctness control. This does not measure whole-game lag improvement relative to BY.',
        transition_scope='Rare castle auto-walk repair with finite attacks/pending release preserved. EasyLink separate framegraph and retained special-form art plus frozen victory projectile pools remain explicit source-WATCH limits.',
        route_scope='BY full route proofs are historical evidence. N changes timing; an old BY Mega Man controller stream dies earlier on DQ. Fresh actual-DQ ordinary routing is active; no all-roster final recordings claim.',
        main_changed=False, accepted_release=False, goal_complete=False)
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], sha(output))


if __name__ == '__main__':
    main()
