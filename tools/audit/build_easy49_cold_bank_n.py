"""Use unused MM3 audio-bank tail for existing bank-called cold closures."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-samus-bomb-m'
H = V / 'root49-easy-cold-bank-n'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode = True
    assert not H.exists()
    previous = json.loads((P / 'report.json').read_text())
    assert previous['status'] == 'PASS_PRIVATE_SAMUS_BOMB_STEP_BUILD_ONLY'
    expected = dict(previous['source_hashes'])
    assert all(sha(P / 'source' / n) == v for n, v in expected.items())
    u = json.loads((R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json').read_text())
    assert all(sha(R / n) == v for n, v in u['source_hashes'].items())
    H.mkdir()
    shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    config = S / 'smb1base.cfg'
    text = config.read_text()
    old = '    MM3_AUDIO:        load = PRGA_0b, type = ro, optional=yes;'
    assert text.count(old) == 1 and 'LEGACY_COLD' not in text
    config.write_text(text.replace(old, old + '\n    LEGACY_COLD:      load = PRGA_0b, type = ro, optional=yes;'))
    helper = S / 'src/samus_legacy_bomb.s'
    text = helper.read_text()
    assert text.count('.segment "SPECIAL_EXTRA"') == 1
    helper.write_text(text.replace('.segment "SPECIAL_EXTRA"', '.segment "LEGACY_COLD"'))
    path = S / 'src/megaman_weapons.s'
    text = path.read_text()
    start = text.index('.proc MegaManCoinBrick\n')
    end = text.index('.endproc', start) + len('.endproc')
    body = text[start:end]
    assert 'jsr ' not in body and 'farcall ' not in body
    refs = []
    for f in (S / 'src').glob('*.s'):
        refs += [(f.name, line.strip()) for line in f.read_text().splitlines() if 'MegaManCoinBrick' in line]
    assert sorted(refs) == [('collision.s', 'farcall MegaManCoinBrick'), ('megaman_weapons.s', '.proc MegaManCoinBrick')]
    path.write_text(text[:start] + '.pushseg\n.segment "LEGACY_COLD"\n' + body + '\n.popseg' + text[end:])
    for n in ['smb1base.cfg', 'src/samus_legacy_bomb.s', 'src/megaman_weapons.s']:
        expected[n] = sha(S / n)
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    old = 'ROOT = Path(' + repr(str(P / 'source')) + ')'
    assert text.count(old) == 1
    driver.write_text(text.replace(old, 'ROOT = Path(' + repr(str(S)) + ')'))
    report = dict(status='BUILDING_UNUSED_BANK_TAIL_COLD_RELOCATION', script_sha256=sha(__file__),
                  parent_report_sha256=sha(P / 'report.json'), source_hashes=expected,
                  closures=['MegaManCoinBrick', 'SamusLegacyBombStep'], new_bank_crossings=0,
                  original_coin_references=refs, builds=[], main_changed=False,
                  complete_Easy_behavior=False, accepted_release=False, goal_complete=False)

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    spec = importlib.util.spec_from_file_location('cold_n_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
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
        audio = next(s for s in im.segs.values() if s['name'] == 'MM3_AUDIO')
        old_audio = next(s for s in before.segs.values() if s['name'] == 'MM3_AUDIO')
        assert (audio['start'], audio['size'], audio['ooffs']) == (old_audio['start'], old_audio['size'], old_audio['ooffs'])
        assert im.raw[audio['ooffs']:audio['ooffs'] + audio['size']] == before.raw[audio['ooffs']:audio['ooffs'] + audio['size']]
        cold = next(s for s in im.segs.values() if s['name'] == 'LEGACY_COLD')
        assert cold['ooffs'] == audio['ooffs'] + audio['size']
        assert before.raw[cold['ooffs']:cold['ooffs'] + cold['size']] == bytes([255]) * cold['size']
        assert (cold['ooffs'] - 16) // 8192 == 11 and cold['start'] + cold['size'] <= 0xc000
        row.update(ROM_sha256=sha(im.path), RAM_exact=True, CHR_exact=True, ROM_size_exact=True,
                   MM3_audio_bytes_and_addresses_exact=True, new_code_uses_only_old_FF_padding=True,
                   segments={n: next(s for s in im.segs.values() if s['name'] == n) for n in ['GUEST', 'SAMUS', 'SPECIAL_EXTRA', 'LEGACY_COLD', 'MM3_AUDIO']})
        save()
    assert all(sha(S / n) == h for n, h in expected.items())
    assert all(sha(R / n) == h for n, h in u['source_hashes'].items())
    report['status'] = 'PASS_PRIVATE_COLD_BANK_RELOCATION_BUILD_ONLY'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
