"""Check that the combined source still builds with Crossover disabled."""
from pathlib import Path
import hashlib, json, subprocess, sys

R = Path(__file__).resolve().parents[2]
H = R / 'build/verification/root49-easy-combined-bq'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = H / 'baseline-ce'
    out.mkdir(exist_ok=False)
    assert sha(H / 'report.json') == '2736ac1e4238d237fce859e18ae29f7ef137ed4b2f386e3078c2a2438021e838'
    build = json.loads((H / 'report.json').read_text())
    before = R / 'build/smb-crossover-mmc3-baseline.nes'
    old_hash = sha(before)
    rows = []
    for mapper in ['mmc3', 'mmc5']:
        log_path = out / (mapper + '.log')
        with log_path.open('wb') as log:
            rc = subprocess.run([sys.executable, str(H / 'build-driver.py'), '--mapper', mapper, '--baseline'],
                                cwd=R, stdout=log, stderr=subprocess.STDOUT).returncode
        rom = H / 'source/build' / ('smb-crossover-' + mapper + '-baseline.nes')
        row = dict(mapper=mapper, exit=rc, passed=rc == 0 and rom.exists(), log_sha256=sha(log_path))
        if rom.exists():
            row['ROM_sha256'] = sha(rom)
            if mapper == 'mmc3':
                row['byte_exact_existing_workspace_baseline'] = sha(rom) == old_hash
                row['passed'] &= row['byte_exact_existing_workspace_baseline']
        rows.append(row)
        print(mapper, row, flush=True)
    assert sha(before) == old_hash
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    result = dict(status='PASS_BQ_BASELINE_BUILDS' if all(x['passed'] for x in rows) else 'RETAINED_BQ_BASELINE_NEGATIVE',
                  script_sha256=sha(__file__), rows=rows, existing_MMC3_baseline_sha256=old_hash,
                  qualification='Compilation/header check; MMC3 additionally byte-exact to existing workspace baseline. No new ordinary baseline playthrough.',
                  accepted_release=False, goal_complete=False)
    (out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], sha(out / 'report.json'), flush=True)
    return 0 if all(x['passed'] for x in rows) else 1


if __name__ == '__main__':
    raise SystemExit(main())
