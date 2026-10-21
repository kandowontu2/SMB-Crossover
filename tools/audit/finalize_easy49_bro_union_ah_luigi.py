"""Use retained full native logs for Luigi's ordinary title guards."""
from pathlib import Path
import hashlib, json

R = Path(__file__).resolve().parents[2]
H = R / 'build/verification/root49-easy-bro-union-ab'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    original = H / 'ordinary-luigi-ag/report.json'
    assert sha(original) == '04488a3632fd30f50c3b12464b448d363307984b0151a1cac2857541450ee4d6'
    report = json.loads(original.read_text())
    assert report['status'] == 'RETAINED_AB_LUIGI_DIFFERENCES'
    assert len(report['rows']) == 2
    for row in report['rows']:
        mp = row['mapper']
        native = R / 'build/verification' / ('smb-crossover-' + mp + '-run-root49ab-luigi-fixed-ag-8-v0-' + mp + '.log')
        assert 'ORDINARY LUIGI title verified: mode=0 selected=8' in native.read_text()
        assert row['exit'] == 0 and row['result']['cleared'] and row['result']['all_six_stages']
        assert row['result']['frames'] == 17412 and row['result']['polls'] == 17411 and row['result']['deaths'] == 0
        assert row['actual_trace_rows'] == row['parent_trace_rows'] == 17412 and not row['first_differences']
        assert not row['passed'] and not row['title_mode_and_character_guard']
        folder = R / row['route_path'];m = json.loads((folder / 'manifest.json').read_text())
        assert sha(folder / 'manifest.json') == row['manifest_sha256']
        assert m['verified_through_2_2'] and m['full_frame_audit'] and m['controller_only'] and not m['memory_or_register_writes']
        assert m['inputs_sha256'] == report['inputs_sha256']
        row.update(passed=True, title_mode_and_character_guard=True, full_native_log_sha256=sha(native))
    build = json.loads((H / 'report.json').read_text())
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    report.update(status='PASS_AB_ORDINARY_LUIGI_BOTH_MAPPERS_EXACT_Y_TRAJECTORY',
                  finalizer_sha256=sha(__file__), original_AG_report_sha256=sha(original),
                  verifier_erratum='AG searched truncated driver output for the title guard. Both complete native logs contain it; no source, inputs or emulator run changed.')
    output = H / 'ordinary-luigi-ag/report-ah.json';assert not output.exists()
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], sha(output), flush=True)


if __name__ == '__main__':
    main()
