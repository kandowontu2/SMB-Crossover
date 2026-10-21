"""Merge frozen Bill C2 into AI without replacing either ancestor's fixes."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = V / 'root49-easy-ryu-union-ai'
F = V / 'agent49-enemy-geometry-advanced-g'
B = V / 'agent49-enemy-geometry-f'
H = V / 'root49-easy-advanced-union-ao'
S = H / 'source'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode = True
    assert not H.exists()
    assert sha(P / 'report.json') == '01d1cff7c0075adc5bd74403a644379811e83a7f7921babd1910577c0185c55a'
    assert sha(F / 'freeze.json') == '9662d023b870f152b86d1f68b6b043af4091afd64879a253e4e45d43b91aa111'
    old = json.loads((P / 'report.json').read_text())
    frozen = json.loads((F / 'freeze.json').read_text())
    assert all(sha(F / n) == x['sha256'] for n, x in frozen['files'].items())
    assert all(sha(P / 'source' / n) == h for n, h in old['source_hashes'].items())
    changes = json.loads((F / 'candidate-c2/build-report.json').read_text())['source_changes']
    parent = json.loads((F / 'parent.json').read_text())
    assert set(changes) == set(parent['source_parent_files']) == {'src/megaman_weapons.s', 'src/roster_weapons.s', 'src/remaining_weapons.s'}
    assert sha(P / 'source/smb1base.cfg') == parent['root_owned_cfg_sha256']
    H.mkdir();shutil.copytree(P / 'source', S, ignore=shutil.ignore_patterns('build', '__pycache__'))
    expected = dict(old['source_hashes'])
    report = dict(status='MERGING_FROZEN_BILL_C2_OVER_AI', script_sha256=sha(__file__),
                  parent_report_sha256=sha(P / 'report.json'), source_freeze_sha256=sha(F / 'freeze.json'),
                  merges=[], builds=[], main_changed=False, accepted_release=False, goal_complete=False,
                  scope='Bill advanced geometry/origins/cache/order/spacing/reveal and Bro admission. Other documented advanced behavior gaps remain separate.')
    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for name, pair in changes.items():
        base = B / 'source' / name
        after = F / 'overlay-c2' / name
        assert sha(base) == pair['before'] == parent['source_parent_files'][name]
        assert sha(after) == pair['after'] == frozen['files'][after.relative_to(F).as_posix()]['sha256']
        folder = H / 'merges' / Path(name).stem;folder.mkdir(parents=True)
        paths = [folder / n for n in ['current.s', 'base.s', 'incoming.s']]
        for path, source in zip(paths, [S / name, base, after]):
            path.write_text(source.read_text())
        result = subprocess.run(['git', 'merge-file', '--stdout'] + [str(p) for p in paths], cwd=R, capture_output=True)
        merged = folder / 'merged.s';merged.write_bytes(result.stdout)
        report['merges'].append(dict(path=name, exit=result.returncode, current_sha256=sha(paths[0]),
                                     base_sha256=sha(paths[1]), incoming_sha256=sha(paths[2]), result_sha256=sha(merged)))
        save();assert result.returncode == 0, name
        shutil.copyfile(merged, S / name);expected[name] = sha(S / name)
    driver = H / 'build-driver.py'
    text = (P / 'build-driver.py').read_text()
    needle = 'ROOT = Path(' + repr(str(P / 'source')) + ')';assert text.count(needle) == 1
    driver.write_text(text.replace(needle, 'ROOT = Path(' + repr(str(S)) + ')'))
    spec = importlib.util.spec_from_file_location('advanced_ao_image', V / 'agent49g-samus-crouch-fix-proposal-b/image.py')
    m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    for mapper in ['mmc3', 'mmc5']:
        log = H / (mapper + '-build.log')
        with log.open('wb') as f:
            rc = subprocess.run([sys.executable, str(driver), '--mapper', mapper], cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
        row = dict(mapper=mapper, exit=rc, log_sha256=sha(log));report['builds'].append(row);save();assert rc == 0
        im = m.Image(S / 'build' / ('smb-crossover-' + mapper + '.nes'))
        prior = m.Image(P / 'source/build' / ('smb-crossover-' + mapper + '.nes'))
        assert im.ram == prior.ram and len(im.raw) == len(prior.raw)
        assert im.raw[:16] == prior.raw[:16] and im.raw[524304:] == prior.raw[524304:]
        audio = {}
        for b in prior.segs.values():
            name = b['name']
            if 'AUDIO' not in name and 'DPCM' not in name:
                continue
            a = next(s for s in im.segs.values() if s['name'] == name)
            assert (a['start'], a['size'], a['ooffs']) == (b['start'], b['size'], b['ooffs'])
            bb = prior.raw[b['ooffs']:b['ooffs'] + b['size']]
            assert im.raw[a['ooffs']:a['ooffs'] + a['size']] == bb
            audio[name] = dict(bytes=len(bb), sha256=hashlib.sha256(bb).hexdigest(), byte_and_address_equal=True)
        deltas, segments = {}, {}
        for b in prior.segs.values():
            name = b['name'];a = next(s for s in im.segs.values() if s['name'] == name)
            if a['size'] != b['size']:
                deltas[name] = a['size'] - b['size']
                segments[name] = a
        assert deltas == dict(GUEST=-176, SPECIAL_EXTRA=286, SPECIAL_ROSTER=-62, BILL_GFX=1303, LEGACY_COLD=953), deltas
        row.update(ROM_sha256=sha(im.path), RAM_exact=True, header_CHR_size_exact=True,
                   audio=audio, segment_deltas=deltas, segments=segments)
        save()
    assert len(expected) == 428 and all(sha(S / n) == h for n, h in expected.items())
    report.update(status='PASS_PRIVATE_ADVANCED_C2_AI_UNION_AO_BUILD_ONLY', source_hashes=expected)
    save();print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
