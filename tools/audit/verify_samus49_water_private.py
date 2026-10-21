"""Run existing Samus and shared water checks in L's isolated checkout."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
L = ROOT / 'build/verification/root49k-samus-water-private-build-l'
OWN = L / 'targeted-regression-a'
SOURCE = L / 'source'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OWN.exists()
    built = json.loads((L / 'report.json').read_text())
    assert built['status'] == 'PASS-build-and-scoped-layout-only-not-accepted'
    assert all(sha(SOURCE / n) == h for n, h in built['source407_hashes'].items())
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    assert workspace_bytes(ROOT) + 100_000_000 < 30_000_000_000
    OWN.mkdir()
    for path in (ROOT / 'tests').rglob('*'):
        if path.is_file():
            target = SOURCE / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                assert sha(target) == sha(path)
            else:
                shutil.copyfile(path, target)
    for n in ('tools/run_mesen.py', 'tools/luigi_native_review.py'):
        shutil.copyfile(ROOT / n, SOURCE / n)
    fixtures = {str(p.relative_to(SOURCE)): sha(p) for p in (SOURCE / 'tests').rglob('*') if p.is_file()}
    names = sorted(p.stem for p in (SOURCE / 'tests').glob('samus-*.lua'))
    # Retain exactly the 28 established suite cases, excluding probe/helper files.
    staged = json.loads((ROOT / 'build/verification/root49-integrated-private-build-k/staged-current-summary.json').read_text())
    names = sorted({c['test'] for c in staged['unchanged_cases'] if c['test'].startswith('samus-')})
    names += ['guest-head-upper-extent', 'expanded-environment', 'player-outlines-render',
              'water-motion-differential', 'water-expansion-differential', 'water-corner-differential', 'water-oam-differential']
    assert len(names) == len(set(names)) == 35
    report = dict(status='running', goal_complete=False, tests=names, fixture_hashes=fixtures,
                  build_report_sha256=sha(L / 'report.json'), cases=[], failures=[],
                  scope='Existing 28 Samus and seven shared collision/render/water fixtures per mapper; not a full suite or ordinary route.')
    path = OWN / 'report.json'
    def save():
        path.write_text(json.dumps(report, indent=2) + '\n')
    save()
    def run(mapper, name):
        argv = [sys.executable, 'tools/run_mesen.py', f'tests/{name}.lua', f'build/smb-crossover-{mapper}.nes', '--timeout', '90']
        result = subprocess.run(argv, cwd=SOURCE, capture_output=True, text=True)
        log = OWN / f'{mapper}-{name}.log'
        log.write_text(result.stdout + result.stderr, encoding='utf-8')
        return dict(mapper=mapper, test=name, exit=result.returncode,
                    passed=result.returncode == 0 and 'PASS ' in result.stdout,
                    log_sha256=sha(log), ROM_sha256=sha(SOURCE / f'build/smb-crossover-{mapper}.nes'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        tasks = [pool.submit(run, mapper, name) for mapper in ('mmc3', 'mmc5') for name in names]
        for future in concurrent.futures.as_completed(tasks):
            case = future.result()
            report['cases'].append(case)
            if not case['passed']:
                report['failures'].append([case['mapper'], case['test']])
            save()
    assert all(sha(SOURCE / n) == h for n, h in fixtures.items())
    assert all(sha(SOURCE / n) == h for n, h in built['source407_hashes'].items())
    report.update(status='PASS-targeted-only' if not report['failures'] else 'FAIL-retained',
                  source407_and_fixtures_exact_after=True, cases_count=len(report['cases']), workspace_after_bytes=workspace_bytes(ROOT))
    save()
    print(json.dumps({k: v for k, v in report.items() if k not in ('fixture_hashes', 'cases', 'tests')}), flush=True)
    raise SystemExit(bool(report['failures']))


if __name__ == '__main__':
    main()
