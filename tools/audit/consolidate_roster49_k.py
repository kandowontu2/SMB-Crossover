"""Bind K's unchanged full-suite successes to the source-backed head revision."""
from pathlib import Path
import hashlib
import json
import shutil
import zlib

ROOT = Path(__file__).resolve().parents[2]
K = ROOT / 'build/verification/root49-integrated-private-build-k'
QA = K / 'qa-suite-b'
REV = ROOT / 'build/verification/root49k-head-fixture-migration-a'
OUT = K / 'staged-current-summary.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists()
    built = json.loads((K / 'report.json').read_text())
    full = json.loads((QA / 'report.json').read_text())
    summary_path = K / 'source/build/verification/summary-build.json'
    assert sha(summary_path) == full['summary_sha256']
    summary = json.loads(summary_path.read_text())
    assert full['status'] == 'FAIL-retained' and full['exit'] == 1
    expected = [f'guest-head-upper-extent failed for smb-crossover-{m}' for m in ('mmc3', 'mmc5')]
    assert summary['failures'] == expected == full['failures']
    assert len(summary['cases']) == 759
    assert all(c['result'] == 'passed' for c in summary['cases'])
    keys = [(c['test'], c['rom']) for c in summary['cases']]
    assert len(keys) == len(set(keys))
    assert all(sha(K / 'source' / n) == h for n, h in built['source407_hashes'].items())
    current = {n: sha(ROOT / n) for n in full['fixture_and_runner_hashes']}
    changes = [n for n, h in full['fixture_and_runner_hashes'].items() if current[n] != h]
    assert changes == ['tests/guest-head-upper-extent.lua'], changes
    revision = json.loads((REV / 'report.json').read_text())
    assert revision['status'] == 'PASS-source-backed-fixture-revision'
    assert sha(ROOT / changes[0]) == revision['new_sha256']
    assert full['fixture_and_runner_hashes'][changes[0]] == revision['old_sha256']
    assert revision['only_one_pose_offset_revised']
    assert revision['other31poses_and_all_three_heights_and_native_rules_unchanged']
    positives = []
    for mapper in ('mmc3', 'mmc5'):
        rom = K / f'source/build/smb-crossover-{mapper}.nes'
        log = ROOT / revision['positive_logs'][mapper]['path']
        assert sha(log) == revision['positive_logs'][mapper]['sha256']
        text = log.read_text()
        assert 'PASS guest head cutoffs: all32 poses at3 roof/HUD heights' in text
        assert f'File CRC32: 0x{zlib.crc32(rom.read_bytes()) & 0xffffffff:08X}' in text
        assert f'PRG+CHR CRC32: 0x{zlib.crc32(rom.read_bytes()[16:]) & 0xffffffff:08X}' in text
        old = K / f'source/build/verification/smb-crossover-{mapper}-guest-head-upper-extent.log'
        preserved = REV / f'{mapper}-full-original-negative.log'
        if preserved.exists():
            assert sha(preserved) == sha(old)
        else:
            shutil.copyfile(old, preserved)
        positives.append(dict(test='guest-head-upper-extent', rom=rom.stem, result='passed',
                              ROM_sha256=sha(rom), log=str(log.relative_to(ROOT)), log_sha256=sha(log),
                              original_negative=str(preserved.relative_to(ROOT)), original_negative_sha256=sha(preserved)))
    report = dict(status='PASS-staged-current-fixtures', goal_complete=False, accepted_release=False,
                  single_full_run=False, cases=761, full_suite_unchanged_passes=759,
                  source_backed_revised_fixture_passes=2,
                  qualification='759 unchanged cases from the complete K run plus two separately executed head fixtures. Original two old-fixture failures retained. This is not one green full run or an ordinary route proof.',
                  source407_exact=True, compiled_report_sha256=sha(K / 'report.json'),
                  raw_full_report_sha256=sha(QA / 'report.json'), raw_full_summary_sha256=sha(summary_path),
                  fixture_revision_sha256=sha(REV / 'report.json'), only_current_fixture_changes=changes,
                  unchanged_cases=summary['cases'], separately_executed=positives)
    OUT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('unchanged_cases', 'separately_executed')}))


if __name__ == '__main__':
    main()
