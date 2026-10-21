"""Admit Mario's explicit aliases without permitting RAM relocation/allocation."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-union-g'
B = V / 'root49-easy-union-f'
H = V / 'root49-easy-union-h'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ALIASES = dict(MarioSourceActive='XgIndex', MarioRunCap='XgDash', MarioJustCrouched='XgJumpUsed',
               MarioJumpRise='XgRise', MarioJumpEnd='XgJumpStart', MarioJumpEndHigh='XgJumpHeight',
               MarioJumpMin='XgWall', MarioJumpMinHigh='XgWallContact', MarioJumpFraction='XgCeiling')


def main():
    sys.dont_write_bytecode = True
    assert not H.exists()
    previous = json.loads((P / 'report.json').read_text())
    expected = previous['source_hashes']
    assert previous['builds'][0]['exit'] == 0
    assert all(sha(P / 'source' / n) == v for n, v in expected.items())
    u = json.loads((R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json').read_text())
    assert all(sha(R / n) == v for n, v in u['source_hashes'].items())
    H.mkdir()
    shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    text = (S / 'src/mario_source.s').read_text()
    assert all(f'{n} := {target}' in text for n, target in ALIASES.items())
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    old = 'ROOT = Path(' + repr(str(P / 'source')) + ')'
    assert text.count(old) == 1
    driver.write_text(text.replace(old, 'ROOT = Path(' + repr(str(S)) + ')'))
    report = dict(status='BUILDING_MARIO_SHARED_UNION_H', script_sha256=sha(__file__),
                  retained_G_validation_negative_sha256=sha(P / 'report.json'),
                  validation_correction='Nine explicitly named aliases of existing exclusive-avatar Xg bytes are new symbols, not new allocations. Require every original symbol exact and SRAM segment size exact.',
                  source_hashes=expected, aliases=ALIASES, builds=[], main_changed=False,
                  Mario_final_validation_pending=True, complete_Easy_behavior=False, accepted_release=False, goal_complete=False)

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    spec = importlib.util.spec_from_file_location('union_h_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
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
        before = mod.Image(B / ('source/build/smb-crossover-' + mapper + '.nes'))
        assert all(im.ram.get(n) == value for n, value in before.ram.items())
        assert set(im.ram) - set(before.ram) == set(ALIASES)
        assert all(im.ram[n] == before.ram[target] for n, target in ALIASES.items())
        assert next(s['size'] for s in im.segs.values() if s['name'] == 'SRAM') == next(s['size'] for s in before.segs.values() if s['name'] == 'SRAM')
        assert im.raw[16 + 64 * 8192:] == before.raw[16 + 64 * 8192:]
        ds = next(s for s in im.segs.values() if s['name'] == 'BASS_DPCM')
        old_ds = next(s for s in before.segs.values() if s['name'] == 'BASS_DPCM')
        assert im.raw[ds['ooffs']:ds['ooffs'] + ds['size']] == before.raw[old_ds['ooffs']:old_ds['ooffs'] + old_ds['size']]
        row.update(ROM_sha256=sha(im.path), old_RAM_exact=True, new_RAM_bytes=0, CHR_exact=True, DPCM_exact=True,
                   segments={n: next(s for s in im.segs.values() if s['name'] == n) for n in ['GUEST', 'PLAYER', 'SAMUS', 'SPECIAL_EXTRA', 'SPECIAL_ROSTER', 'INVENTORY', 'OBJECT', 'ROSTER', 'TITLE', 'RENDER', 'COLLISION', 'FIXED']})
        save()
    assert all(sha(S / n) == h for n, h in expected.items())
    assert all(sha(R / n) == h for n, h in u['source_hashes'].items())
    report['status'] = 'PASS_PRIVATE_SHARED_MARIO_UNION_H_BUILD_ONLY'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
