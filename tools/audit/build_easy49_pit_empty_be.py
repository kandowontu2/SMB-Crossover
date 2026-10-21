"""Reuse distinct-cell empty-air probes for Pit's symmetric arrow rectangles."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-advanced-union-ap'
H = V / 'root49-easy-pit-empty-be'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not H.exists()
    assert sha(P / 'report.json') == 'e1215e073905879a580fea13dfe55dad26d9fe11a0595bbe7fbfdf915a822b6e'
    parent = json.loads((P / 'report.json').read_text())
    assert all(sha(P / 'source' / name) == digest for name, digest in parent['source_hashes'].items())
    H.mkdir()
    shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    changed = S / 'src/megaman_weapons.s'
    before = changed.read_text()
    needle = '  cpy #71                       ; Sophia\'s standard missile also has symmetric corners.\n  jeq BillPrepare\nProbe:\n'
    assert before.count(needle) == 1
    after = needle.replace('Probe:\n', '''  ; Pit's three arrow tiers have symmetric extents. Reuse the distinct-cell
  ; empty-air path; solid cells retain the existing facing/row probe order.
  cpy #26
  bcc Probe
  cpy #29
  bcs Probe
  lda SelectedCharacter
  cmp #CHARACTER_PIT
  jeq BillPrepare
Probe:
''')
    changed.write_text(before.replace(needle, after))
    driver = H / 'build-driver.py'
    content = (P / 'build-driver.py').read_text()
    needle = 'ROOT = Path(' + repr(str(P / 'source')) + ')'
    assert content.count(needle) == 1
    driver.write_text(content.replace(needle, 'ROOT = Path(' + repr(str(S)) + ')'))
    spec = importlib.util.spec_from_file_location('pit_be_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    report = dict(status='BUILDING_PRIVATE_PIT_DISTINCT_CELL_CANDIDATE', script_sha256=sha(__file__),
                  parent_report_sha256=sha(P / 'report.json'), source_changes={'src/megaman_weapons.s':
                      dict(before=parent['source_hashes']['src/megaman_weapons.s'], after=sha(changed))},
                  builds=[], RAM_changed=False, config_changed=False, CHR_changed=False,
                  qualification='Optimization candidate only; native contact equivalence and performance remain required.',
                  main_changed=False, accepted_release=False, goal_complete=False)

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for mapper in ['mmc3', 'mmc5']:
        log = H / (mapper + '-build.log')
        with log.open('wb') as stream:
            rc = subprocess.run([sys.executable, str(driver), '--mapper', mapper], cwd=R, stdout=stream, stderr=subprocess.STDOUT).returncode
        row = dict(mapper=mapper, exit=rc, log_sha256=sha(log))
        report['builds'].append(row)
        save()
        assert rc == 0
        im = m.Image(S / 'build' / ('smb-crossover-' + mapper + '.nes'))
        old = m.Image(P / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
        assert im.ram == old.ram and im.raw[:16] == old.raw[:16] and im.raw[524304:] == old.raw[524304:]
        assert len(im.raw) == len(old.raw)
        audio = {}
        for segment in old.segs.values():
            name = segment['name']
            if segment.get('type') != 'ro' or ('AUDIO' not in name and 'DPCM' not in name):
                continue
            now = next(s for s in im.segs.values() if s['name'] == name)
            assert (now['start'], now['size'], now['ooffs']) == (segment['start'], segment['size'], segment['ooffs'])
            assert im.raw[now['ooffs']:now['ooffs'] + now['size']] == old.raw[segment['ooffs']:segment['ooffs'] + segment['size']]
            audio[name] = dict(bytes=now['size'], exact=True)
        deltas = {}
        for segment in old.segs.values():
            now = next(s for s in im.segs.values() if s['name'] == segment['name'])
            if now['size'] != segment['size']:
                deltas[segment['name']] = now['size'] - segment['size']
        assert deltas == {'GUEST': 18}, deltas
        arrays = {}
        for name in ['ShotLeft', 'ShotRight', 'ShotTop', 'ShotBottom', 'RadiusX', 'RadiusY']:
            hook = im.hook(name, 'MegaManWeapons')
            old_hook = old.hook(name, 'MegaManWeapons')
            values = list(im.raw[hook['rom_offset'] + 25:hook['rom_offset'] + 28])
            assert values == list(old.raw[old_hook['rom_offset'] + 25:old_hook['rom_offset'] + 28])
            arrays[name] = values
        assert arrays == dict(ShotLeft=[252, 250, 249], ShotRight=[4, 6, 7], ShotTop=[253, 253, 252], ShotBottom=[3, 3, 4], RadiusX=[4, 6, 7], RadiusY=[3, 3, 4])
        row.update(ROM_sha256=sha(im.path), RAM_header_CHR_size_exact=True, audio=audio,
                   segment_deltas=deltas, actual_Pit_extents=arrays)
        save()
    expected = dict(parent['source_hashes'])
    expected['src/megaman_weapons.s'] = sha(changed)
    assert all(sha(S / name) == digest for name, digest in expected.items())
    report.update(status='PASS_PRIVATE_PIT_DISTINCT_CELL_BUILD_ONLY', source_hashes=expected)
    save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
