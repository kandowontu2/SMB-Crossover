"""Fresh controller-only Pit replay on the integrated build, both mappers."""
from pathlib import Path
import hashlib, json, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-union-t-pit-route-a'
T = V / 'root49-easy-union-t'
P = R / 'build/roster-through-2-2/agent49s2-pit-fixed-al-6-v0-mmc3'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not H.exists()
    assert sha(T / 'report.json') == '99b62c608a5fb96c1c121c00cba9edafe0514333d11b939597474a09348278e9'
    build = json.loads((T / 'report.json').read_text())
    assert all(sha(T / 'source' / n) == h for n, h in build['source_hashes'].items())
    assert sha(P / 'inputs.csv') == '08c70fa94266b80c9ba448e44c368c733d09f22c02574a327cb00fc3d22c5e65'
    pm = json.loads((P / 'manifest.json').read_text())
    assert pm['verified_through_2_2'] and pm['controller_only'] and not pm['memory_or_register_writes']
    assert pm['result']['deaths'] == 0 and pm['result']['frames'] == 23980
    for n, key in [('roster_harness.lua', 'harness_sha256'), ('roster_audit.lua', 'audit_sha256')]:
        assert sha(R / 'tools/playthroughs' / n) == pm[key]
    H.mkdir()
    report = dict(status='RUNNING_FRESH_PIT_ON_COMBINED_T', script_sha256=sha(__file__),
                  parent_manifest_sha256=sha(P / 'manifest.json'), replay_sha256=sha(P / 'inputs.csv'),
                  build_sha256=sha(T / 'report.json'), controller_only=True, memory_or_register_writes=False,
                  record=False, accepted_release=False, goal_complete=False, rows=[])

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for mapper in ['mmc3', 'mmc5']:
        tag = 'root49t-pit-fixed-a'
        rom = T / 'source/build' / ('smb-crossover-' + mapper + '.nes')
        argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '6', '--mapper', mapper,
                '--rom', str(rom), '--tag', tag, '--replay', str(P / 'inputs.csv'), '--frames', '24020',
                '--timeout', '300', '--workspace-cap-gb', '50', '--policy', str(P / 'policy.lua')]
        log = H / (mapper + '-run.log')
        with log.open('wb') as f:
            rc = subprocess.run(argv, cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
        folder = R / 'build/roster-through-2-2' / (tag + '-6-v0-' + mapper)
        path = folder / 'manifest.json'
        manifest = json.loads(path.read_text()) if path.exists() else None
        report['rows'].append(dict(mapper=mapper, exit=rc, ROM_sha256=sha(rom), output=folder.relative_to(R).as_posix(),
                                  manifest_sha256=sha(path) if path.exists() else None,
                                  result=manifest.get('result') if manifest else None,
                                  verified=bool(manifest and manifest.get('verified_through_2_2')), log_sha256=sha(log)))
        save()
        print(mapper, rc, report['rows'][-1]['result'], flush=True)
    assert all(sha(T / 'source' / n) == h for n, h in build['source_hashes'].items())
    passed = all(r['exit'] == 0 and r['verified'] for r in report['rows'])
    report['status'] = 'PASS_FRESH_PIT_SIX_STAGES_BOTH_MAPPERS_ON_T' if passed else 'RETAINED_PIT_REPLAY_DIVERGENCE_ON_T'
    report['qualification'] = 'Actual fixed power-on inputs, no route grants. Unrecorded audit; not all upgrades/attacks, waveform or source-perfect proof.'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
