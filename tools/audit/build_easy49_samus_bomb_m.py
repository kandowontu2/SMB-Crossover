"""Add original Easy Samus's immediate bomb-boost position/cache update."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-union-k'
H = V / 'root49-easy-samus-bomb-m'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode = True
    assert not H.exists()
    previous = json.loads((P / 'report.json').read_text())
    assert previous['status'] == 'PASS_PRIVATE_LINK_RECTANGLE_UNION_K_BUILD_ONLY'
    expected = dict(previous['source_hashes'])
    assert all(sha(P / 'source' / n) == v for n, v in expected.items())
    u = json.loads((R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json').read_text())
    assert all(sha(R / n) == v for n, v in u['source_hashes'].items())
    H.mkdir()
    shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    path = S / 'src/samus_weapons.s'
    text = path.read_text()
    old = '''  lda #1
  sta Player_State
  sta SmSourceJumped
NoBoost:
  rts
BombBlocks:'''
    new = '''  lda #1
  sta Player_State
  lda CrossoverBehaviorVersion
  beq LegacyStep
  lda #1
  sta SmSourceJumped
  rts
LegacyStep:
  ; Old hitProj retains jumped history and immediately updates both axes.
  phx
  phy
  farcall SamusLegacyBombStep
  ply
  plx
NoBoost:
  rts
BombBlocks:'''
    assert text.count(old) == 1
    path.write_text(text.replace(old, new))
    helper = R / 'tools/audit/samus49_legacy_bomb_step.s'
    shutil.copyfile(helper, S / 'src/samus_legacy_bomb.s')
    entry = S / 'src/entrypoint.s'
    text = entry.read_text()
    assert 'samus_legacy_bomb.s' not in text
    entry.write_text(text + '\n.if ::ENABLE_CROSSOVER\n.include "samus_legacy_bomb.s"\n.endif\n')
    for n in ['src/samus_weapons.s', 'src/samus_legacy_bomb.s', 'src/entrypoint.s']:
        expected[n] = sha(S / n)
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    old = 'ROOT = Path(' + repr(str(P / 'source')) + ')'
    assert text.count(old) == 1
    driver.write_text(text.replace(old, 'ROOT = Path(' + repr(str(S)) + ')'))
    report = dict(status='BUILDING_PRIVATE_SAMUS_LEGACY_BOMB_STEP', script_sha256=sha(__file__),
                  parent_report_sha256=sha(P / 'report.json'), helper_source_sha256=sha(helper),
                  source_hashes=expected, builds=[], main_changed=False,
                  complete_Easy_behavior=False, accepted_release=False, goal_complete=False,
                  scope='Immediate old position integration, original jumped history and refresh of existing native hitpoint projection. Does not certify all source Samus rectangle/cache geometry.',
                  source_anchors=[dict(path=str(p), sha256=sha(p)) for p in [
                      R / 'reference/crossover/decompiled/scripts/com/smbc/characters/Samus.as',
                      R / 'reference/crossover2/extracted/scripts/com/smbc/characters/Samus.as',
                      R / 'reference/crossover/decompiled/scripts/com/smbc/main/AnimatedObject.as',
                      R / 'reference/crossover/decompiled/scripts/com/smbc/data/HRect.as']])

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    spec = importlib.util.spec_from_file_location('bomb_m_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
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
                   cold_helper=im.hook('SamusLegacyBombStep'),
                   segments={n: next(s for s in im.segs.values() if s['name'] == n) for n in ['GUEST', 'PLAYER', 'SAMUS', 'SPECIAL_EXTRA', 'ROSTER', 'TITLE', 'RENDER']})
        save()
    assert all(sha(S / n) == h for n, h in expected.items())
    assert all(sha(R / n) == h for n, h in u['source_hashes'].items())
    report['status'] = 'PASS_PRIVATE_SAMUS_BOMB_STEP_BUILD_ONLY'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
