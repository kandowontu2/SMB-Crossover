"""Stage frozen Mario V with shared modes and the Samus head mode boundary."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys, zipfile
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-union-f'
H = V / 'root49-easy-union-g'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode = True
    assert not H.exists()
    previous = json.loads((P / 'report.json').read_text())
    assert previous['status'] == 'PASS_PRIVATE_BILL_PROJECTION_UNION_BUILD_ONLY'
    expected = dict(previous['source_hashes'])
    assert all(sha(P / 'source' / n) == v for n, v in expected.items())
    u = json.loads((R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json').read_text())
    assert all(sha(R / n) == v for n, v in u['source_hashes'].items())
    incoming_root = V / 'specialist-mario-easy-hard-source-a/overlay-v'
    manifest = json.loads((incoming_root / 'manifest.json').read_text())
    archive = incoming_root / 'own-overlay.zip'
    assert sha(archive) == manifest['own_overlay_sha256'] == 'cd723624f2e78bcbc1c9935576e6943903912dc22975c65bac80d5d8e042c5ca'
    H.mkdir()
    shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    incoming_dir = H / 'mario-overlay'
    with zipfile.ZipFile(archive) as z:
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
        z.extractall(incoming_dir)
    report = dict(status='MERGING_PRIVATE_MARIO_V_AND_SAMUS_HEAD', script_sha256=sha(__file__),
                  parent_report_sha256=sha(P / 'report.json'), Mario_manifest_sha256=sha(incoming_root / 'manifest.json'),
                  Mario_validation_still_pending=True, source_hashes=expected, merges=[], builds=[],
                  main_changed=False, complete_Easy_behavior=False, accepted_release=False, goal_complete=False)

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for n, hashes in manifest['own_files'].items():
        incoming = incoming_dir / n
        assert sha(incoming) == hashes['after_sha256']
        if hashes['before_sha256'] is None:
            assert not (S / n).exists()
            shutil.copyfile(incoming, S / n)
            expected[n] = sha(S / n)
            continue
        ancestor = incoming_root / 'merge-base' / n
        assert sha(ancestor) == hashes['before_sha256']
        if n == 'src/entrypoint.s':
            before, after = ancestor.read_text(), incoming.read_text()
            assert after == before + '\n.if ::ENABLE_CROSSOVER\n.include "guest_legacy_injury.s"\n.include "mario_source.s"\n.endif\n\n'
            current = (S / n).read_text()
            assert current.count('.include "guest_legacy_injury.s"') == 1
            assert '.include "mario_source.s"' not in current
            (S / n).write_text(current + '\n.if ::ENABLE_CROSSOVER\n.include "mario_source.s"\n.endif\n')
            report['merges'].append(dict(path=n, resolution='Root shared legacy include already present; append only the new Mario include after existing tail includes.',
                                         base_sha256=sha(ancestor), incoming_sha256=sha(incoming), result_sha256=sha(S / n)))
            expected[n] = sha(S / n)
            save()
            continue
        folder = H / 'merges' / Path(n).stem
        folder.mkdir(parents=True)
        current, base, other = [folder / name for name in ['current.s', 'base.s', 'incoming.s']]
        current.write_text((S / n).read_text())
        base.write_text(ancestor.read_text())
        other.write_text(incoming.read_text())
        result = subprocess.run(['git', 'merge-file', '--stdout', str(current), str(base), str(other)], cwd=R, capture_output=True)
        merged = folder / 'merged.s'
        merged.write_bytes(result.stdout)
        report['merges'].append(dict(path=n, exit=result.returncode, current_sha256=sha(current), base_sha256=sha(base),
                                     incoming_sha256=sha(other), result_sha256=sha(merged)))
        save()
        assert result.returncode == 0, n
        shutil.copyfile(merged, S / n)
        expected[n] = sha(S / n)
    # Original1.0 Brick.hitFromBelow permits upright suits1/2 to break;
    # 2.02 Samus.changeBrickState always selects BOUNCER outside Morph Ball.
    path = S / 'src/megaman_weapons.s'
    text = path.read_text()
    old = '''SamusHead:
  ; Hosted Samus breaks with her head in the first two suits. Wave suit
  ; bumps instead, and Morph Ball cannot break bricks by contact.
  lda SmBall'''
    new = '''SamusHead:
  ; Easy uses the original suit rule;2.02 only bumps while upright.
  lda CrossoverBehaviorVersion
  bne SmallHead
  lda SmBall'''
    assert text.count(old) == 1
    path.write_text(text.replace(old, new))
    expected['src/megaman_weapons.s'] = sha(path)
    report['Samus_head_scope'] = 'Mode-only ordinary brick breaking boundary; Morph Ball NONE/item activation is not certified by this hunk.'
    report['Samus_head_sources'] = [dict(path=str(p), sha256=sha(p)) for p in [
        R / 'reference/crossover/decompiled/scripts/com/smbc/ground/Brick.as',
        R / 'reference/crossover2/extracted/scripts/com/smbc/characters/Samus.as']]
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    old = 'ROOT = Path(' + repr(str(P / 'source')) + ')'
    assert text.count(old) == 1
    driver.write_text(text.replace(old, 'ROOT = Path(' + repr(str(S)) + ')'))
    spec = importlib.util.spec_from_file_location('union_g_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
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
                   segments={n: next(s for s in im.segs.values() if s['name'] == n) for n in ['GUEST', 'PLAYER', 'SAMUS', 'SPECIAL_EXTRA', 'SPECIAL_ROSTER', 'INVENTORY', 'OBJECT', 'TITLE', 'RENDER', 'COLLISION', 'FIXED']})
        save()
    assert all(sha(S / n) == h for n, h in expected.items())
    assert all(sha(R / n) == h for n, h in u['source_hashes'].items())
    report['status'] = 'PASS_PRIVATE_MARIO_AND_SAMUS_HEAD_UNION_BUILD_ONLY'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
