"""Merge only the frozen Link rectangle overlay into shared union H."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys, zipfile
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-union-h'
H = V / 'root49-easy-union-k'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode = True
    assert not H.exists()
    previous = json.loads((P / 'report.json').read_text())
    assert previous['status'] == 'PASS_PRIVATE_SHARED_MARIO_UNION_H_BUILD_ONLY'
    expected = dict(previous['source_hashes'])
    assert all(sha(P / 'source' / n) == v for n, v in expected.items())
    u = json.loads((R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json').read_text())
    assert all(sha(R / n) == v for n, v in u['source_hashes'].items())
    incoming_root = V / 'agent-lsr-easy-link-rect-animation-k/frozen-k'
    frozen_path = incoming_root / 'implementation-freeze-k.json'
    assert sha(frozen_path) == 'b938fbe90c94816c574918836d2d2fbffa1101859a726d43df70fe8410b591cc'
    frozen = json.loads(frozen_path.read_text())
    parent_archive = V / 'agent-lsr-easy-link-order-a/source-link-order-j.zip'
    assert sha(parent_archive) == frozen['parent_archive_sha256']
    assert frozen['integration_overlay'] == ['src/entrypoint.s', 'src/easy_lsr.s', 'src/easy_link_rect_animation.s']
    H.mkdir()
    shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    report = dict(status='MERGING_FROZEN_LINK_RECTANGLES', script_sha256=sha(__file__),
                  parent_report_sha256=sha(P / 'report.json'), Link_rectangle_freeze_sha256=sha(frozen_path),
                  source_hashes=expected, merges=[], builds=[], main_changed=False,
                  complete_Easy_behavior=False, accepted_release=False, goal_complete=False)

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    with zipfile.ZipFile(parent_archive) as archive:
        for n in frozen['integration_overlay']:
            incoming = incoming_root / 'after' / n
            assert sha(incoming) == frozen['source_catalog'][n]
            if n not in archive.namelist():
                assert n == 'src/easy_link_rect_animation.s' and not (S / n).exists()
                shutil.copyfile(incoming, S / n)
                expected[n] = sha(S / n)
                continue
            folder = H / 'merges' / Path(n).stem
            folder.mkdir(parents=True)
            current, base, other = [folder / name for name in ['current.s', 'base.s', 'incoming.s']]
            current.write_text((S / n).read_text())
            base.write_text(archive.read(n).decode().replace('\r\n', '\n'))
            other.write_text(incoming.read_text())
            result = subprocess.run(['git', 'merge-file', '--stdout', str(current), str(base), str(other)], cwd=R, capture_output=True)
            merged = folder / 'merged.s'
            merged.write_bytes(result.stdout)
            report['merges'].append(dict(path=n, exit=result.returncode, current_sha256=sha(current), base_sha256=sha(base), incoming_sha256=sha(other), result_sha256=sha(merged)))
            save()
            assert result.returncode == 0, n
            shutil.copyfile(merged, S / n)
            expected[n] = sha(S / n)
    assert sha(S / 'src/megaman_palette.s') == previous['source_hashes']['src/megaman_palette.s']
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    old = 'ROOT = Path(' + repr(str(P / 'source')) + ')'
    assert text.count(old) == 1
    driver.write_text(text.replace(old, 'ROOT = Path(' + repr(str(S)) + ')'))
    spec = importlib.util.spec_from_file_location('union_k_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
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
        assert im.ram == before.ram
        assert im.raw[16 + 64 * 8192:] == before.raw[16 + 64 * 8192:]
        row.update(ROM_sha256=sha(im.path), RAM_exact=True, CHR_exact=True,
                   segments={n: next(s for s in im.segs.values() if s['name'] == n) for n in ['GUEST', 'PLAYER', 'SAMUS', 'SPECIAL_EXTRA', 'SPECIAL_ROSTER', 'INVENTORY', 'OBJECT', 'ROSTER', 'TITLE', 'RENDER']})
        save()
    assert all(sha(S / n) == h for n, h in expected.items())
    assert all(sha(R / n) == h for n, h in u['source_hashes'].items())
    report['status'] = 'PASS_PRIVATE_LINK_RECTANGLE_UNION_K_BUILD_ONLY'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
