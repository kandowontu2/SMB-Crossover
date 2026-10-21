"""Supply the original fixture include root to the ten nested-test wrappers."""
from pathlib import Path
import hashlib, json, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-whip-phase-y'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    original = H / 'native/checks-a/report.json'
    assert sha(original) == 'aa0b2d4d395d7f7f94f3d3a41ee8bf53f3a7a73cbd4da2482d064b0995fda1d2'
    old = json.loads(original.read_text())
    assert len(old['rows']) == 22
    failed = [row for row in old['rows'] if row['exit'] != 0]
    assert len(failed) == 10
    out = H / 'native/checks-b';out.mkdir(parents=True, exist_ok=False)
    report = dict(status='RERUNNING_NESTED_FIXTURES_WITH_EXPLICIT_INCLUDE_ROOT', script_sha256=sha(__file__),
                  original_report_sha256=sha(original), original_passing_groups=12, rows=[], route_proof=False)

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for row in failed:
        mapper, name = row['mapper'], row['kind']
        old_log = H / 'native/checks-a' / (mapper + '-' + name + '.log')
        assert 'cannot open ' in old_log.read_text() and 'No such file or directory' in old_log.read_text()
        test = R / 'tests' / (name + '.lua')
        assert sha(test) == row['original_test_sha256']
        wrapper = out / (mapper + '-' + name + '.lua')
        wrapper.write_text('TEST_DIR=' + json.dumps((R / 'tests').as_posix() + '/') + '\n'
                           + 'dofile(TEST_DIR.."menu-bootstrap.lua")\ndofile(' + json.dumps(test.as_posix()) + ')\n')
        rom = H / 'source/build' / ('smb-crossover-' + mapper + '.nes')
        log = out / (mapper + '-' + name + '.log')
        with log.open('wb') as f:
            rc = subprocess.run([sys.executable, str(R / 'tools/run_mesen.py'), str(wrapper), str(rom),
                                 '--timeout', '120'], cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
        report['rows'].append(dict(mapper=mapper, kind=name, exit=rc, log_sha256=sha(log),
                                   original_test_sha256=sha(test), wrapper_sha256=sha(wrapper)))
        save();print(mapper, name, rc, flush=True)
    passed = all(row['exit'] == 0 for row in report['rows'])
    report['status'] = 'PASS_ALL_TWENTY_TWO_Y_GROUPS_WITH_ORIGINAL_FIXTURE_INCLUDE_ROOT' if passed else 'RETAINED_Y_FIXTURE_RUNTIME_FAILURES'
    save();print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
