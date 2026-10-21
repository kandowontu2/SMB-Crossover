"""Merge the frozen two-file Bill/HammerBro repair into combined Y."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-whip-phase-y'
F = V / 'agent49-enemy-geometry-f'
G = V / 'agent49-bill-growth-e'
H = V / 'root49-easy-bro-union-ab'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode = True
    assert not H.exists()
    assert sha(P / 'report.json') == 'f0377dd12cae59749f85fe42651c113a18e67c3c8291a14b3610b8ba889821bc'
    assert sha(F / 'freeze.json') == 'e45a288c08779b756e568847d48340890a69e45ac1d6c09e6586c0f9b74ffe25'
    prior = json.loads((P / 'report.json').read_text())
    frozen = json.loads((F / 'freeze.json').read_text())
    source_changes = json.loads((F / 'build-report.json').read_text())['source_changes']
    assert set(source_changes) == {'src/megaman_weapons.s', 'src/roster_weapons.s'}
    assert all(sha(P / 'source' / n) == h for n, h in prior['source_hashes'].items())
    assert sha(P / 'source/smb1base.cfg') == sha(F / 'source/smb1base.cfg')
    H.mkdir()
    shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    expected = dict(prior['source_hashes'])
    report = dict(status='MERGING_FROZEN_BOUNDED_HAMMERBRO_REPAIR', script_sha256=sha(__file__),
                  parent_report_sha256=sha(P / 'report.json'), source_freeze_sha256=sha(F / 'freeze.json'),
                  inherited_config_sha256=sha(S / 'smb1base.cfg'), merges=[], builds=[],
                  main_changed=False, accepted_release=False, goal_complete=False,
                  scope='Bill types11..13 only; source primary/head rectangles, not a broad enemy-geometry completion claim.')

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for name, values in source_changes.items():
        base = G / 'source' / name
        incoming = F / 'overlay' / name
        assert sha(base) == values['before'] and sha(incoming) == values['after']
        assert sha(incoming) == frozen['files'][incoming.relative_to(F).as_posix()]['sha256']
        folder = H / 'merges' / Path(name).stem;folder.mkdir(parents=True)
        paths = [folder / n for n in ['current.s', 'base.s', 'incoming.s']]
        for path, source in zip(paths, [S / name, base, incoming]):
            path.write_text(source.read_text())
        result = subprocess.run(['git', 'merge-file', '--stdout'] + [str(p) for p in paths], cwd=R, capture_output=True)
        merged = folder / 'merged.s';merged.write_bytes(result.stdout)
        report['merges'].append(dict(path=name, exit=result.returncode, current_sha256=sha(paths[0]),
                                     base_sha256=sha(paths[1]), incoming_sha256=sha(paths[2]), result_sha256=sha(merged)))
        save()
        assert result.returncode == 0, name
        shutil.copyfile(merged, S / name);expected[name] = sha(S / name)
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    old = 'ROOT = Path(' + repr(str(P / 'source')) + ')'
    assert text.count(old) == 1
    driver.write_text(text.replace(old, 'ROOT = Path(' + repr(str(S)) + ')'))
    spec = importlib.util.spec_from_file_location('bro_aa_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    mod = importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for mapper in ['mmc3', 'mmc5']:
        log = H / (mapper + '-build.log')
        with log.open('wb') as f:
            rc = subprocess.run([sys.executable, str(driver), '--mapper', mapper], cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
        row = dict(mapper=mapper, exit=rc, log_sha256=sha(log));report['builds'].append(row);save()
        assert rc == 0
        im = mod.Image(S / ('build/smb-crossover-' + mapper + '.nes'))
        oldim = mod.Image(P / ('source/build/smb-crossover-' + mapper + '.nes'))
        assert im.ram == oldim.ram and len(im.raw) == len(oldim.raw)
        assert im.raw[16 + 64 * 8192:] == oldim.raw[16 + 64 * 8192:]
        for name in ['MM3_AUDIO'] + [s['name'] for s in oldim.segs.values() if 'DPCM' in s['name']]:
            a = next(s for s in im.segs.values() if s['name'] == name)
            b = next(s for s in oldim.segs.values() if s['name'] == name)
            assert (a['start'], a['size'], a['ooffs']) == (b['start'], b['size'], b['ooffs'])
            assert im.raw[a['ooffs']:a['ooffs'] + a['size']] == oldim.raw[b['ooffs']:b['ooffs'] + b['size']]
        row.update(ROM_sha256=sha(im.path), RAM_exact=True, CHR_exact=True, audio_bytes_and_addresses_exact=True,
                   segments={n: next(s for s in im.segs.values() if s['name'] == n)
                             for n in ['GUEST', 'BILL_GFX', 'LEGACY_COLD', 'SAMUS', 'ROSTER', 'SPECIAL_EXTRA']})
        save()
    assert all(sha(S / n) == h for n, h in expected.items())
    report['source_hashes'] = expected
    report['status'] = 'PASS_PRIVATE_BOUNDED_HAMMERBRO_UNION_AA_BUILD_ONLY';save()
    print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
