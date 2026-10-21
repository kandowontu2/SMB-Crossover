"""Retarget the frozen growth core and hardware pixel review, without oracle edits."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-union-t'
P = V / 'agent49-bill-growth-e'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(H / 'report.json') == '99b62c608a5fb96c1c121c00cba9edafe0514333d11b939597474a09348278e9'
    report = dict(status='RUNNING_COMBINED_T_GROWTH', script_sha256=sha(__file__),
                  build_sha256=sha(H / 'report.json'), rows=[], route_proof=False)
    path = H / 'growth-native-report.json'

    def save():
        path.write_text(json.dumps(report, indent=2) + '\n')

    for name in ['native.lua', 'review_art.py']:
        assert not (H / name).exists()
        shutil.copyfile(P / name, H / name)
    original = (P / 'run_native.py').read_text()
    adapted = original
    for old, new in [
        ("im=m.Image(H/a.kind/f'smb-crossover-{a.mapper}.nes');oracle=m.Image(H/'candidate'/im.path.name)",
         "im=m.Image(H/'source/build'/f'smb-crossover-{a.mapper}.nes');oracle=im"),
        ("sha(H/'build-report.json')", "sha(H/'report.json')"),
    ]:
        assert adapted.count(old) == 1
        adapted = adapted.replace(old, new)
    launcher = H / 'growth-rebound-launcher.py'
    launcher.write_text(adapted)
    report['original_launcher_sha256'] = sha(P / 'run_native.py')
    report['rebound_launcher_sha256'] = sha(launcher)
    report['core_sha256'] = sha(H / 'native.lua')
    assert sha(H / 'native.lua') == sha(P / 'native.lua')
    save()
    for mapper in ['mmc3', 'mmc5']:
        for kind in ['full', 'visual']:
            tag = 'growth-' + kind + '-' + mapper + '-a'
            log = H / (tag + '-run.log')
            argv = [sys.executable, str(launcher), '--mapper', mapper, '--kind', 'candidate', '--tag', tag]
            if kind == 'visual':
                argv.append('--visual-only')
            with log.open('wb') as f:
                rc = subprocess.run(argv, cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
            host = H / 'native' / tag / 'host-report.json'
            result = json.loads(host.read_text()) if host.exists() else None
            report['rows'].append(dict(mapper=mapper, kind=kind, exit=rc,
                                       host_sha256=sha(host) if host.exists() else None,
                                       result=result, log_sha256=sha(log)))
            save()
            print(mapper, kind, rc, flush=True)
            assert rc == 0 and result and result['admitted']
    pixel = (P / 'review_native_pixels.py').read_text()
    for old, new in [('final-m3-g', 'growth-full-mmc3-a'), ('final-m5-k', 'growth-full-mmc5-a'),
                     ('visual-m3-l', 'growth-visual-mmc3-a'), ('visual-m5-m', 'growth-visual-mmc5-a'),
                     ("H/'candidate'", "H/'source/build'")]:
        assert pixel.count(old) == 1
        pixel = pixel.replace(old, new)
    reviewer = H / 'growth-rebound-pixel-review.py'
    reviewer.write_text(pixel)
    log = H / 'growth-pixel-review.log'
    with log.open('wb') as f:
        rc = subprocess.run([sys.executable, str(reviewer)], cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
    report['hardware_pixel_review_exit'] = rc
    save()
    assert rc == 0
    report['hardware_pixel_review_sha256'] = sha(H / 'native-pixel-review.json')
    report['status'] = 'PASS_COMBINED_T_GROWTH_AND_ACTUAL_HARDWARE_PIXELS'
    save()
    print(report['status'], sha(path), flush=True)


if __name__ == '__main__':
    main()
