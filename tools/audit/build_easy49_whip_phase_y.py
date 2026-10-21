"""Add the frozen Link phase correction to the profiled private shot admission."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-whip-hot-v'
H = V / 'root49-easy-whip-phase-y'
S = H / 'source'
F = V / 'agent-lsr-easy-link-freeze-phase-n'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not H.exists()
    assert sha(P / 'report.json') == 'e908da36f96a53c04151f8bbf06b8fd8c6e60ea7d6f8cd73ab2163b879c5fad2'
    assert sha(F / 'implementation-freeze-n.json') == 'c869830884eb8fad2e4afdc39ff83898af4b24de6c93070bc8f83a5dceffaf9d'
    previous = json.loads((P / 'report.json').read_text())
    frozen = json.loads((F / 'implementation-freeze-n.json').read_text())
    assert all(sha(P / 'source' / n) == h for n, h in previous['source_hashes'].items())
    H.mkdir()
    shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    name = 'src/guest_powerups.s'
    row = frozen['overlay'][name]
    assert sha(S / name) == row['before_sha256']
    assert sha(F / 'after-guest_powerups.s') == row['after_sha256']
    shutil.copyfile(F / 'after-guest_powerups.s', S / name)
    expected = dict(previous['source_hashes']);expected[name] = sha(S / name)
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    old = 'ROOT = Path(' + repr(str(P / 'source')) + ')'
    assert text.count(old) == 1
    driver.write_text(text.replace(old, 'ROOT = Path(' + repr(str(S)) + ')'))
    report = dict(status='BUILDING_PRIVATE_WHIP_AND_PHASE', script_sha256=sha(__file__),
                  parent_report_sha256=sha(P / 'report.json'), freeze_sha256=sha(F / 'implementation-freeze-n.json'),
                  source_hashes=expected, builds=[], main_changed=False, accepted_release=False, goal_complete=False)

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    spec = importlib.util.spec_from_file_location('phase_y_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    mod = importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for mapper in ['mmc3', 'mmc5']:
        log = H / (mapper + '-build.log')
        with log.open('wb') as f:
            rc = subprocess.run([sys.executable, str(driver), '--mapper', mapper], cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
        row = dict(mapper=mapper, exit=rc, log_sha256=sha(log));report['builds'].append(row);save()
        assert rc == 0
        im = mod.Image(S / ('build/smb-crossover-' + mapper + '.nes'))
        oldim = mod.Image(P / ('source/build/smb-crossover-' + mapper + '.nes'))
        assert im.ram == oldim.ram and im.raw[16 + 64 * 8192:] == oldim.raw[16 + 64 * 8192:]
        row.update(ROM_sha256=sha(im.path), RAM_exact=True, CHR_exact=True,
                   GUEST_size=next(s['size'] for s in im.segs.values() if s['name'] == 'GUEST'),
                   SAMUS_size=next(s['size'] for s in im.segs.values() if s['name'] == 'SAMUS'))
        save()
    assert all(sha(S / n) == h for n, h in expected.items())
    report['status'] = 'PASS_PRIVATE_WHIP_AND_PHASE_Y_BUILD_ONLY';save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
