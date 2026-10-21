"""Skip Easy Link/Simon bank calls for foreign shots; retain the actual helpers."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-union-t'
H = V / 'root49-easy-whip-hot-v'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode = True
    assert not H.exists()
    previous = json.loads((P / 'report.json').read_text())
    assert sha(P / 'report.json') == '99b62c608a5fb96c1c121c00cba9edafe0514333d11b939597474a09348278e9'
    assert all(sha(P / 'source' / n) == h for n, h in previous['source_hashes'].items())
    H.mkdir()
    shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    path = S / 'src/megaman_weapons.s'
    text = path.read_text()
    for helper in ['EasyWhipProbe', 'EasyWhipEnvelope']:
        old = '  farcall ' + helper + '\n'
        assert text.count(old) == 1
        label = helper + 'AdmissionDone'
        guard = ('  ; EasyWhipEligible accepts only adjacent Link/Simon IDs under Easy.\n'
                 '  lda SelectedCharacter\n  sec\n  sbc #CHARACTER_LINK\n  cmp #2\n  bcs ' + label
                 + '\n  lda CrossoverBehaviorVersion\n  bne ' + label + '\n' + old + label + ':\n')
        text = text.replace(old, guard)
    path.write_text(text)
    expected = dict(previous['source_hashes'])
    expected['src/megaman_weapons.s'] = sha(path)
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    old = 'ROOT = Path(' + repr(str(P / 'source')) + ')'
    assert text.count(old) == 1
    driver.write_text(text.replace(old, 'ROOT = Path(' + repr(str(S)) + ')'))
    report = dict(status='BUILDING_PRIVATE_WHIP_HOT_ADMISSION', parent_report_sha256=sha(P / 'report.json'),
                  script_sha256=sha(__file__), source_hashes=expected, builds=[], main_changed=False,
                  accepted_release=False, goal_complete=False,
                  contract='Only A/flags admission work changes on skipped calls; the next existing caller instructions overwrite both before use. X/Y and RAM unchanged. Eligible active calls retain the old helper.')

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    spec = importlib.util.spec_from_file_location('whip_v_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for mapper in ['mmc3', 'mmc5']:
        log = H / (mapper + '-build.log')
        with log.open('wb') as f:
            rc = subprocess.run([sys.executable, str(driver), '--mapper', mapper], cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
        row = dict(mapper=mapper, exit=rc, log_sha256=sha(log))
        report['builds'].append(row)
        save()
        assert rc == 0
        im = mod.Image(S / ('build/smb-crossover-' + mapper + '.nes'))
        before = mod.Image(P / ('source/build/smb-crossover-' + mapper + '.nes'))
        assert im.ram == before.ram and len(im.raw) == len(before.raw)
        assert im.raw[16 + 64 * 8192:] == before.raw[16 + 64 * 8192:]
        row.update(ROM_sha256=sha(im.path), RAM_exact=True, CHR_exact=True,
                   GUEST_size=next(s['size'] for s in im.segs.values() if s['name'] == 'GUEST'))
        save()
    assert all(sha(S / n) == h for n, h in expected.items())
    report['status'] = 'PASS_PRIVATE_WHIP_HOT_ADMISSION_BUILD_ONLY'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
