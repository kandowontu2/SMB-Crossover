"""Restore the original Link spring powers in Easy only, on private union C."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-union-c'
H = V / 'root49-easy-link-spring-e'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode = True
    assert not H.exists()
    previous = json.loads((P / 'report.json').read_text())
    assert previous['status'] == 'PASS_PRIVATE_MODE_UNION_C_BUILD_ONLY'
    expected = dict(previous['source_hashes'])
    assert all(sha(P / 'source' / n) == v for n, v in expected.items())
    u = json.loads((R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json').read_text())
    assert all(sha(R / n) == v for n, v in u['source_hashes'].items())
    H.mkdir()
    shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    source = R / 'reference/crossover/decompiled/scripts/com/smbc/characters/Link.as'
    modern = R / 'reference/crossover2/extracted/scripts/com/smbc/characters/Link.as'
    assert 'defSpringPwr = 400;' in source.read_text() and 'boostSpringPwr = 800;' in source.read_text()
    assert 'DEF_SPRING_PWR:int = 450;' in modern.read_text() and 'BOOST_SPRING_PWR:int = 950;' in modern.read_text()
    path = S / 'src/megaman_environment.s'
    text = path.read_text()
    old = '''  cmp #CHARACTER_LUIGI
  beq Done                      ; Luigi now uses that same native spring engine.
  sec
  sbc #CHARACTER_BILL'''
    new = '''  cmp #CHARACTER_LUIGI
  beq Done                      ; Luigi now uses that same native spring engine.
  cmp #CHARACTER_LINK
  bne IndexedSpring
  lda CrossoverBehaviorVersion
  bne IndexedSpring
  ; Linked1.0 Link:400/800;2.02 remains450/950 in the indexed table.
  lda #$ab
  sta MmVY
  lda #$aa
  sta MmVY+1
  lda #$fc
  sta MmVY+2
  lda JumpspringForce
  cmp #$f4
  bne LinkStore
  lda #$55
  sta MmVY
  sta MmVY+1
  lda #$f9
  sta MmVY+2
LinkStore:
  lda #0
  sta XgRise
  jmp Store
IndexedSpring:
  lda SelectedCharacter
  sec
  sbc #CHARACTER_BILL'''
    assert text.count(old) == 1
    path.write_text(text.replace(old, new))
    expected['src/megaman_environment.s'] = sha(path)
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    old = 'ROOT = Path(' + repr(str(P / 'source')) + ')'
    assert text.count(old) == 1
    driver.write_text(text.replace(old, 'ROOT = Path(' + repr(str(S)) + ')'))
    report = dict(status='BUILDING_PRIVATE_LINK_SPRING', script_sha256=sha(__file__),
                  parent_report_sha256=sha(P / 'report.json'), source_hashes=expected,
                  source_anchors=[dict(path=str(source), sha256=sha(source), powers=[400, 800]),
                                  dict(path=str(modern), sha256=sha(modern), powers=[450, 950])],
                  builds=[], main_changed=False, accepted_release=False,
                  complete_Easy_behavior=False, goal_complete=False)

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    spec = importlib.util.spec_from_file_location('spring_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for mapper in ['mmc3', 'mmc5']:
        log = H / (mapper + '-build.log')
        with log.open('wb') as f:
            rc = subprocess.run([sys.executable, str(driver), '--mapper', mapper], cwd=R,
                                stdout=f, stderr=subprocess.STDOUT).returncode
        row = dict(mapper=mapper, exit=rc, log_sha256=sha(log))
        report['builds'].append(row)
        save()
        assert rc == 0
        im = mod.Image(S / ('build/smb-crossover-' + mapper + '.nes'))
        before = mod.Image(P / ('source/build/smb-crossover-' + mapper + '.nes'))
        assert im.ram == before.ram
        assert im.raw[16 + 64 * 8192:] == before.raw[16 + 64 * 8192:]
        def resident_globals(image):
            result = {}
            for symbol in image.data['sym']:
                if symbol.get('scope') != 1 or 'seg' not in symbol or 'val' not in symbol:
                    continue
                seg = image.segs[symbol['seg']]
                if 'ooffs' not in seg or symbol['val'] < 0x8000:
                    continue
                offset = seg['ooffs'] + symbol['val'] - seg['start']
                bank = (offset - 16) // 8192
                if bank in [62, 63]:
                    result[symbol['name']] = (bank, symbol['val'])
            return result
        assert resident_globals(im) == resident_globals(before)
        diffs = {str(bank): [i for i in range(8192) if im.raw[16 + bank * 8192 + i] != before.raw[16 + bank * 8192 + i]] for bank in [62, 63]}
        row.update(ROM_sha256=sha(im.path), RAM_exact=True, CHR_exact=True, resident_global_addresses_exact=True, resident_byte_diffs=diffs)
        report['retained_negative'] = dict(path='root49-easy-link-spring-d/report.json', sha256=sha(V / 'root49-easy-link-spring-d/report.json'), reason='Whole resident-bank byte identity overconstrained legitimate farcall target relocations after growth in TITLE; global resident entry addresses remain exact.')
        save()
    assert all(sha(S / n) == v for n, v in expected.items())
    assert all(sha(R / n) == v for n, v in u['source_hashes'].items())
    report['status'] = 'PASS_PRIVATE_LINK_SPRING_BUILD_ONLY'
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
