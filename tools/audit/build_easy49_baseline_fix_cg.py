"""Repair baseline-only conditional guards; retain exact tested crossover ROMs."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-combined-bq'
H = V / 'root49-easy-combined-cg'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(P / 'report.json') == '2736ac1e4238d237fce859e18ae29f7ef137ed4b2f386e3078c2a2438021e838'
    parent = json.loads((P / 'report.json').read_text())
    assert all(sha(P / 'source' / n) == h for n, h in parent['source_hashes'].items())
    assert not H.exists()
    H.mkdir()
    shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    path = S / 'src/collision.s'
    before = path.read_bytes()
    lf = b'\r\n' if b'\r\n' in before else b'\n'
    anchor = lf.join([b'HandlePowerUpCollision:', b'.if ::ENABLE_CROSSOVER', b'      farcall MarioSourcePowerupCollision, jmp', b'.else', b'HandlePowerUpCollision:', b''])
    replacement = lf.join([b'HandlePowerUpCollision:', b'.if ::ENABLE_CROSSOVER', b'      farcall MarioSourcePowerupCollision, jmp', b'.else', b''])
    assert before.count(anchor) == 1
    updated = before.replace(anchor, replacement)
    water = b'       jsr GuestWaterStompPolicy    ;Cached native/source enemy eligibility.'
    assert updated.count(water) == 1
    guard = lf.join([b'.if ::ENABLE_CROSSOVER', water, b'.else', b'       lda AreaType                 ;Original water-level injury policy.', b'.endif'])
    path.write_bytes(updated.replace(water, guard))
    hashes = dict(parent['source_hashes'])
    hashes['src/collision.s'] = sha(path)
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    needle = 'ROOT = Path(' + repr(str(P / 'source')) + ')'
    assert text.count(needle) == 1
    driver.write_text(text.replace(needle, 'ROOT = Path(' + repr(str(S)) + ')'))
    old_baseline = R / 'build/smb-crossover-mmc3-baseline.nes'
    original_baseline = sha(old_baseline)
    report = dict(status='BUILDING_BASELINE_GUARD_FIX_CG', script_sha256=sha(__file__),
                  parent_build_sha256=sha(P / 'report.json'),
                  source_changes={'src/collision.s': dict(before=hashlib.sha256(before).hexdigest(), after=sha(path))},
                  source_hashes=hashes, builds=[],
                  scope='Remove duplicate baseline label and retain original AreaType water policy when Crossover is disabled. No emitted crossover bytes should change.',
                  main_changed=False, accepted_release=False, goal_complete=False)
    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for baseline in [False, True]:
        for mapper in ['mmc3', 'mmc5']:
            name = mapper + ('-baseline' if baseline else '')
            log_path = H / (name + '.log')
            args = [sys.executable, str(driver), '--mapper', mapper] + (['--baseline'] if baseline else [])
            with log_path.open('wb') as log:
                rc = subprocess.run(args, cwd=R, stdout=log, stderr=subprocess.STDOUT).returncode
            rom = S / 'build' / ('smb-crossover-' + name + '.nes')
            row = dict(mapper=mapper, baseline=baseline, exit=rc, passed=rc == 0 and rom.exists(), log_sha256=sha(log_path))
            if rom.exists():
                row['ROM_sha256'] = sha(rom)
                if not baseline:
                    row['byte_exact_tested_BQ'] = sha(rom) == next(x['ROM_sha256'] for x in parent['builds'] if x['mapper'] == mapper)
                    row['passed'] &= row['byte_exact_tested_BQ']
                elif mapper == 'mmc3':
                    row['byte_exact_existing_workspace_baseline'] = sha(rom) == original_baseline
                    row['passed'] &= row['byte_exact_existing_workspace_baseline']
            report['builds'].append(row)
            save()
            print(name, row, flush=True)
    assert all(sha(S / n) == h for n, h in hashes.items())
    assert all(sha(P / 'source' / n) == h for n, h in parent['source_hashes'].items())
    assert sha(old_baseline) == original_baseline
    passed = len(report['builds']) == 4 and all(x['passed'] for x in report['builds'])
    report['status'] = 'PASS_CG_BASELINE_FIX_CROSSOVER_ROMS_EXACT_BQ' if passed else 'RETAINED_CG_BASELINE_BUILD_NEGATIVE'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
